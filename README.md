# TorrentMagnet

Lokální, spolehlivý a soukromý stahovač torrentů / magnetů s automatickým hledáním a překladem titulků.
A local, reliable and private torrent / magnet downloader with automatic subtitle search and translation.

Engine: **libtorrent 2.0** (stejná knihovna jako qBittorrent / Deluge) · čistě lokálně na `127.0.0.1` · bez reklam, bez telemetrie.
Engine: **libtorrent 2.0** (the same library qBittorrent / Deluge use) · runs purely locally on `127.0.0.1` · no ads, no telemetry.

---

## 🇨🇿 Česky

### Co to umí
- **Magnet i .torrent** – vlož magnet odkaz (i víc najednou), přetáhni `.torrent` soubor, nebo vlož přímý odkaz.
- **Spolehlivé dotažení** – magnet → metadata → kompletní stažení v jednom kroku; každý kousek se ověřuje (SHA), takže se stáhne buď celý a ověřený soubor, nebo to jasně řekne, že chybí seedeři.
- **Fronta** – stahuje max. 3 filmy najednou, po dokončení automaticky pokračuje dalším.
- **Přeskok pomalých** – pomalý / zaseknutý torrent jde dočasně na konec fronty a vrátí se k němu později.
- **Auto-stop po dokončení** – hotový torrent se sám zastaví a přestane sdílet (lze vypnout).
- **🇨🇿/🇺🇦 Titulky automaticky** – jakmile jsou metadata, appka sama na pozadí (během stahování) najde české a ukrajinské titulky na OpenSubtitles a uloží je vedle videa. **Když hotové nejsou, stáhne anglické a automaticky je přeloží.** U torrentu se objeví vlaječka (`≈` = strojový překlad). Bez API klíče.
- **Mazání ve frontě** – zaškrtni torrenty a smaž označené / dokončené / vše (i se soubory).

### Spuštění
**Windows:** dvojklik na `START.cmd`
**macOS / Linux:** v Terminálu `chmod +x START.command` (jen poprvé), pak dvojklik na `START.command` (nebo `./START.command`)

Při prvním spuštění si aplikace do složky `.venv` sama nainstaluje engine (libtorrent) – potřebuje internet, chvíli to trvá. Pak se otevře prohlížeč na `http://127.0.0.1:8765`.

Potřebuješ **Python 3.9–3.12** (Windows: při instalaci zaškrtni „Add python.exe to PATH"; macOS: `brew install python` nebo z python.org).

### Nastavení (tlačítko Nastavení)
Limity rychlosti · počet souběžných stahování (výchozí 3) · auto-titulky zap/vyp · práh „pomalého" stahování · stahování po pořádku · sdílet po dokončení · otevírat prohlížeč při startu.

---

## 🇬🇧 English

### Features
- **Magnet & .torrent** – paste a magnet link (several at once), drop a `.torrent` file, or paste a direct link.
- **Reliable completion** – magnet → metadata → full download in one go; every piece is hash-verified, so you either get the complete, verified file or a clear "not enough seeders" message.
- **Queue** – downloads up to 3 movies at once and continues automatically when one finishes.
- **Slow-skip** – a slow / stalled torrent is moved to the back of the queue and retried later.
- **Auto-stop on completion** – a finished torrent stops and stops seeding automatically (can be turned off).
- **🇨🇿/🇺🇦 Automatic subtitles** – as soon as metadata is available, the app searches OpenSubtitles in the background (while downloading) for Czech and Ukrainian subtitles and saves them next to the video. **If ready-made ones aren't available, it downloads English subtitles and translates them automatically.** A flag appears on the torrent (`≈` = machine translation). No API key required.
- **Bulk delete** – tick torrents and delete the selected / finished / all of them (including files).

### Run it
**Windows:** double-click `START.cmd`
**macOS / Linux:** run `chmod +x START.command` once, then double-click `START.command` (or `./START.command`)

On first launch the app installs its engine (libtorrent) into a `.venv` folder – it needs internet and takes a moment. Then your browser opens at `http://127.0.0.1:8765`.

Requires **Python 3.9–3.12** (Windows: tick "Add python.exe to PATH" during install; macOS: `brew install python` or from python.org).

### Settings
Speed limits · max concurrent downloads (default 3) · auto-subtitles on/off · "slow" threshold · sequential download · keep seeding after completion · open browser on start.

---

## Jak to funguje / How it works
- `app/server.py` – HTTP server + třída `TorrentEngine` nad libtorrent / HTTP server + `TorrentEngine` class over libtorrent.
- `app/public/` – webové rozhraní (HTML/CSS/JS) / the web UI.
- Stav, fronta a resume se ukládají do `config/` / state, queue and resume data are stored in `config/`.
- Stažené soubory jdou do `downloads/` (nebo zvolené složky) / downloads go to `downloads/` (or a folder you choose).

## Poznámky / Notes
- Titulky: OpenSubtitles (XML-RPC, bez klíče) · překlad: veřejný překladový endpoint (bez klíče). Strojový překlad není dokonalý, ale je použitelný. / Subtitles via OpenSubtitles (key-less XML-RPC); translation via a public endpoint. Machine translation isn't perfect but it's usable.
- Stahuj jen obsah, ke kterému máš práva. / Only download content you have the rights to.

## Licence / License
MIT
