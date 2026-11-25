"""Rebuild only the marked regions of the static site using cases.json."""
from html import escape
import json
from pathlib import Path
import re

SITE = Path(__file__).resolve().parents[1] / "site"
DATA = SITE / "portfolio"
PAGE = SITE / "index.html"
cases = json.loads((DATA / "cases.json").read_text(encoding="utf-8"))
if len({case["id"] for case in cases}) != len(cases):
    raise ValueError("Идентификаторы работ должны быть уникальными.")
if not cases:
    raise ValueError("Добавьте хотя бы одну работу в cases.json.")
def title(case):
    return escape(case.get("short_title") or case["title"], quote=True)

def number(value):
    return f"{value / 1000:g}".replace(".", ",")

def image(case, sizes, hero=False):
    path = Path(case["thumbnail"])
    small = path.with_stem(path.stem + "-360")
    src = escape("portfolio/" + path.as_posix(), quote=True)
    variants = ""
    if (DATA / small).is_file():
        # Source thumbnails have slightly different native widths. Use their actual sizes.
        import struct
        content = (DATA / path).read_bytes()
        if content[12:16] == b"VP8L":
            width = 1 + (int.from_bytes(content[21:25], "little") & 0x3fff)
        elif content[12:16] == b"VP8 ":
            width = struct.unpack_from("<H", content, 26)[0] & 0x3fff
        else:
            width = 0
        if width > 360:
            variants = f' srcset="portfolio/{escape(small.as_posix())} 360w, {src} {width}w" sizes="{sizes}"'
    loading = "eager" if hero else "lazy"
    return f'<img src="{src}"{variants} loading="{loading}" decoding="async" alt="Обложка «{title(case)}»">'

ranked = sorted(cases, key=lambda case: -case["views_approx"])
for case in cases:
    for field in ("thumbnail", "source"):
        if not (DATA / case[field]).is_file():
            raise ValueError(f'Нет изображения: {case[field]}')
    if not re.fullmatch(r"[a-z0-9_-]+", case["id"]):
        raise ValueError("Используйте латиницу и цифры в id работы.")

def card(case, featured):
    cat = escape(case["category"].split(" / ")[-1])
    size = "(max-width: 680px) 90vw, 32vw" if featured else "(max-width: 680px) 46vw, 20vw"
    video = ""
    if case.get("video_url"):
        url = escape(case["video_url"], quote=True)
        video = f'<a class="case-video" href="{url}">Выпуск на YouTube</a>'
    return f'''<article class="case">
  <a class="case-link" data-view="{case['id']}" data-title="{title(case)}" href="portfolio/{escape(case['source'])}" aria-label="Открыть исходный скриншот: {title(case)}">
    <span class="case-image">{image(case,size)}<span class="zoom" aria-hidden="true">⤢</span></span>
    <span class="case-meta"><span>{cat}</span><span>{number(case['views_approx'])} тыс. просмотров</span></span>
    <h3>{title(case)}</h3>
  </a>{video}
</article>'''

hero = []
ordered = sorted(cases, key=lambda c: ["talgo", "dodo", "tank500"].index(c["id"]) if c["id"] in ["talgo","dodo","tank500"] else 3)[:3]
for i, case in enumerate(ordered):
    hero.append(f'''<a class="cover cover-{i+1}" data-hero="{case['id']}" href="portfolio/{escape(case['source'])}" aria-label="Рассмотреть обложку «{title(case)}», {number(case['views_approx'])} тыс. просмотров"><span class="view-tag">{number(case['views_approx'])} тыс. <span>просмотров</span></span>{image(case,"(max-width: 680px) 50vw, 22vw",True)}</a>''')
total = sum(c["views_approx"] for c in cases)
updated = PAGE.read_text(encoding="utf-8")
def replace_region(key, content):
    global updated
    pattern = f"<!-- {key} -->.*?<!-- /{key} -->"
    updated, count = re.subn(pattern, lambda _: f"<!-- {key} -->{content}<!-- /{key} -->", updated, flags=re.S)
    if count != 1:
        raise ValueError(f"Не найдена область {key} в index.html")
replace_region("hero-covers", "\n".join(hero))
replace_region("featured", "\n".join(card(c, True) for c in ranked[:3]))
replace_region("other", "\n".join(card(c, False) for c in ranked[3:]))
temp = PAGE.with_suffix(".tmp")
temp.write_text(updated, encoding="utf-8")
temp.replace(PAGE)
print(f"Готово. Работ: {len(cases)}. Просмотров по скриншотам: {total}.")
