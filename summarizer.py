"""
KUCHEN - AI-gestützte Zusammenfassung
Erstellt ~2 Minuten Lesezeit-Zusammenfassungen (ca. 300–400 Wörter)
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import OpenAI

# Ca. 300 Wörter = ~2 Minuten Lesezeit
TARGET_SUMMARY_LENGTH = 350


def summarize_article(title: str, source: str, content: str, language: str) -> str:
    """
    Erstellt eine gut lesbare Zusammenfassung mit max. 2 Minuten Lesezeit.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    lang_instruction = "Deutsch" if language == "de" else "Englisch"

    prompt = f"""Du bist ein professioneller Nachrichtenredakteur. Fasse den folgenden Nachrichtenartikel in einem Fließtext zusammen.

WICHTIG:
- Schreibe die Zusammenfassung auf {lang_instruction}.
- Die Zusammenfassung soll maximal 2 Minuten Lesezeit haben (ca. 300–400 Wörter).
- Halte die wichtigsten Fakten, Hintergründe und Schlussfolgerungen bei.
- Schreibe in klarem, sachlichem Stil.
- Keine Aufzählungen, sondern fließender Text.

Titel: {title}
Quelle: {source}

Artikelinhalt:
{content[:6000]}

Zusammenfassung:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du erstellst prägnante, gut lesbare Nachrichtenzusammenfassungen."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Zusammenfassung konnte nicht erstellt werden: {str(e)}]"
