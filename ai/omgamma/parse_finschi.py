"""Parse IC(n,r,*) representative strings out of saved Finschi catalog
HTML pages (data/om_XY.html)."""
import re


def parse_ic_strings(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    # lines like: IC(8,3,&nbsp;12) = ++-+... possibly with tags around
    text = re.sub(r'<[^>]+>', '', html)
    text = text.replace('&nbsp;', ' ')
    out = []
    for m in re.finditer(r'IC\((\d+),\s*(\d+),\s*(\d+)\)\s*=\s*([+-]+)',
                         text):
        n, r, k, s = int(m.group(1)), int(m.group(2)), int(m.group(3)), \
            m.group(4)
        out.append((n, r, k, s))
    return out


if __name__ == "__main__":
    import sys
    for t in parse_ic_strings(sys.argv[1]):
        print(t[0], t[1], t[2], t[3])
