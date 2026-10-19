#!/usr/bin/env python3
"""Collecte automatique de flux RSS pour la veille BTS SIO SISR.
Exécution par GitHub Actions : aucune dépendance externe.
"""
import json
import re
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

OUT = Path("data/veille-rss.json")
FEEDS = [
    ("ZATAZ", "https://www.zataz.com/feed/"),
    ("DataBreaches.net", "https://databreaches.net/feed/"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
]

class TextOnly(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def clean(value, limit=180):
    if not value:
        return ""
    text = TextOnly()
    text.feed(value)
    return re.sub(r"\s+", " ", unescape(" ".join(text.parts))).strip()[:limit]

def normal_date(value):
    if not value:
        return ""
    try:
        d = parsedate_to_datetime(value)
    except (ValueError, TypeError, IndexError):
        try:
            d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return ""
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def classify(title, description=""):
    # Le titre prime sur l'extrait : évite les classements trompeurs.
    def from_text(text):
        value = text.lower()
        if re.search(r"fuite|exfiltrat|breach|leak|stolen data|compromised data|data exposure", value):
            return "breach"
        if re.search(r"vuln[ée]rab|faille|patch|cve-|flaw|zero.day|exploit", value):
            return "vuln"
        if re.search(r"ransom|cyberatta|pirat|hack|malware|phishing|attaque|attack", value):
            return "attack"
        return "general"
    title_category = from_text(title)
    return title_category if title_category != "general" else from_text(description)

def one(parent, name):
    node = parent.find(name)
    return node.text.strip() if node is not None and node.text else ""

def extract(xml, source):
    root = ET.fromstring(xml)
    result = []
    atom_ns = "{http://www.w3.org/2005/Atom}"
    rss = root.findall("./channel/item")
    atom = root.findall(f"{atom_ns}entry")
    for entry in rss[:35]:
        title = clean(one(entry, "title"), 190)
        desc = clean(one(entry, "description"), 190)
        link = one(entry, "link")
        date = normal_date(one(entry, "pubDate") or one(entry, "{http://purl.org/dc/elements/1.1/}date"))
        if urlsplit(link).scheme != "https" or not title:
            continue
        category = classify(title, desc)
        if source == "BleepingComputer" and category == "general" and "/news/security/" not in link:
            continue
        result.append({"title":title, "description":desc, "source":source, "link":link,
                       "published":date, "category":category})
    for entry in atom[:35]:
        title = clean(one(entry, f"{atom_ns}title"), 190)
        desc = clean(one(entry, f"{atom_ns}summary") or one(entry, f"{atom_ns}content"), 190)
        url = ""
        for tag in entry.findall(f"{atom_ns}link"):
            if tag.attrib.get("rel", "alternate") == "alternate":
                url = tag.attrib.get("href", "")
                break
        date = normal_date(one(entry, f"{atom_ns}published") or one(entry, f"{atom_ns}updated"))
        if urlsplit(url).scheme != "https" or not title:
            continue
        category = classify(title, desc)
        if source == "BleepingComputer" and category == "general" and "/news/security/" not in url:
            continue
        result.append({"title":title, "description":desc, "source":source, "link":url,
                       "published":date, "category":category})
    return result

def main():
    all_items, sources_ok, failed = [], [], []
    for name, url in FEEDS:
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; PortfolioBTS-RSS/1.0)",
                                        "Accept": "application/rss+xml, application/atom+xml, text/xml, */*"})
            with urlopen(req, timeout=18) as response:
                content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("Flux trop volumineux")
            current = extract(content, name)
            if not current:
                raise ValueError("Aucun article lisible")
            sources_ok.append(name)
            all_items.extend(current)
            print(f"{name}: {len(current)} articles")
        except Exception as exc:
            failed.append(name)
            print(f"{name}: {exc}", file=sys.stderr)
    if not all_items:
        raise SystemExit("Aucun flux disponible : données existantes conservées.")
    seen, items = set(), []
    for item in sorted(all_items, key=lambda a: a["published"], reverse=True):
        key = item["link"].split("#", 1)[0].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        items.append(item)
        if len(items) == 24:
            break
    OUT.parent.mkdir(parents=True, exist_ok=True)
    output = {"generated_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
              "sources_ok": sources_ok, "sources_unavailable":failed, "items":items}
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Enregistré {len(items)} articles dans {OUT}")

if __name__ == "__main__":
    main()
