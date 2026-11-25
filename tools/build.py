#!/usr/bin/env python3
"""Generator dema Wszystko dla Parkietu.
Treść podstron: tools/content/*.html (pierwsza linia = JSON z meta w komentarzu).
Tokeny w treści: %R% (ścieżka do katalogu głównego), %I:nazwa% (ikona SVG), %GAL:kategoria|limit% (galeria).
Uruchom: python3 tools/build.py
"""
import json, os, re, hashlib, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://impulseo-pl.github.io/wszystko-dla-parkietu/"
TEL = "510 865 534"
TEL_H = "+48510865534"

I = {
 "phone": '<path d="M5 4h3l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v3a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
 "star": '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
 "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/>',
 "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
 "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
 "wind": '<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h7"/>',
 "leaf": '<path d="M5 19c0-8 6-14 15-14 0 9-6 15-14 15"/><path d="M5 19 13 11"/>',
 "tool": '<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3z"/><path d="M14.5 6.5 17 4l3 3-2.5 2.5"/>',
 "map": '<path d="m9 4-6 2v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
 "chat": '<path d="M4 5h16v11H8l-4 4z"/>',
 "arrows": '<path d="M9 6 3 12l6 6M15 6l6 6-6 6"/>',
 "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "chev": '<path d="m6 9 6 6 6-6"/>',
 "home": '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/>',
 "ruler": '<path d="M3 17 17 3l4 4L7 21z"/><path d="m7 13 2 2M10 10l2 2M13 7l2 2"/>',
 "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
}
def icon(n, cls=""):
    fill = ' fill="currentColor" stroke="none"' if n in ("star",) else ' fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    c = f' class="{cls}"' if cls else ""
    return f'<svg viewBox="0 0 24 24"{fill}{c} aria-hidden="true">{I[n]}</svg>'

LOGO_MARK = '<svg viewBox="0 0 32 32" aria-hidden="true"><g fill="#f4bd0b"><path d="M5 13 13 5l4 4-8 8z"/><path d="M15 9l4-4 8 8-4 4z" opacity=".72"/><path d="M5 25l8-8 4 4-8 8z" opacity=".72"/><path d="M15 21l4-4 8 8-4 4z"/></g></svg>'

PORADY = [
 ("panele-czy-parkiet", "Panele czy parkiet"),
 ("jakie-lakiery", "Jaki lakier na parkiet"),
 ("jak-dbac-o-parkiet", "Jak dbać o parkiet"),
 ("szczeliny-w-parkietach", "Szczeliny w parkiecie zimą"),
 ("listwy-wykonczeniowe", "Listwy przypodłogowe"),
 ("klasy-parkietow", "Klasy parkietu"),
]
MENU = [("start", "index.html", "Start"), ("oferta", "oferta.html", "Oferta"), ("cennik", "cennik.html", "Cennik"),
        ("realizacje", "realizacje.html", "Realizacje"), ("porady", "porady.html", "Porady"), ("kontakt", "kontakt.html", "Kontakt")]

AC = ' aria-current="page"'

def ver(p):
    return hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()[:8]

def gallery(spec, R):
    cat, _, lim = spec.partition("|")
    rows = [l.split("|") for l in open(os.path.join(ROOT, "tools/gallery.txt")).read().split("\n") if l.strip()]
    labels = {"parkiety": "Renowacja parkietu", "deski": "Deski i podłogi drewniane", "schody": "Schody drewniane",
              "sale": "Sala gimnastyczna", "nowe": "Nowa podłoga drewniana", "praca": "Przy pracy"}
    if cat == "teaser":
        pick = ["parkiety-01.webp", "schody-04.webp", "deski-11.webp", "sale-04.webp", "nowe-13.webp", "parkiety-17.webp", "schody-14.webp", "deski-06.webp", "parkiety-05.webp"]
        rows = [r for p in pick for r in rows if r[1].endswith(p)]
    elif cat != "all":
        rows = [r for r in rows if r[0] == cat]
    if lim:
        rows = rows[:int(lim)]
    out = []
    for c, n, w, h in rows:
        out.append(f'<figure data-c="{c}"><img src="{R}img/{n}" alt="{labels[c]}, realizacja Wszystko dla Parkietu" loading="lazy" width="{w}" height="{h}"></figure>')
    return "\n".join(out)

def counts():
    rows = [l.split("|") for l in open(os.path.join(ROOT, "tools/gallery.txt")).read().split("\n") if l.strip()]
    d = {}
    for r in rows:
        d[r[0]] = d.get(r[0], 0) + 1
    d["all"] = len(rows)
    return d

def header(active, sub, R):
    items = []
    for key, href, label in MENU:
        if key == "porady":
            cur = ' cur' if active == "porady" else ''
            links = "".join(f'<a href="{R}porady/{s}.html"{AC if sub == s else ""}>{t}</a>' for s, t in PORADY)
            items.append(f'<div class="dd{cur}"><button type="button" aria-expanded="false">Porady {icon("chev")}</button><div class="dd-list"><a href="{R}porady.html"{AC if active=="porady" and not sub else ""}>Wszystkie porady</a>{links}</div></div>')
        else:
            ac = ' aria-current="page"' if active == key else ''
            items.append(f'<a href="{R}{href}"{ac}>{label}</a>')
    return f'''<a class="skip" href="#tresc">Przejdź do treści</a>
<div class="topbar"><div class="wrap"><div><span>Bezpłatna wycena: <a href="tel:{TEL_H}">{TEL}</a></span><span class="hide-m">Telefon czynny codziennie <b>7:00-21:00</b></span></div><div class="hide-m"><span>Śląskie · Małopolskie · Świętokrzyskie</span></div></div></div>
<header class="nav">
  <div class="wrap nav-in">
    <a href="{R}index.html" class="logo" aria-label="Wszystko dla Parkietu, strona główna">
      <span class="logo-mark">{LOGO_MARK}</span>
      <span class="logo-txt"><b>Wszystko dla Parkietu</b><small>Artur Rejek · cyklinowanie</small></span>
    </a>
    <nav class="menu" aria-label="Menu główne">
      {"".join(items)}
    </nav>
    <div class="nav-cta">
      <a href="tel:{TEL_H}" class="btn btn-y">{icon("phone")}<span>{TEL}</span></a>
      <button class="burger" type="button" aria-label="Menu" aria-expanded="false"><span></span></button>
    </div>
  </div>
</header>'''

def footer(active, sub, R):
    def li(key, href, label):
        ac = ' aria-current="page"' if active == key and not sub else ''
        return f'<li><a href="{R}{href}"{ac}>{label}</a></li>'
    mapa = "".join(li(k, h, l) for k, h, l in MENU)
    por = "".join(f'<li><a href="{R}porady/{s}.html"{AC if sub == s else ""}>{t}</a></li>' for s, t in PORADY)
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a href="{R}index.html" class="logo"><span class="logo-mark">{LOGO_MARK}</span><span class="logo-txt"><b>Wszystko dla Parkietu</b><small>F.U. Artur Rejek</small></span></a>
        <p>Bezpyłowe cyklinowanie, układanie parkietów i podłóg drewnianych, montaż i renowacja schodów, podłogi w salach gimnastycznych.</p>
        <a class="foot-tel" href="tel:{TEL_H}">{TEL}</a>
        <p style="margin-top:6px">Codziennie 7:00-21:00</p>
      </div>
      <div><h4>Mapa strony</h4><ul>{mapa}</ul></div>
      <div><h4>Porady</h4><ul>{por}</ul></div>
      <div><h4>Kontakt</h4><ul>
        <li>ul. Fryderyka Chopina 4a<br>42-400 Poręba</li>
        <li><a href="mailto:biurocyklinowanie@interia.pl">biurocyklinowanie@interia.pl</a></li>
        <li><a href="https://www.facebook.com/profile.php?id=100057044276317" target="_blank" rel="noopener">Facebook</a></li>
        <li style="margin-top:8px">Zawiercie, Poręba, Myszków, Siewierz, Olkusz, Wolbrom, Częstochowa, Tarnowskie Góry, Bytom i okolice</li>
      </ul></div>
    </div>
    <div class="foot-bottom"><span>© 2026 F.U. Wszystko dla Parkietu Artur Rejek</span><span>Projekt strony: <a href="https://impulseo.pl" target="_blank" rel="noopener">Impulseo</a></span></div>
  </div>
</footer>
<div class="callbar"><a href="tel:{TEL_H}">{icon("phone")} Zadzwoń</a><a href="{R}kontakt.html#formularz">{icon("doc")} Darmowa wycena</a></div>'''

def page(src):
    raw = open(src, encoding="utf-8").read()
    m = re.match(r"<!--(\{.*?\})-->\n", raw, re.S)
    meta = json.loads(m.group(1))
    body = raw[m.end():]
    out = meta["out"]
    depth = out.count("/")
    R = "../" * depth
    active, sub = meta.get("active", ""), meta.get("sub", "")
    body = re.sub(r"%I:(\w+)%", lambda x: icon(x.group(1)), body)
    body = re.sub(r"%GAL:([\w|]+)%", lambda x: gallery(x.group(1), R), body)
    c = counts()
    body = re.sub(r"%N:(\w+)%", lambda x: str(c.get(x.group(1), 0)), body)
    body = body.replace("%R%", R).replace("%TEL%", TEL).replace("%TELH%", TEL_H)
    url = BASE + ("" if out == "index.html" else out)
    og = BASE + "img/" + meta.get("og", "porownania/jodelka-sala-po.webp")
    ld = {
        "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness",
        "name": "F.U. Wszystko dla Parkietu Artur Rejek", "telephone": TEL_H, "email": "biurocyklinowanie@interia.pl",
        "url": BASE, "image": BASE + "img/bus-firmowy.webp",
        "address": {"@type": "PostalAddress", "streetAddress": "ul. Fryderyka Chopina 4a", "postalCode": "42-400", "addressLocality": "Poręba", "addressCountry": "PL"},
        "geo": {"@type": "GeoCoordinates", "latitude": 50.4858574, "longitude": 19.336819},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "07:00", "closes": "21:00"}],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "6"},
        "areaServed": ["Zawiercie", "Poręba", "Myszków", "Siewierz", "Olkusz", "Wolbrom", "Szczekociny", "Częstochowa", "Tarnowskie Góry", "Bytom"],
        "sameAs": ["https://www.facebook.com/profile.php?id=100057044276317"],
    }
    html = f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["desc"]}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{meta["title"]}">
<meta property="og:description" content="{meta["desc"]}">
<meta property="og:image" content="{og}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="pl_PL">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14213a">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%2314213a'/%3E%3Cg fill='%23f4bd0b'%3E%3Cpath d='M5 13 13 5l4 4-8 8z'/%3E%3Cpath d='M15 21l4-4 8 8-4 4z'/%3E%3C/g%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}assets/styles.css?v={ver("assets/styles.css")}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
{header(active, sub, R)}
<main id="tresc">
{body.strip()}
</main>
{footer(active, sub, R)}
<script src="{R}assets/main.js?v={ver("assets/main.js")}" defer></script>
</body>
</html>
'''
    dst = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8").write(html)
    return out

def article(src):
    raw = open(src, encoding="utf-8").read()
    first, _, body = raw.partition("\n")
    m = json.loads(first)
    slug = m["slug"]
    links = "".join(f'<li><a href="%R%porady/{s}.html"{AC if s == slug else ""}>{t}</a></li>' for s, t in PORADY)
    idx = [s for s, _ in PORADY].index(slug)
    nxt = PORADY[(idx + 1) % len(PORADY)]
    frag = f'''<!--{json.dumps({"out": "porady/" + slug + ".html", "active": "porady", "sub": slug, "title": m["title"], "desc": m["desc"], "og": m["img"]}, ensure_ascii=False)}-->
<section class="pagehead">
  <div class="wrap">
    <div class="crumbs"><a href="%R%index.html">Start</a> / <a href="%R%porady.html">Porady</a> / {[t for s, t in PORADY if s == slug][0]}</div>
    <span class="eyebrow">Nasz ekspert radzi</span>
    <h1>{m["h1"]}</h1>
  </div>
</section>
<section class="sec">
  <div class="wrap article">
    <article class="prose">
      <p class="lead">{m["lead"]}</p>
      <img src="%R%img/{m["img"]}" alt="{m["h1"]}" style="border-radius:14px;margin:1.6em 0;aspect-ratio:16/9;object-fit:cover;width:100%" loading="lazy">
{body.strip()}
      <p style="margin-top:2em"><a class="link" href="%R%porady/{nxt[0]}.html">Następna porada: {nxt[1]}</a></p>
    </article>
    <aside class="aside">
      <div class="aside-box"><h3>Porady</h3><ul>{links}</ul></div>
      <div class="aside-box aside-cta"><h3>Bezpłatna wycena</h3><p>Zadzwoń, przyjedziemy obejrzeć podłogę i doradzimy na miejscu.</p><a href="tel:%TELH%" class="btn btn-y">%I:phone% %TEL%</a></div>
    </aside>
  </div>
</section>
'''
    tmp = os.path.join(ROOT, "tools/.tmp-" + slug + ".html")
    open(tmp, "w", encoding="utf-8").write(frag)
    out = page(tmp)
    os.remove(tmp)
    return out

if __name__ == "__main__":
    for f in sorted(glob.glob(os.path.join(ROOT, "tools/content/*.html"))):
        print(page(f))
    for f in sorted(glob.glob(os.path.join(ROOT, "tools/porady/*.html"))):
        print(article(f))
