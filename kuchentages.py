#!/usr/bin/env python3
"""
KUCHEN - Hauptskript für die tägliche Nachrichtenzusammenfassung
Läuft idealerweise täglich um 7:00 Uhr morgens
"""

import os
import json
from pathlib import Path

# Lädt .env falls vorhanden (z.B. OPENAI_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from datetime import datetime

from config import NEWS_SOURCES, HEADLINES_COUNT
from news_fetcher import fetch_articles, fetch_article_content
from summarizer import summarize_article


def select_top_headlines(articles: list[dict], n: int = HEADLINES_COUNT) -> list[dict]:
    """
    Wählt die n relevantesten Artikel aus.
    Einfache Heuristik: abwechslungsreiche Quellen, neuere Artikel bevorzugt.
    """
    # Gruppieren nach Quelle, um Vielfalt zu sichern
    by_source = {}
    for a in articles:
        src = a["source"]
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(a)

    selected = []
    used_sources = set()
    round_num = 0

    while len(selected) < n and round_num < 20:
        for src, arts in by_source.items():
            if len(selected) >= n:
                break
            idx = round_num % len(arts) if arts else 0
            if idx < len(arts):
                art = arts[idx]
                if art["id"] not in [s["id"] for s in selected]:
                    selected.append(art)
        round_num += 1

    return selected[:n]


def run_kuchentages():
    """Hauptablauf: Artikel holen, zusammenfassen, HTML generieren."""
    print("🍰 KUCHEN startet – Nachrichten werden gesammelt...")

    articles = fetch_articles()
    print(f"   {len(articles)} Artikel gefunden.")

    headlines = select_top_headlines(articles)
    print(f"   Top {len(headlines)} Headlines ausgewählt.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("   ⚠️ OPENAI_API_KEY nicht gesetzt. Verwende RSS-Texte als Platzhalter.")

    results = []
    for i, art in enumerate(headlines, 1):
        print(f"   [{i}/{len(headlines)}] {art['source']}: {art['title'][:50]}...")

        # Vollständigen Artikeltext extrahieren
        full_text = fetch_article_content(art["url"])
        has_full_text = len(full_text.strip()) > 500

        if has_full_text:
            display_text = full_text
            print(f"      → Volltext geladen ({len(full_text)} Zeichen)")
        else:
            # Fallback: AI-Zusammenfassung oder RSS-Teaser
            if api_key:
                display_text = summarize_article(
                    art["title"],
                    art["source"],
                    art["content"] or art["summary_rss"],
                    art["language"],
                )
            else:
                display_text = (
                    art["summary_rss"]
                    or "Kein vollständiger Inhalt verfügbar. Bitte Originalartikel lesen."
                )

        results.append({
            "id": art["id"],
            "title": art["title"],
            "source": art["source"],
            "url": art["url"],
            "summary": display_text,
        })

    # Speichern
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "headlines": results,
    }

    json_path = output_dir / "kuchentages.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    html_path = output_dir / "index.html"
    generate_html(data, html_path)

    print(f"\n✅ KUCHEN fertig! Dateien in {output_dir}")
    print(f"   Öffne {html_path} im Browser.")
    return data


def generate_html(data: dict, path: Path):
    """Erzeugt die KUCHEN-Webseite."""
    headlines_html = ""
    for h in data["headlines"]:
        summary_escaped = h["summary"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        headlines_html += f"""
        <article class="headline" data-id="{h['id']}">
            <button class="headline-btn" onclick="toggleSummary('{h['id']}')">
                <h2>{h['title']}</h2>
                <span class="source">{h['source']}</span>
                <span class="expand">▼</span>
            </button>
            <div class="summary" id="summary-{h['id']}">
                <div class="summary-text">{summary_escaped.replace(chr(10), '<br>')}</div>
                <a href="{h['url']}" target="_blank" rel="noopener">Original lesen →</a>
            </div>
        </article>
        """

    # Datum gestalterisch: "DO 19 · FEB · 2026"
    dt = datetime.strptime(data["date"], "%Y-%m-%d")
    monate = ["JAN","FEB","MÄR","APR","MAI","JUN","JUL","AUG","SEP","OKT","NOV","DEZ"]
    date_formatted = f"{dt.day:02d} · {monate[dt.month-1]} · {dt.year}"
    weekday = ["MO","DI","MI","DO","FR","SA","SO"][dt.weekday()]

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KUCHEN</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #A8D8EA;
            --card: #E84A5F;
            --card-soft: #FF6B6B;
            --white: #ffffff;
            --yellow: #FFD93D;
            --yellow-warm: #F4D03F;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            min-height: 100vh;
            color: var(--white);
            line-height: 1.6;
            padding: 2rem 1rem 3rem;
            position: relative;
            overflow-x: hidden;
        }}
        .shapes {{
            position: fixed;
            inset: 0;
            pointer-events: none;
            overflow: hidden;
        }}
        .shape {{
            position: absolute;
            background: rgba(255,255,255,0.4);
            border-radius: 2px;
        }}
        .shape.circle {{ border-radius: 50%; }}
        .shape.tri {{
            width: 0; height: 0;
            background: transparent;
            border-left: 40px solid transparent;
            border-right: 40px solid transparent;
            border-bottom: 70px solid rgba(255,255,255,0.35);
        }}
        .shape.sq {{ border-radius: 4px; }}
        .shape {{ width: 80px; height: 80px; top: 15%; left: 5%; }}
        .shape:nth-child(2) {{ width: 120px; height: 120px; top: 60%; right: 8%; left: auto; }}
        .shape:nth-child(3) {{ width: 50px; height: 50px; top: 35%; right: 15%; left: auto; }}
        .shape:nth-child(4) {{ width: 100px; height: 100px; bottom: 20%; left: 10%; }}
        .shape:nth-child(5) {{ width: 60px; height: 60px; top: 80%; right: 25%; left: auto; }}
        .shape:nth-child(6) {{ width: 140px; height: 140px; top: 10%; right: 5%; left: auto; }}
        .shape:nth-child(7) {{ width: 45px; height: 45px; top: 50%; left: 3%; }}
        .shape:nth-child(8) {{ width: 90px; height: 90px; bottom: 10%; right: 10%; left: auto; }}
        .container {{ max-width: 600px; margin: 0 auto; position: relative; z-index: 1; }}
        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        h1 {{
            font-size: 2.8rem;
            font-weight: 700;
            margin: 0;
            color: var(--white);
            letter-spacing: -0.03em;
        }}
        .date {{
            margin-top: 0.75rem;
            font-size: 0.8rem;
            font-weight: 500;
            letter-spacing: 0.2em;
            color: rgba(255,255,255,0.9);
            text-transform: uppercase;
        }}
        .date span {{ opacity: 0.7; font-weight: 400; }}
        .headline {{
            background: linear-gradient(135deg, var(--card) 0%, var(--card-soft) 100%);
            border-radius: 12px;
            margin-bottom: 0.6rem;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(232,74,95,0.25);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .headline:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(232,74,95,0.35);
        }}
        .headline-btn {{
            width: 100%;
            text-align: left;
            padding: 1.2rem 1.5rem;
            border: none;
            background: transparent;
            cursor: pointer;
            font-family: inherit;
            font-size: 1rem;
            color: var(--white);
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
            position: relative;
            padding-right: 3rem;
            transition: background 0.2s ease;
        }}
        .headline-btn:hover {{ background: rgba(255,255,255,0.08); }}
        .headline h2 {{
            margin: 0;
            font-size: 1.05rem;
            font-weight: 600;
            line-height: 1.45;
            color: var(--white);
        }}
        .source {{
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: rgba(255,255,255,0.85);
        }}
        .expand {{
            position: absolute;
            right: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: rgba(255,255,255,0.25);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.55rem;
            font-weight: 700;
            transition: transform 0.3s ease, background 0.2s ease;
        }}
        .headline-btn:hover .expand {{ background: rgba(255,255,255,0.4); }}
        .headline.expanded .expand {{ transform: translateY(-50%) rotate(180deg); background: rgba(255,255,255,0.4); }}
        .summary {{
            display: none;
            padding: 0 1.5rem 1.25rem;
            border-top: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.08);
        }}
        .headline.expanded .summary {{ display: block; animation: slideDown 0.3s ease; }}
        @keyframes slideDown {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .summary-text {{
            padding-top: 1rem;
            font-size: 0.9rem;
            color: rgba(255,255,255,0.95);
            white-space: pre-wrap;
            font-weight: 400;
            line-height: 1.65;
        }}
        .summary-text br {{ display: block; content: ""; margin-top: 0.5em; }}
        .summary a {{
            display: inline-block;
            margin-top: 0.75rem;
            color: var(--yellow-warm);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        }}
        .summary a:hover {{ text-decoration: underline; }}
        footer {{
            margin-top: 2rem;
            text-align: center;
            font-size: 0.8rem;
            font-weight: 500;
            color: rgba(255,255,255,0.7);
            letter-spacing: 0.1em;
        }}
    </style>
</head>
<body>
    <div class="shapes">
        <div class="shape circle"></div>
        <div class="shape circle"></div>
        <div class="shape circle"></div>
        <div class="shape circle"></div>
        <div class="shape sq"></div>
        <div class="shape sq"></div>
        <div class="shape sq"></div>
        <div class="shape sq"></div>
    </div>
    <div class="container">
        <header>
            <h1>KUCHEN</h1>
            <p class="date">{weekday} &nbsp; {date_formatted}</p>
        </header>
        <main>
            {headlines_html}
        </main>
        <footer>Täglich um 7 Uhr</footer>
    </div>
    <script>
        function toggleSummary(id) {{
            document.querySelector('[data-id="' + id + '"]').classList.toggle('expanded');
        }}
    </script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    run_kuchentages()
