/* Giấc ngủ cho con — điều hướng, bộ lọc, bốn công cụ.
   Không gọi ra mạng. Dữ liệu nằm trong localStorage của trình duyệt này. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var qsa = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  };
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };
  var store = {
    get: function (k, d) {
      try { var v = localStorage.getItem('gn.' + k); return v ? JSON.parse(v) : d; }
      catch (e) { return d; }
    },
    set: function (k, v) {
      try { localStorage.setItem('gn.' + k, JSON.stringify(v)); } catch (e) {}
      push(k, v);
    }
  };
  /* Khi trang chạy như một Artifact thì đồng bộ thêm lên server,
     để mở ở máy khác vẫn thấy. Không có thì chỉ dùng localStorage. */
  var DB = null, RELOAD = [], timers = {};
  function localAt(k) {
    try { return +localStorage.getItem('gn.at.' + k) || 0; } catch (e) { return 0; }
  }
  function push(k, v) {
    var at = Date.now();
    try { localStorage.setItem('gn.at.' + k, String(at)); } catch (e) {}
    if (!DB) return;
    clearTimeout(timers[k]);
    timers[k] = setTimeout(function () {
      try { DB.doc('data/' + k).set({ v: v, at: at }); } catch (e) {}
    }, 800);
  }
  /* bỏ dấu để tìm kiếm gõ không dấu vẫn ra */
  function fold(s) {
    return String(s).toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/đ/g, 'd');
  }

  /* ================= điều hướng ================= */
  var SECS = qsa('main section');
  var navOl = $('chnav'), side = $('side'), scrim = $('scrim'), burger = $('burger'),
      nowEl = $('now'), ofEl = $('of'), pager = $('pager');
  var MAP = {}, cur = null, spy = null;

  /* nhãn phân cách trong mục lục chương 02 */
  var DIVIDERS = {
    'Sáu việc của bố mẹ': 'Trước khi ăn dặm · 0–6 tháng',
    'Bốn giai đoạn': 'Trong khi ăn dặm · 6–18 tháng'
  };

  SECS.forEach(function (sec, si) {
    var picks = [];
    qsa('h3', sec).forEach(function (el, hi) {
      if (el.classList.contains('scen-g') || el.classList.contains('food-g')) return;
      var lab = el.textContent.replace(/\s+/g, ' ').trim();
      if (!lab) return;
      var id = el.id || (sec.id + '--' + hi);
      el.id = id; el.classList.add('anchor');
      picks.push({ id: id, label: lab });
    });
    MAP[sec.id] = { sec: sec, idx: si, title: sec.dataset.title || sec.id, picks: picks };
  });

  navOl.innerHTML = SECS.map(function (sec, i) {
    var m = MAP[sec.id];
    var pinned = sec.id === 'nghen';
    var subs = m.picks.map(function (p) {
      var d = DIVIDERS[p.label]
        ? '<li class="divider">' + esc(DIVIDERS[p.label]) + '</li>' : '';
      return d + '<li><a href="#' + p.id + '" data-jump="' + p.id + '">' + esc(p.label) + '</a></li>';
    }).join('');
    return '<li data-sec="' + sec.id + '">' +
      '<button type="button" class="ch-btn" data-go="' + sec.id + '" aria-current="false">' +
      '<span class="n">' + (pinned ? '⚠' : pad(i)) + '</span><span>' + esc(m.title) + '</span></button>' +
      (subs && !pinned ? '<ul class="sub-list">' + subs + '</ul>' : '') + '</li>';
  }).join('');

  function watch(sec) {
    if (spy) spy.disconnect();
    var as = qsa('.anchor', sec);
    if (!as.length || !window.IntersectionObserver) return;
    spy = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        qsa('.sub-list a', navOl).forEach(function (l) { l.classList.remove('on'); });
        var hit = navOl.querySelector('.sub-list a[data-jump="' + e.target.id + '"]');
        if (hit) hit.classList.add('on');
      });
    }, { rootMargin: '-12% 0px -74% 0px', threshold: 0 });
    as.forEach(function (a) { spy.observe(a); });
  }

  function buildPager(i) {
    var p = SECS[i - 1], n = SECS[i + 1];
    pager.innerHTML =
      (p ? '<button class="pg" type="button" data-go="' + p.id + '"><small>Trước</small><b>' + esc(MAP[p.id].title) + '</b></button>' : '<span></span>') +
      (n ? '<button class="pg pg--next" type="button" data-go="' + n.id + '"><small>Tiếp</small><b>' + esc(MAP[n.id].title) + '</b></button>' : '<span></span>');
  }

  function show(id, anchor, push) {
    var m = MAP[id]; if (!m) return;
    if (cur !== id) {
      SECS.forEach(function (s) { s.classList.toggle('live', s.id === id); });
      qsa('li', navOl).forEach(function (li) {
        if (!li.hasAttribute('data-sec')) return;
        var on = li.getAttribute('data-sec') === id;
        li.classList.toggle('on', on);
        li.querySelector('.ch-btn').setAttribute('aria-current', on ? 'true' : 'false');
      });
      nowEl.textContent = m.title;
      ofEl.textContent = (m.idx === 0 ? '⚠' : pad(m.idx)) + ' / ' + pad(SECS.length - 1);
      buildPager(m.idx); watch(m.sec); cur = id;
    }
    if (push !== false) { try { history.replaceState(null, '', '#' + (anchor || id)); } catch (e) {} }
    var t = anchor ? document.getElementById(anchor) : null;
    if (t) {
      var off = (innerWidth < 900 ? 66 : 14);
      var y = t.getBoundingClientRect().top + scrollY - off;
      scrollTo(0, y);
    } else { scrollTo(0, 0); }
  }

  function closeSide() { side.classList.remove('open'); if (scrim) scrim.classList.remove('on'); burger.setAttribute('aria-expanded', 'false'); }

  document.addEventListener('click', function (e) {
    var go = e.target.closest('[data-go]');
    if (go) { show(go.getAttribute('data-go')); closeSide(); return; }
    var jump = e.target.closest('[data-jump]');
    if (jump) {
      e.preventDefault();
      var id = jump.getAttribute('data-jump');
      var el = document.getElementById(id);
      var sec = el && el.closest ? el.closest('section') : null;
      show(sec ? sec.id : id.split('--')[0], id); closeSide(); return;
    }
  });
  burger.addEventListener('click', function () {
    var open = side.classList.toggle('open');
    if (scrim) scrim.classList.toggle('on', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  if ($('sidex')) $('sidex').addEventListener('click', closeSide);
  if (scrim) scrim.addEventListener('click', closeSide);

  /* ================= bộ lọc giai đoạn — chương 02 ================= */
  (function () {
    var box = $('stagebox'); if (!box) return;
    var nowEl2 = $('stage-now');
    var NAMES = { 1: '5–6 tháng · TẬP NUỐT', 2: '7–8 tháng · TẬP NHÁ',
                  3: '9–11 tháng · TẬP NHAI', 4: '12–18 tháng · ĂN CÙNG MÂM' };
    function apply(st) {
      qsa('.chip', box).forEach(function (c) {
        c.classList.toggle('on', !!st && c.getAttribute('data-stage') === String(st));
      });
      qsa('[data-stage]', document).forEach(function (el) {
        if (el.classList.contains('chip')) return;
        var s = +el.getAttribute('data-stage');
        el.hidden = !!st && s !== st && s !== st + 1;
        el.classList.toggle('now', !!st && s === st);
        el.classList.toggle('dim', !!st && s === st + 1);
      });
      nowEl2.innerHTML = st
        ? 'Đang xem: <b>' + esc(NAMES[st]) + '</b>' + (NAMES[st + 1] ? ' — và mốc kế tiếp ở dưới.' : '')
        : 'Đang xem tất cả bốn giai đoạn. Chưa chắc con ở đâu thì chọn theo <b>việc con làm được</b> — chính xác hơn theo tuổi.';
      store.set('stage', st || 0);
    }
    qsa('.chip', box).forEach(function (c) {
      c.addEventListener('click', function () {
        var s = +c.getAttribute('data-stage');
        apply(c.classList.contains('on') ? 0 : s);
      });
    });
    $('stage-all').addEventListener('click', function () { apply(0); });
    apply(store.get('stage', 0));
  })();

  /* ================= tìm trong chương ================= */
  (function () {
    qsa('.docsearch').forEach(function (box) {
      var sec = box.closest('section'); if (!sec) return;
      var q = box.querySelector('.doc-q'), count = box.querySelector('.doc-count');
      var kids = [].slice.call(sec.children);
      /* đơn vị lọc: hàng trong .grp, hàng bảng, đoạn văn, và các khối
         không có hàng (.card / .sos) thì lọc nguyên khối theo chữ của nó */
      var units = qsa('.rows > li, tbody tr', sec)
        .concat(kids.filter(function (e) {
          return e.tagName === 'P' || e.classList.contains('card')
            || e.classList.contains('sos') || e.classList.contains('src');
        }));
      /* danh sách gạch đầu dòng nằm trực tiếp trong chương: lọc từng dòng */
      var lists = kids.filter(function (e) { return e.tagName === 'UL'; });
      lists.forEach(function (ul) {
        units = units.concat([].slice.call(ul.children));
      });
      var wraps = qsa('.grp, .tw', sec).concat(lists);
      var rules = kids.filter(function (e) { return e.tagName === 'HR'; });
      var empty = document.createElement('p');
      empty.className = 'empty'; empty.hidden = true;
      empty.textContent = 'Không có dòng nào khớp. Thử một từ ngắn hơn.';
      box.parentNode.insertBefore(empty, box.nextSibling);

      function heads(on) {
        for (var i = 0; i < kids.length; i++) {
          var el = kids[i], tag = el.tagName;
          if (tag !== 'H3' && tag !== 'H4') continue;
          if (!on) { el.hidden = false; continue; }
          var lvl = tag === 'H3' ? 3 : 4, any = false;
          for (var j = i + 1; j < kids.length; j++) {
            var t2 = kids[j].tagName;
            if (t2 === 'H3' || (lvl === 4 && t2 === 'H4')) break;
            if (t2 === 'H3' || t2 === 'H4') continue;
            if (!kids[j].hidden) { any = true; break; }
          }
          el.hidden = !any;
        }
      }

      function run() {
        var t = fold(q.value.trim()), on = !!t, n = 0;
        units.forEach(function (el) {
          if (el === empty) return;
          var ok = !on || fold(el.textContent).indexOf(t) > -1;
          el.hidden = !ok; if (ok && on) n++;
          if (!ok) { var d = el.querySelector && el.querySelector('details'); if (d) d.open = false; }
        });
        wraps.forEach(function (w) {
          var us = w.tagName === 'UL'
            ? [].slice.call(w.children)
            : qsa('.rows > li, tbody tr', w);
          w.hidden = on && us.length > 0 && !us.some(function (u) { return !u.hidden; });
        });
        rules.forEach(function (r) { r.hidden = on; });
        heads(on);
        empty.hidden = !on || n > 0;
        count.textContent = on ? n + ' dòng' : '';
      }
      q.addEventListener('input', run);
      q.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { q.value = ''; run(); }
      });
      run();
    });
  })();

  /* ================= tìm kiếm kịch bản — lọc theo tuổi và nhóm ================= */
  (function () {
    var box = $('scenbox'); if (!box) return;
    var q = $('scen-q'), count = $('scen-count');
    var items = qsa('.scen'), ghs = qsa('.scen-g'), ahs = qsa('.scen-a');
    var fa = '', fg = '';
    var empty = document.createElement('p');
    empty.className = 'empty'; empty.hidden = true;
    empty.textContent = 'Không có kịch bản nào khớp. Bỏ bớt một nút lọc, hoặc gõ từ ngắn hơn.';
    $('scenlist').appendChild(empty);

    function run() {
      var t = fold(q.value.trim()), n = 0;
      items.forEach(function (el) {
        var ok = (!fa || el.getAttribute('data-age') === fa) &&
                 (!fg || el.getAttribute('data-group') === fg) &&
                 (!t || fold(el.getAttribute('data-text')).indexOf(t) > -1);
        el.hidden = !ok; if (ok) n++;
        if (!ok) el.open = false;
      });
      ghs.forEach(function (h) {
        var a = h.getAttribute('data-age'), g = h.getAttribute('data-group');
        h.hidden = !items.some(function (el) {
          return !el.hidden && el.getAttribute('data-age') === a
                            && el.getAttribute('data-group') === g;
        });
      });
      ahs.forEach(function (h) {
        var a = h.getAttribute('data-age');
        h.hidden = !items.some(function (el) {
          return !el.hidden && el.getAttribute('data-age') === a;
        });
      });
      empty.hidden = n > 0;
      count.textContent = n + '/' + items.length + ' kịch bản';
    }

    q.addEventListener('input', run);
    q.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { q.value = ''; run(); }
    });
    qsa('.chip', box).forEach(function (c) {
      c.addEventListener('click', function () {
        var isAge = c.hasAttribute('data-a');
        var row = c.parentNode;
        if (isAge) fa = c.getAttribute('data-a') || '';
        else fg = c.getAttribute('data-g') || '';
        qsa('.chip', row).forEach(function (x) { x.classList.toggle('on', x === c); });
        run();
      });
    });
    run();
  })();

  /* ================= tìm kiếm thực phẩm ================= */
  (function () {
    var box = $('foodbox'); if (!box) return;
    var q = $('food-q'), count = $('food-count');
    var items = qsa('.food'), groups = qsa('.food-g');
    var g = '', age = '';
    function run() {
      var t = fold(q.value.trim()), n = 0;
      items.forEach(function (el) {
        var okA = true;
        if (age) {
          var m = (el.getAttribute('data-from') || '').match(/(\d+)/);
          okA = m ? (+m[1] <= +age) : true;
        }
        var ok = (!g || el.getAttribute('data-group') === g) && okA &&
                 (!t || fold(el.getAttribute('data-text')).indexOf(t) > -1);
        el.hidden = !ok; if (ok) n++;
        if (!ok) el.open = false;
      });
      groups.forEach(function (h) {
        var key = h.getAttribute('data-group');
        var wrap = h.nextElementSibling;
        var any = items.some(function (el) { return !el.hidden && el.getAttribute('data-group') === key; });
        h.hidden = !any; if (wrap && wrap.classList.contains('foods')) wrap.hidden = !any;
      });
      count.textContent = n + '/' + items.length;
    }
    q.addEventListener('input', run);
    qsa('.chip', box).forEach(function (c) {
      c.addEventListener('click', function () {
        var row = c.parentNode;
        if (c.hasAttribute('data-fg')) g = c.getAttribute('data-fg');
        else age = c.getAttribute('data-fa');
        qsa('.chip', row).forEach(function (x) { x.classList.toggle('on', x === c); });
        run();
      });
    });
    run();
  })();

  /* ================= nhật ký ngủ ================= */
  (function () {
    var host = $('nhatky'); if (!host) return;
    var log = store.get('nhatky', []);

    function hnay() {             /* hôm nay, dạng 2026-12-15 */
      var t = new Date();
      return t.getFullYear() + '-' + pad(t.getMonth() + 1) + '-' + pad(t.getDate());
    }
    function vn(iso) {            /* 2026-12-15 → 15/12/2026 */
      var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso || ''));
      return m ? m[3] + '/' + m[2] + '/' + m[1] : (iso || '—');
    }
    function mins(t) {            /* "20:15" → số phút từ 0h */
      var m = /^(\d{1,2})[:h.]?(\d{2})$/.exec(String(t).trim());
      return m ? (+m[1]) * 60 + (+m[2]) : null;
    }
    function gap(a, b) {          /* b - a, vòng qua nửa đêm */
      if (a === null || b === null) return null;
      var d = b - a; return d < 0 ? d + 1440 : d;
    }
    function avg(xs) {
      var v = xs.filter(function (x) { return x !== null && !isNaN(x); });
      return v.length ? Math.round(v.reduce(function (a, b) { return a + b; }, 0) / v.length) : null;
    }
    function fmt(m) { return m === null ? '—' : m + ' phút'; }

    function canhbao() {
      var L = log.slice(-7), w = [];
      var last3 = log.slice(-3);
      if (last3.length === 3 && last3.every(function (r) { return gap(mins(r.bg), mins(r.bn)) > 60; })) {
        w.push('Ba đêm liền bố mất hơn 60 phút mới vào giấc.');
      }
      var last2 = log.slice(-2);
      if (last2.length === 2 && last2.every(function (r) { return r.bh !== null && r.bh < 4; })) {
        w.push('Hai đêm liền bố ngủ dưới 4 giờ.');
      }
      if (last2.length === 2 && last2.every(function (r) { return r.cm; })) {
        w.push('Hai đêm liền có chóng mặt lúc đứng dậy.');
      }
      return w;
    }

    function render() {
      log.sort(function (a, b) { return a.d < b.d ? -1 : 1; });
      var h = ['<h4>Nhật ký ngủ</h4>',
        '<p>Ghi <b>mỗi sáng, một phút</b>. Đừng ghi lúc nửa đêm. Nhìn theo tuần, không nhìn từng đêm.</p>',
        '<div class="li-row fld fld--2">' +
        '<div><label for="n-d">Ngày <span>hiện ra dạng ngày/tháng/năm</span></label>' +
        '<div class="tools" style="gap:8px"><input type="date" id="n-d" style="flex:1 1 150px">' +
        '<button class="btn btn--q" id="n-hnay" type="button">Ngày hôm nay</button></div></div>' +
        '<div><label for="n-cd">Giờ tắt đèn của con</label><input type="text" id="n-cd" placeholder="19:00"></div>' +
        '<div><label for="n-cn">Giờ con <b>thật sự</b> ngủ</label><input type="text" id="n-cn" placeholder="20:15"></div>' +
        '<div><label for="n-cl">Số lần con dậy trong đêm</label><input type="text" id="n-cl" inputmode="numeric" placeholder="3"></div>' +
        '<div><label for="n-cs">Giờ con dậy sáng</label><input type="text" id="n-cs" placeholder="06:30"></div>' +
        '<div><label for="n-bg">Giờ bố lên giường</label><input type="text" id="n-bg" placeholder="21:00"></div>' +
        '<div><label for="n-bn">Giờ bố vào giấc</label><input type="text" id="n-bn" placeholder="22:10"></div>' +
        '<div><label for="n-bh">Bố ngủ mấy giờ <span>ghi số, ví dụ 4.5</span></label><input type="text" id="n-bh" inputmode="decimal" placeholder="4.5"></div>' +
        '<div><label><input type="checkbox" id="n-cm"> Đêm qua có chóng mặt lúc đứng dậy</label></div>' +
        '<div style="align-self:end"><button class="btn" id="n-add" type="button">Ghi vào sổ</button></div></div>'];

      if (log.length) {
        var L = log.slice(-7);
        h.push('<div class="gwrap"><table><thead><tr><th>Ngày</th><th>Con vào giấc mất</th>' +
               '<th>Con dậy</th><th>Bố vào giấc mất</th><th>Bố ngủ</th><th></th></tr></thead><tbody>');
        log.slice().reverse().forEach(function (r, i) {
          var idx = log.length - 1 - i;
          h.push('<tr><td>' + esc(vn(r.d)) + '</td><td>' + fmt(gap(mins(r.cd), mins(r.cn))) + '</td>' +
                 '<td>' + (r.cl === null ? '—' : r.cl + ' lần') + '</td>' +
                 '<td>' + fmt(gap(mins(r.bg), mins(r.bn))) + (r.cm ? ' · chóng mặt' : '') + '</td>' +
                 '<td>' + (r.bh === null ? '—' : r.bh + ' giờ') + '</td>' +
                 '<td><button data-del="' + idx + '" style="border:0;background:none;color:var(--ink-mute);cursor:pointer">×</button></td></tr>');
        });
        h.push('</tbody></table></div>');
        h.push('<p class="jstat"><b>Trung bình 7 ngày gần nhất.</b> Con vào giấc mất ' +
               fmt(avg(L.map(function (r) { return gap(mins(r.cd), mins(r.cn)); }))) +
               ' · bố vào giấc mất ' +
               fmt(avg(L.map(function (r) { return gap(mins(r.bg), mins(r.bn)); }))) + '.</p>');

        var w = canhbao();
        if (w.length) {
          h.push('<div class="alert"><b>Tới ngưỡng đổi ca.</b> ' + w.join(' ') +
                 ' Đổi ngay đêm sau, không bàn lại — ngưỡng ở chương 06.</div>');
        }
        h.push('<p class="jstat" style="margin-top:10px">Cột <b>con vào giấc mất bao lâu</b> ' +
               'chính là số dùng cho cách tắt đèn muộn lại ở chương 04.</p>');
        h.push('<div class="tools" style="margin-top:12px">' +
               '<button class="btn btn--q" id="n-out" type="button">Xuất ra để chép đi nơi khác</button></div>' +
               '<textarea id="n-box" hidden rows="6" style="width:100%;margin-top:8px;font-size:12px"></textarea>');
      } else {
        h.push('<p class="jstat">Chưa có đêm nào. Ghi sáng mai là bắt đầu.</p>');
      }
      h.push('<p class="jstat" style="margin-top:12px">Số nhập ở đây nằm trong trình duyệt của máy này, ' +
             'không gửi đi đâu. Đổi máy hoặc xoá dữ liệu trình duyệt là mất — nên thỉnh thoảng bấm xuất.</p>');
      host.innerHTML = h.join('');

      $('n-d').value = hnay();
      $('n-hnay').addEventListener('click', function () { $('n-d').value = hnay(); });
      $('n-add').addEventListener('click', function () {
        var d = $('n-d').value.trim(); if (!d) return;
        log.push({
          d: d, cd: $('n-cd').value.trim(), cn: $('n-cn').value.trim(),
          cl: $('n-cl').value.trim() === '' ? null : +$('n-cl').value.trim(),
          cs: $('n-cs').value.trim(), bg: $('n-bg').value.trim(), bn: $('n-bn').value.trim(),
          bh: $('n-bh').value.trim() === '' ? null : parseFloat($('n-bh').value),
          cm: $('n-cm').checked
        });
        store.set('nhatky', log); render();
      });
      qsa('[data-del]', host).forEach(function (b) {
        b.addEventListener('click', function () {
          log.splice(+b.getAttribute('data-del'), 1); store.set('nhatky', log); render();
        });
      });
      if ($('n-out')) {
        $('n-out').addEventListener('click', function () {
          var t = $('n-box');
          var head = 'ngay\tden_tat\tcon_ngu\tso_lan_day\tcon_day_sang\tbo_len_giuong\tbo_vao_giac\tbo_ngu_gio\tchong_mat';
          t.value = head + '\n' + log.map(function (r) {
            return [vn(r.d), r.cd, r.cn, r.cl, r.cs, r.bg, r.bn, r.bh, r.cm ? 'co' : ''].join('\t');
          }).join('\n');
          t.hidden = false; t.select();
        });
      }
    }
    RELOAD.push(function () { log = store.get('nhatky', []); render(); });
    render();
  })();

  /* ================= bảng chia ca ================= */
  (function () {
    var host = $('chiaca'); if (!host) return;
    var F = [
      ['ca1', 'Ca ngủ của bố — từ mấy giờ tới mấy giờ', '21:00 – 03:00'],
      ['ca2', 'Ca trực của bố — từ mấy giờ tới mấy giờ', '03:00 – 09:00'],
      ['ai1', 'Ai trực nửa đầu đêm', 'Mẹ'],
      ['ai2', 'Ai trực nửa sau đêm', 'Bố'],
      ['ongba', 'Ông bà nhận ca nào, ngày nào', 'Thứ ba và thứ sáu, 5h–9h'],
      ['doi', 'Ngày đổi ca hằng tuần', 'Chủ nhật']
    ];
    var d = store.get('chiaca', {});
    function render() {
      var h = ['<h4>Bảng chia ca</h4>',
        '<p>Điền rồi bấm in, dán tủ lạnh. Để ông bà đọc được mà không cần ai giải thích.</p>',
        '<div class="fld fld--2">'];
      F.forEach(function (f) {
        h.push('<div><label for="c-' + f[0] + '">' + f[1] + '</label>' +
               '<input type="text" id="c-' + f[0] + '" placeholder="' + f[2] + '" value="' +
               esc(d[f[0]] || '') + '"></div>');
      });
      h.push('</div><div class="tools" style="margin-top:12px">' +
             '<button class="btn" id="c-print" type="button">In bảng này</button></div>');
      host.innerHTML = h.join('');
      qsa('input', host).forEach(function (t) {
        t.addEventListener('input', function () {
          d[t.id.slice(2)] = t.value; store.set('chiaca', d);
        });
      });
      $('c-print').addEventListener('click', function () { window.print(); });
    }
    RELOAD.push(function () { d = store.get('chiaca', {}); render(); });
    render();
  })();

  /* ================= ba câu hỏi cho bác sĩ ================= */
  (function () {
    var host = $('bacsi'); if (!host) return;
    var Q = [
      ['q1', 'Mất ngủ mấy đêm liền thì phải báo, thay vì gắng thêm?'],
      ['q2', 'Dấu hiệu nào là dấu hiệu phải gọi ngay, không chờ lịch khám?'],
      ['q3', 'Thuốc đang dùng có cần đổi giờ uống khi ca đêm đổi giờ ngủ không?'],
      ['sdt', 'Số điện thoại bác sĩ'],
      ['bv', 'Bệnh viện gần nhất — tên và đường đi']
    ];
    var d = store.get('bacsi', {});
    function render() {
      var h = ['<h4>Ba câu hỏi cho bác sĩ</h4>',
        '<p>Mang ba câu đầu tới buổi khám gần nhất, xin bác sĩ ghi giúp con số, rồi chép vào đây. ' +
        '<b>Mục này không tự đặt ngưỡng nào.</b></p>', '<div class="fld">'];
      Q.forEach(function (q) {
        h.push('<div><label for="b-' + q[0] + '">' + q[1] + '</label>' +
               '<input type="text" id="b-' + q[0] + '" value="' + esc(d[q[0]] || '') + '"></div>');
      });
      h.push('</div><div class="tools" style="margin-top:12px">' +
             '<button class="btn" id="b-print" type="button">In trang này</button></div>');
      host.innerHTML = h.join('');
      qsa('input', host).forEach(function (t) {
        t.addEventListener('input', function () {
          d[t.id.slice(2)] = t.value; store.set('bacsi', d);
        });
      });
      $('b-print').addEventListener('click', function () { window.print(); });
    }
    RELOAD.push(function () { d = store.get('bacsi', {}); render(); });
    render();
  })();

  /* ================= danh sách kiểm trước ngày dự sinh ================= */
  (function () {
    var host = $('check'); if (!host) return;
    var C = [
      ['Ngay bây giờ', [
        'Chốt khung giờ hai ca, viết ra giấy',
        'Hỏi bác sĩ ba câu ở chương 06',
        'Mua cũi và nệm']],
      ['Còn 6 tuần · 04/10', [
        'Lắp cũi ở nhà ngoại, kê đúng chỗ đã chốt',
        'Lắp lưới chống muỗi',
        'Lắp màn che sáng',
        'Lắp đèn ngủ, công tắc trong tầm tay khi đang ngồi trên giường']],
      ['Còn 4 tuần · 18/10', [
        'Mua nốt danh sách đồ ở chương 02',
        'Nói chuyện với ông bà ngoại',
        'In trang A4 dán tủ lạnh']],
      ['Còn 2 tuần · 01/11', [
        'Đi thử đường đêm trong bóng tối, chân trần',
        'Chạy thử luật tiền đình: ngồi đếm tới 10, đứng đếm tới 5',
        'Soạn giỏ đêm',
        'Nấu sẵn và cấp đông bảy tới mười bữa']],
      ['Còn 1 tuần · 08/11', [
        'Chạy thử ca đêm một tuần, đúng khung giờ đã chốt',
        'Đọc lại mục ⚠ Ngủ an toàn một lần nữa']],
      ['Trước ngày dọn về nhà mình', [
        'Kê xong phòng ở nhà mình',
        'Đi thử đường đêm ở phòng mới',
        'Giữ nguyên ga, túi ngủ và thứ tự nghi thức']]
    ];
    var done = store.get('check', {});
    function render() {
      var all = 0, ok = 0;
      var h = ['<h4>Danh sách kiểm trước ngày dự sinh</h4>',
               '<p>Ngày dự sinh <b>15/11</b>. Bấm để đánh dấu xong.</p>'];
      C.forEach(function (g, gi) {
        h.push('<p class="jstat" style="margin:14px 0 4px;font-weight:700;color:var(--ink-2)">' + esc(g[0]) + '</p><ul class="cl">');
        g[1].forEach(function (t, ti) {
          var k = gi + '-' + ti; all++; if (done[k]) ok++;
          h.push('<li><label style="cursor:pointer;display:flex;gap:8px;align-items:flex-start">' +
                 '<input type="checkbox" data-k="' + k + '"' + (done[k] ? ' checked' : '') + '>' +
                 '<span' + (done[k] ? ' style="color:var(--ink-3);text-decoration:line-through"' : '') + '>' +
                 esc(t) + '</span></label></li>');
        });
        h.push('</ul>');
      });
      h.unshift('');
      host.innerHTML = h.join('') +
        '<p class="jstat" style="margin-top:12px"><b>' + ok + '/' + all + '</b> việc đã xong.</p>' +
        '<div class="tools" style="margin-top:8px"><button class="btn btn--q" id="k-print" type="button">In danh sách</button></div>';
      qsa('[data-k]', host).forEach(function (b) {
        b.addEventListener('change', function () {
          done[b.getAttribute('data-k')] = b.checked; store.set('check', done); render();
        });
      });
      $('k-print').addEventListener('click', function () { window.print(); });
    }
    RELOAD.push(function () { done = store.get('check', {}); render(); });
    render();
  })();

  /* ================= đồng bộ giữa các máy ================= */
  /* Mỗi công cụ là một tài liệu trong kho dùng chung của trang. Máy nào
     ghi sau thì thắng, so bằng mốc thời gian. Không có kho thì trang vẫn
     chạy bình thường, chỉ là dữ liệu nằm riêng từng máy. */
  (function () {
    if (!(window.claude && typeof claude.use === 'function')) return;
    var KEYS = ['nhatky', 'chiaca', 'bacsi', 'check'];
    claude.use('db').then(function (db) {
      if (!db) return;
      DB = db;
      KEYS.forEach(function (k) {
        var ref;
        try { ref = db.doc('data/' + k); } catch (e) { return; }
        ref.onSnapshot(function (snap) {
          if (!snap || !snap.exists) return;
          var d = snap.data();
          if (!d || d.v === undefined || d.v === null) return;
          var at = +d.at || 0;
          if (at <= localAt(k)) return;          /* bản ở máy này mới hơn */
          try {
            localStorage.setItem('gn.' + k, JSON.stringify(d.v));
            localStorage.setItem('gn.at.' + k, String(at));
          } catch (e) { return; }
          RELOAD.forEach(function (f) { try { f(); } catch (e) {} });
        }, function () {});
      });
    }, function () {});
  })();

  /* ================= khởi động ================= */
  var h = (location.hash || '').replace('#', '');
  if (h && MAP[h.split('--')[0]]) show(h.split('--')[0], h.indexOf('--') > -1 ? h : null, false);
  else show(SECS[1] ? SECS[1].id : SECS[0].id, null, false);
})();
