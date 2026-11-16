import re, json, sys, os
# Dựng lại trang demo sau khi chạy lại notebook: python demo/_build/build_site.py
S = os.path.dirname(os.path.abspath(__file__)); DEMO = os.path.dirname(S)
tpl = open(os.path.join(S, 'template.html'), encoding='utf-8').read()
old = open(os.path.join(DEMO, 'ban_cu', 'trang_ban_nha.html'), encoding='utf-8').read()
data = []
for name in ['MODEL', 'LISTINGS']:
    m = re.search(r'^const %s = .*?;$' % name, old, re.M); assert m, name; data.append(m.group(0))
m = re.search(r'^const MODEL_TABLE = \[.*?\];$', old, re.M | re.S); assert m; data.append(m.group(0))
data.append('const TREND = ' + json.dumps(json.load(open(os.path.join(DEMO, '..', 'model', 'xu_huong_gia.json'), encoding='utf-8')), ensure_ascii=False) + ';')
cred = json.load(open(os.path.join(S, 'credits.json'), encoding='utf-8'))
for c in cred:
    c['cropped'] = c['key'] in ('hero', 'h1-b'); c.pop('size', None)
    c['site'] = {'flickr': 'Flickr', 'rawpixel': 'Rawpixel'}.get(c['site'], c['site'])
USED = set(re.findall(r'assets/img/([a-z0-9-]+)\.jpg', tpl))
for arr in re.findall(r'const (?:EXT|INT) = (.*?);', tpl): USED |= set(re.findall(r'"([a-z0-9]+-[a-z0-9-]+)"', arr))
cred = [c for c in cred if c['key'] in USED]
data.append('const CREDITS = ' + json.dumps(cred, ensure_ascii=False) + ';')
used = sorted(set(re.findall(r'#i-([a-z0-9-]+)', tpl)) | set(re.findall(r'icon\("([a-z0-9-]+)"', tpl)) |
              set(re.findall(r'\["([a-z0-9-]+)", "', tpl)) | {'trending-down', 'trending-up', 'check', 'circle-alert', 'minus'})
syms = []
for n in used:
    p = os.path.join(S, 'icons', n + '.svg')
    if not os.path.exists(p): continue
    inner = re.search(r'<svg[^>]*>(.*)</svg>', open(p, encoding='utf-8').read(), re.S).group(1)
    syms.append(f'<symbol id="i-{n}" viewBox="0 0 24 24">' + re.sub(r'\s*\n\s*', '', inner).replace(' />', '/>') + '</symbol>')
missing = [n for n in re.findall(r'#i-([a-z0-9-]+)', tpl) if not os.path.exists(os.path.join(S, 'icons', n + '.svg'))]
print('icons:', len(syms), 'missing:', sorted(set(missing)))
sprite = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + ''.join(syms) + '</svg>'
out = tpl.replace('<!--@@ICONS@@-->', '<!-- Icon: Lucide (ISC) -->\n' + sprite).replace('/*@@DATA@@*/', '\n'.join(data))
open(os.path.join(DEMO, 'trang_ban_nha.html'), 'w', encoding='utf-8').write(out)
print('written', len(out))
