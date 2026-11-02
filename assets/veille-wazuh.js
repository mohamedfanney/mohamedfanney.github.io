(function(){
"use strict";
var search=document.getElementById("vwSearchForm");if(!search)return;
var input=document.getElementById("vwInput"),list=document.getElementById("vwResults"),status=document.getElementById("vwStatus");
var more=document.getElementById("vwMore"),table=document.querySelector("#vwSources tbody"),webLink=document.getElementById("vwWebSearch");
var items=[],sources=[],date="",filter="all",limit=8;
function safe(url){try{var u=new URL(url);return u.protocol==="https:"?u.href:""}catch(e){return ""}}
function normalize(x){return String(x||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase()}
function dstr(x){var d=new Date(x);return x&&!isNaN(d.getTime())?d.toLocaleDateString("fr-FR",{day:"2-digit",month:"short",year:"numeric"}):"Non daté"}
var categories={version:"Version",security:"Sécurité",feature:"Fonctionnalité",general:"Actualité"};
var modal=document.createElement("dialog");modal.className="vw-detail-dialog";modal.setAttribute("aria-label","Détail de la publication");
modal.innerHTML='<div class="vw-detail-inner"><div class="vw-dialog-top"><span class="vw-tag">PUBLICATION · SOURCE</span><button type="button" aria-label="Fermer">✕</button></div><h3></h3><span class="vw-tag" id="vwMeta"></span><p id="vwText"></p><p class="vw-reco">Piste d’analyse : vérifier les versions concernées, la portée des risques et les correctifs sur la source officielle ; tester avant tout déploiement. Cette piste ne constitue pas une analyse personnelle validée.</p><a target="_blank" rel="noopener noreferrer" id="vwOriginal">Lire la source originale ↗</a></div>';
document.body.appendChild(modal);modal.querySelector("button").onclick=function(){modal.close()};
modal.addEventListener("click",function(e){if(e.target===modal)modal.close()});
function show(item){
modal.querySelector("h3").textContent=item.title;
modal.querySelector("#vwMeta").textContent=(item.source||"Source")+" · "+dstr(item.published)+" · "+(categories[item.category]||"Actualité");
modal.querySelector("#vwText").textContent=item.description||"Consultez la source pour davantage d'informations.";
var link=modal.querySelector("#vwOriginal");link.href=safe(item.link)||"https://documentation.wazuh.com/current/";
if(typeof modal.showModal==="function")modal.showModal();else window.open(link.href,"_blank","noopener,noreferrer");
}
function render(){
var terms=normalize(input.value).trim().split(/\s+/).filter(Boolean);
var filtered=items.filter(function(x){if(filter!=="all"&&x.category!==filter)return false;var hay=normalize([x.title,x.description,x.source,x.version||""].join(" "));return terms.every(function(t){return hay.includes(t)})});
list.replaceChildren();
filtered.slice(0,limit).forEach(function(item){
var b=document.createElement("button");b.className="vw-hit";b.type="button";
var badge=document.createElement("span");badge.className="vw-tag";badge.textContent=categories[item.category]||"Actualité";
var t=document.createElement("b");t.textContent=item.title||"Publication";
var p=document.createElement("span");p.className="desc";p.textContent=item.description||"Ouvrir pour consulter la source.";
var meta=document.createElement("span");meta.className="vw-tag";meta.textContent=(item.source||"Source")+" · "+dstr(item.published);
b.append(badge,t,p,meta);b.onclick=function(){show(item)};list.append(b);
});
if(!filtered.length){var empty=document.createElement("p");empty.textContent="Aucun résultat dans les publications indexées. Essayez un autre mot-clé ou la recherche Web.";empty.className="vw-info";list.append(empty)}
status.textContent=filtered.length+" résultat(s) sur "+items.length+" publication(s) indexée(s)"+(date?" · Collecte : "+dstr(date):" · Première collecte programmée");
more.hidden=filtered.length<=limit;
webLink.href="https://www.google.com/search?q="+encodeURIComponent((input.value.trim()||"Wazuh")+" site:wazuh.com OR site:github.com/wazuh OR site:cert.ssi.gouv.fr");
}
function renderSources(){
table.replaceChildren();
sources.forEach(function(s){
var tr=document.createElement("tr"),td=document.createElement("td"),link=document.createElement("a");
link.href=safe(s.url)||"https://wazuh.com/";link.target="_blank";link.rel="noopener noreferrer";link.textContent=s.name;td.append(link);tr.append(td);
["6 h (auto), 1 semaine (analyse)",s.checked?dstr(s.checked):"À initialiser",(s.selected||"Source suivie")+" · "+(s.status||"À vérifier")].forEach(function(v){var c=document.createElement("td");c.textContent=v;tr.append(c)});table.append(tr);
});
}
search.addEventListener("submit",function(e){e.preventDefault();limit=8;render()});input.addEventListener("input",function(){limit=8;render()});
document.querySelectorAll("[data-vw-suggest]").forEach(function(b){b.onclick=function(){input.value=b.dataset.vwSuggest;limit=8;render();input.focus()}});
document.querySelectorAll("[data-vw-filter]").forEach(function(b){b.onclick=function(){filter=b.dataset.vwFilter;limit=8;document.querySelectorAll("[data-vw-filter]").forEach(function(t){t.setAttribute("aria-pressed",String(t===b))});render()}});
more.onclick=function(){limit+=8;render()};
fetch("data/veille-wazuh.json?v="+Date.now(),{cache:"no-store"}).then(function(r){if(!r.ok)throw Error("HTTP");return r.json()}).then(function(data){
items=(Array.isArray(data.items)?data.items:[]).filter(function(x){return x&&x.title&&safe(x.link)}).slice(0,100);
items.sort(function(a,b){return(Date.parse(b.published)||0)-(Date.parse(a.published)||0)});
sources=Array.isArray(data.sources)?data.sources:[];date=data.generated_at||"";renderSources();render();
}).catch(function(){status.textContent="Index temporairement indisponible. Ouvrez les sources officielles.";render()});
})();