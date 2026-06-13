"use strict";

// ---------- SVG ikony (feather-style, dedi barvu i velikost z rodice) ----------
const ICONS = {
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
  layers: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
  magnet: '<path d="m6 15-4-4 6.75-6.77a7.79 7.79 0 0 1 11 11L13 22l-4-4 6.39-6.36a2.14 2.14 0 0 0-3-3L6 15"/><path d="m5 8 4 4"/><path d="m12 15 4 4"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
  film: '<rect x="2" y="2" width="20" height="20" rx="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
  plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  folder: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
  "folder-open": '<path d="M6 14l1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.55 6a2 2 0 0 1-1.94 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.93a2 2 0 0 1 1.66.9l.82 1.2a2 2 0 0 0 1.66.9H18a2 2 0 0 1 2 2v2"/>',
  edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
  play: '<polygon points="5 3 19 12 5 21 5 3"/>',
  pause: '<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  "file-text": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
  refresh: '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
  x: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  trash: '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  "upload-cloud": '<polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>',
  inbox: '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  zap: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  "hard-drive": '<line x1="22" y1="12" x2="2" y2="12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/><line x1="6" y1="16" x2="6.01" y2="16"/><line x1="10" y1="16" x2="10.01" y2="16"/>',
  alert: '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  subs: '<rect x="3" y="5" width="18" height="14" rx="2"/><line x1="7" y1="11" x2="11" y2="11"/><line x1="7" y1="15" x2="15" y2="15"/><line x1="14" y1="11" x2="17" y2="11"/>',
  moon: '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
  sun: '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>',
  search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
};

// vlaječky pro titulky (vlastní SVG – emoji vlajky se na Windows nezobrazují)
const FLAG_UA = '<svg viewBox="0 0 24 16"><rect width="24" height="8" fill="#0057b7"/><rect y="8" width="24" height="8" fill="#ffd700"/></svg>';
const FLAG_CZ = '<svg viewBox="0 0 24 16"><rect width="24" height="8" fill="#fff"/><rect y="8" width="24" height="8" fill="#d7141a"/><polygon points="0,0 13,8 0,16" fill="#11457e"/></svg>';
const FLAGS = { ua: FLAG_UA, uk: FLAG_UA, cs: FLAG_CZ };  // "uk" = alias pro starší data
const LANG_NAME = { ua: "UA", uk: "UA", cs: "CZ" };

function svg(name, extraClass) {
  const body = ICONS[name] || "";
  return `<svg class="${extraClass || ""}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`;
}
function ic(name, extraClass) {
  return `<span class="ico ${extraClass || ""}">${svg(name)}</span>`;
}
function flagsHTML(langs, trLangs) {
  if (!langs || !langs.length) return "";
  const tr = new Set(trLangs || []);
  const items = langs.filter(l => FLAGS[l]).map(l => {
    const isTr = tr.has(l);
    const title = LANG_NAME[l] + (isTr ? " titulky – strojový překlad z angličtiny" : " titulky přidány");
    return `<span class="sub-flag${isTr ? " translated" : ""}" title="${title}">${FLAGS[l]}${LANG_NAME[l]}${isTr ? "≈" : ""}</span>`;
  }).join("");
  return `<span class="sub-flags">${items}</span>`;
}
function fillIcons(root) {
  (root || document).querySelectorAll("[data-icon]").forEach(el => {
    if (!el.dataset.filled) { el.innerHTML = svg(el.dataset.icon); el.dataset.filled = "1"; }
  });
}

// ---------- Pomocné funkce ----------
function fmtBytes(n) {
  n = Number(n) || 0;
  if (n < 1024) return n + " B";
  const u = ["KB", "MB", "GB", "TB"];
  let i = -1;
  do { n /= 1024; i++; } while (n >= 1024 && i < u.length - 1);
  return n.toFixed(n < 10 ? 2 : 1) + " " + u[i];
}
function fmtSpeed(n) { return fmtBytes(n) + "/s"; }
function fmtEta(s) {
  s = Number(s) || 0;
  if (s <= 0) return "—";
  if (s < 60) return s + " s";
  if (s < 3600) return Math.floor(s / 60) + " min";
  if (s < 86400) return Math.floor(s / 3600) + " h " + Math.floor((s % 3600) / 60) + " min";
  return Math.floor(s / 86400) + " d";
}
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function isVideo(name) { return /\.(mkv|mp4|avi|mov|wmv|m4v|webm|ts|mpg|mpeg|flv)$/i.test(name || ""); }

async function api(path, opts) {
  const res = await fetch(path, opts);
  return res.json().catch(() => ({ ok: false, error: "Neplatná odpověď serveru." }));
}

function toast(msg, kind) {
  const t = document.getElementById("toast");
  const icon = kind === "err" ? "alert" : (kind === "ok" ? "check-circle" : "zap");
  t.innerHTML = ic(icon) + "<span>" + esc(msg) + "</span>";
  t.className = "toast" + (kind ? " " + kind : "");
  t.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { t.hidden = true; }, 4000);
}

// ---------- Záložky přidávání ----------
document.querySelectorAll(".tab").forEach(tab => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`.tab-panel[data-panel="${tab.dataset.tab}"]`).classList.add("active");
  });
});

// ---------- Přidání magnetu ----------
const addMsg = document.getElementById("addMsg");
function showAddMsg(msg, kind) {
  addMsg.innerHTML = msg ? (ic(kind === "err" ? "alert" : "check-circle") + "<span>" + esc(msg) + "</span>") : "";
  addMsg.className = "add-msg" + (kind ? " " + kind : "");
}

document.getElementById("addMagnetBtn").addEventListener("click", async () => {
  const raw = document.getElementById("magnetInput").value.trim();
  if (!raw) { showAddMsg("Vlož aspoň jeden magnet odkaz.", "err"); return; }
  const lines = raw.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
  let added = 0, dup = 0, fail = 0;
  for (const line of lines) {
    const r = await api("/api/add-magnet", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ magnet: line }),
    });
    if (r.ok && r.duplicate) dup++;
    else if (r.ok) added++;
    else fail++;
  }
  const parts = [];
  if (added) parts.push(`${added} přidáno`);
  if (dup) parts.push(`${dup} už ve frontě`);
  if (fail) parts.push(`${fail} chyba`);
  showAddMsg(parts.join(", ") || "Hotovo.", fail ? "err" : "ok");
  if (added) document.getElementById("magnetInput").value = "";
  refresh();
});

// ---------- Přidání odkazu ----------
document.getElementById("addLinkBtn").addEventListener("click", async () => {
  const url = document.getElementById("linkInput").value.trim();
  if (!url) { showAddMsg("Vlož odkaz.", "err"); return; }
  const r = await api("/api/add-link", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  showAddMsg(r.ok ? (r.message || "Přidáno.") : (r.error || "Chyba."), r.ok ? "ok" : "err");
  if (r.ok) document.getElementById("linkInput").value = "";
  refresh();
});

// ---------- Nahrání .torrent souboru ----------
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("torrentFile");
dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => uploadTorrents(fileInput.files));
["dragover", "dragenter"].forEach(ev =>
  dropZone.addEventListener(ev, e => { e.preventDefault(); dropZone.classList.add("dragover"); }));
["dragleave", "drop"].forEach(ev =>
  dropZone.addEventListener(ev, e => { e.preventDefault(); dropZone.classList.remove("dragover"); }));
dropZone.addEventListener("drop", e => uploadTorrents(e.dataTransfer.files));

async function uploadTorrents(files) {
  if (!files || !files.length) return;
  let added = 0, fail = 0;
  for (const f of files) {
    if (!f.name.toLowerCase().endsWith(".torrent")) { fail++; continue; }
    const fd = new FormData();
    fd.append("torrent", f, f.name);
    const r = await api("/api/add-torrent", { method: "POST", body: fd });
    if (r.ok) added++; else fail++;
  }
  showAddMsg(`${added} přidáno${fail ? ", " + fail + " chyba" : ""}.`, fail ? "err" : "ok");
  fileInput.value = "";
  refresh();
}

// ---------- Akce nad torrenty ----------
async function taskAction(infohash, action) {
  if (action === "remove_data" && !(await confirmDialog("Opravdu smazat torrent VČETNĚ stažených souborů z disku? Tohle nejde vrátit."))) return;
  if (action === "remove" && !(await confirmDialog("Odebrat torrent z fronty? Stažené soubory zůstanou na disku."))) return;
  const r = await api("/api/action", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ infohash, action }),
  });
  if (!r.ok) toast(r.error || "Akce selhala.", "err");
  refresh();
}

async function bulkAction(action) {
  const r = await api("/api/bulk-action", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, infohashes: currentInfohashes }),
  });
  if (!r.ok) toast(r.error || "Akce selhala.", "err");
  refresh();
}
document.getElementById("pauseAllBtn").addEventListener("click", () => bulkAction("pause"));
document.getElementById("resumeAllBtn").addEventListener("click", () => bulkAction("resume"));

// ---------- Výběr ve frontě + hromadné mazání ----------
function updateSelCount() {
  const n = selected.size;
  const cnt = document.getElementById("selCount");
  if (cnt) cnt.textContent = n ? `(${n})` : "";
  const all = document.getElementById("selectAll");
  if (all) all.checked = currentInfohashes.length > 0 && currentInfohashes.every(ih => selected.has(ih));
}

document.getElementById("queue").addEventListener("change", e => {
  if (!e.target.classList || !e.target.classList.contains("task-check")) return;
  const task = e.target.closest(".task");
  if (!task) return;
  const ih = task.dataset.ih;
  if (e.target.checked) selected.add(ih); else selected.delete(ih);
  task.classList.toggle("selected", e.target.checked);
  updateSelCount();
});

document.getElementById("selectAll").addEventListener("change", e => {
  if (e.target.checked) currentInfohashes.forEach(ih => selected.add(ih));
  else selected.clear();
  document.querySelectorAll("#queue .task").forEach(task => {
    const on = selected.has(task.dataset.ih);
    const cb = task.querySelector(".task-check"); if (cb) cb.checked = on;
    task.classList.toggle("selected", on);
  });
  updateSelCount();
});

async function bulkDelete(ihs, confirmMsg) {
  ihs = (ihs || []).filter(Boolean);
  if (!ihs.length) { toast("Nic k smazání.", "err"); return; }
  if (!(await confirmDialog(confirmMsg))) return;
  const r = await api("/api/bulk-action", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "remove_data", infohashes: ihs }),
  });
  ihs.forEach(ih => selected.delete(ih));
  if (r.ok) toast(`Smazáno: ${ihs.length} torrentů i se soubory.`, "ok");
  else toast(r.error || "Mazání selhalo.", "err");
  refresh();
}
const allInfohashes = () => allTasks.map(t => t.infohash);

document.getElementById("delSelectedBtn").addEventListener("click", () => {
  const ihs = [...selected].filter(ih => allInfohashes().includes(ih));
  if (!ihs.length) { toast("Nejdřív zaškrtni torrenty ve frontě.", "err"); return; }
  bulkDelete(ihs, `Smazat ${ihs.length} označených torrentů VČETNĚ stažených souborů z disku?\nTohle nejde vrátit.`);
});
document.getElementById("delFinishedBtn").addEventListener("click", () => {
  const ihs = allTasks.filter(t => t.isFinished || t.state === "seeding").map(t => t.infohash);
  if (!ihs.length) { toast("Žádné dokončené (stažené) torrenty.", "err"); return; }
  bulkDelete(ihs, `Smazat ${ihs.length} dokončených (stažených) torrentů VČETNĚ souborů z disku?\nTohle nejde vrátit.`);
});
document.getElementById("delAllBtn").addEventListener("click", () => {
  const ihs = allInfohashes();
  if (!ihs.length) { toast("Fronta je prázdná.", "err"); return; }
  bulkDelete(ihs, `Smazat VŠECH ${ihs.length} torrentů VČETNĚ všech stažených souborů z disku?\nTohle nejde vrátit.`);
});

async function openTaskFolder(infohash) {
  await api("/api/open-folder", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ infohash }),
  });
}

// ---------- Vykreslení fronty ----------
const STATE_LABEL = {
  downloading: "Stahuji", seeding: "Hotovo", stalled: "Hledám zdroje",
  metadata: "Metadata", checking: "Kontrola", error: "Chyba",
  paused: "Pozastaveno", active: "Aktivní",
};
let currentInfohashes = [];
let prevOrder = "";
let selected = new Set();
let allTasks = [];
let curFilter = "all";
let curSearch = "";

function renderTasks(tasks) {
  const queue = document.getElementById("queue");
  const empty = document.getElementById("emptyState");
  currentInfohashes = tasks.map(t => t.infohash);
  const allIh = allTasks.map(t => t.infohash);
  [...selected].forEach(ih => { if (!allIh.includes(ih)) selected.delete(ih); });
  document.getElementById("selectBar").hidden = !allTasks.length;

  if (!tasks.length) {
    queue.querySelectorAll(".task").forEach(e => e.remove());
    empty.style.display = "";
    if (allTasks.length) {
      empty.querySelector("h3").textContent = "Nic neodpovídá";
      empty.querySelector("p").textContent = "Zkus jiný filtr nebo vymaž hledání.";
    } else {
      empty.querySelector("h3").textContent = "Zatím tu nic není";
      empty.querySelector("p").textContent = "Přidej magnet odkaz nebo .torrent soubor nahoře a stahování se rozjede.";
    }
    prevOrder = "";
    updateSelCount();
    return;
  }
  empty.style.display = "none";

  const existing = {};
  queue.querySelectorAll(".task").forEach(el => { existing[el.dataset.ih] = el; });

  tasks.forEach(t => {
    let el = existing[t.infohash];
    if (!el) {
      // Karta se vytvoří JEN jednou. Pak se hodnoty aktualizují na místě (žádné blikání).
      el = document.createElement("div");
      el.dataset.ih = t.infohash;
      el.className = "task";
      el.innerHTML = taskSkeleton();
      queue.appendChild(el);
    } else {
      delete existing[t.infohash];
    }
    updateTask(el, t);
  });
  Object.values(existing).forEach(el => el.remove());

  // Přeskládat jen když se pořadí opravdu změní – přesun uzlu jinak restartuje animace (= blikání).
  const order = currentInfohashes.join("|");
  if (order !== prevOrder) {
    tasks.forEach(t => {
      const el = queue.querySelector(`.task[data-ih="${CSS.escape(t.infohash)}"]`);
      if (el) queue.appendChild(el);
    });
    prevOrder = order;
  }
  updateSelCount();
}

function taskSkeleton() {
  return `
    <div class="task-head">
      <input type="checkbox" class="task-check" title="Označit" />
      <span class="task-icon">
        <svg class="ring" viewBox="0 0 44 44"><circle class="ring-bg" cx="22" cy="22" r="19"></circle><circle class="ring-fg" data-h="ring" cx="22" cy="22" r="19"></circle></svg>
        <span class="task-glyph" data-h="icon"></span>
      </span>
      <div class="task-head-main">
        <div class="task-name" data-h="name"></div>
        <div class="task-sub">
          <span class="task-badge" data-h="badge"><span class="bdot"></span><span class="blabel" data-h="badgeLabel"></span></span>
          <span class="pct" data-h="pct"></span>
          <span data-h="subs"></span>
        </div>
      </div>
    </div>
    <div class="progress-wrap"><div class="progress-bar" data-h="bar"></div></div>
    <div class="task-meta">
      <span class="m" data-h="m-size">${ic("hard-drive")}<span data-h="v-size"></span></span>
      <span class="m" data-h="m-down">${ic("download")}<b data-h="v-down"></b></span>
      <span class="m" data-h="m-eta">${ic("clock")}<b data-h="v-eta"></b></span>
      <span class="m" data-h="m-up">${ic("upload")}<span data-h="v-up"></span></span>
      <span class="m" data-h="m-conn">${ic("users")}<span data-h="v-conn"></span></span>
      <span class="m" data-h="m-swarm" title="Zdroje v celém roji (tracker/DHT)">${ic("zap")}<span data-h="v-swarm"></span></span>
    </div>
    <div class="task-health" data-h="health"></div>
    <div class="task-actions" data-h="actions"></div>
  `;
}

function setShow(el, show) { if (el) el.style.display = show ? "" : "none"; }

function updateTask(el, t) {
  const q = s => el.querySelector(`[data-h="${s}"]`);
  const active = t.state === "downloading" || t.state === "metadata" || t.state === "checking";
  const stateChanged = el.dataset.state !== t.state;
  const pausedChanged = el.dataset.paused !== String(!!t.paused);
  const nameChanged = el.dataset.name !== t.name;
  const healthChanged = el.dataset.health !== (t.health || "");

  if (stateChanged) {
    el.dataset.state = t.state;
    el.className = "task state-" + t.state;
    q("badge").className = "task-badge badge-" + t.state;
    q("badgeLabel").textContent = STATE_LABEL[t.state] || t.state;
    q("bar").className = "progress-bar " + t.state + (active ? " active-anim" : "");
  }
  if (nameChanged) {
    el.dataset.name = t.name;
    q("icon").innerHTML = svg(isVideo(t.name) ? "film" : "file");
    q("name").textContent = t.name;
  }
  if (stateChanged || pausedChanged) {
    el.dataset.paused = String(!!t.paused);
    q("actions").innerHTML = actionsHTML(t);
  }

  // hodnoty, které se mění každý tik – jen text, žádné překreslování struktury
  q("pct").textContent = t.progress.toFixed(1) + " %";
  const pctClamp = Math.min(100, Math.max(0, t.progress));
  q("bar").style.width = pctClamp + "%";
  const ring = q("ring");
  if (ring) ring.style.strokeDashoffset = (119.38 * (1 - pctClamp / 100)).toFixed(1);

  if (t.totalLength) q("v-size").innerHTML = `${fmtBytes(t.completedLength)} / <b>${fmtBytes(t.totalLength)}</b>`;
  else q("v-size").textContent = "velikost se zjišťuje…";

  const showDown = t.state === "downloading" || t.downloadSpeed > 0;
  setShow(q("m-down"), showDown);
  setShow(q("m-eta"), showDown);
  if (showDown) { q("v-down").textContent = fmtSpeed(t.downloadSpeed); q("v-eta").textContent = fmtEta(t.eta); }

  setShow(q("m-up"), t.uploadSpeed > 0);
  if (t.uploadSpeed > 0) q("v-up").textContent = fmtSpeed(t.uploadSpeed);

  q("v-conn").innerHTML = `<b>${t.numSeeds}</b>s / <b>${t.numPeers}</b>p`;

  const hasSwarm = t.swarmSeeds != null || t.swarmPeers != null;
  setShow(q("m-swarm"), hasSwarm);
  if (hasSwarm) q("v-swarm").innerHTML = `roj <b>${t.swarmSeeds ?? "?"}</b>s / <b>${t.swarmPeers ?? "?"}</b>p`;

  // vlaječky titulků (≈ = strojový překlad z angličtiny)
  const subsKey = (t.subtitles || []).join(",") + "|" + (t.subtitlesTr || []).join(",");
  if (el.dataset.subs !== subsKey) {
    el.dataset.subs = subsKey;
    q("subs").innerHTML = flagsHTML(t.subtitles, t.subtitlesTr);
  }

  if (stateChanged || healthChanged) {
    el.dataset.health = t.health || "";
    const healthEl = q("health");
    if (t.health) {
      setShow(healthEl, true);
      const icoName = t.state === "seeding" ? "check-circle" : (t.state === "error" || t.state === "stalled" ? "alert" : "zap");
      healthEl.className = "task-health " + t.state;
      healthEl.innerHTML = ic(icoName) + "<span>" + esc(t.health) + "</span>";
    } else {
      setShow(healthEl, false);
    }
  }

  // obnovit stav zaškrtnutí po překreslení (className se výše mohl přepsat)
  const cb = el.querySelector(".task-check");
  if (cb) cb.checked = selected.has(t.infohash);
  el.classList.toggle("selected", selected.has(t.infohash));
}

function actionsHTML(t) {
  const ih = t.infohash;
  const pauseBtn = !t.paused
    ? `<button onclick="taskAction('${ih}','pause')">${ic("pause")}<span class="lbl">Pozastavit</span></button>`
    : `<button onclick="taskAction('${ih}','resume')">${ic("play")}<span class="lbl">Spustit</span></button>`;
  return `
    ${pauseBtn}
    <button onclick="openTaskFolder('${ih}')">${ic("folder")}<span class="lbl">Složka</span></button>
    <button class="subs-btn" onclick="findSubtitles('${ih}', this)">${ic("subs")}<span class="lbl">Titulky CZ/UA</span></button>
    <button onclick="taskAction('${ih}','force_announce')">${ic("refresh")}<span class="lbl">Hledat zdroje</span></button>
    <button onclick="taskAction('${ih}','recheck')">${ic("check")}<span class="lbl">Ověřit data</span></button>
    <button class="danger" onclick="taskAction('${ih}','remove')">${ic("x")}<span class="lbl">Odebrat</span></button>
    <button class="danger" onclick="taskAction('${ih}','remove_data')">${ic("trash")}<span class="lbl">Smazat i data</span></button>
  `;
}

async function findSubtitles(ih, btn) {
  let restore = null;
  if (btn) {
    restore = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="ico spin">${svg("refresh")}</span><span class="lbl">Hledám titulky…</span>`;
  }
  toast("Hledám ukrajinské a české titulky…");
  const r = await api("/api/subtitles", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ infohash: ih }),
  });
  if (btn) { btn.disabled = false; if (restore != null) btn.innerHTML = restore; }
  if (r.ok) toast(r.message || "Titulky přidány.", "ok");
  else toast(r.error || "Titulky se nepodařilo najít.", "err");
  refresh();
}

window.taskAction = taskAction;
window.openTaskFolder = openTaskFolder;
window.findSubtitles = findSubtitles;

// ---------- Periodické obnovení ----------
let refreshTimer = null;
async function refresh() {
  try {
    const data = await api("/api/tasks");
    if (!data.ok) return;
    document.getElementById("globalDown").textContent = fmtSpeed(data.stat.downloadSpeed);
    document.getElementById("globalUp").textContent = fmtSpeed(data.stat.uploadSpeed);
    document.getElementById("globalCount").textContent = data.stat.count;
    if (data.settings) document.getElementById("downloadDir").textContent = data.settings.download_dir;
    allTasks = data.tasks || [];
    updateFilterCounts(allTasks);
    renderTasks(applyFilter(allTasks));
  } catch (e) { /* server možná startuje */ }
}
function startRefresh() {
  refresh();
  clearInterval(refreshTimer);
  refreshTimer = setInterval(refresh, 1500);
}

// ---------- Filtry + hledání ----------
function taskGroup(t) {
  if (t.isFinished || t.state === "seeding") return "seeding";
  if (t.paused) return "paused";
  return "downloading"; // downloading / metadata / stalled / checking
}
function applyFilter(tasks) {
  const q = curSearch.trim().toLowerCase();
  return tasks.filter(t => {
    if (q && !(t.name || "").toLowerCase().includes(q)) return false;
    return curFilter === "all" || taskGroup(t) === curFilter;
  });
}
function updateFilterCounts(tasks) {
  const c = { all: tasks.length, downloading: 0, seeding: 0, paused: 0 };
  tasks.forEach(t => { c[taskGroup(t)]++; });
  document.querySelectorAll("[data-count]").forEach(el => {
    const v = c[el.dataset.count]; el.textContent = v ? v : "";
  });
}
document.getElementById("filterChips").addEventListener("click", e => {
  const chip = e.target.closest(".chip");
  if (!chip) return;
  document.querySelectorAll("#filterChips .chip").forEach(c => c.classList.remove("active"));
  chip.classList.add("active");
  curFilter = chip.dataset.filter;
  renderTasks(applyFilter(allTasks));
});
document.getElementById("searchInput").addEventListener("input", e => {
  curSearch = e.target.value;
  renderTasks(applyFilter(allTasks));
});

// ---------- Motiv (světlý / tmavý) ----------
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = document.querySelector("#themeToggle .ico");
  if (btn) btn.innerHTML = svg(theme === "light" ? "moon" : "sun");
  try { localStorage.setItem("tm-theme", theme); } catch (e) {}
}
document.getElementById("themeToggle").addEventListener("click", () => {
  const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
  applyTheme(next);
});

// ---------- Potvrzovací dialog (hezký, místo systémového confirm) ----------
function confirmDialog(text, okLabel) {
  return new Promise(resolve => {
    const modal = document.getElementById("confirmModal");
    document.getElementById("confirmText").textContent = text;
    document.getElementById("confirmOk").innerHTML = `<span class="ico">${svg("check")}</span> ${okLabel || "Potvrdit"}`;
    modal.hidden = false;
    const ok = document.getElementById("confirmOk");
    const cancel = document.getElementById("confirmCancel");
    const done = (val) => { modal.hidden = true; ok.onclick = null; cancel.onclick = null; modal.onclick = null; resolve(val); };
    ok.onclick = () => done(true);
    cancel.onclick = () => done(false);
    modal.onclick = (e) => { if (e.target === modal) done(false); };
  });
}

// ---------- Složka ----------
document.getElementById("pickFolderBtn").addEventListener("click", async () => {
  const r = await api("/api/pick-folder", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  if (r.ok) { toast("Složka nastavena.", "ok"); refresh(); return; }
  // fallback (např. na macOS bez systémového dialogu): zeptat se na cestu textem
  const cur = document.getElementById("downloadDir").textContent || "";
  const p = prompt("Zadej cestu ke složce pro stahování:", cur);
  if (!p) return;
  const s = await api("/api/settings", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ download_dir: p }),
  });
  if (s.ok) { toast("Složka nastavena.", "ok"); refresh(); }
  else toast(s.error || "Složku se nepodařilo nastavit.", "err");
});
document.getElementById("openFolderBtn").addEventListener("click", () => {
  api("/api/open-folder", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
});

// ---------- Nastavení ----------
const settingsModal = document.getElementById("settingsModal");
document.getElementById("settingsBtn").addEventListener("click", async () => {
  const s = await api("/api/settings");
  document.getElementById("setMaxDown").value = s.max_download_kbps ?? 0;
  document.getElementById("setMaxUp").value = s.max_upload_kbps ?? 0;
  document.getElementById("setConcurrent").value = s.max_concurrent ?? 3;
  document.getElementById("setAutoSubs").checked = s.auto_subtitles !== false;
  document.getElementById("setSlowSkip").checked = s.slow_skip !== false;
  document.getElementById("setSlowKbps").value = s.slow_skip_kbps ?? 30;
  document.getElementById("setSequential").checked = !!s.sequential;
  document.getElementById("setKeepSeeding").checked = !!s.keep_seeding;
  document.getElementById("setAutoOpen").checked = s.auto_open_browser !== false;
  settingsModal.hidden = false;
});
document.getElementById("saveSettingsBtn").addEventListener("click", async () => {
  const body = {
    max_download_kbps: Number(document.getElementById("setMaxDown").value) || 0,
    max_upload_kbps: Number(document.getElementById("setMaxUp").value) || 0,
    max_concurrent: Number(document.getElementById("setConcurrent").value) || 3,
    auto_subtitles: document.getElementById("setAutoSubs").checked,
    slow_skip: document.getElementById("setSlowSkip").checked,
    slow_skip_kbps: Number(document.getElementById("setSlowKbps").value) || 30,
    sequential: document.getElementById("setSequential").checked,
    keep_seeding: document.getElementById("setKeepSeeding").checked,
    auto_open_browser: document.getElementById("setAutoOpen").checked,
  };
  const r = await api("/api/settings", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (r.ok) { toast("Nastavení uloženo.", "ok"); settingsModal.hidden = true; refresh(); }
  else toast(r.error || "Uložení selhalo.", "err");
});

// ---------- Log ----------
const logsModal = document.getElementById("logsModal");
async function loadLog() {
  const r = await api("/api/logs");
  document.getElementById("logContent").textContent = r.log || "Log je prázdný.";
}
document.getElementById("logsBtn").addEventListener("click", () => { logsModal.hidden = false; loadLog(); });
document.getElementById("refreshLogBtn").addEventListener("click", loadLog);

document.querySelectorAll(".modal-close").forEach(b =>
  b.addEventListener("click", () => b.closest(".modal").hidden = true));
document.querySelectorAll(".modal").forEach(m =>
  m.addEventListener("click", e => { if (e.target === m) m.hidden = true; }));

// ---------- Start ----------
fillIcons();
let savedTheme = "dark";
try { savedTheme = localStorage.getItem("tm-theme") || "dark"; } catch (e) {}
applyTheme(savedTheme);
startRefresh();
