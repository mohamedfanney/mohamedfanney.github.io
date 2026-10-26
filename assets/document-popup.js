(function(){
'use strict';
var dialog=document.getElementById('documentDialog');
if(!dialog)return;
var heading=dialog.querySelector('#documentDialogTitle');
var frame=dialog.querySelector('iframe');
var openLink=dialog.querySelector('[data-document-open]');
var download=dialog.querySelector('[data-document-download]');
var close=dialog.querySelector('[data-document-close]');
var priorFocus=null;
document.addEventListener('click',function(e){
var trigger=e.target.closest('[data-document-popup]'); if(!trigger)return;
var raw=trigger.getAttribute('href'); if(!raw)return;
var url;try{url=new URL(raw,document.baseURI)}catch(error){return}
if(url.origin!==location.origin||!/^https?:$/.test(url.protocol)||typeof dialog.showModal!=='function')return;
e.preventDefault();priorFocus=trigger;
var name=trigger.getAttribute('data-document-title')||trigger.textContent.trim()||'Document';
var pdf=/\.pdf$/i.test(url.pathname);
heading.textContent=name;openLink.href=url.href;download.hidden=!pdf;
if(pdf){download.href=url.href;download.setAttribute('download',url.pathname.split('/').pop());}
else{download.removeAttribute('href');download.removeAttribute('download');}
frame.title=(pdf?'PDF : ':'Fiche : ')+name;
frame.src=pdf?url.href+'#toolbar=1&navpanes=0':url.href;
document.body.style.overflow='hidden';
dialog.showModal();close.focus();
});
close.addEventListener('click',function(){dialog.close()});
dialog.addEventListener('close',function(){frame.removeAttribute('src');document.body.style.overflow='';if(priorFocus&&typeof priorFocus.focus==='function')priorFocus.focus();priorFocus=null});
dialog.addEventListener('click',function(e){if(e.target===dialog)dialog.close()});
})();