#!/usr/bin/env python3
"""Veille BTS SIO : Wazuh RSS, versions GitHub, avis sécurité et CERT-FR."""
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from html import unescape

OUT = Path("data/veille-wazuh.json")
FEEDS = [
    ("Blog officiel Wazuh", "https://wazuh.com/feed/", "feature"),
    ("Wazuh GitHub Releases", "https://github.com/wazuh/wazuh/releases.atom", "version"),
    ("CERT-FR – avis", "https://www.cert.ssi.gouv.fr/avis/feed/", "security"),
]
UA = {"User-Agent": "Mozilla/5.0 (BTS-SISR Wazuh Watch)", "Accept": "application/rss+xml, application/atom+xml, application/json, */*"}
class Plain(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.parts=[]
    def handle_data(self, s): self.parts.append(s)
def clean(s):
    v=Plain()
    try:v.feed(s or "")
    except Exception:return ""
    return re.sub(r"\s+"," ",unescape(" ".join(v.parts))).strip()[:210]
def iso(value):
    if not value:return ""
    try:d=parsedate_to_datetime(value)
    except (ValueError,TypeError,IndexError):
        try:d=datetime.fromisoformat(value.replace("Z","+00:00"))
        except (TypeError,ValueError):return ""
    if d.tzinfo is None:d=d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat().replace("+00:00","Z")
def load(url):
    with urlopen(Request(url,headers=UA),timeout=18) as response:data=response.read(1_000_001)
    if len(data)>1_000_000:raise ValueError("Flux trop volumineux")
    return data
def category(title,desc,default):
    t=(title+" "+desc).lower()
    if re.search(r"cve-\d|ghsa-|vulnerab|security advisory|exploit|patch|faille|vulnérab",t):return "security"
    if re.search(r"release|version|v\d+\.\d+|upgrade",title.lower()):return "version"
    return default
def extract(data,name,default):
    root=ET.fromstring(data); atom="{http://www.w3.org/2005/Atom}"
    entries=root.findall("./channel/item")+root.findall(atom+"entry")
    articles=[]
    for e in entries[:50]:
        def field(tag):
            v=e.find(tag);return v.text.strip() if v is not None and v.text else ""
        title=clean(field("title") or field(atom+"title"))
        desc=clean(field("description") or field(atom+"summary") or field(atom+"content"))
        url=field("link")
        if not url:
            for link in e.findall(atom+"link"):
                if link.attrib.get("rel","alternate")=="alternate":
                    url=link.attrib.get("href","");break
        published=iso(field("pubDate") or field(atom+"published") or field(atom+"updated"))
        if not title or urlsplit(url).scheme!="https":continue
        if name.startswith("CERT-FR") and "wazuh" not in (title+" "+desc).lower():continue
        articles.append({"title":title,"description":desc,"source":name,"link":url,"published":published,"category":category(title,desc,default)})
    return articles
def main():
    previous={}
    if OUT.exists():
        try:previous=json.loads(OUT.read_text(encoding="utf-8"))
        except (ValueError,OSError):pass
    now=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    articles=[];sources=[]
    for name,url,kind in FEEDS:
        try:
            current=extract(load(url),name,kind);articles.extend(current)
            state="OK";info=("Versions et correctifs" if kind=="version" else "Avis liés à Wazuh" if kind=="security" else "Actualités et fonctionnalités")
            print(name,len(current))
        except Exception as error:
            state="Indisponible";info="Collecte impossible : "+str(error)[:70]
            print(name,error,file=sys.stderr)
        sources.append({"name":name,"url":url,"checked":now,"status":state,"selected":info})
    try:
        advisories=json.loads(load("https://api.github.com/repos/wazuh/wazuh/security-advisories?per_page=30"))
        if not isinstance(advisories,list):raise ValueError("Réponse non exploitable")
        for a in advisories:
            title=clean(a.get("summary") or a.get("ghsa_id") or "")
            link=a.get("html_url","")
            if title and urlsplit(link).scheme=="https":
                articles.append({"title":title,"description":clean(a.get("description")),"source":"Wazuh GitHub Advisories","link":link,"published":iso(a.get("published_at")),"category":"security"})
        state="OK"
    except Exception as error:
        state="Accès API non confirmé"
        print("GitHub advisories",error,file=sys.stderr)
    sources.append({"name":"Wazuh GitHub Advisories","url":"https://github.com/wazuh/wazuh/security/advisories","checked":now,"status":state,"selected":"Vulnérabilités officielles"})
    all_articles=articles+previous.get("items",[])
    distinct=set();items=[]
    for a in sorted(all_articles,key=lambda x:x.get("published",""),reverse=True):
        url=a.get("link","")
        if not url.startswith("https://") or url in distinct or not a.get("title"):continue
        distinct.add(url);items.append(a)
        if len(items)>=100:break
    if not items:raise SystemExit("Aucune publication, anciennes données conservées.")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps({"topic":"Wazuh SIEM/XDR","generated_at":now,"sources":sources,"items":items},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Index généré :",len(items),"publications.")
if __name__=="__main__":main()
