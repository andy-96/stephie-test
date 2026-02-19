"""
KUCHEN - Nachrichtenzusammenfassung
Konfiguration der Nachrichtenquellen und Einstellungen
"""

# RSS-Feeds der Nachrichtenportale
# Format: (Name, RSS-URL, Sprache)
NEWS_SOURCES = [
    # Österreich
    ("Salzburger Nachrichten", "https://www.sn.at/feed/rss", "de"),
    ("Der Standard", "https://www.derstandard.at/rss", "de"),
    ("ORF.at", "https://rss.orf.at/news.xml", "de"),
    # Deutschland
    ("Tagesschau", "https://www.tagesschau.de/xml/rss2/", "de"),
    ("Die Zeit", "https://newsfeed.zeit.de/alles", "de"),
    # International
    ("BBC", "https://feeds.bbci.co.uk/news/world/rss.xml", "en"),
    ("The Economist", "https://www.economist.com/full/rss.xml", "en"),
    ("New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "en"),
    ("Wall Street Journal", "https://feeds.content.dowjones.io/public/rss/topstories", "en"),
]

# Wie viele Artikel insgesamt sammeln (vor der Auswahl der 10 besten)
MAX_ARTICLES_TO_FETCH = 50

# Wie viele Headlines in der täglichen Übersicht
HEADLINES_COUNT = 10
