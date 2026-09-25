#!/usr/bin/env python3
"""Dựng index.html từ các file .md nội dung.

Sửa nội dung ở file .md rồi chạy:  python3 build.py
"""
import base64, html, re, pathlib, unicodedata

HERE = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- cấu hình
TITLE = "Giấc ngủ cho con"
EMOJI = "🌙"

PINNED = dict(id="angoan", file="00-ngu-an-toan.md", num="⚠", hero="cw",
              shape="sh-a", title="Ngủ an toàn — kiểm ngay",
              lede="Sáu điều kiểm trong một phút, trước giấc đầu tiên của con.")

CHAPTERS = [
    dict(id="nenmong", file="01-nen-mong.md", num="01", hero="c1", shape="sh-c",
         title="Nền móng",
         lede="Bố giữ điều kiện ngủ — con tự vào giấc. Ba trụ và hai bảng ranh giới cứng."),
    dict(id="truockhisinh", file="02-truoc-khi-con-ra-doi.md", num="02", hero="c2", shape="sh-b",
         title="Trước khi con ra đời",
         lede="Phòng, cũi, điều hoà, đồ phải mua, chia ca đêm, và một câu nói với ông bà."),
    dict(id="nhipngay", file="03-nhip-ngay.md", num="03", hero="c3", shape="sh-r",
         title="Nhịp ngày",
         lede="Thời gian biểu số giờ thức theo tháng tuổi, giấc ngày, giờ lên giường, ánh sáng sáng sớm."),
    dict(id="datxuong", file="04-dat-xuong.md", num="04", hero="c4", shape="sh-q",
         title="Đặt xuống & tập tự ngủ",
         lede="Nghi thức đặt ngủ, rồi bảy cách xếp cạnh nhau để nhà mình chọn."),
    dict(id="thucdem", file="05-khi-con-thuc-dem.md", num="05", hero="c5", shape="sh-p",
         title="Khi con thức đêm",
         lede="Khủng hoảng ngủ, ác mộng, sợ tối, và chuyện dậy lúc năm giờ sáng."),
    dict(id="bome", file="06-giac-ngu-cua-bo-me.md", num="06", hero="c6", shape="sh-s",
         title="Giấc ngủ của bố mẹ",
         lede="Chia ca theo sức, khối ngủ lõi, luật an toàn trong đêm, và ngưỡng phải báo bác sĩ."),
    dict(id="kichban", file="07-kich-ban.md", num="07", hero="c7", shape="sh-c",
         title="31 kịch bản",
         lede="Mở lúc đang bí. Lọc theo tuổi và theo nhóm, hoặc gõ vào ô tìm kiếm."),
    dict(id="congcu", file="08-cong-cu-so.md", num="08", hero="c8", shape="sh-b",
         title="Công cụ & sổ",
         lede="Nhật ký ngủ, bảng chia ca, một trang Do & Don't. Chương cuối."),
]

# ---------------------------------------------------------------- markdown
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'<em>\1</em>', s)
    def _a(m):
        txt, href = m.group(1), m.group(2)
        if href.startswith('#'):
            return ('<a href="' + href + '" data-jump="' + href[1:] + '">' + txt + '</a>')
        return '<a href="' + href + '">' + txt + '</a>'
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _a, s)
    s = s.replace('⚠', '<span class="warn-i">⚠</span>')
    return s

LAB_SAY = re.compile(r'^(Nói|Làm|Ví dụ|Câu nói)\b')
LAB_NO = re.compile(r'^(Đừng nói|Không|Tránh)\b')

def split_label(txt):
    m = re.match(r'\*\*(.+?):\*\*\s*(.*)$', txt)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, txt

def lab_class(lab):
    if not lab: return ''
    if LAB_NO.match(lab): return ' lab-no'
    if LAB_SAY.match(lab): return ' lab-say'
    return ''

def split_title(head):
    m = re.match(r'^\*\*(.+?)\*\*(?:\s*—\s*(.*))?$', head.strip())
    if m:
        return m.group(1).strip(), (m.group(2) or '').strip()
    return None, ''

ORDER = {'Ví dụ': 0, 'Câu nói': 0, 'Nói': 0, 'Làm': 1,
         'Đừng nói': 2, 'Tránh': 2, 'Hệ quả': 3, 'Vì sao': 3, 'Lưu ý': 4}

def render_list(items):
    o, li, sub = ['<ul>'], False, False
    for d, txt in items:
        if d == 0:
            if sub: o.append('</ul>'); sub = False
            if li: o.append('</li>')
            o.append('<li>' + inline(txt)); li = True
        else:
            if not li: o.append('<li>'); li = True
            if not sub: o.append('<ul class="sub">'); sub = True
            lab, _ = split_label(txt)
            cls = (lab_class(lab).strip() or 'plain')
            if txt.strip().startswith('✕'):
                cls = 'no'
            o.append('<li class="' + cls + '">' + inline(txt) + '</li>')
    if sub: o.append('</ul>')
    if li: o.append('</li>')
    o.append('</ul>')
    return ''.join(o)

def render_rows(items):
    """Hàng bung ra: tiêu đề + việc cần làm; mở ra có Ví dụ · Đừng nói · Hệ quả."""
    groups = []
    for d, txt in items:
        if d == 0:
            groups.append([txt, []])
        elif groups:
            groups[-1][1].append(txt)
    o = ['<ul class="rows">']
    for head, kids in groups:
        title, action = split_title(head)
        if title is None:
            lab, rest = split_label(head)
            if lab:
                o.append('<li class="r--flat' + lab_class(lab) + '">'
                         '<span class="lab">' + inline(lab) + '</span>'
                         '<span class="ra">' + inline(rest) + '</span></li>')
            else:
                o.append('<li class="r--flat"><span class="ra">' + inline(head) + '</span></li>')
            continue
        ra = ('<span class="ra">' + inline(action) + '</span>') if action else ''
        if not kids:
            o.append('<li class="r--flat"><span class="rt">' + inline(title) + '</span>' + ra + '</li>')
            continue
        rows = []
        for k in kids:
            kl, kr = split_label(k)
            rows.append((ORDER.get(kl, 9), kl or 'Ghi chú', kr))
        if not action:
            for idx, (_, kl, kr) in enumerate(rows):
                if kl == 'Làm':
                    action = kr
                    ra = '<span class="ra">' + inline(action) + '</span>'
                    rows.pop(idx)
                    break
        rows.sort(key=lambda x: x[0])
        o.append('<li><details class="r"><summary><span class="rt">' + inline(title) + '</span>'
                 + ra + '</summary><div class="rmore">')
        for _, kl, kr in rows:
            cls = (lab_class(kl) or '').replace('lab-', '').strip()
            o.append('<p class="' + cls + '"><b>' + inline(kl) + '</b>' + inline(kr) + '</p>')
        o.append('</div></details></li>')
    o.append('</ul>')
    return ''.join(o)

# ---------------------------------------------------------------- khối :::
def render_block(head, inner):
    parts = [x.strip() for x in head.split('|')]
    spec = parts[0].split()
    kind = spec[0]

    if kind == 'grp':
        tone = spec[1] if len(spec) > 1 else 'y'
        title = parts[1] if len(parts) > 1 else ''
        return ('<div class="grp grp--' + tone + '"><div class="grp-h">' + inline(title)
                + '</div>' + md(inner, rows=True) + '</div>')

    if kind == 'tl':
        return '<div class="tl">' + md(inner) + '</div>'

    if kind == 'stage':
        age = ' '.join(spec[1:])
        sub = parts[1] if len(parts) > 1 else ''
        stage_n = parts[2] if len(parts) > 2 else ''
        attr = ' data-stage="' + html.escape(stage_n, quote=True) + '"' if stage_n else ''
        return ('<div class="tl-i"' + attr + '><div class="tl-age"><b>' + inline(age) + '</b>'
                + ('<span>' + inline(sub) + '</span>' if sub else '')
                + '</div><div class="tl-card">' + md(inner) + '</div></div>')

    if kind == 'part':
        letter = spec[1] if len(spec) > 1 else ''
        name = parts[1] if len(parts) > 1 else ''
        age = parts[2] if len(parts) > 2 else ''
        note = parts[3] if len(parts) > 3 else ''
        return ('<div class="part" id="part-' + letter.lower() + '"><span class="part-k">Phần '
                + inline(letter) + '</span><b>' + inline(name) + '</b>'
                + ('<span class="part-age">' + inline(age) + '</span>' if age else '')
                + ('<p>' + inline(note) + '</p>' if note else '') + '</div>')

    if kind == 'tip':
        return '<p class="tip">' + md(inner).replace('<p>', '').replace('</p>', ' ') + '</p>'

    if kind == 'sos':
        return '<div class="sos">' + md(inner) + '</div>'

    if kind == 'card':
        title = parts[1] if len(parts) > 1 else ''
        return ('<div class="card">' + ('<h4>' + inline(title) + '</h4>' if title else '')
                + md(inner) + '</div>')

    if kind == 'figs':
        out = ['<div class="figs">']
        for ln in inner:
            t = ln.strip()
            if not t.startswith('- '):
                continue
            bits = [x.strip() for x in t[2:].split('|')]
            name, cap = bits[0], (bits[1] if len(bits) > 1 else '')
            f = HERE / 'img' / (name + '.png')
            if not f.exists():
                continue
            b64 = base64.b64encode(f.read_bytes()).decode('ascii')
            out.append('<figure class="fig"><img alt="" loading="lazy" '
                       'src="data:image/png;base64,' + b64 + '">'
                       '<figcaption>' + inline(cap) + '</figcaption></figure>')
        out.append('</div>')
        return ''.join(out)

    if kind == 'rows':
        return md(inner, rows=True)

    if kind == 'widget':
        return WIDGETS.get(spec[1], '')

    if kind == 'filter':
        return FILTERS.get(spec[1], '')

    return md(inner)

def md(lines, rows=False):
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        if s.startswith(':::') and s != ':::':
            head = s[3:].strip()
            depth, j, inner = 1, i + 1, []
            while j < len(lines):
                t = lines[j].strip()
                if t.startswith(':::') and t != ':::':
                    depth += 1
                elif t == ':::':
                    depth -= 1
                    if depth == 0: break
                inner.append(lines[j]); j += 1
            i = j + 1
            out.append(render_block(head, inner))
            continue
        if s == '---':
            out.append('<hr>'); i += 1; continue
        if s.startswith('#'):
            lvl = len(s) - len(s.lstrip('#'))
            txt = s.lstrip('#').strip()
            tag = 'h3' if lvl <= 2 else 'h4'
            out.append('<%s>%s</%s>' % (tag, inline(txt), tag)); i += 1; continue
        if s.startswith('|'):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl.append(lines[i].strip()); i += 1
            cells = lambda r: [c.strip() for c in r.strip('|').split('|')]
            head = cells(tbl[0])
            body = [cells(r) for r in tbl[2:]]
            def cell(c):
                # nhiều ý trong một ô → gạch đầu dòng
                if '·' in c and c.count('·') >= 1 and len(c) > 60:
                    bits = [b.strip() for b in c.split('·')]
                    # chỉ tách khi mỗi mảnh vẫn đủ cặp ** — không thì để nguyên
                    if all(bit.count('**') % 2 == 0 for bit in bits):
                        return ('<ul class="cl">'
                                + ''.join('<li>' + inline(b) + '</li>' for b in bits) + '</ul>')
                return inline(c)
            h = ''.join('<th>%s</th>' % inline(c) for c in head)
            b = ''.join('<tr>' + ''.join('<td>%s</td>' % cell(c) for c in r) + '</tr>' for r in body)
            extra = ' dd' if any('✅' in c for c in head) else ''
            out.append('<div class="tw%s"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (extra, h, b))
            continue
        if s.startswith('> '):
            q = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                q.append(lines[i].strip()[2:]); i += 1
            out.append('<blockquote><p>' + '<br>'.join(inline(x) for x in q) + '</p></blockquote>')
            continue
        if s.startswith('- '):
            items = []
            while i < len(lines):
                raw = lines[i]
                st = raw.strip()
                if st.startswith('- '):
                    items.append([1 if raw.startswith('  ') else 0, st[2:]])
                    i += 1
                elif st and raw.startswith(' ') and items:
                    items[-1][1] += ' ' + st
                    i += 1
                else:
                    break
            out.append(render_rows(items) if rows else render_list(items))
            continue
        p = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^\s*(#|\||>|- |---|:::)', lines[i]):
            p.append(lines[i].strip()); i += 1
        txt = ' '.join(p)
        m = re.match(r'^\*?Cơ sở:\s*(.*?)\*?$', txt)
        if m:
            head, bul = m.group(1).strip(), []
            while i < len(lines) and lines[i].strip().startswith('- '):
                bul.append(lines[i].strip()[2:]); i += 1
            inner_html = ('<p>' + inline(head) + '</p>') if head else ''
            if bul:
                inner_html += '<ul>' + ''.join('<li>' + inline(b) + '</li>' for b in bul) + '</ul>'
            out.append('<details class="src"><summary>Cơ sở</summary>' + inner_html + '</details>')
            continue
        out.append('<p>%s</p>' % inline(txt))
    return '\n'.join(out)

# ---------------------------------------------------------------- kịch bản
def build_scenarios(body):
    """Kịch bản hai cấp: tuổi ở ngoài, nhóm tình huống ở trong."""
    intro = re.split(r'(?m)^# ', body)[0]
    out = [md(intro.split('\n'))]
    out.append('<div class="scen-list" id="scenlist">')
    n = 0
    for ablk in re.split(r'\n(?=# )', body):
        am = re.match(r'# ([^|\n]+)\|\s*([a-z0-9]+)', ablk)
        if not am:
            continue
        alabel, akey = am.group(1).strip(), am.group(2).strip()
        out.append('<h3 class="scen-a" data-age="%s">%s</h3>'
                   % (akey, inline(alabel)))
        for gblk in re.split(r'\n(?=## )', ablk)[1:]:
            gm = re.match(r'## ([^|\n]+)\|\s*([a-z0-9]+)', gblk)
            if not gm:
                continue
            glabel, gkey = gm.group(1).strip(), gm.group(2).strip()
            out.append('<h4 class="scen-g" data-age="%s" data-group="%s">%s</h4>'
                       % (akey, gkey, inline(glabel)))
            for it in re.split(r'\n(?=### )', gblk)[1:]:
                lines = it.strip().split('\n')
                head = lines[0][4:].strip()
                code, title = (head.split('·', 1) + [''])[:2]
                code, title = code.strip(), title.strip()
                rest = [x for x in lines[1:] if x.strip() and x.strip() != '---']
                why = ''
                if rest and rest[-1].strip().startswith('> '):
                    why = re.sub(r'^\*\*Vì sao:\*\*\s*', '', rest[-1].strip()[2:])
                    rest = rest[:-1]
                inner = ''.join('<p class="%s">%s</p>'
                                % ('do' if r.startswith('**Làm ngay') else 'dont', inline(r))
                                for r in rest)
                txt = html.escape(strip_md(' '.join([code, title, alabel, glabel, why] + rest)).lower(),
                                  quote=True)
                n += 1
                out.append(
                    '<details class="scen" data-age="%s" data-group="%s" data-text="%s">'
                    '<summary><span class="scode">%s</span><span class="stitle">%s</span>'
                    '<span class="sage">%s</span></summary>'
                    '<div class="sbody">%s%s</div></details>'
                    % (akey, gkey, txt, inline(code), inline(title), inline(alabel), inner,
                       ('<span class="why"><b>Vì sao</b>' + inline(why) + '</span>') if why else ''))
    out.append('</div>')
    return '\n'.join(out).replace('__SCEN_N__', str(n))

def strip_md(s):
    return re.sub(r'[*`>#\[\]]', ' ', s)

# ---------------------------------------------------------------- thực phẩm
FOOD_FIELDS = ['Giàu', 'Theo tuổi', 'Mùa', 'Lưu ý']

def build_foods(body):
    """07 — phần ::: foods ... ::: dựng thành thẻ lọc được."""
    out = []
    for blk in re.split(r'\n(?=# )', body):
        m = re.match(r'# (.+)', blk)
        if not m:
            out.append(md(blk.split('\n'))); continue
        gname = m.group(1).strip()
        if not gname.startswith('Nhóm '):
            out.append(md(blk.split('\n'))); continue
        label = gname[5:].strip()
        key = label.split('·')[0].strip()
        out.append('<h3 class="food-g" data-group="%s">%s</h3><div class="foods">' % (html.escape(key, quote=True), inline(label)))
        for it in re.split(r'\n(?=## )', blk)[1:]:
            lines = [x for x in it.strip().split('\n') if x.strip()]
            head = lines[0][3:].strip()
            bits = [b.strip() for b in head.split('·')]
            name = bits[0]
            frm = bits[1] if len(bits) > 1 else ''
            rows = []
            for ln in lines[1:]:
                mm = re.match(r'^-\s*\*\*(.+?)\*\*\s*—\s*(.*)$', ln.strip())
                if mm:
                    rows.append((mm.group(1).strip(), mm.group(2).strip()))
            txt = html.escape(strip_md(head + ' ' + ' '.join(v for _, v in rows)).lower(), quote=True)
            months = ''
            for k, v in rows:
                if k == 'Mùa':
                    months = v
            body_html = ''.join(
                '<p><b>%s</b>%s</p>' % (inline(k), inline(v)) for k, v in rows)
            out.append(
                '<details class="food" data-group="%s" data-from="%s" data-text="%s">'
                '<summary><span class="fname">%s</span><span class="ffrom">%s</span></summary>'
                '<div class="fbody">%s</div></details>'
                % (html.escape(key, quote=True), html.escape(frm, quote=True), txt,
                   inline(name), inline(frm), body_html))
        out.append('</div>')
    return '\n'.join(out)

# ---------------------------------------------------------------- bộ lọc
FILTERS = {}

FILTERS['stage'] = '''
<div class="searchbox" id="stagebox">
 <b class="sb-h">Con đang ở đâu?</b>
 <div class="chips"><span class="ck-l">Theo tuổi</span>
  <button type="button" class="chip" data-stage="1">5–6 tháng</button>
  <button type="button" class="chip" data-stage="2">7–8 tháng</button>
  <button type="button" class="chip" data-stage="3">9–11 tháng</button>
  <button type="button" class="chip" data-stage="4">12–18 tháng</button>
 </div>
 <div class="chips"><span class="ck-l">Theo việc</span>
  <button type="button" class="chip" data-stage="1">Mới tập nuốt</button>
  <button type="button" class="chip" data-stage="2">Nhá được đồ lợn cợn</button>
  <button type="button" class="chip" data-stage="3">Nhai được, bốc được</button>
  <button type="button" class="chip" data-stage="4">Ăn được miếng cắt</button>
 </div>
 <div class="sb-foot"><span class="hint" id="stage-now">Đang xem tất cả bốn giai đoạn.</span>
  <button type="button" class="btn btn--q" id="stage-all">Xem tất cả</button></div>
</div>'''

FILTERS['doc'] = '''
<div class="searchbox docsearch">
 <div class="tools">
  <div class="search"><input type="text" class="doc-q" placeholder="Gõ để tìm trong chương này…" autocomplete="off"></div>
  <span class="count doc-count"></span>
 </div>
 <span class="hint">Gõ vài chữ là được — <b>điều hoà</b>, <b>muỗi</b>, <b>ca ngủ</b>, <b>ngoại</b>, <b>đèn</b>.
  Không có dấu vẫn ra. Bấm <b>Xoá</b> hoặc xoá hết chữ để xem lại cả chương.</span>
</div>'''

FILTERS['scen'] = '''
<div class="searchbox" id="scenbox">
 <div class="tools">
  <div class="search"><input type="text" id="scen-q" placeholder="Gõ tình huống…" autocomplete="off"></div>
  <span class="count" id="scen-count"></span>
 </div>
 <div class="chips"><span class="ck-l">Tuổi</span>
  <button type="button" class="chip on" data-a="">Tất cả</button>
  <button type="button" class="chip" data-a="a">0–3 tháng</button>
  <button type="button" class="chip" data-a="b">4–12 tháng</button>
  <button type="button" class="chip" data-a="c">1–3 tuổi</button>
  <button type="button" class="chip" data-a="d">Mọi tuổi</button>
 </div>
 <div class="chips"><span class="ck-l">Nhóm</span>
  <button type="button" class="chip on" data-g="">Tất cả</button>
  <button type="button" class="chip" data-g="truoc">Trước giờ ngủ</button>
  <button type="button" class="chip" data-g="dem">Trong đêm</button>
  <button type="button" class="chip" data-g="ngay">Giấc ngày</button>
  <button type="button" class="chip" data-g="som">Dậy sớm</button>
  <button type="button" class="chip" data-g="ongba">Ông bà</button>
  <button type="button" class="chip" data-g="bome">Bố mẹ</button>
  <button type="button" class="chip" data-g="doicho">Đổi chỗ</button>
  <button type="button" class="chip" data-g="om">Ốm</button>
 </div>
 <span class="hint">Hai hàng nút lọc chồng nhau được. Gõ vài chữ cũng ra —
  <b>võng</b>, <b>chóng mặt</b>, <b>5 giờ</b>, <b>ác mộng</b>. Không dấu vẫn tìm được.</span>
</div>'''

FILTERS['food'] = '''
<div class="searchbox" id="foodbox">
 <div class="tools">
  <div class="search"><input type="text" id="food-q" placeholder="Gõ tên món…" autocomplete="off"></div>
  <span class="count" id="food-count"></span>
 </div>
 <div class="chips"><span class="ck-l">Nhóm</span>
  <button type="button" class="chip on" data-fg="">Tất cả</button>
  <button type="button" class="chip" data-fg="Đạm động vật">Đạm động vật</button>
  <button type="button" class="chip" data-fg="Đạm thực vật">Đạm thực vật</button>
  <button type="button" class="chip" data-fg="Rau">Rau</button>
  <button type="button" class="chip" data-fg="Quả">Quả</button>
  <button type="button" class="chip" data-fg="Tinh bột">Tinh bột</button>
  <button type="button" class="chip" data-fg="Sữa">Sữa</button>
 </div>
 <div class="chips"><span class="ck-l">Con ăn được</span>
  <button type="button" class="chip on" data-fa="">Mọi tuổi</button>
  <button type="button" class="chip" data-fa="6">Từ 6 tháng</button>
  <button type="button" class="chip" data-fa="7">Từ 7 tháng</button>
  <button type="button" class="chip" data-fa="9">Từ 9 tháng</button>
  <button type="button" class="chip" data-fa="12">Từ 12 tháng</button>
 </div>
</div>'''

# ---------------------------------------------------------------- widget
WIDGETS = {}
WIDGETS['nhatky'] = '<div class="card" id="nhatky"></div>'
WIDGETS['chiaca'] = '<div class="card" id="chiaca"></div>'
WIDGETS['bacsi'] = '<div class="card" id="bacsi"></div>'
WIDGETS['check'] = '<div class="card" id="check"></div>'

# ---------------------------------------------------------------- dựng
def chapter_html(ch, body):
    if ch['id'] == 'kichban':
        inner = build_scenarios(body)
    elif ch['id'] == 'thucpham':
        inner = build_foods(body)
    else:
        inner = md(body.split('\n'))
    def _h3(m):
        txt = m.group(1)
        plain = re.sub(r'<[^>]+>', '', txt).strip()
        key = plain.split('·')[0].strip() if '·' in plain else plain
        if re.fullmatch(r'[A-Za-z0-9]{1,3}', key):
            slug = key.lower()
        else:
            slug = re.sub(r'[^a-z0-9]+', '-',
                          unicodedata.normalize('NFD', plain.lower())
                          .encode('ascii', 'ignore').decode()).strip('-')[:40]
        return '<h3 id="%s-%s">%s</h3>' % (ch['id'], slug, txt)
    inner = re.sub(r'<h3>(.*?)</h3>', _h3, inner)
    num = ('Chương ' + ch['num']) if ch['num'] not in ('⚠',) else 'Khẩn'
    return ('<section id="%s" data-title="%s">\n'
            '<header class="chero %s"><span class="cshape %s" aria-hidden="true"></span>'
            '<span class="pnum">%s</span><h2>%s</h2>'
            '<p class="lede">%s</p></header>\n%s\n</section>'
            % (ch['id'], html.escape(ch['title'], quote=True), ch['hero'], ch['shape'],
               num, inline(ch['title']), inline(ch['lede']), inner))

def read(name):
    p = HERE / name
    if not p.exists():
        return '*(chưa có nội dung)*'
    txt = p.read_text(encoding='utf-8')
    return re.sub(r'^#\s+[^\n]*\n', '', txt, count=1)

def main():
    css = (HERE / 'styles.css').read_text(encoding='utf-8')
    js = (HERE / 'app.js').read_text(encoding='utf-8')
    secs = [chapter_html(PINNED, read(PINNED['file']))]
    for ch in CHAPTERS:
        secs.append(chapter_html(ch, read(ch['file'])))
    out = f'''<title>{TITLE}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@700;800&family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
<div class="app">
  <header class="topbar">
    <button class="burger" id="burger" type="button" aria-expanded="false" aria-controls="side"><i aria-hidden="true"></i><span>Mục lục</span></button>
    <span class="now" id="now">&nbsp;</span>
    <span class="of" id="of">&nbsp;</span>
  </header>
  <aside class="side" id="side" aria-label="Mục lục">
    <div class="side-head">
      <b><span class="bmoji" aria-hidden="true">{EMOJI}</span>{TITLE}</b>
      <button class="side-x" id="sidex" type="button" aria-label="Đóng mục lục">&times;</button>
    </div>
    <nav class="side-nav"><ol id="chnav"></ol></nav>
  </aside>
  <div class="scrim" id="scrim"></div>
  <main class="doc">
    <div class="doc-in">
{chr(10).join(secs)}
      <nav class="pager" id="pager"></nav>
      <footer>Mục này không thay bác sĩ. Mọi dấu hiệu bất thường thì đi khám —
      các mốc “đi khám khi” nằm ở cuối chương 02, 03 và trong nhóm H của chương 06.</footer>
    </div>
  </main>
</div>
<script>
{js}
</script>'''
    (HERE / 'index.html').write_text(out, encoding='utf-8')
    print('index.html · %.1f KB' % (len(out.encode('utf-8')) / 1024))

    # Bản đứng riêng cho GitHub Pages — có doctype và khai báo bảng mã,
    # để mở thẳng bằng trình duyệt cũng đúng dấu tiếng Việt.
    docs = HERE / 'docs'
    docs.mkdir(exist_ok=True)
    page = ('<!doctype html>\n<html lang="vi">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<meta name="description" content="S\u1ed5 tay dinh d\u01b0\u1ee1ng v\u00e0 n\u1ebfp \u0103n cho con 0\u201312 tu\u1ed5i.">\n'
            '<link rel="icon" href="data:image/svg+xml,'
            '%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E'
            '%3Ctext y=%2226%22 font-size=%2226%22%3E%F0%9F%8D%9A%3C/text%3E%3C/svg%3E">\n'
            '</head>\n<body>\n' + out + '\n</body>\n</html>\n')
    (docs / 'index.html').write_text(page, encoding='utf-8')
    (docs / '.nojekyll').write_text('', encoding='utf-8')
    print('docs/index.html · %.1f KB' % (len(page.encode('utf-8')) / 1024))

if __name__ == '__main__':
    main()
