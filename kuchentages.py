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
from news_fetcher import fetch_articles
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

        if api_key:
            summary = summarize_article(
                art["title"],
                art["source"],
                art["content"] or art["summary_rss"],
                art["language"],
            )
        else:
            summary = (
                art["summary_rss"]
                or "Kein Inhalt verfügbar. Bitte OPENAI_API_KEY setzen für AI-Zusammenfassungen."
            )

        results.append({
            "id": art["id"],
            "title": art["title"],
            "source": art["source"],
            "url": art["url"],
            "summary": summary,
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

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KUCHEN – Nachrichtenzusammenfassung</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --coral: #FF6B6B;
            --turquoise: #00D9C0;
            --sunny: #FFD93D;
            --lime: #6BCB77;
            --tangerine: #FF8C42;
            --sky: #4ECDC4;
            --hot-pink: #FF6B9D;
            --text: #1a1a2e;
            --text-soft: #4a4a6a;
            --white: #ffffff;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Outfit', -apple-system, sans-serif;
            background: linear-gradient(135deg, #FFF5E6 0%, #FFE4EC 30%, #E6F9FF 70%, #E8FFF0 100%);
            min-height: 100vh;
            color: var(--text);
            line-height: 1.7;
            padding: 2rem 1rem 3rem;
        }}
        .container {{ max-width: 680px; margin: 0 auto; }}
        header {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}
        h1 {{
            font-size: 3rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(135deg, var(--coral), var(--tangerine));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }}
        .date {{
            color: var(--text-soft);
            font-size: 0.95rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }}
        .headline {{
            background: rgba(255,255,255,0.9);
            backdrop-filter: blur(12px);
            border-radius: 16px;
            margin-bottom: 0.75rem;
            box-shadow: 0 4px 24px rgba(255,107,107,0.08), 0 2px 8px rgba(0,0,0,0.04);
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.8);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .headline:hover {{
            transform: translateY(-1px);
            box-shadow: 0 8px 32px rgba(255,107,107,0.12), 0 4px 12px rgba(0,0,0,0.06);
        }}
        .headline-btn {{
            width: 100%;
            text-align: left;
            padding: 1.25rem 1.5rem;
            border: none;
            background: transparent;
            cursor: pointer;
            font-family: inherit;
            font-size: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            position: relative;
            padding-right: 3rem;
            transition: background 0.2s ease;
        }}
        .headline-btn:hover {{ background: rgba(255,107,107,0.04); }}
        .headline h2 {{
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
            line-height: 1.45;
            color: var(--text);
        }}
        .source {{
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            background: linear-gradient(90deg, var(--coral), var(--tangerine));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .expand {{
            position: absolute;
            right: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--turquoise), var(--sky));
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.6rem;
            font-weight: 700;
            transition: transform 0.3s ease, background 0.2s ease;
        }}
        .headline-btn:hover .expand {{ background: linear-gradient(135deg, var(--coral), var(--hot-pink)); }}
        .headline.expanded .expand {{ transform: translateY(-50%) rotate(180deg); }}
        .summary {{
            display: none;
            padding: 0 1.5rem 1.5rem;
            border-top: 1px solid rgba(78,205,196,0.2);
            background: linear-gradient(180deg, rgba(78,205,196,0.03) 0%, transparent 100%);
        }}
        .headline.expanded .summary {{ display: block; animation: slideDown 0.3s ease; }}
        @keyframes slideDown {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .summary-text {{
            padding-top: 1rem;
            font-size: 0.95rem;
            color: var(--text-soft);
            white-space: pre-wrap;
        }}
        .summary-text br {{ display: block; content: ""; margin-top: 0.5em; }}
        .summary a {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 1rem;
            padding: 0.5rem 0;
            color: var(--coral);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            transition: color 0.2s ease, gap 0.2s ease;
        }}
        .summary a:hover {{ color: var(--tangerine); gap: 0.5rem; }}
        footer {{
            margin-top: 2.5rem;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 500;
            color: var(--text-soft);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍰 KUCHEN</h1>
            <p class="date">Nachrichtenzusammenfassung · {data['date']}</p>
        </header>
        <main>
            {headlines_html}
        </main>
        <footer>Täglich um 7 Uhr · KUCHEN</footer>
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
