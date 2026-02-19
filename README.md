# 🍰 KUCHEN – Tägliche Nachrichtenzusammenfassung

KUCHEN scannt jeden Morgen wichtige Nachrichtenportale aus Österreich und der Welt und erstellt eine übersichtliche Zusammenfassung mit etwa 10 Headlines. Jede Headline kann angeklickt werden – dahinter verbirgt sich eine Kurzfassung (max. 2 Leseminuten).

## Ablauf

- **Täglich um 7:00 Uhr**: Automatischer Lauf
- **~10 Headlines** pro Tag
- Pro Headline: **Titel** (Original), **Nachrichtenportal**, **Kurzfassung** (ca. 2 Min Lesezeit)

## Nachrichtenquellen

| Quelle | Land |
|--------|------|
| Salzburger Nachrichten | Österreich |
| Der Standard | Österreich |
| ORF.at | Österreich |
| Tagesschau | Deutschland |
| Die Zeit | Deutschland |
| BBC | UK |
| The Economist | UK |
| New York Times | USA |
| Wall Street Journal | USA |

## Installation

### 1. Python

Stelle sicher, dass Python 3.10 oder neuer installiert ist:

```bash
python3 --version
```

### 2. Abhängigkeiten installieren

Empfohlen: Virtuelle Umgebung (venv) verwenden:

```bash
cd /Users/andy/Code/stephie-test
python3 -m venv .venv
source .venv/bin/activate   # unter Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. OpenAI API-Key (für die Zusammenfassungen)

Für die KI-gestützten Zusammenfassungen wird ein [OpenAI API-Key](https://platform.openai.com/api-keys) benötigt. Ohne Key werden nur die RSS-Texte verwendet.

**Einfachste Variante** – `.env`-Datei anlegen:

```bash
cp .env.example .env
```

Dann in `.env` deinen API-Key eintragen:

```
OPENAI_API_KEY=sk-dein-api-key-hier
```

Alternativ kann der Key auch mit `export OPENAI_API_KEY="sk-..."` gesetzt werden.

## Nutzung

### Manuell ausführen

```bash
# Falls venv aktiviert:
python kuchentages.py

# Oder mit vollem Pfad:
python3 kuchentages.py
```

Die Ausgabe landet in `output/`:

- `output/index.html` – Webseite zum Öffnen im Browser
- `output/kuchentages.json` – Rohdaten

Öffne `output/index.html` im Browser.

### Automatisch täglich um 7:00 Uhr (macOS)

```bash
crontab -e
```

Dann folgende Zeile einfügen (Pfad anpassen):

```
0 7 * * * cd /Users/andy/Code/stephie-test && .venv/bin/python kuchentages.py
```

Oder ohne venv:

```
0 7 * * * cd /Users/andy/Code/stephie-test && /usr/bin/python3 kuchentages.py
```

Oder mit `open` die HTML-Datei direkt öffnen:

```
0 7 * * * cd /Users/andy/Code/stephie-test && /usr/bin/python3 kuchentages.py && open output/index.html
```

**Hinweis**: `cron` nutzt eine reduzierte Umgebung. Damit `OPENAI_API_KEY` verfügbar ist, kannst du ihn in eine `.env`-Datei legen und das Skript so anpassen, dass es diese Datei lädt. Alternativ den Key in `crontab` setzen:

```
0 7 * * * OPENAI_API_KEY="sk-..." cd /Users/andy/Code/stephie-test && /usr/bin/python3 kuchentages.py
```

## Im Internet hosten (Handy, Tablet, etc.)

KUCHEN kann kostenlos über **GitHub Pages** online gestellt werden. Dann erreichst du es von überall.

### Schritte

1. **Projekt zu GitHub hochladen** (falls noch nicht geschehen):
   ```bash
   git add .
   git commit -m "KUCHEN"
   git branch -M main
   git remote add origin https://github.com/DEIN-USERNAME/stephie-test.git
   git push -u origin main
   ```

2. **GitHub Pages aktivieren**:
   - Im Repo: **Settings** → **Pages**
   - Bei **Source**: „GitHub Actions“ wählen
   - Speichern

3. **OpenAI API-Key als Secret hinzufügen** (für KI-Zusammenfassungen):
   - Im Repo: **Settings** → **Secrets and variables** → **Actions**
   - **New repository secret**
   - Name: `OPENAI_API_KEY`
   - Value: dein API-Key

4. **Ersten Lauf starten**:
   - **Actions** → Workflow „KUCHEN täglich“ → **Run workflow**

Fertig. Die URL lautet z.B.:
`https://DEIN-USERNAME.github.io/stephie-test/`

### Manuell aktualisieren

Unter **Actions** → „KUCHEN täglich“ → **Run workflow** kannst du jederzeit manuell eine neue Ausgabe erzeugen.

---

## Anpassungen

- **Quellen ändern**: In `config.py` die Liste `NEWS_SOURCES` bearbeiten
- **Anzahl Headlines**: In `config.py` den Wert `HEADLINES_COUNT` ändern (Standard: 10)

## Lizenz

Für den privaten Gebrauch.
