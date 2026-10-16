var FIRST_ID = (document.querySelector('.hm-section') || { id: '' }).id;

(function(){
  var app = document.getElementById('hm-app');
  var nav = document.getElementById('hm-nav');
  var content = document.getElementById('hm-content');
  var search = document.getElementById('hm-search');
  var hits = document.getElementById('hm-hits');
  var secs = Array.prototype.slice.call(document.querySelectorAll('.hm-section'));
  var index = [];

  secs.forEach(function(sec){
    var grp = document.createElement('div');
    grp.className = 'hm-navgroup';
    var top = document.createElement('a');
    top.className = 'hm-navtop';
    top.href = '#' + sec.id;
    top.setAttribute('data-target', sec.id);
    top.textContent = sec.getAttribute('data-title');
    grp.appendChild(top);
    var subsWrap = document.createElement('div');
    subsWrap.className = 'hm-navsubs';
    var subs = [];
    var hs = sec.querySelectorAll('h2[id]');
    for (var i = 0; i < hs.length; i++) {
      var h = hs[i];
      var a = document.createElement('a');
      a.className = 'hm-navsub';
      a.href = '#' + h.id;
      a.setAttribute('data-target', sec.id);
      a.setAttribute('data-sub', h.id);
      a.textContent = h.textContent;
      subsWrap.appendChild(a);
      var txt = h.textContent;
      var n = h.nextElementSibling;
      while (n && n.tagName !== 'H2') { if (!n.classList.contains('hm-diagram')) { txt += ' ' + n.textContent; } n = n.nextElementSibling; }
      subs.push({ el: a, text: txt.toLowerCase() });
    }
    grp.appendChild(subsWrap);
    nav.appendChild(grp);
    var lead = '';
    var c = sec.firstElementChild;
    while (c && c.tagName !== 'H2') { lead += ' ' + c.textContent; c = c.nextElementSibling; }
    index.push({ grp: grp, top: top, title: sec.getAttribute('data-title').toLowerCase(), lead: lead.toLowerCase(), subs: subs });
  });

  function showSection(id, subId){
    for (var i = 0; i < secs.length; i++) { secs[i].classList.toggle('active', secs[i].id === id); }
    var tops = nav.querySelectorAll('.hm-navtop');
    for (var j = 0; j < tops.length; j++) {
      var on = tops[j].getAttribute('data-target') === id;
      tops[j].classList.toggle('active', on);
      if (!search.value.trim()) { tops[j].parentNode.classList.toggle('open', on); }
    }
    var subs = nav.querySelectorAll('.hm-navsub');
    for (var k = 0; k < subs.length; k++) { subs[k].classList.toggle('active', !!subId && subs[k].getAttribute('data-sub') === subId); }
    content.scrollTop = 0;
    if (subId) {
      var el = document.getElementById(subId);
      if (el) { setTimeout(function(){ el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 60); }
    }
    app.classList.remove('nav');
    try { history.replaceState(null, '', '#' + (subId || id)); } catch (e) { }
  }

  function go(a){ showSection(a.getAttribute('data-target'), a.getAttribute('data-sub')); }

  nav.addEventListener('click', function(e){
    var a = e.target.closest('.hm-navsub, .hm-navtop');
    if (!a) { return; }
    e.preventDefault();
    go(a);
  });
  content.addEventListener('click', function(e){
    var a = e.target.closest('a[data-target]');
    if (a) { e.preventDefault(); go(a); return; }
    var img = e.target.closest('.hm-content img');
    if (img) { openZoom(img); }
  });

  search.addEventListener('input', function(){
    var q = search.value.trim().toLowerCase();
    var groups = 0;
    var count = 0;
    index.forEach(function(g){
      var topMatch = !q || g.title.indexOf(q) >= 0 || g.lead.indexOf(q) >= 0;
      var any = false;
      g.subs.forEach(function(s){
        var m = q && s.text.indexOf(q) >= 0;
        s.el.style.display = (!q || m || (q && g.title.indexOf(q) >= 0)) ? '' : 'none';
        if (m) { any = true; count++; }
      });
      var show = !q || topMatch || any;
      g.grp.style.display = show ? '' : 'none';
      if (show && q) { groups++; }
      if (q) { g.grp.classList.toggle('open', show); }
    });
    if (!q) {
      var act = nav.querySelector('.hm-navtop.active');
      index.forEach(function(g){ g.grp.classList.toggle('open', g.top === act); });
      hits.textContent = '';
    } else {
      hits.textContent = groups ? count + ' topic' + (count === 1 ? '' : 's') + ' in ' + groups + ' chapter' + (groups === 1 ? '' : 's') : 'Nothing found';
    }
  });
  search.addEventListener('keydown', function(e){
    if (e.key === 'Enter') {
      var first = nav.querySelector('.hm-navgroup:not([style*="none"]) .hm-navsub:not([style*="none"])') || nav.querySelector('.hm-navgroup:not([style*="none"]) .hm-navtop');
      if (first) { go(first); }
    }
    if (e.key === 'Escape') { search.value = ''; search.dispatchEvent(new Event('input')); }
  });

  var zoom = document.getElementById('hm-zoom');
  var zimg = document.getElementById('hm-zoomimg');
  function openZoom(img){ zimg.src = img.src; zimg.alt = img.alt; zoom.classList.add('open'); }
  zoom.addEventListener('click', function(){ zoom.classList.remove('open'); zimg.removeAttribute('src'); });
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && zoom.classList.contains('open')) { zoom.classList.remove('open'); zimg.removeAttribute('src'); } });

  document.getElementById('hm-menu').addEventListener('click', function(){ app.classList.toggle('nav'); });
  document.getElementById('hm-scrim').addEventListener('click', function(){ app.classList.remove('nav'); });

  var start = FIRST_ID, startSub = null;
  var hash = (location.hash || '').replace('#', '');
  if (hash) {
    var t = document.getElementById(hash);
    if (t) {
      var s = t.closest('.hm-section');
      if (s) { start = s.id; startSub = t.tagName === 'H2' ? t.id : null; }
    }
  }
  showSection(start, startSub);
})();
