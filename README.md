# TikTok Auto-Poster (DW Documentary → eigenständige Zusammenfassungen)

Erzeugt täglich automatisch ein kurzes TikTok-Video: Thema aus einem neuen
DW-Documentary-Video, aber mit **komplett eigenem Skript, eigenen KI-Bildern
und eigener Stimme** (kein Reupload fremden Materials).

## Was du einmalig einrichten musst

### 1. Gemini API-Key (kostenlos)
1. Gehe zu https://aistudio.google.com
2. "Get API key" → neuen Key erstellen
3. Kopieren, brauchst du gleich für GitHub Secrets

### 2. TikTok Developer App
1. Gehe zu https://developers.tiktok.com → App registrieren
2. Produkt "Content Posting API" hinzufügen
3. Redirect-URI eintragen (z.B. `https://localhost/callback` reicht fürs Testen)
4. Du bekommst einen `client_key` und `client_secret`
5. **Einmaliger OAuth-Login:** Öffne im Browser die Autorisierungs-URL
   (Format steht in der TikTok-Doku unter "Login Kit"), logge dich mit dem
   TikTok-Konto ein, das posten soll, und erlaube den Zugriff.
   Du bekommst dabei einen `authorization_code` in der Redirect-URL.
6. Tausche den Code einmalig gegen `access_token` + `refresh_token`
   (POST an `https://open.tiktokapi.com/v2/oauth/token/`).
   Den `refresh_token` brauchst du für GitHub Secrets — er ist 1 Jahr gültig
   und wird vom Skript automatisch erneuert.
7. **Wichtig:** Bis TikTok deine App geprüft hat ("Audit"), werden alle
   Posts automatisch auf "Nur privat sichtbar" gesetzt. Das ist normal und
   kein Fehler im Skript. Für den Review brauchst du ein Demo-Video vom
   kompletten Ablauf — reiche das ein, sobald das Skript zuverlässig läuft.

### 3. GitHub Repository einrichten
1. Neues (privates!) GitHub-Repo erstellen
2. Diesen Code hochladen (`git push`)
3. Unter **Settings → Secrets and variables → Actions** folgende Secrets anlegen:
   - `GEMINI_API_KEY`
   - `TIKTOK_CLIENT_KEY`
   - `TIKTOK_CLIENT_SECRET`
   - `TIKTOK_REFRESH_TOKEN`
4. Fertig — der Workflow läuft ab jetzt jeden Tag automatisch
   (siehe `.github/workflows/daily_post.yml`, Zeit anpassbar über die Cron-Zeile)

## Lokal testen (bevor du es in GitHub Actions laufen lässt)

```bash
pip install -r requirements.txt
sudo apt install ffmpeg   # oder: brew install ffmpeg (Mac)

export GEMINI_API_KEY="dein-key"
python main.py
```

Ohne gesetzte TIKTOK_*-Variablen wird das Video nur lokal in `output/`
erzeugt, aber nicht hochgeladen — gut zum Prüfen, wie es aussieht.

## Wichtige Hinweise

- **Ein Kanal-Video pro Tag:** Das Skript verarbeitet pro Lauf nur das
  jeweils neueste, noch nicht verarbeitete Video. Postet der Quellkanal
  seltener, entsteht auch seltener ein neues TikTok-Video.
- **Rechtlich sauber bleiben:** `summarize.py` ist bewusst so formuliert,
  dass Gemini das Originalskript NICHT nacherzählt, sondern eine wirklich
  eigenständige Formulierung der Fakten erstellt. Wirf gelegentlich einen
  Blick auf die generierten Skripte, um das zu prüfen.
- **Kosten:** Bei normaler Nutzung (1 Video/Tag) bleibst du im kostenlosen
  Kontingent von Gemini, Pollinations.ai, edge-tts und GitHub Actions.
