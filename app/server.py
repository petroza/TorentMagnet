# -*- coding: utf-8 -*-
"""
TorrentMagnet
Lokální spolehlivý torrent / magnet downloader pro Windows.

Engine: libtorrent (stejná knihovna, na které běží qBittorrent a Deluge).
Žádný externí proces, žádné JSON-RPC, žádné mazání metadata záznamů.
Magnet -> metadata -> kompletní stažení probíhá v jednom plynulém kroku
a libtorrent ověřuje SHA1 / SHA256 každého kousku, takže se stáhne buď
celý a ověřený soubor, nebo aplikace jasně řekne, že chybí seedeři.

Běží jen na 127.0.0.1, bez reklam, bez telemetrie.
"""
from __future__ import annotations

import gzip
import json
import os
import re
import socket
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import xmlrpc.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import libtorrent as lt
except Exception as exc:  # pragma: no cover - kontrola závislosti při startu
    print("=" * 60)
    print("  CHYBA: knihovna libtorrent není nainstalovaná.")
    print("  Spusť prosím START.cmd, který ji nainstaluje automaticky.")
    print("  Detail:", exc)
    print("=" * 60)
    sys.exit(1)

# ----------------------------------------------------------------------------
# Cesty a konstanty
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "app" / "public"
CONFIG = ROOT / "config"
RESUME_DIR = CONFIG / "resume"
TORRENTS = ROOT / "torrents"
LOGS = ROOT / "logs"
DEFAULT_DOWNLOADS = ROOT / "downloads"
SETTINGS_FILE = CONFIG / "settings.json"
SOURCES_FILE = CONFIG / "sources.json"
APP_LOG_FILE = LOGS / "app.log"

APP_HOST = "127.0.0.1"
APP_PORT = int(os.environ.get("TORRENTMAGNET_PORT", "8765"))
APP_VERSION = "1.0"

# Kvalitní veřejné trackery. Přidávají se ke každému torrentu i magnetu,
# aby se zdroje našly i u magnetů bez trackerů a u torrentů s mrtvými trackery.
# DHT/PEX/LSD běží nezávisle na tomto seznamu.
DEFAULT_TRACKERS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://explodie.org:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://uploads.gamecoast.net:6969/announce",
    "udp://tracker1.bt.moack.co.kr:80/announce",
    "https://tracker.tamersunion.org:443/announce",
    "udp://tracker.0x7c0.com:6969/announce",
    "udp://9.rarbg.com:2810/announce",
]

# Spolehlivé DHT bootstrap uzly pro hledání peerů bez trackeru.
DHT_BOOTSTRAP = ",".join([
    "router.bittorrent.com:6881",
    "dht.transmissionbt.com:6881",
    "router.utorrent.com:6881",
    "dht.libtorrent.org:25401",
    "router.bitcomet.com:6881",
])


# ----------------------------------------------------------------------------
# Pomocné funkce
# ----------------------------------------------------------------------------
def ensure_dirs() -> None:
    for p in (CONFIG, RESUME_DIR, TORRENTS, LOGS, DEFAULT_DOWNLOADS):
        p.mkdir(parents=True, exist_ok=True)


def app_log(message: str) -> None:
    try:
        ensure_dirs()
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {message}\n"
        with APP_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def is_client_disconnect(exc: BaseException) -> bool:
    """Prohlížeč zavřel spojení. Není to chyba aplikace."""
    if isinstance(exc, (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):
        return True
    winerror = getattr(exc, "winerror", None)
    err_no = getattr(exc, "errno", None)
    return winerror in (10053, 10054) or err_no in (32, 104, 10053, 10054)


def default_settings() -> Dict[str, Any]:
    return {
        "download_dir": str(DEFAULT_DOWNLOADS.resolve()),
        "auto_open_browser": True,
        "max_download_kbps": 0,      # 0 = bez limitu
        "max_upload_kbps": 0,        # 0 = bez limitu
        "max_concurrent": 3,         # kolik torrentů stahuje současně
        "sequential": False,         # stahovat po pořádku (pro náhled videa)
        "keep_seeding": False,       # po dokončení dál sdílet
        "slow_skip": True,           # pomalé/zaseknuté torrenty přeskočit a vrátit se k nim později
        "slow_skip_kbps": 30,        # hranice "pomalého" stahování v KB/s
        "auto_subtitles": True,      # automaticky hledat CZ/UA titulky během stahování
    }


def load_settings() -> Dict[str, Any]:
    ensure_dirs()
    data = default_settings()
    if SETTINGS_FILE.exists():
        try:
            loaded = json.loads(SETTINGS_FILE.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                data.update(loaded)
        except Exception:
            pass
    try:
        Path(data["download_dir"]).expanduser().mkdir(parents=True, exist_ok=True)
    except Exception:
        data["download_dir"] = str(DEFAULT_DOWNLOADS.resolve())
        DEFAULT_DOWNLOADS.mkdir(parents=True, exist_ok=True)
    return data


def save_settings_file(data: Dict[str, Any]) -> None:
    ensure_dirs()
    SETTINGS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        n = int(float(str(value).strip()))
    except Exception:
        n = default
    return max(minimum, min(maximum, n))


def safe_filename(name: str) -> str:
    name = name.replace("\\", "_").replace("/", "_")
    name = re.sub(r"[^A-Za-z0-9._ -]+", "_", name).strip(" ._")
    return name or "soubor.torrent"


def info_hash_from_obj(obj: Any) -> str:
    """Vrátí hex info-hash z handle / status / add_torrent_params.
    Preferuje v1 (klasický 40-znakový SHA1), jinak v2.
    """
    try:
        ihs = obj.info_hashes() if callable(getattr(obj, "info_hashes", None)) else obj.info_hashes
        v1 = str(ihs.v1)
        if v1 and set(v1) != {"0"}:
            return v1.lower()
        v2 = str(ihs.v2)
        if v2 and set(v2) != {"0"}:
            return v2.lower()
    except Exception:
        pass
    try:
        return str(obj.info_hash()).lower()
    except Exception:
        return ""


def normalize_magnet_hash(raw: str) -> str:
    """Z magnet odkazu nebo holého hashe udělá hex info-hash (kvůli porovnání duplicit)."""
    m = re.search(r"(?:^|[?&])xt=urn:btih:([^&]+)", raw, re.I)
    if not m:
        m = re.search(r"btih:([^&\s]+)", raw, re.I)
    if not m:
        return ""
    h = urllib.parse.unquote(m.group(1)).strip()
    if re.fullmatch(r"[a-fA-F0-9]{40}", h):
        return h.lower()
    if re.fullmatch(r"[A-Z2-7]{32}", h.upper()):
        try:
            import base64
            return base64.b32decode(h.upper()).hex().lower()
        except Exception:
            return ""
    return h.lower()


def human_state(status: Any) -> Tuple[str, str]:
    """Vrátí (technický stav, lidský popis) podle stavu libtorrent torrentu."""
    st = status.state
    States = lt.torrent_status.states
    paused = bool(getattr(status, "paused", False))
    if status.errc and status.errc.value() != 0:
        return "error", f"Chyba: {status.errc.message()}"
    if st == States.checking_resume_data:
        return "checking", "Kontroluji uložená data…"
    if st == States.checking_files:
        return "checking", "Ověřuji už stažené kousky…"
    if st == States.downloading_metadata:
        return "metadata", "Načítám metadata z magnetu (DHT/trackery)…"
    # Dokončený torrent je "Hotovo" i když je zastavený (sdílení vypnuté po dokončení).
    if status.is_finished:
        if paused:
            return "seeding", "Hotovo. Soubor je kompletní a ověřený. Sdílení automaticky zastaveno."
        return "seeding", "Hotovo. Soubor je kompletní a ověřený. Sdílím dál ostatním."
    if paused:
        return "paused", "Pozastaveno."
    if st == States.downloading:
        if status.download_rate <= 0 and status.num_peers == 0:
            return "stalled", "Hledám peery. Pokud to dlouho stojí na 0, torrent má málo / žádné seedery."
        if status.download_rate <= 0 and status.num_seeds == 0:
            return "stalled", "Připojeno k peerům, ale nikdo nemá kompletní soubor (0 seederů)."
        return "downloading", "Stahuji."
    return "active", "Pracuji…"


# ----------------------------------------------------------------------------
# Titulky (OpenSubtitles, bez API klíče – přes XML-RPC a registrovaný user-agent)
# ----------------------------------------------------------------------------
OS_RPC_URL = "https://api.opensubtitles.org/xml-rpc"
OS_USER_AGENT = "VLSub 0.10.2"
# kód jazyka (klíč = přípona souboru .xx.srt a kód ve vlaječce):
#   os = jazyk v OpenSubtitles (639-2), gt = cílový kód pro překladač (Google),
#   ukrajinština se navenek značí "ua", ale překladač ji zná jako "uk".
SUBTITLE_LANGS = {
    "ua": {"os": "ukr", "gt": "uk", "label": "ukrajinské", "decode": ["utf-8-sig", "utf-8", "cp1251", "koi8-u"]},
    "cs": {"os": "cze", "gt": "cs", "label": "české", "decode": ["utf-8-sig", "utf-8", "cp1250", "iso-8859-2"]},
}

VIDEO_EXTS = (".mkv", ".mp4", ".avi", ".mov", ".wmv", ".m4v", ".webm", ".ts", ".mpg", ".mpeg", ".flv")


JUNK_TOKEN = re.compile(r"^(1080p|720p|2160p|480p|4k|uhd|bluray|blu-ray|brrip|bdrip|web-?rip|web-?dl|hdrip|dvdrip|"
                        r"hdtv|cam|ts|x264|x265|h264|h265|hevc|av1|xvid|divx|aac|ac3|eac3|dts|dd|ddp|ddp?5|"
                        r"atmos|truehd|flac|mp3|hdr|hdr10|dv|sdr|10bit|8bit|remux|repack|proper|extended|"
                        r"unrated|internal|limited|yts|yify|rarbg|evo|fgt|galaxyrg|amzn|nf|hmax|dsnp|atvp|"
                        r"multi|dual|dubbed|dub|dabing|hallowed)([\-.].*)?$", re.I)
YEAR_TOKEN = re.compile(r"^(19|20)\d{2}$")


def clean_movie_query(name: str) -> str:
    """Z názvu releasu / souboru udělá čistý hledací dotaz.
    '[www.UIndex.org] - The Super Mario Galaxy Movie 2026 BluRay 1080p ...' -> 'The Super Mario Galaxy Movie 2026'
    """
    q = name
    for ext in VIDEO_EXTS:
        if q.lower().endswith(ext):
            q = q[: -len(ext)]
    # 1) pryč s [tagy], {tagy}, (skupinami) na začátku/uvnitř – často názvy webů/trackerů
    q = re.sub(r"[\[\{][^\]\}]*[\]\}]", " ", q)
    # 2) pryč s doménami (www.uindex.org, yts.mx, …) – PŘED nahrazením teček mezerami
    q = re.sub(r"\b(?:www\.)?[a-z0-9][a-z0-9-]*\.(?:org|com|net|to|me|tv|cc|info|eu|io|mx|ag|si)\b", " ", q, flags=re.I)
    # 3) tečky/podtržítka -> mezery, pryč s úvodními oddělovači
    q = q.replace(".", " ").replace("_", " ")
    q = re.sub(r"^[\s\-–—:|]+", "", q)
    tokens = q.split()
    keep: List[str] = []
    for tok in tokens:
        if JUNK_TOKEN.match(tok):
            break
        keep.append(tok)
        if YEAR_TOKEN.match(tok):
            break
    result = " ".join(keep).strip(" -–—:|")
    return result or " ".join(tokens[:6])


def decode_subtitle(raw: bytes, declared: str, lang_key: str) -> str:
    """Dekóduje stažený titulkový soubor do textu. Zkusí deklarované kódování, pak typická pro daný jazyk."""
    candidates: List[str] = []
    if declared:
        candidates.append(declared)
    candidates += SUBTITLE_LANGS.get(lang_key, {}).get("decode", [])
    candidates += ["utf-8-sig", "utf-8", "cp1252", "cp1250", "cp1251", "iso-8859-2", "latin-1"]
    for enc in candidates:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("latin-1", errors="replace")


# ---- Strojový překlad titulků (free Google endpoint, bez API klíče) ----
def gtranslate(text: str, source: str, target: str) -> str:
    """Přeloží text přes veřejný překladový endpoint. Bez API klíče."""
    url = ("https://translate.googleapis.com/translate_a/single?client=gtx"
           f"&sl={source}&tl={target}&dt=t&q={urllib.parse.quote(text)}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (TorrentMagnet)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8", errors="replace"))
    return "".join(seg[0] for seg in (data[0] or []) if seg and seg[0] is not None)


def gtranslate_lines(lines: List[str], target: str) -> List[str]:
    """Přeloží seznam jednořádkových textů. Dávkuje po ~1600 znacích (řádky odděluje \\n,
    endpoint počet řádků zachová). Při nesouladu počtu spadne na překlad po řádku.
    """
    out: List[str] = []
    i, n = 0, len(lines)
    while i < n:
        chunk: List[str] = []
        size = 0
        while i < n and (not chunk or size + len(lines[i]) + 1 <= 1600):
            s = (lines[i].replace("\n", " ").strip() or "♪")
            chunk.append(s)
            size += len(s) + 1
            i += 1
        parts: Optional[List[str]] = None
        try:
            parts = gtranslate("\n".join(chunk), "en", target).split("\n")
        except Exception:
            parts = None
        if not parts or len(parts) != len(chunk):
            parts = []
            for s in chunk:
                try:
                    parts.append(gtranslate(s, "en", target))
                except Exception:
                    parts.append(s)
        out.extend(parts)
    return out


def parse_srt(text: str) -> List[Tuple[str, str]]:
    """Rozparsuje SRT na seznam (časování, text). Text víceřádkového titulku spojí mezerou."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")
    cues: List[Tuple[str, str]] = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.split("\n")
        ti = next((j for j, l in enumerate(lines) if "-->" in l), -1)
        if ti == -1:
            continue
        timing = lines[ti].strip()
        body = " ".join(l.strip() for l in lines[ti + 1:] if l.strip())
        cues.append((timing, body))
    return cues


def translate_srt(srt_text: str, target: str) -> str:
    """Přeloží celý SRT (jen text titulků, časování a číslování zachová) do cílového jazyka."""
    cues = parse_srt(srt_text)
    if not cues:
        return ""
    translated = gtranslate_lines([c[1] for c in cues], target)
    out: List[str] = []
    for n, (timing, body) in enumerate(cues):
        out.append(str(n + 1))
        out.append(timing)
        out.append("" if not body else (translated[n] if n < len(translated) else body))
        out.append("")
    return "\n".join(out).strip() + "\n"


# ----------------------------------------------------------------------------
# Torrentový engine na libtorrent
# ----------------------------------------------------------------------------
class TorrentEngine:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.session: Optional[lt.session] = None
        self.handles: Dict[str, lt.torrent_handle] = {}     # info_hash -> handle
        self.sources: Dict[str, Dict[str, Any]] = {}        # info_hash -> zdroj (magnet/torrent + save_path)
        self._active_since: Dict[str, float] = {}           # info_hash -> kdy začal aktivně stahovat (pro přeskok pomalých)
        self._subs_inflight: set = set()                    # info_hash, pro které právě běží hledání titulků
        self._subs_tried_session: set = set()               # info_hash bez nalezených titulků – už v této relaci nezkoušet (po restartu zas)
        self._subs_lock = threading.Lock()                  # serializace hledání titulků (šetrné k OpenSubtitles)
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None

    # --- start / stop ---------------------------------------------------
    def start(self) -> None:
        ensure_dirs()
        settings = load_settings()
        pack = self._build_settings_pack(settings)
        self.session = lt.session(pack)
        # IP filtr prázdný = nic neblokujeme.
        self.sources = self._load_sources()
        self._restore_torrents()
        self._stop.clear()
        self._worker = threading.Thread(target=self._loop, name="lt-worker", daemon=True)
        self._worker.start()
        app_log(f"libtorrent {lt.version} engine spuštěn. RPC ne, čistý in-process engine.")

    def shutdown(self) -> None:
        self._stop.set()
        if self._worker:
            self._worker.join(timeout=3)
        with self.lock:
            if self.session:
                try:
                    self._save_all_resume(blocking=True)
                except Exception as e:
                    app_log(f"Uložení resume při ukončení selhalo: {e}")
                try:
                    self.session.pause()
                except Exception:
                    pass
        app_log("Engine ukončen, data uložena.")

    def _build_settings_pack(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        dl = safe_int(settings.get("max_download_kbps", 0), 0, 0, 10_000_000)
        ul = safe_int(settings.get("max_upload_kbps", 0), 0, 0, 10_000_000)
        conc = safe_int(settings.get("max_concurrent", 5), 5, 1, 50)
        return {
            "user_agent": f"TorrentMagnet/{APP_VERSION} libtorrent/{lt.version}",
            "peer_fingerprint": "-TM0100-",
            "listen_interfaces": "0.0.0.0:6881,[::]:6881",
            "enable_dht": True,
            "enable_lsd": True,
            "enable_upnp": True,
            "enable_natpmp": True,
            "dht_bootstrap_nodes": DHT_BOOTSTRAP,
            "announce_to_all_trackers": True,
            "announce_to_all_tiers": True,
            "connections_limit": 800,
            "active_downloads": conc,
            "active_seeds": max(conc, 5),
            "active_limit": conc + max(conc, 5) + 5,
            "download_rate_limit": dl * 1024,
            "upload_rate_limit": ul * 1024,
            "alert_mask": (
                lt.alert_category.status
                | lt.alert_category.error
                | lt.alert_category.storage
            ),
            # robustnost a rychlost
            "aio_threads": 4,
            "checking_mem_usage": 256,
            "request_timeout": 20,
            "peer_connect_timeout": 12,
            "max_failcount": 6,
            "allow_multiple_connections_per_ip": True,
            "enable_outgoing_utp": True,
            "enable_incoming_utp": True,
            "enable_outgoing_tcp": True,
            "enable_incoming_tcp": True,
        }

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        with self.lock:
            if not self.session:
                return
            self.session.apply_settings(self._build_settings_pack(settings))
            seq = bool(settings.get("sequential", False))
            for h in self.handles.values():
                try:
                    h.set_sequential_download(seq)
                except Exception:
                    pass

    # --- perzistence zdrojů --------------------------------------------
    def _load_sources(self) -> Dict[str, Dict[str, Any]]:
        if SOURCES_FILE.exists():
            try:
                data = json.loads(SOURCES_FILE.read_text(encoding="utf-8-sig"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {}

    def _save_sources(self) -> None:
        try:
            SOURCES_FILE.write_text(json.dumps(self.sources, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            app_log(f"Uložení sources.json selhalo: {e}")

    # --- přidávání ------------------------------------------------------
    def _common_atp(self, atp: "lt.add_torrent_params", save_path: str, settings: Dict[str, Any]) -> None:
        atp.save_path = save_path
        # přidej výchozí trackery (nezahodí ty z magnetu/torrentu)
        try:
            existing = list(atp.trackers)
        except Exception:
            existing = []
        for tr in DEFAULT_TRACKERS:
            if tr not in existing:
                existing.append(tr)
        atp.trackers = existing
        # vlajky: nepauzovat, nechat auto-managed, odebírat aktualizace stavu
        atp.flags &= ~lt.torrent_flags.paused
        atp.flags |= lt.torrent_flags.auto_managed | lt.torrent_flags.update_subscribe
        atp.flags |= lt.torrent_flags.apply_ip_filter
        if bool(settings.get("sequential", False)):
            atp.flags |= lt.torrent_flags.sequential_download

    def add_magnet(self, magnet: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        magnet = magnet.strip()
        if not magnet.lower().startswith("magnet:"):
            raise ValueError("Tohle není platný magnet odkaz.")
        settings = load_settings()
        save_path = save_path or settings["download_dir"]
        Path(save_path).mkdir(parents=True, exist_ok=True)
        atp = lt.parse_magnet_uri(magnet)
        ih = info_hash_from_obj(atp)
        with self.lock:
            if ih and ih in self.handles:
                return {"ok": True, "duplicate": True, "infohash": ih,
                        "message": "Tento torrent už je ve frontě. Nepřidávám duplicitu."}
            self._common_atp(atp, save_path, settings)
            handle = self.session.add_torrent(atp)
            ih = info_hash_from_obj(handle) or ih
            self.handles[ih] = handle
            self.sources[ih] = {
                "type": "magnet",
                "magnet": magnet,
                "save_path": save_path,
                "added": int(time.time()),
            }
            self._save_sources()
        app_log(f"Přidán magnet {ih} -> {save_path}")
        return {"ok": True, "infohash": ih, "message": "Magnet přidán. Načítám metadata a hned poté stahuji celý obsah."}

    def add_torrent_bytes(self, content: bytes, filename: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        if not content or content[:1] != b"d":
            raise ValueError("Neplatný .torrent soubor.")
        settings = load_settings()
        save_path = save_path or settings["download_dir"]
        Path(save_path).mkdir(parents=True, exist_ok=True)
        ti = lt.torrent_info(lt.bdecode(content))
        ih = info_hash_from_obj(ti)
        # ulož .torrent pro pozdější obnovu
        torrent_path = TORRENTS / f"{ih or safe_filename(filename)}.torrent"
        try:
            torrent_path.write_bytes(content)
        except Exception:
            pass
        with self.lock:
            if ih and ih in self.handles:
                return {"ok": True, "duplicate": True, "infohash": ih,
                        "message": "Tento torrent už je ve frontě. Nepřidávám duplicitu."}
            atp = lt.add_torrent_params()
            atp.ti = ti
            self._common_atp(atp, save_path, settings)
            handle = self.session.add_torrent(atp)
            ih = info_hash_from_obj(handle) or ih
            self.handles[ih] = handle
            self.sources[ih] = {
                "type": "torrent",
                "torrent_file": str(torrent_path),
                "save_path": save_path,
                "added": int(time.time()),
            }
            self._save_sources()
        app_log(f"Přidán .torrent {ih} ({ti.name()}) -> {save_path}")
        return {"ok": True, "infohash": ih, "name": ti.name(),
                "message": "Torrent přidán. Stahuji celý obsah."}

    def add_link(self, url: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Přijme magnet odkaz nebo přímý http(s) odkaz na .torrent soubor."""
        url = url.strip()
        low = url.lower()
        if low.startswith("magnet:"):
            return self.add_magnet(url, save_path)
        if re.match(r"^https?://", low) and ".torrent" in low:
            req = urllib.request.Request(url, headers={"User-Agent": f"TorrentMagnet/{APP_VERSION}"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                content = resp.read(50_000_000)
            filename = safe_filename(Path(urllib.parse.urlparse(url).path).name or "remote.torrent")
            return self.add_torrent_bytes(content, filename, save_path)
        raise ValueError("Podporuji magnet odkaz nebo přímý odkaz na .torrent soubor.")

    # --- obnova po restartu --------------------------------------------
    def _restore_torrents(self) -> None:
        settings = load_settings()
        for ih, src in list(self.sources.items()):
            try:
                atp = self._atp_from_source(ih, src)
                if atp is None:
                    continue
                self._common_atp(atp, src.get("save_path", settings["download_dir"]), settings)
                handle = self.session.add_torrent(atp)
                real_ih = info_hash_from_obj(handle) or ih
                self.handles[real_ih] = handle
            except Exception as e:
                app_log(f"Obnova torrentu {ih} selhala: {e}")
        if self.handles:
            app_log(f"Obnoveno {len(self.handles)} torrentů z minula.")

    def _atp_from_source(self, ih: str, src: Dict[str, Any]) -> Optional["lt.add_torrent_params"]:
        # nejdřív zkus rychlé pokračování z resume dat
        rd = RESUME_DIR / f"{ih}.fastresume"
        if rd.exists():
            try:
                atp = lt.read_resume_data(rd.read_bytes())
                return atp
            except Exception as e:
                app_log(f"Resume data {ih} nečitelná, beru zdroj znovu: {e}")
        if src.get("type") == "magnet" and src.get("magnet"):
            return lt.parse_magnet_uri(src["magnet"])
        if src.get("type") == "torrent" and src.get("torrent_file"):
            tp = Path(src["torrent_file"])
            if tp.exists():
                atp = lt.add_torrent_params()
                atp.ti = lt.torrent_info(str(tp))
                return atp
        return None

    # --- resume data ----------------------------------------------------
    def _save_all_resume(self, blocking: bool = False) -> None:
        if not self.session:
            return
        requested = 0
        with self.lock:
            for h in self.handles.values():
                try:
                    if h.is_valid() and h.status().has_metadata:
                        h.save_resume_data(lt.torrent_handle.save_info_dict)
                        requested += 1
                except Exception:
                    pass
        if blocking and requested:
            # počkej na save_resume_data alerty a ulož je
            deadline = time.time() + 5
            saved = 0
            while saved < requested and time.time() < deadline:
                self.session.wait_for_alert(500)
                for a in self.session.pop_alerts():
                    self._handle_alert(a)
                    if isinstance(a, lt.save_resume_data_alert):
                        saved += 1

    def _write_resume_alert(self, alert: "lt.save_resume_data_alert") -> None:
        try:
            ih = info_hash_from_obj(alert.handle)
            buf = lt.write_resume_data_buf(alert.params)
            (RESUME_DIR / f"{ih}.fastresume").write_bytes(buf)
        except Exception as e:
            app_log(f"Zápis resume dat selhal: {e}")

    # --- akce nad frontou ----------------------------------------------
    def _get_handle(self, ih: str) -> "lt.torrent_handle":
        with self.lock:
            h = self.handles.get(ih)
        if not h or not h.is_valid():
            raise ValueError("Torrent už není ve frontě.")
        return h

    def action(self, ih: str, action: str) -> Dict[str, Any]:
        if action in ("pause", "resume", "recheck", "force_announce", "up", "down", "top", "bottom"):
            h = self._get_handle(ih)
            if action == "pause":
                h.unset_flags(lt.torrent_flags.auto_managed)
                h.pause()
            elif action == "resume":
                h.set_flags(lt.torrent_flags.auto_managed)
                h.resume()
            elif action == "recheck":
                h.force_recheck()
            elif action == "force_announce":
                h.force_reannounce()
                h.force_dht_announce()
            elif action == "up":
                h.queue_position_up()
            elif action == "down":
                h.queue_position_down()
            elif action == "top":
                h.queue_position_top()
            elif action == "bottom":
                h.queue_position_bottom()
            return {"ok": True}
        if action in ("remove", "remove_data"):
            return self.remove(ih, delete_data=(action == "remove_data"))
        raise ValueError("Neznámá akce.")

    def remove(self, ih: str, delete_data: bool = False) -> Dict[str, Any]:
        with self.lock:
            h = self.handles.get(ih)
            if h and h.is_valid():
                flags = lt.session.delete_files if delete_data else 0
                try:
                    self.session.remove_torrent(h, flags)
                except Exception:
                    self.session.remove_torrent(h)
            self.handles.pop(ih, None)
            self.sources.pop(ih, None)
            self._save_sources()
        # ukliď resume soubor
        try:
            (RESUME_DIR / f"{ih}.fastresume").unlink(missing_ok=True)
        except Exception:
            pass
        app_log(f"Odebrán torrent {ih} (data smazána={delete_data}).")
        return {"ok": True}

    def bulk_action(self, ihs: List[str], action: str) -> Dict[str, Any]:
        results = []
        for ih in ihs:
            try:
                results.append({"infohash": ih, **self.action(ih, action)})
            except Exception as e:
                results.append({"infohash": ih, "ok": False, "error": str(e)})
        return {"ok": True, "results": results}

    # --- stav fronty ----------------------------------------------------
    def list_tasks(self) -> Dict[str, Any]:
        settings = load_settings()
        tasks: List[Dict[str, Any]] = []
        total_down = 0
        total_up = 0
        with self.lock:
            handles = list(self.handles.items())
        for ih, h in handles:
            if not h.is_valid():
                continue
            try:
                s = h.status()
            except Exception:
                continue
            state, health = human_state(s)
            total = int(s.total_wanted or 0)
            done = int(s.total_wanted_done or 0)
            progress = round((done / total * 100), 1) if total else (100.0 if s.is_seeding else 0.0)
            total_down += int(s.download_rate or 0)
            total_up += int(s.upload_rate or 0)
            name = s.name or self.sources.get(ih, {}).get("magnet", "")[:60] or "Načítám…"
            tasks.append({
                "infohash": ih,
                "name": name,
                "state": state,
                "health": health,
                "progress": progress,
                "totalLength": total,
                "completedLength": done,
                "downloadSpeed": int(s.download_rate or 0),
                "uploadSpeed": int(s.upload_rate or 0),
                "numPeers": int(s.num_peers or 0),
                "numSeeds": int(s.num_seeds or 0),
                "swarmSeeds": int(s.num_complete) if s.num_complete is not None and s.num_complete >= 0 else None,
                "swarmPeers": int(s.num_incomplete) if s.num_incomplete is not None and s.num_incomplete >= 0 else None,
                "hasMetadata": bool(s.has_metadata),
                "isFinished": bool(s.is_finished),
                "isSeeding": bool(s.is_seeding),
                "paused": bool(getattr(s, "paused", False)),
                "savePath": s.save_path or self.sources.get(ih, {}).get("save_path", ""),
                "queuePosition": int(s.queue_position) if s.queue_position is not None else -1,
                "eta": self._eta(total, done, int(s.download_rate or 0)),
                "subtitles": list(self.sources.get(ih, {}).get("subtitles", [])),
                "subtitlesTr": list(self.sources.get(ih, {}).get("subtitles_tr", [])),
            })
        # seřaď podle pozice ve frontě (stahující nahoře)
        tasks.sort(key=lambda t: (t["queuePosition"] if t["queuePosition"] >= 0 else 9999))
        return {
            "ok": True,
            "tasks": tasks,
            "stat": {"downloadSpeed": total_down, "uploadSpeed": total_up, "count": len(tasks)},
            "settings": settings,
            "version": APP_VERSION,
            "libtorrent": str(lt.version),
        }

    @staticmethod
    def _eta(total: int, done: int, speed: int) -> int:
        if not total or done >= total or speed <= 0:
            return 0
        return int((total - done) / speed)

    def files_of(self, ih: str) -> Dict[str, Any]:
        h = self._get_handle(ih)
        s = h.status()
        if not s.has_metadata:
            return {"ok": True, "files": [], "message": "Metadata se ještě načítají."}
        ti = h.torrent_file()
        fs = ti.files()
        priorities = h.get_file_priorities()
        progress = h.file_progress()
        files = []
        for i in range(fs.num_files()):
            size = fs.file_size(i)
            files.append({
                "index": i,
                "path": fs.file_path(i),
                "name": Path(fs.file_path(i)).name,
                "size": size,
                "completed": int(progress[i]) if i < len(progress) else 0,
                "priority": int(priorities[i]) if i < len(priorities) else 4,
            })
        return {"ok": True, "files": files}

    # --- titulky --------------------------------------------------------
    def find_subtitles(self, ih: str) -> Dict[str, Any]:
        """Dohledá CZ/UA titulky. Když hotové na netu nejsou, stáhne anglické a automaticky přeloží."""
        h = self._get_handle(ih)
        s = h.status()
        if not s.has_metadata:
            return {"ok": False, "error": "Metadata se ještě načítají, zkus titulky za chvíli."}
        ti = h.torrent_file()
        fs = ti.files()
        best_i, best_size = -1, -1
        for i in range(fs.num_files()):
            p = fs.file_path(i)
            if p.lower().endswith(VIDEO_EXTS) and fs.file_size(i) > best_size:
                best_i, best_size = i, fs.file_size(i)
        save_path = s.save_path or self.sources.get(ih, {}).get("save_path", "")
        if best_i >= 0:
            video_full = Path(save_path) / fs.file_path(best_i)
            target_dir = video_full.parent
            stem = video_full.stem
        else:
            target_dir = Path(save_path)
            stem = Path(ti.name()).stem
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        local_eng = self._local_english_srt(h, save_path)
        query = clean_movie_query(ti.name() or s.name or "")
        app_log(f"Hledám titulky pro '{query}' (torrent {ih})")
        try:
            found = self._obtain_subtitles(query, target_dir, stem, local_eng)
        except Exception as e:
            app_log(f"Hledání titulků selhalo: {e}")
            return {"ok": False, "error": f"Hledání titulků selhalo (služba nedostupná?): {e}"}
        if found:
            with self.lock:
                src = self.sources.setdefault(ih, {})
                subs = set(src.get("subtitles", []))
                tr = set(src.get("subtitles_tr", []))
                for k, info in found.items():
                    subs.add(k)
                    (tr.add(k) if info.get("translated") else tr.discard(k))
                src["subtitles"] = sorted(subs)
                src["subtitles_tr"] = sorted(tr)
                self._save_sources()
            parts = [SUBTITLE_LANGS[k]["label"] + (" (překlad z AJ)" if v.get("translated") else "")
                     for k, v in found.items()]
            return {"ok": True, "found": list(found.keys()), "message": "Přidány titulky: " + ", ".join(parts) + "."}
        return {"ok": False, "found": [], "error": "Nenašel jsem CZ/UA ani anglické titulky pro tento film."}

    def _local_english_srt(self, h: "lt.torrent_handle", save_path: str) -> Optional[str]:
        """Najde KOMPLETNĚ stažený anglický .srt přímo v torrentu (pokud ho release obsahuje)."""
        try:
            ti = h.torrent_file()
            fs = ti.files()
            prog = h.file_progress()
            for i in range(fs.num_files()):
                p = fs.file_path(i)
                low = p.lower()
                if not low.endswith(".srt") or not any(t in low for t in (".en", "eng", "english")):
                    continue
                if i < len(prog) and prog[i] < fs.file_size(i):
                    continue  # ještě není dostažený
                full = Path(save_path) / p
                if full.is_file() and full.stat().st_size > 200:
                    app_log(f"  našel jsem anglické titulky v torrentu: {Path(p).name}")
                    return decode_subtitle(full.read_bytes(), "", "en")
        except Exception:
            pass
        return None

    def _obtain_subtitles(self, query: str, target_dir: Path, stem: str,
                          local_eng: Optional[str]) -> Dict[str, Dict[str, Any]]:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(25)
        found: Dict[str, Dict[str, Any]] = {}
        eng_text: Optional[str] = local_eng
        try:
            srv = xmlrpc.client.ServerProxy(OS_RPC_URL)
            login = srv.LogIn("", "", "en", OS_USER_AGENT)
            token = login.get("token")
            if not token:
                raise RuntimeError(f"přihlášení k OpenSubtitles selhalo ({login.get('status')})")
            os_langs = ",".join(v["os"] for v in SUBTITLE_LANGS.values()) + ",eng"

            def search(q: str):
                try:
                    return srv.SearchSubtitles(token, [{"query": q, "sublanguageid": os_langs}], {"limit": 80}).get("data") or []
                except Exception:
                    return []

            data = search(query)
            if not data:
                noyear = re.sub(r"\s*(19|20)\d{2}\s*$", "", query).strip()
                if noyear and noyear != query:
                    app_log(f"  bez výsledku, zkouším dotaz bez roku: '{noyear}'")
                    data = search(noyear)

            def best_link(os_lang: str):
                cand = [d for d in data if d.get("SubLanguageID") == os_lang
                        and str(d.get("SubFormat", "srt")).lower() == "srt"]
                if not cand:
                    cand = [d for d in data if d.get("SubLanguageID") == os_lang]
                if not cand:
                    return None
                b = max(cand, key=lambda x: int(x.get("SubDownloadsCnt") or 0))
                return (b.get("SubDownloadLink"), b.get("SubEncoding", "")) if b.get("SubDownloadLink") else None

            def fetch(link: str) -> bytes:
                req = urllib.request.Request(link, headers={"User-Agent": OS_USER_AGENT})
                with urllib.request.urlopen(req, timeout=25) as r:
                    return gzip.decompress(r.read())

            for key, meta in SUBTITLE_LANGS.items():
                # 1) hotové titulky přímo v cílovém jazyce
                direct = best_link(meta["os"])
                if direct:
                    try:
                        text = decode_subtitle(fetch(direct[0]), direct[1], key)
                        (target_dir / f"{stem}.{key}.srt").write_text(text, encoding="utf-8")
                        found[key] = {"file": f"{stem}.{key}.srt", "translated": False}
                        app_log(f"  {meta['label']} titulky uloženy (hotové).")
                        continue
                    except Exception as e:
                        app_log(f"  {meta['label']} – chyba stažení: {e}")
                # 2) fallback: anglické titulky + automatický strojový překlad
                if eng_text is None:
                    el = best_link("eng")
                    if el:
                        try:
                            eng_text = decode_subtitle(fetch(el[0]), el[1], "en")
                        except Exception as e:
                            app_log(f"  anglické titulky – chyba stažení: {e}")
                if eng_text:
                    try:
                        app_log(f"  překládám anglické titulky -> {meta['label']} …")
                        translated = translate_srt(eng_text, meta.get("gt", key))
                        if translated.strip():
                            (target_dir / f"{stem}.{key}.srt").write_text(translated, encoding="utf-8")
                            found[key] = {"file": f"{stem}.{key}.srt", "translated": True}
                            app_log(f"  {meta['label']} titulky uloženy (strojový překlad z AJ).")
                    except Exception as e:
                        app_log(f"  překlad -> {meta['label']} selhal: {e}")
            try:
                srv.LogOut(token)
            except Exception:
                pass
        finally:
            socket.setdefaulttimeout(old_timeout)
        return found

    def _auto_subtitles_scan(self) -> None:
        """Automaticky (na pozadí, během stahování) dohledá titulky pro torrenty,
        které už mají metadata a ještě se pro ně titulky nehledaly.
        """
        if not bool(load_settings().get("auto_subtitles", True)):
            return
        with self.lock:
            items = list(self.handles.items())
        for ih, h in items:
            try:
                if not h.is_valid() or not h.status().has_metadata:
                    continue
            except Exception:
                continue
            src = self.sources.get(ih, {})
            if src.get("subtitles"):
                continue  # titulky už máme
            if ih in self._subs_inflight or ih in self._subs_tried_session:
                continue
            self._subs_inflight.add(ih)
            threading.Thread(target=self._auto_subtitle_worker, args=(ih,), name="subs", daemon=True).start()

    def _auto_subtitle_worker(self, ih: str) -> None:
        try:
            with self._subs_lock:  # hledáme jen jedny titulky naráz (šetrné k službě)
                if self._stop.is_set():
                    return
                res = self.find_subtitles(ih)
            # Když se našlo, find_subtitles už uložil "subtitles" (pak se přeskakuje samo).
            # Když hledání proběhlo, ale nic nenašlo -> v této relaci už nezkoušet (po restartu zas).
            # Když nastala chyba služby (bez klíče "found") -> necháme, zkusí se znovu příště.
            if isinstance(res, dict) and "found" in res and not res.get("found"):
                self._subs_tried_session.add(ih)
        except Exception as e:
            app_log(f"Auto-titulky {ih} chyba: {e}")
        finally:
            self._subs_inflight.discard(ih)

    # --- alert smyčka na pozadí ----------------------------------------
    def _enforce_seeding_policy(self) -> None:
        """Pojistka k auto-stopu: dokončené torrenty se po stažení zastaví a přestanou
        sdílet (pokud uživatel v nastavení nezapnul další sdílení). Pokryje i případy,
        kdy se torrent dokončil mimo alert (obnova po restartu apod.).
        """
        if bool(load_settings().get("keep_seeding", False)):
            return
        with self.lock:
            handles = list(self.handles.values())
        for h in handles:
            try:
                if not h.is_valid():
                    continue
                s = h.status()
                if s.is_finished and not getattr(s, "paused", False):
                    h.unset_flags(lt.torrent_flags.auto_managed)
                    h.pause()
                    app_log(f"Sdílení po dokončení zastaveno (pojistka): {info_hash_from_obj(h)}")
            except Exception:
                pass

    # Doba (s), po kterou necháme torrent na pokoji, než ho označíme za pomalý.
    SLOW_TRIAL_SECONDS = 120

    def _rotate_slow_torrents(self) -> None:
        """Pokud stahuje víc torrentů, než je povoleno současně, a některý z aktivních
        je trvale pomalý/zaseknutý, pošle ho na konec fronty. Tím dostane šanci čekající
        torrent a k pomalému se to vrátí později (rotace / pozdější retry).
        """
        settings = load_settings()
        if not bool(settings.get("slow_skip", True)):
            return
        slow_bytes = safe_int(settings.get("slow_skip_kbps", 30), 30, 1, 1_000_000) * 1024
        now = time.time()
        with self.lock:
            items = list(self.handles.items())

        active, waiting, present = [], [], set()
        for ih, h in items:
            try:
                if not h.is_valid():
                    continue
                s = h.status()
            except Exception:
                continue
            present.add(ih)
            if s.is_finished or getattr(s, "paused", False) or not s.has_metadata:
                self._active_since.pop(ih, None)
                continue
            States = lt.torrent_status.states
            if s.state == States.downloading:
                active.append((ih, h, s))
            else:
                # auto-managed torrent, který chce stahovat, ale čeká na volný slot
                waiting.append(ih)

        # ukliď záznamy o torrentech, které už nejsou
        for ih in list(self._active_since.keys()):
            if ih not in present:
                self._active_since.pop(ih, None)

        if not waiting:
            return  # není koho pustit místo pomalého → nemá smysl rotovat

        for ih, h, s in active:
            started = self._active_since.get(ih)
            if started is None:
                self._active_since[ih] = now
                continue
            if (now - started) >= self.SLOW_TRIAL_SECONDS and int(s.download_rate or 0) < slow_bytes:
                try:
                    h.queue_position_bottom()
                    self._active_since.pop(ih, None)
                    app_log(f"Pomalý torrent přeskočen na konec fronty (vrátíme se k němu): {ih} "
                            f"({int(s.download_rate or 0)//1024} KB/s)")
                except Exception:
                    pass

    def _loop(self) -> None:
        last_resume = time.time()
        last_policy = 0.0
        last_rotate = time.time()
        while not self._stop.is_set():
            try:
                self.session.wait_for_alert(1000)
                for a in self.session.pop_alerts():
                    self._handle_alert(a)
                now = time.time()
                # pojistka pro auto-stop sdílení po dokončení (každé ~4 s)
                if now - last_policy > 4:
                    self._enforce_seeding_policy()
                    last_policy = now
                # rotace pomalých torrentů (každých ~15 s)
                if now - last_rotate > 15:
                    self._rotate_slow_torrents()
                    self._auto_subtitles_scan()
                    last_rotate = now
                # pravidelné ukládání resume dat (každých 25 s)
                if now - last_resume > 25:
                    self._save_all_resume(blocking=False)
                    last_resume = now
            except Exception as e:
                app_log(f"Chyba ve worker smyčce: {e}")
                time.sleep(0.5)

    def _handle_alert(self, alert: Any) -> None:
        if isinstance(alert, lt.save_resume_data_alert):
            self._write_resume_alert(alert)
        elif isinstance(alert, lt.metadata_received_alert):
            ih = info_hash_from_obj(alert.handle)
            app_log(f"Metadata načtena: {ih}")
            try:
                alert.handle.save_resume_data(lt.torrent_handle.save_info_dict)
            except Exception:
                pass
        elif isinstance(alert, lt.torrent_finished_alert):
            ih = info_hash_from_obj(alert.handle)
            app_log(f"DOKONČENO a ověřeno: {ih}")
            settings = load_settings()
            if not bool(settings.get("keep_seeding", False)):
                try:
                    # Vypnout auto-management, jinak by session torrent znovu rozjela kvůli seedování.
                    alert.handle.unset_flags(lt.torrent_flags.auto_managed)
                    alert.handle.pause()
                    app_log(f"Sdílení po dokončení automaticky zastaveno: {ih}")
                except Exception:
                    pass
            try:
                alert.handle.save_resume_data(lt.torrent_handle.save_info_dict)
            except Exception:
                pass
        elif isinstance(alert, lt.torrent_error_alert):
            ih = info_hash_from_obj(alert.handle)
            app_log(f"Chyba torrentu {ih}: {alert.message()}")


ENGINE = TorrentEngine()


# ----------------------------------------------------------------------------
# HTTP server
# ----------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = f"TorrentMagnet/{APP_VERSION}"

    def handle(self) -> None:
        try:
            super().handle()
        except Exception as e:
            if is_client_disconnect(e):
                return
            raise

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def send_raw(self, raw: bytes, content_type: str, status: int = 200, no_store: bool = False) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            if no_store:
                self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)
        except Exception as e:
            if is_client_disconnect(e):
                return
            raise

    def send_json(self, obj: Any, status: int = 200) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_raw(raw, "application/json; charset=utf-8", status, no_store=True)

    def read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def parse_multipart(self) -> Tuple[Dict[str, str], Dict[str, Tuple[str, bytes]]]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")
        m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
        if not m:
            raise ValueError("Chybí multipart boundary.")
        boundary = (m.group(1) or m.group(2)).encode("utf-8")
        delimiter = b"--" + boundary
        fields: Dict[str, str] = {}
        files: Dict[str, Tuple[str, bytes]] = {}
        for part in body.split(delimiter):
            part = part.strip()
            if not part or part == b"--":
                continue
            if part.endswith(b"--"):
                part = part[:-2]
            part = part.strip(b"\r\n")
            if b"\r\n\r\n" not in part:
                continue
            raw_headers, data = part.split(b"\r\n\r\n", 1)
            header_text = raw_headers.decode("utf-8", errors="replace")
            disp = ""
            for line in header_text.splitlines():
                if line.lower().startswith("content-disposition:"):
                    disp = line
                    break
            name_m = re.search(r'name="([^"]+)"', disp)
            if not name_m:
                continue
            name = name_m.group(1)
            filename_m = re.search(r'filename="([^"]*)"', disp)
            if filename_m:
                files[name] = (safe_filename(filename_m.group(1)), data)
            else:
                fields[name] = data.decode("utf-8", errors="replace")
        return fields, files

    # --- GET ------------------------------------------------------------
    def do_GET(self) -> None:
        try:
            if self.path.startswith("/api/tasks"):
                self.send_json(ENGINE.list_tasks())
                return
            if self.path.startswith("/api/settings"):
                self.send_json({"ok": True, **load_settings(), "version": APP_VERSION, "libtorrent": str(lt.version)})
                return
            if self.path.startswith("/api/logs"):
                log = ""
                try:
                    log = APP_LOG_FILE.read_text(encoding="utf-8", errors="replace")[-12000:]
                except Exception:
                    pass
                self.send_json({"ok": True, "log": log or "Log je zatím prázdný."})
                return
            if self.path.startswith("/api/files"):
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                ih = (q.get("infohash") or [""])[0]
                self.send_json(ENGINE.files_of(ih))
                return
            if self.path.startswith("/api/open-folder"):
                p = Path(load_settings()["download_dir"])
                open_system_path(p)
                self.send_json({"ok": True, "path": str(p)})
                return
            # statické soubory
            self._serve_static()
        except Exception as e:
            if is_client_disconnect(e):
                return
            app_log(f"GET chyba {self.path}: {e}")
            self.send_json({"ok": False, "error": str(e)}, 500)

    def _serve_static(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/", ""):
            path = "/index.html"
        full = (PUBLIC / path.lstrip("/")).resolve()
        if not str(full).startswith(str(PUBLIC.resolve())) or not full.exists() or full.is_dir():
            self.send_raw(b"404", "text/plain; charset=utf-8", 404)
            return
        ctype = "text/html; charset=utf-8"
        if full.suffix == ".css":
            ctype = "text/css; charset=utf-8"
        elif full.suffix == ".js":
            ctype = "application/javascript; charset=utf-8"
        elif full.suffix == ".svg":
            ctype = "image/svg+xml"
        self.send_raw(full.read_bytes(), ctype, 200)

    # --- POST -----------------------------------------------------------
    def do_POST(self) -> None:
        try:
            if self.path.startswith("/api/add-magnet"):
                data = self.read_json()
                magnet = str(data.get("magnet") or data.get("url") or "").strip()
                save_path = (data.get("download_dir") or "").strip() or None
                self.send_json(ENGINE.add_magnet(magnet, save_path))
                return

            if self.path.startswith("/api/add-link"):
                data = self.read_json()
                url = str(data.get("url") or "").strip()
                save_path = (data.get("download_dir") or "").strip() or None
                self.send_json(ENGINE.add_link(url, save_path))
                return

            if self.path.startswith("/api/add-torrent"):
                fields, files = self.parse_multipart()
                if "torrent" not in files:
                    self.send_json({"ok": False, "error": "Nebyl nahrán .torrent soubor."}, 400)
                    return
                filename, content = files["torrent"]
                save_path = (fields.get("download_dir") or "").strip() or None
                self.send_json(ENGINE.add_torrent_bytes(content, filename, save_path))
                return

            if self.path.startswith("/api/action"):
                data = self.read_json()
                ih = str(data.get("infohash", "")).strip().lower()
                action = str(data.get("action", "")).strip()
                if not ih:
                    self.send_json({"ok": False, "error": "Chybí infohash."}, 400)
                    return
                self.send_json(ENGINE.action(ih, action))
                return

            if self.path.startswith("/api/bulk-action"):
                data = self.read_json()
                ihs = [str(x).strip().lower() for x in (data.get("infohashes") or []) if str(x).strip()]
                action = str(data.get("action", "")).strip()
                self.send_json(ENGINE.bulk_action(ihs, action))
                return

            if self.path.startswith("/api/subtitles"):
                data = self.read_json()
                ih = str(data.get("infohash", "")).strip().lower()
                if not ih:
                    self.send_json({"ok": False, "error": "Chybí infohash."}, 400)
                    return
                self.send_json(ENGINE.find_subtitles(ih))
                return

            if self.path.startswith("/api/settings"):
                data = self.read_json()
                settings = load_settings()
                if "download_dir" in data:
                    raw = str(data["download_dir"]).strip().strip('"')
                    if raw:
                        p = Path(raw).expanduser()
                        if not p.is_absolute():
                            p = (ROOT / p).resolve()
                        p.mkdir(parents=True, exist_ok=True)
                        settings["download_dir"] = str(p)
                for key in ("auto_open_browser", "sequential", "keep_seeding", "slow_skip", "auto_subtitles"):
                    if key in data:
                        settings[key] = bool(data[key])
                if "max_download_kbps" in data:
                    settings["max_download_kbps"] = safe_int(data["max_download_kbps"], 0, 0, 10_000_000)
                if "max_upload_kbps" in data:
                    settings["max_upload_kbps"] = safe_int(data["max_upload_kbps"], 0, 0, 10_000_000)
                if "max_concurrent" in data:
                    settings["max_concurrent"] = safe_int(data["max_concurrent"], 3, 1, 50)
                if "slow_skip_kbps" in data:
                    settings["slow_skip_kbps"] = safe_int(data["slow_skip_kbps"], 30, 1, 1_000_000)
                save_settings_file(settings)
                ENGINE.apply_settings(settings)
                self.send_json({"ok": True, "settings": settings})
                return

            if self.path.startswith("/api/pick-folder"):
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    selected = filedialog.askdirectory(title="Vyber složku pro stahování")
                    root.destroy()
                    if selected:
                        settings = load_settings()
                        settings["download_dir"] = str(Path(selected))
                        save_settings_file(settings)
                        self.send_json({"ok": True, "path": settings["download_dir"]})
                    else:
                        self.send_json({"ok": False, "error": "Složka nebyla vybrána."})
                except Exception as e:
                    self.send_json({"ok": False, "error": f"Výběr složky nejde otevřít: {e}"}, 500)
                return

            if self.path.startswith("/api/open-folder"):
                data = self.read_json()
                ih = str(data.get("infohash", "")).strip().lower()
                if ih and ih in ENGINE.sources:
                    p = Path(ENGINE.sources[ih].get("save_path", load_settings()["download_dir"]))
                else:
                    p = Path(load_settings()["download_dir"])
                open_system_path(p)
                self.send_json({"ok": True, "path": str(p)})
                return

            self.send_raw(b"404", "text/plain; charset=utf-8", 404)
        except Exception as e:
            if is_client_disconnect(e):
                return
            app_log(f"POST chyba {self.path}: {e}")
            self.send_json({"ok": False, "error": str(e)}, 500)


def open_system_path(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        import subprocess
        subprocess.Popen(["open", str(path)])
    else:
        import subprocess
        subprocess.Popen(["xdg-open", str(path)])


def bind_server() -> Tuple[ThreadingHTTPServer, int]:
    """Naváže web server na 8765, a když je port obsazený (např. běží stará verze),
    automaticky zkusí další volný port. Vrátí server a skutečný port.
    """
    last_err: Optional[Exception] = None
    for port in range(APP_PORT, APP_PORT + 20):
        try:
            return ThreadingHTTPServer((APP_HOST, port), Handler), port
        except OSError as e:
            last_err = e
            continue
    raise RuntimeError(f"Nepodařilo se obsadit žádný port {APP_PORT}–{APP_PORT + 19}: {last_err}")


def main() -> None:
    ensure_dirs()
    try:
        server, port = bind_server()
    except Exception as e:
        print(f"CHYBA: {e}")
        app_log(f"Bind serveru selhal: {e}")
        input("Stiskni Enter pro zavření…")
        return
    url = f"http://{APP_HOST}:{port}"
    print("=" * 60)
    print(f"  TorrentMagnet  (engine: libtorrent {lt.version})")
    print("=" * 60)
    print(f"  Web:             {url}")
    if port != APP_PORT:
        print(f"  (port {APP_PORT} byl obsazený – nejspíš běží jiná/stará verze)")
    print(f"  Stažené soubory: {load_settings()['download_dir']}")
    print("  Zavření:         Ctrl+C v tomto okně")
    print("=" * 60)
    app_log(f"Start aplikace TorrentMagnet na portu {port}.")
    try:
        ENGINE.start()
        print(f"  Engine: OK (libtorrent {lt.version})")
    except Exception as e:
        print(f"  Engine: CHYBA - {e}")
        app_log(f"Start engine selhal: {e}")
    if load_settings().get("auto_open_browser", True):
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUkončuji…")
    finally:
        app_log("Ukončuji web server.")
        try:
            ENGINE.shutdown()
        except Exception:
            pass
        server.server_close()


if __name__ == "__main__":
    main()
