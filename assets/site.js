/* Shared navigation + section renderer.
   A page sets window.PAGE = {id, kicker, title, lede, sections:[...]} in data/page-<id>.js,
   then loads this file. Section types: kpis, cards, table, steps, links, prose, note.
   To add a page: add an entry to NAV, create data/page-<id>.js and <id>.html. */
(function () {
  var NAV = [
    ['index', 'అవలోకనం', 'index.html'],
    ['karthika', 'కార్తీక పురాణం ప్యాక్', 'karthika.html'],
    ['production', 'నిర్మాణ మార్గదర్శి', 'production.html'],
    ['homams', 'హోమాలు & వ్రతాలు', 'homams.html'],
    ['team', 'బృందం & నియామకం', 'team.html'],
    ['growth', 'వృద్ధి & ఆదాయం', 'growth.html'],
    ['library', 'గ్రంథాలయం', 'library.html']
  ];
  var C = ['var(--c1)', 'var(--c2)', 'var(--c3)', 'var(--c6)', 'var(--c5)', 'var(--c7)', 'var(--c8)', 'var(--c4)'];
  function el(t, c, txt) { var e = document.createElement(t); if (c) e.className = c; if (txt != null) e.textContent = txt; return e; }
  function link(u, txt) { var a = el('a', '', txt); a.href = u; if (/^https?:/.test(u)) { a.target = '_blank'; a.rel = 'noopener'; } return a; }

  function nav(cur) {
    var n = el('nav', 'sx-nav'), i = el('div', 'sx-nav-in');
    var b = link('index.html', 'ధర్మ ప్రచార వేదిక'); b.className = 'sx-brand'; i.appendChild(b);
    NAV.forEach(function (x) { var a = link(x[2], x[1]); a.className = 'sx-l'; if (x[0] === cur) a.setAttribute('aria-current', 'page'); i.appendChild(a); });
    n.appendChild(i); return n;
  }
  function centerCur() { var a = document.querySelector('.sx-nav [aria-current]'); if (a && a.parentNode.scrollWidth > a.parentNode.clientWidth) a.parentNode.scrollLeft = a.offsetLeft - a.parentNode.clientWidth / 2 + a.offsetWidth / 2; }
  window.SX_NAV = function (cur) { var n = nav(cur); setTimeout(centerCur, 0); return n; };

  function searchBox(ph, onInput) { var s = el('input', 'sx-in'); s.type = 'search'; s.placeholder = ph || 'శోధించండి…'; s.addEventListener('input', function () { onInput(s.value.trim()); }); return s; }

  var R = {
    kpis: function (s, box) { var g = el('div', 'sx-kpis'); s.items.forEach(function (k) { var d = el('div', 'sx-kpi'); d.append(el('span', 'l', k.label), el('span', 'v', k.value)); if (k.note) d.append(el('span', 'n', k.note)); g.append(d); }); box.append(g); },
    note: function (s, box) { var d = el('div', 'sx-note'); d.textContent = s.text; box.append(d); },
    prose: function (s, box) { var d = el('div', 'sx-prose'); s.paras.forEach(function (p) { d.append(el('p', '', p)); }); box.append(d); },
    steps: function (s, box) {
      var ol = el('ol', 'sx-steps');
      s.items.forEach(function (it) { var li = el('li'); li.append(el('h4', '', it.title)); if (it.body) li.append(el('p', '', it.body)); var m = el('div', 'sx-meta'); (it.tags || []).forEach(function (t) { m.append(el('span', 'sx-pill', t)); }); if (m.childNodes.length) { m.style.marginTop = '6px'; li.append(m); } ol.append(li); });
      box.append(ol);
    },
    cards: function (s, box) {
      var tools, g = el('div', 'sx-grid'), cards = [];
      s.items.forEach(function (it, idx) {
        var c = el('div', 'sx-card'); c.style.setProperty('--c', it.color || C[(it.ci != null ? it.ci : idx) % C.length]);
        var h = el('div'); h.append(el('h3', '', it.title)); if (it.en) h.append(el('div', 'en', it.en)); c.append(h);
        if (it.meta && it.meta.length) { var m = el('div', 'sx-meta'); it.meta.forEach(function (t) { var cls = 'sx-pill'; if (t.charAt(0) === '!') { cls += ' warn'; t = t.slice(1); } m.append(el('span', cls, t)); }); c.append(m); }
        if (it.body) c.append(el('p', '', it.body));
        (it.groups || []).forEach(function (gr) { var hh = el('div', '', gr[0]); hh.style.cssText = 'font-size:.8rem;font-weight:600;margin-top:4px'; var ul = el('ul'); gr[1].forEach(function (b) { ul.append(el('li', '', b)); }); c.append(hh, ul); });
        if (it.bullets) { var ul = el('ul'); it.bullets.forEach(function (b) { ul.append(el('li', '', b)); }); c.append(ul); }
        if (it.links) { var lu = el('ul'); lu.style.listStyle = 'none'; lu.style.paddingLeft = '0'; it.links.forEach(function (l) { var li = el('li'); if (l.v) li.append(el('i', 'sx-v ' + l.v, l.v), document.createTextNode(' ')); li.append(link(l.u, l.l)); lu.append(li); }); c.append(lu); }
        c.dataset.text = [it.title, it.en, it.body, (it.meta || []).join(' '), (it.bullets || []).join(' ')].join(' ');
        c.dataset.filter = it.filter || ''; cards.push(c); g.append(c);
      });
      if (s.search || s.filters) {
        tools = el('div', 'sx-tools'); var q = '', f = 'all';
        var apply = function () { cards.forEach(function (c) { var ok = (!q || c.dataset.text.indexOf(q) >= 0) && (f === 'all' || c.dataset.filter === f); c.classList.toggle('sx-hide', !ok); }); };
        if (s.filters) { [['all', 'అన్నీ']].concat(s.filters).forEach(function (x) { var b = el('button', 'sx-chip', x[1]); b.type = 'button'; b.setAttribute('aria-pressed', String(x[0] === 'all')); b.onclick = function () { f = x[0]; tools.querySelectorAll('.sx-chip').forEach(function (z) { z.setAttribute('aria-pressed', String(z === b)); }); apply(); }; tools.append(b); }); }
        if (s.search) tools.append(searchBox(s.search, function (v) { q = v; apply(); }));
        box.append(tools);
      }
      box.append(g);
    },
    table: function (s, box) {
      var rows = s.rows.slice(), sortK = null, dir = 1, q = '', f = 'all';
      var wrap = el('div', 'sx-tbox'), t = el('table', 'sx-tbl'), th = el('thead'), tr = el('tr'), tb = el('tbody');
      s.columns.forEach(function (c) { var h = el('th', '', c[1]); h.onclick = function () { dir = sortK === c[0] ? -dir : 1; sortK = c[0]; draw(); }; tr.append(h); });
      th.append(tr); t.append(th, tb); wrap.append(t);
      function draw() {
        var list = rows.filter(function (r) { return (!q || JSON.stringify(r).indexOf(q) >= 0) && (f === 'all' || r[s.filterKey] === f); });
        if (sortK) list.sort(function (a, b) { var x = a[sortK], y = b[sortK]; return (typeof x === 'number' && typeof y === 'number' ? x - y : String(x).localeCompare(String(y))) * dir; });
        tb.replaceChildren.apply(tb, list.map(function (r) {
          var row = el('tr'); if (r._dim) row.style.opacity = '.55'; if (r._bold) row.style.fontWeight = '600';
          s.columns.forEach(function (c) { var v = r[c[0]], td = el('td', c[2] === 'num' ? 'num' : ''); if (c[2] === 'link' && v) td.append(link(v, 'లింక్ ↗')); else if (c[2] === 'num' && typeof v === 'number') td.textContent = v.toLocaleString('en-IN'); else td.textContent = v == null ? '' : v; row.append(td); });
          return row;
        }));
      }
      if (s.search || s.filterKey) {
        var tools = el('div', 'sx-tools');
        if (s.filterKey) { var vals = ['all'].concat(Array.from(new Set(rows.map(function (r) { return r[s.filterKey]; })))); vals.forEach(function (v) { var b = el('button', 'sx-chip', v === 'all' ? 'అన్నీ' : v); b.type = 'button'; b.setAttribute('aria-pressed', String(v === 'all')); b.onclick = function () { f = v; tools.querySelectorAll('.sx-chip').forEach(function (z) { z.setAttribute('aria-pressed', String(z === b)); }); draw(); }; tools.append(b); }); }
        if (s.search) tools.append(searchBox(s.search, function (v) { q = v; draw(); }));
        box.append(tools);
      }
      box.append(wrap); draw();
    },
    links: function (s, box) {
      var g = el('div', 'sx-links'), items = [];
      s.groups.forEach(function (gr, i) {
        var c = el('div', 'sx-card'); c.style.setProperty('--c', C[i % C.length]); c.append(el('h3', '', gr.name)); if (gr.note) c.append(el('p', '', gr.note));
        var ul = el('ul'); gr.links.forEach(function (l) { var li = el('li'); li.append(el('i', 'sx-v ' + (l.v || 'L'), l.v || 'L'), link(l.u, l.l)); li.dataset.text = l.l + ' ' + gr.name; items.push(li); ul.append(li); });
        c.append(ul); g.append(c);
      });
      if (s.search) { var tools = el('div', 'sx-tools'); tools.append(searchBox(s.search, function (q) { items.forEach(function (li) { li.classList.toggle('sx-hide', !!q && li.dataset.text.indexOf(q) < 0); }); })); box.append(tools); }
      box.append(g);
    }
  };

  function render(P) {
    document.body.prepend(nav(P.id)); setTimeout(centerCur, 0);
    var root = document.getElementById('sx'); root.classList.add('has-toc');
    var toc = el('aside', 'sx-toc'), main = el('main', 'sx-main');
    var hero = el('header', 'sx-hero'); hero.append(el('div', 'k', P.kicker || 'సనాతన ధర్మ ప్రచార వేదిక'), el('h1', '', P.title)); if (P.lede) hero.append(el('p', '', P.lede)); main.append(hero);
    P.sections.forEach(function (s, i) {
      var id = s.id || ('s' + i), sec = el('section', 'sx-sec'); sec.id = id;
      if (s.title) { sec.append(el('h2', '', s.title)); var a = link('#' + id, s.title); toc.append(a); }
      if (s.sub) sec.append(el('p', 'sub', s.sub));
      try { R[s.type](s, sec); } catch (e) { sec.append(el('div', 'sx-note', 'విభాగం లోడ్ కాలేదు: ' + e.message)); }
      main.append(sec);
    });
    root.append(toc, main);
    var foot = el('footer', 'sx-foot', P.foot || 'పంచాంగ తేదీలను ముద్రిత తెలుగు పంచాంగంతో, ధరలను స్థానిక కోట్‌లతో నిర్ధారించండి. గ్రంథ లింకులు మూడవ పక్ష సైట్లు – ఆధునిక అనువాదాలు/రికార్డింగ్‌లకు కాపీరైట్ ఉండవచ్చు.');
    document.body.append(foot);
    if ('IntersectionObserver' in window) {
      var links = toc.querySelectorAll('a');
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); }); }); }, { rootMargin: '-40% 0px -55% 0px' });
      main.querySelectorAll('.sx-sec').forEach(function (s) { io.observe(s); });
    }
  }
  if (window.PAGE) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { render(window.PAGE); }); else render(window.PAGE); }
})();
