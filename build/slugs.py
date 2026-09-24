import json, unicodedata, re

def to_slug(title):
    """simple-icons title -> slug (their documented algorithm)."""
    s = title.lower()
    for a, b in (('+', 'plus'), ('.', 'dot'), ('&', 'and'),
                 ('đ', 'd'), ('ħ', 'h'), ('ı', 'i'), ('ĸ', 'k'),
                 ('ŀ', 'l'), ('ł', 'l'), ('ß', 'ss'), ('ŧ', 't'), ('ø', 'o')):
        s = s.replace(a, b)
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', s)

def load():
    d = json.load(open('build/simple-icons.json', encoding='utf-8'))
    icons = d['icons'] if isinstance(d, dict) else d
    m = {}
    for it in icons:
        m[to_slug(it['title'])] = {'title': it['title'], 'hex': '#' + it['hex']}
    return m
