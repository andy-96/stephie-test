"""
KUCHEN - Nachrichten-Fetcher
Lädt Artikel von RSS-Feeds und extrahiert Inhalte
"""

import feedparser
import requests
from datetime import datetime
from urllib.parse import urlparse
import hashlib
import re

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False

from config import NEWS_SOURCES, MAX_ARTICLES_TO_FETCH

USER_AGENT = "KUCHEN-News-Aggregator/1.0 (Personal News Summary)"


def clean_html(text: str) -> str:
    """Entfernt HTML-Tags und überschüssige Leerzeichen."""
    if not text:
        return ""
    # Einfache HTML-Tag-Entfernung
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_article_content(url: str, max_chars: int = 50000) -> str:
    """Versucht, den vollen Artikelinhalt von einer URL zu extrahieren."""
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        if HAS_TRAFILATURA:
            content = trafilatura.extract(response.text)
            if content and len(content.strip()) > 100:
                return content[:max_chars]

        return ""
    except Exception:
        return ""


def fetch_articles() -> list[dict]:
    """Sammelt Artikel von allen konfigurierten RSS-Feeds."""
    all_articles = []

    for source_name, feed_url, lang in NEWS_SOURCES:
        try:
            feed = feedparser.parse(
                feed_url,
                agent=USER_AGENT,
                request_headers={"Accept": "application/rss+xml, application/xml"},
            )

            for i, entry in enumerate(feed.entries[:15]):  # Max pro Quelle
                if len(all_articles) >= MAX_ARTICLES_TO_FETCH:
                    break

                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "")
                published = getattr(entry, "published_parsed", None)

                if not title or not link:
                    continue

                # Beschreibung aus RSS (oft nur Teaser)
                summary_rss = ""
                if hasattr(entry, "summary"):
                    summary_rss = clean_html(entry.summary)
                elif hasattr(entry, "description"):
                    summary_rss = clean_html(entry.description)

                # Keine Extraktion beim initialen Fetch (zu langsam) – wird später für die Top 10 gemacht
                article = {
                    "id": hashlib.md5(f"{link}{title}".encode()).hexdigest()[:12],
                    "title": title,
                    "source": source_name,
                    "url": link,
                    "summary_rss": summary_rss,
                    "content": summary_rss,
                    "published": published,
                    "language": lang,
                }
                all_articles.append(article)

        except Exception as e:
            print(f"Fehler bei {source_name} ({feed_url}): {e}")

    return all_articles[:MAX_ARTICLES_TO_FETCH]
