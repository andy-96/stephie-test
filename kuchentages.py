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
    <style>
        :root {{
            --bg: #faf8f5;
            --text: #1a1a1a;
            --accent: #c45c26;
            --card: #fff;
            --muted: #6b6b6b;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 720px; margin: 0 auto; }}
        header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid var(--accent);
        }}
        h1 {{
            font-size: 2.5rem;
            margin: 0;
            color: var(--accent);
        }}
        .date {{
            color: var(--muted);
            font-size: 0.95rem;
            margin-top: 0.5rem;
        }}
        .headline {{
            background: var(--card);
            border-radius: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            overflow: hidden;
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
            gap: 0.25rem;
        }}
        .headline-btn:hover {{ background: #f5f2ef; }}
        .headline h2 {{
            margin: 0;
            font-size: 1.15rem;
            font-weight: 600;
            line-height: 1.4;
        }}
        .source {{
            font-size: 0.8rem;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .expand {{
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.7rem;
            color: var(--muted);
            transition: transform 0.2s;
        }}
        .headline-btn {{
            position: relative;
            padding-right: 2.5rem;
        }}
        .headline.expanded .expand {{ transform: translateY(-50%) rotate(180deg); }}
        .summary {{
            display: none;
            padding: 0 1.5rem 1.5rem;
            border-top: 1px solid #eee;
        }}
        .headline.expanded .summary {{ display: block; }}
        .summary-text {{
            padding-top: 1rem;
            font-size: 0.95rem;
            color: #333;
            white-space: pre-wrap;
        }}
        .summary-text br {{ display: block; content: ""; margin-top: 0.5em; }}
        .summary a {{
            display: inline-block;
            margin-top: 1rem;
            color: var(--accent);
            text-decoration: none;
            font-size: 0.9rem;
        }}
        .summary a:hover {{ text-decoration: underline; }}
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
        <footer style="margin-top: 2rem; text-align: center; color: var(--muted); font-size: 0.85rem;">
            Täglich um 7 Uhr · KUCHEN
        </footer>
    </div>
    <script>
        function toggleSummary(id) {{
            const el = document.querySelector('[data-id="' + id + '"]');
            el.classList.toggle('expanded');
        }}
    </script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    run_kuchentages()
