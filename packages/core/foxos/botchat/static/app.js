/* 狐狸OS 智能体聊天窗口（无构建步骤的纯 JS）。界面与交互参考 OpenBot（MIT，© 2026 CopilotKit）：
   左侧智能体列表；对话里流式文字、工具卡片（差异、终端输出）、委托卡片、审批按钮；每个智能体的设置分页与 OpenBot 对应。 */
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const S = {
  lang: localStorage.getItem("foxos.lang") || "",
  dict: {}, bots: [], current: null, view: "chat", messages: {}, live: {}, running: {}, approvals: [], activity: [], control: {}, prefs: {},
  machines: ["local"], skillsByBot: {}, agents: null, connectors: null, jobs: {}, attach: [], paused: {}, terminals: {}, desktopOwner: null,
};
const ICONS = ["sparkles", "robot", "code", "terminal-2", "search", "world", "pencil", "chart-bar", "bug", "book", "database", "brush", "mail",
  "calendar", "file-text", "shield-check", "rocket", "brain", "bolt", "cpu", "cloud", "palette", "flask", "briefcase", "music", "camera", "heart", "leaf"];
const COLORS = ["#E8743B", "#3B82F6", "#10B981", "#8B5CF6", "#EF4444", "#F59E0B", "#0EA5E9", "#EC4899", "#64748B", "#14B8A6"];
const KIND_ICON = { read: "file-search", edit: "pencil", delete: "trash", move: "arrows-move", search: "search", execute: "terminal-2", think: "bulb",
  fetch: "world-download", switch_mode: "switch-horizontal", other: "tool" };
const ACP_KINDS = ["read", "edit", "delete", "move", "search", "execute", "fetch", "think", "other"];

// ------------------------------------------------------------------ 基础
function t(key, ...args) {
  let s = S.dict[key];
  if (s == null) s = key;
  return args.length ? s.replace(/\{(\d+)\}/g, (m, i) => (args[+i] ?? "")) : s;
}
function esc(s) { return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function h(html) { const d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstElementChild; }
async function api(method, path, body, raw) {
  const opt = { method, headers: { "X-FoxOS": "1", "X-FoxOS-Lang": S.lang || "" } };
  if (raw) { opt.body = raw.body; opt.headers["X-Filename"] = encodeURIComponent(raw.name); opt.headers["Content-Type"] = "application/octet-stream"; }
  else if (body !== undefined) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
  const r = await fetch("/api/" + path, opt);
  let j; try { j = await r.json(); } catch { j = { ok: false, error: { code: "ERROR", message: r.statusText } }; }
  if (!j.ok) { const e = new Error(j.error?.message || "error"); e.code = j.error?.code; e.hint = j.error?.hint; throw e; }
  return j.result;
}
function toast(msg, bad) {
  const el = h(`<div class="toast ${bad ? "bad" : ""}">${esc(msg)}</div>`);
  $("#toasts").append(el); setTimeout(() => el.remove(), bad ? 7000 : 3500);
}
async function guard(fn) { try { return await fn(); } catch (e) { toast(e.message + (e.hint ? " — " + e.hint : ""), true); throw e; } }
function botById(id) { return S.bots.find(b => b.id === id); }
function avatar(b, cls = "", dot = "") {
  if (!b) return `<span class="avatar ${cls}"><i class="ti ti-user"></i></span>`;
  const a = b.avatar || {};
  const inner = a.image ? `<img src="/api/file?path=${encodeURIComponent(a.image)}" alt="">` : `<i class="ti ti-${esc(a.icon || "robot")}"></i>`;
  return `<span class="avatar ${cls}" style="background:${esc(a.color || "#888")}">${inner}${dot}</span>`;
}
function agentIcon(id) { return id && id !== "foxos-local" ? `<img src="/api/agents/${encodeURIComponent(id)}/icon" alt="" data-fallback="terminal-2">` : `<i class="ti ti-sparkles"></i>`; }
function backendLabel(b) {
  const be = b.backend || {};
  if (be.kind === "model") return `<span class="chip"><i class="ti ti-cpu"></i>${esc(be.model || "")}</span>`;
  const ag = (S.agents?.installed || []).find(a => a.id === be.agent);
  return `<span class="chip">${agentIcon(be.agent)}${esc(ag?.name || (be.agent === "foxos-local" ? t("agents.local") : be.agent))}</span>`;
}
function fmtTime(ts) { try { return new Date(ts).toLocaleString(S.lang, { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" }); } catch { return ts; } }
function applyI18n(root = document) {
  $$("[data-i18n]", root).forEach(e => e.textContent = t(e.dataset.i18n));
  $$("[data-i18n-title]", root).forEach(e => e.title = t(e.dataset.i18nTitle));
  $$("[data-i18n-placeholder]", root).forEach(e => e.placeholder = t(e.dataset.i18nPlaceholder));
  document.documentElement.lang = S.lang;
  document.title = t("app.title") + " · " + t("app.subtitle");
}
async function loadLang(lang) {
  S.lang = lang; localStorage.setItem("foxos.lang", lang);
  S.dict = await (await fetch(`locales/${lang}.json`)).json();
  applyI18n(); $("#lang").value = lang;
}
function md(text) {
  // 极简 Markdown：代码块、行内代码、粗体、链接（全部先转义）
  let s = esc(text || "");
  s = s.replace(/```[\w-]*\n([\s\S]*?)```/g, (m, c) => `<pre>${c}</pre>`);
  s = s.replace(/`([^`\n]+)`/g, "<code>$1</code>").replace(/\*\*([^*\n]+)\*\*/g, "<b>$1</b>");
  s = s.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
  return s;
}

// ------------------------------------------------------------------ 状态与事件
async function refreshState() {
  const st = await api("GET", "state");
  S.bots = st.bots; S.approvals = st.approvals; S.control = st.control || {}; S.prefs = st.prefs || {}; S.machines = st.machines || ["local"];
  S.activity = st.activity || []; S.paused = st.paused || {}; S.desktopOwner = st.desktop_owner;
  S.running = Object.fromEntries(Object.entries(st.running || {}).map(([k, v]) => [k, v.turn || true]));
  if (!S.current || !botById(S.current)) S.current = (S.bots.find(b => b.main) || S.bots[0])?.id;
  if (S.prefs.theme && S.prefs.theme !== "auto") document.documentElement.dataset.theme = S.prefs.theme;
  else document.documentElement.dataset.theme = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  renderSidebar(); renderActing();
}
function connectEvents() {
  const es = new EventSource("/api/events");
  es.onopen = () => $("#conn-state").classList.remove("down");
  es.onerror = () => $("#conn-state").classList.add("down");
  es.onmessage = m => { try { onEvent(JSON.parse(m.data)); } catch (e) { console.error(e); } };
}
function liveOf(bot, turn) {
  let L = S.live[bot];
  if (!L || L.turn !== turn) L = S.live[bot] = { turn, text: "", cards: {}, order: [], plan: [], skills: [], thoughts: "", user: null };
  return L;
}
function onEvent(e) {
  if (e.type === "state") {
    S.running = Object.fromEntries(Object.entries(e.running || {}).map(([k, v]) => [k, v || true]));
    S.activity = e.activity || []; S.desktopOwner = e.desktop_owner; S.control = e.control || S.control;
    for (const j of e.jobs || []) S.jobs[j.id] = j;
    const n = e.approvals || 0; const b = $("#badge-approvals"); b.textContent = n; b.classList.toggle("hidden", !n);
    renderActing(); renderTakeover(); updateBotDots(); renderJobs();
    return;
  }
  const bot = e.bot; if (!bot) return;
  if (e.type === "error") { if (bot === S.current) toast(e.error?.message || "error", true); return; }
  const L = liveOf(bot, e.turn);
  switch (e.type) {
    case "turn_start": L.user = e.message; S.running[bot] = e.turn; break;
    case "text": L.text += e.text; break;
    case "thought": L.thoughts += e.text; break;
    case "card": if (!L.cards[e.card.id]) L.order.push(e.card.id); L.cards[e.card.id] = e.card; break;
    case "plan": L.plan = e.entries || []; break;
    case "skill": if (!L.skills.includes(e.name)) L.skills.push(e.name); break;
    case "terminal": S.terminals[e.terminalId] = { command: e.command, cwd: e.cwd, output: "", machine: e.machine }; break;
    case "terminal_output": (S.terminals[e.terminalId] ||= { command: "", output: "" }).output = e.output; break;
    case "approval": refreshApprovals(); break;
    case "turn_end":
      (S.messages[bot] ||= []);
      if (L.user && !S.messages[bot].some(m => m.id === L.user.id)) S.messages[bot].push(L.user);
      S.messages[bot].push(e.message); delete S.live[bot]; delete S.running[bot];
      refreshApprovals();
      break;
  }
  if (bot === S.current && S.view === "chat") renderMessagesSoon();
  // 委托卡片里显示被委托智能体的实时进展
  if (S.view === "chat" && bot !== S.current) renderMessagesSoon();
  updateBotDots();
}
async function refreshApprovals() {
  try { S.approvals = (await api("GET", "approvals")).approvals; } catch { return; }
  const b = $("#badge-approvals"); b.textContent = S.approvals.length; b.classList.toggle("hidden", !S.approvals.length);
  if (S.view === "approvals") renderApprovals();
}

// ------------------------------------------------------------------ 侧栏
function renderSidebar() {
  const q = ($("#bot-search").value || "").toLowerCase();
  const list = S.bots.filter(b => !b.hidden || b.id === S.current).filter(b => !q || (b.name + " " + (b.title || "") + " " + b.id).toLowerCase().includes(q));
  list.sort((a, b) => (b.main - a.main) || (b.pinned - a.pinned) || a.name.localeCompare(b.name));
  const el = $("#bot-list"); el.innerHTML = "";
  for (const b of list) {
    const it = h(`<div class="bot-item ${b.id === S.current && S.view === "chat" ? "active" : ""}" data-id="${esc(b.id)}">
      ${avatar(b, "", `<span class="dot" data-dot="${esc(b.id)}"></span>`)}
      <div class="meta"><div class="name">${esc(b.name)}${b.main ? ` <span class="chip accent">${esc(t("bots.main"))}</span>` : ""}</div>
      <div class="sub" data-sub="${esc(b.id)}">${esc(b.title || b.role || "")}</div></div>
      ${b.pinned && !b.main ? '<i class="ti ti-pin pin"></i>' : ""}</div>`);
    it.onclick = () => openBot(b.id);
    el.append(it);
  }
  updateBotDots();
}
function updateBotDots() {
  for (const b of S.bots) {
    const d = $(`[data-dot="${CSS.escape(b.id)}"]`); if (!d) continue;
    d.className = "dot " + (!b.active ? "off" : S.paused[b.id] || S.control?.paused && !(S.control.state?.targets?.length) ? "paused" : S.running[b.id] ? "busy" : "");
    const sub = $(`[data-sub="${CSS.escape(b.id)}"]`);
    if (sub) sub.innerHTML = S.running[b.id] ? `<span class="state">${esc(t("bots.working"))}</span>` : esc(b.title || b.role || "");
  }
}
function renderActing() {
  const el = $("#acting");
  const items = [];
  for (const [bid] of Object.entries(S.running)) { const b = botById(bid); if (b) items.push(`<span class="chip">${avatar(b, "sm")} ${esc(t("acting.running", b.name))}</span>`); }
  for (const a of S.activity) {
    if (a.agent === "human" || !a.agent.startsWith("bot:")) continue;
    const bid = a.agent.slice(4).split(/[/@]/)[0]; const b = botById(bid);
    items.push(`<span class="chip"><i class="ti ti-player-play"></i>${esc(t("acting.did", b?.name || bid, a.command, a.machine || "local"))}${a.desktop ? ` <i class="ti ti-device-desktop"></i>` : ""}</span>`);
  }
  if (S.desktopOwner) items.push(`<span class="chip warn"><i class="ti ti-device-desktop"></i>${esc(t("acting.desktop", S.desktopOwner.agent))}</span>`);
  if (S.control?.paused) items.unshift(`<span class="chip bad"><i class="ti ti-hand-stop"></i>${esc(S.control.state?.targets?.length ? t("control.paused_some", S.control.state.targets.join(", ")) : t("control.paused_all"))}</span>`);
  el.innerHTML = `<b>${esc(t("acting.now"))}</b>` + items.join("");
  el.classList.toggle("hidden", !items.length);
}
function renderTakeover() {
  const b = $("#btn-takeover"); const on = !!S.control?.paused;
  b.classList.toggle("on", on);
  b.innerHTML = on ? `<i class="ti ti-player-play"></i><span>${esc(t("control.resume"))}</span>` : `<i class="ti ti-hand-stop"></i><span>${esc(t("control.take_over"))}</span>`;
}

// ------------------------------------------------------------------ 对话
async function openBot(id) {
  S.current = id; S.view = "chat"; S.attach = [];
  $$(".nav-item").forEach(n => n.classList.remove("active"));
  $("#app").classList.remove("side-open");
  renderSidebar();
  renderChat();
  try { S.messages[id] = (await api("GET", `bots/${encodeURIComponent(id)}/messages?limit=200`)).messages; } catch (e) { S.messages[id] = []; }
  renderMessages(true);
  loadSkillsFor(id);
}
async function loadSkillsFor(id) {
  try { S.skillsByBot[id] = (await api("GET", `skills?bot=${encodeURIComponent(id)}`)).skills; } catch { S.skillsByBot[id] = []; }
}
function renderChat() {
  const b = botById(S.current); const v = $("#view");
  if (!b) { v.innerHTML = `<div class="empty">${esc(t("bots.none"))}</div>`; return; }
  const mach = b.machines || {}; const allowed = mach.allowed || ["local"];
  const paused = S.paused[b.id];
  v.innerHTML = `
  <div class="chat-head">
    <button class="icon-btn only-narrow" id="btn-side"><i class="ti ti-menu-2"></i></button>
    ${avatar(b, "lg")}
    <div class="title"><b>${esc(b.name)}</b>
      <div class="sub">${esc(b.title || "")}
        ${backendLabel(b)}
        <span class="chip" title="${esc(t("chat.machine_tip"))}"><i class="ti ti-device-desktop"></i>
          <select id="sel-machine">${allowed.map(m => `<option value="${esc(m)}" ${m === (mach.default || "local") ? "selected" : ""}>${esc(m === "local" ? t("machines.local") : m)}</option>`).join("")}</select></span>
        <span class="chip"><i class="ti ti-folder"></i>${esc(b.scope || ".")}</span>
        ${b.isolated ? `<span class="chip"><i class="ti ti-lock"></i>${esc(t("settings.isolated"))}</span>` : ""}
      </div></div>
    <button class="btn sm ghost" id="btn-pause-bot" title="${esc(t("chat.pause_bot_tip"))}"><i class="ti ti-${paused ? "player-play" : "player-pause"}"></i>${esc(paused ? t("control.resume") : t("chat.pause_bot"))}</button>
    <button class="icon-btn" id="btn-reset" title="${esc(t("chat.new_conversation"))}"><i class="ti ti-message-plus"></i></button>
    <button class="icon-btn" id="btn-settings" title="${esc(t("chat.settings"))}"><i class="ti ti-settings"></i></button>
  </div>
  <div class="messages" id="messages"><div class="msgs-inner" id="msgs"></div></div>
  <div class="composer-wrap"><div class="composer" id="composer">
    <div class="attach-list" id="attach-list"></div>
    <textarea id="input" rows="2" placeholder="${esc(t("chat.placeholder", b.name))}"></textarea>
    <div class="row">
      <button class="icon-btn" id="btn-attach" title="${esc(t("chat.attach"))}"><i class="ti ti-paperclip"></i></button>
      <button class="icon-btn" id="btn-mention" title="${esc(t("chat.mention"))}"><i class="ti ti-at"></i></button>
      <button class="icon-btn" id="btn-skill" title="${esc(t("chat.skill"))}"><i class="ti ti-slash"></i></button>
      <span class="grow"></span>
      <span class="chip" id="hint-keys">${esc(t("chat.enter_hint"))}</span>
      <button class="btn sm danger hidden" id="btn-stop"><i class="ti ti-player-stop"></i>${esc(t("chat.stop"))}</button>
      <button class="btn primary sm" id="btn-send"><i class="ti ti-send"></i>${esc(t("chat.send"))}</button>
    </div>
    <input type="file" id="file" multiple class="hidden">
  </div></div>`;
  $("#btn-side").onclick = () => $("#app").classList.toggle("side-open");
  $("#btn-settings").onclick = () => openSettings(b.id);
  $("#btn-reset").onclick = () => confirmModal(t("chat.new_conversation"), t("chat.reset_confirm", b.name), async () => {
    await api("POST", `bots/${b.id}/reset`, { keep_memory: true }); S.messages[b.id] = []; renderMessages(true); });
  $("#btn-pause-bot").onclick = () => guard(async () => { await api("POST", `bots/${b.id}/${paused ? "resume" : "pause"}`, {}); await refreshState(); renderChat(); renderMessages(true); });
  $("#sel-machine").onchange = e => guard(async () => { await api("PATCH", `bots/${b.id}`, { default_machine: e.target.value }); await refreshState(); toast(t("chat.machine_set", e.target.value)); });
  const inp = $("#input");
  inp.onkeydown = ev => {
    if (popupKey(ev)) return;
    if (ev.key === "Enter" && !ev.shiftKey && !ev.isComposing) { ev.preventDefault(); send(); }
  };
  inp.oninput = () => { inp.style.height = "auto"; inp.style.height = Math.min(220, inp.scrollHeight) + "px"; updatePopup(); };
  $("#btn-send").onclick = send;
  $("#btn-stop").onclick = () => guard(() => api("POST", `bots/${b.id}/cancel`, {}));
  $("#btn-attach").onclick = () => $("#file").click();
  $("#file").onchange = e => uploadFiles([...e.target.files]);
  $("#btn-mention").onclick = () => { insertAtCursor("@"); updatePopup(); };
  $("#btn-skill").onclick = () => { if (!inp.value) inp.value = "/"; inp.focus(); updatePopup(); };
  $("#composer").ondragover = e => e.preventDefault();
  $("#composer").ondrop = e => { e.preventDefault(); uploadFiles([...e.dataTransfer.files]); };
  inp.onpaste = e => { const f = [...(e.clipboardData?.files || [])]; if (f.length) { e.preventDefault(); uploadFiles(f); } };
  inp.focus();
}
function insertAtCursor(txt) {
  const inp = $("#input"); const p = inp.selectionStart ?? inp.value.length;
  inp.value = inp.value.slice(0, p) + txt + inp.value.slice(p); inp.focus(); inp.selectionStart = inp.selectionEnd = p + txt.length;
}
async function uploadFiles(files) {
  for (const f of files) {
    try {
      const r = await api("POST", "upload", undefined, { name: f.name, body: f });
      S.attach.push(r.path); renderAttach();
    } catch (e) { toast(e.message, true); }
  }
}
function renderAttach() {
  const el = $("#attach-list"); if (!el) return;
  el.innerHTML = S.attach.map((p, i) => `<span class="chip"><i class="ti ti-file"></i>${esc(p.split("/").pop())}<i class="ti ti-x" data-rm="${i}" style="cursor:pointer"></i></span>`).join("");
  $$("[data-rm]", el).forEach(x => x.onclick = () => { S.attach.splice(+x.dataset.rm, 1); renderAttach(); });
}
async function send() {
  const b = botById(S.current); const inp = $("#input");
  const text = inp.value.trim();
  if (!text && !S.attach.length) return;
  closePopup();
  try {
    await api("POST", `bots/${b.id}/send`, { text, attachments: S.attach });
    inp.value = ""; inp.style.height = ""; S.attach = []; renderAttach();
    S.running[b.id] = true; renderMessagesSoon();
  } catch (e) { toast(e.message, true); }
}

// @ 与 / 弹出菜单
let POP = null;
function closePopup() { $("#popup")?.remove(); POP = null; }
function updatePopup() {
  const inp = $("#input"); if (!inp) return;
  const before = inp.value.slice(0, inp.selectionStart);
  const mAt = before.match(/(?:^|\s)@([^\s@]*)$/);
  const mSl = before.match(/^\/([a-z0-9-]*)$/);
  let items = [];
  if (mAt) {
    const q = mAt[1].toLowerCase();
    items = S.bots.filter(x => x.id !== S.current && x.active !== false && (x.name.toLowerCase().includes(q) || x.id.includes(q)))
      .map(x => ({ html: `${avatar(x, "sm")}<div><b>${esc(x.name)}</b><small>${esc(x.title || x.role || "")}</small></div>`, insert: "@" + (/\s/.test(x.name) ? x.id : x.name) + " ", cut: mAt[1].length + 1 }));
  } else if (mSl) {
    const q = mSl[1];
    items = (S.skillsByBot[S.current] || []).filter(s => s.name.includes(q)).slice(0, 40)
      .map(s => ({ html: `<i class="ti ti-${s.kind === "principle" ? "compass" : s.kind === "subagent" ? "users" : "book"}"></i><div><b>/${esc(s.name)}</b><small>${esc(s.description || "")}</small></div>`, insert: "/" + s.name + " ", cut: q.length + 1 }));
  }
  if (!items.length) return closePopup();
  POP = { items, sel: 0 };
  let el = $("#popup");
  if (!el) { el = h(`<div class="popup" id="popup"></div>`); $("#composer").append(el); }
  el.innerHTML = items.map((it, i) => `<div class="opt ${i === 0 ? "sel" : ""}" data-i="${i}">${it.html}</div>`).join("");
  $$(".opt", el).forEach(o => o.onmousedown = ev => { ev.preventDefault(); pickPopup(+o.dataset.i); });
}
function pickPopup(i) {
  const it = POP.items[i]; const inp = $("#input"); const p = inp.selectionStart;
  inp.value = inp.value.slice(0, p - it.cut) + it.insert + inp.value.slice(p);
  inp.selectionStart = inp.selectionEnd = p - it.cut + it.insert.length; closePopup(); inp.focus();
}
function popupKey(ev) {
  if (!POP) return false;
  if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
    POP.sel = (POP.sel + (ev.key === "ArrowDown" ? 1 : -1) + POP.items.length) % POP.items.length;
    $$("#popup .opt").forEach((o, i) => o.classList.toggle("sel", i === POP.sel)); ev.preventDefault(); return true;
  }
  if (ev.key === "Enter" || ev.key === "Tab") { ev.preventDefault(); pickPopup(POP.sel); return true; }
  if (ev.key === "Escape") { closePopup(); return true; }
  return false;
}

// 消息与卡片
let renderTimer = null;
function renderMessagesSoon() { if (!renderTimer) renderTimer = requestAnimationFrame(() => { renderTimer = null; renderMessages(); }); }
function renderMessages(scroll) {
  const box = $("#msgs"); if (!box) return;
  const wrap = $("#messages"); const atBottom = wrap.scrollHeight - wrap.scrollTop - wrap.clientHeight < 80;
  const b = botById(S.current); const msgs = S.messages[S.current] || []; const L = S.live[S.current];
  const parts = [];
  if (!msgs.length && !L) {
    const others = S.bots.filter(x => x.id !== b.id && x.active !== false).slice(0, 3);
    parts.push(`<div class="empty">${avatar(b, "lg")}<h2>${esc(b.name)}</h2><p>${esc(b.role || t("chat.empty"))}</p>
      <div class="suggest">${[t("chat.try_hello"), ...others.map(o => "@" + o.name + " " + t("chat.try_delegate")), "/architect " + t("chat.try_skill")]
        .map(s => `<button class="btn sm" data-suggest="${esc(s)}">${esc(s)}</button>`).join("")}</div></div>`);
  }
  for (const m of msgs) parts.push(renderMsg(m, b));
  if (L) {
    if (L.user && !msgs.some(m => m.id === L.user.id)) parts.push(renderMsg(L.user, b));
    parts.push(renderMsg({ role: "bot", bot: b.id, text: L.text, cards: L.order.map(id => L.cards[id]), plan: L.plan, skills_used: L.skills, live: true, thoughts: L.thoughts, machine: (b.machines || {}).default }, b));
  } else if (S.running[S.current]) {
    parts.push(renderMsg({ role: "bot", bot: b.id, text: "", cards: [], live: true }, b));
  }
  box.innerHTML = parts.join("");
  $$("[data-suggest]", box).forEach(x => x.onclick = () => { $("#input").value = x.dataset.suggest; $("#input").focus(); });
  $$(".card-head", box).forEach(hd => hd.onclick = ev => { if (ev.target.closest("button")) return; hd.parentElement.classList.toggle("collapsed"); });
  $$("[data-approve]", box).forEach(x => x.onclick = () => answerApproval(x.dataset.approve, x.dataset.option || null));
  $$("[data-open-bot]", box).forEach(x => x.onclick = () => openBot(x.dataset.openBot));
  const running = !!S.running[S.current];
  $("#btn-stop")?.classList.toggle("hidden", !running);
  if (scroll || atBottom) wrap.scrollTop = wrap.scrollHeight;
}
function renderMsg(m, b) {
  if (m.role === "user") {
    const from = m.from && m.from !== "human" ? m.from : "";
    const fromBot = from.startsWith("bot:") ? botById(from.slice(4).split(/[/@]/)[0]) : null;
    const who = fromBot ? `${avatar(fromBot, "sm")} ${esc(t("chat.from_bot", fromBot.name))}` : from ? esc(from) : "";
    return `<div class="msg user">${fromBot ? avatar(fromBot) : ""}<div class="body">${who ? `<div class="who">${who}</div>` : ""}
      ${m.text ? `<div class="bubble">${md(m.text)}</div>` : ""}
      ${(m.attachments || []).length ? `<div class="attach-list">${m.attachments.map(a => `<span class="chip"><i class="ti ti-file"></i>${esc(a.split("/").pop())}</span>`).join("")}</div>` : ""}
      ${m.envelope ? `<div class="chip">${esc(t("chat.handoff", m.envelope.from || ""))}</div>` : ""}</div></div>`;
  }
  const bot = botById(m.bot) || b;
  const cards = (m.cards || []).map(c => renderCard(c, m)).join("");
  const skills = (m.skills_used || []).length ? `<div class="skills-used"><i class="ti ti-books"></i>${esc(t("chat.skills_used"))}${m.skills_used.map(s => `<span class="chip accent">${esc(s)}</span>`).join("")}</div>` : "";
  const plan = (m.plan || []).length ? `<div class="card"><div class="card-head"><span class="ico"><i class="ti ti-list-check"></i></span><span class="t">${esc(t("chat.plan"))}</span></div>
    <div class="card-body">${m.plan.map(p => `<div><i class="ti ti-${p.status === "completed" ? "circle-check" : p.status === "in_progress" ? "loader" : "circle"}"></i> ${esc(p.content)}</div>`).join("")}</div></div>` : "";
  const meta = [m.ts ? fmtTime(m.ts) : "", m.duration_ms ? (m.duration_ms / 1000).toFixed(1) + "s" : "", m.machine && m.machine !== "local" ? "@" + m.machine : "",
    m.origin && !["person", "mention"].includes(m.origin) ? t("origin." + m.origin) : ""].filter(Boolean).join(" · ");
  const text = m.text || "";
  return `<div class="msg bot">${avatar(bot)}<div class="body"><div class="who"><b>${esc(bot.name)}</b> ${esc(meta)}</div>
    ${m.thoughts ? `<div class="thought">${esc(m.thoughts.slice(-600))}</div>` : ""}
    ${plan}${cards}
    ${text || m.live ? `<div class="bubble ${m.live ? "caret" : ""}">${md(text)}</div>` : ""}
    ${skills}
    ${m.error ? `<div class="chip bad"><i class="ti ti-alert-triangle"></i>${esc(m.error.message)}</div>` : ""}</div></div>`;
}
function renderCard(c, m) {
  if (c.type === "delegation") return renderDelegation(c);
  const st = c.status || "pending";
  const mach = c.machine && c.machine !== "local" ? `<span class="chip"><i class="ti ti-device-desktop"></i>${esc(c.machine)}</span>` : `<span class="chip"><i class="ti ti-device-desktop"></i>${esc(t("machines.local"))}</span>`;
  const body = [];
  for (const x of c.content || []) {
    if (x.type === "diff") body.push(renderDiff(x));
    else if (x.type === "terminal") { const T = S.terminals[x.terminalId]; body.push(`<div class="term">${T ? `<span class="cmd">$ ${esc(T.command)}</span>\n${esc(T.output)}` : esc(t("chat.terminal_gone"))}</div>`); }
    else if (x.type === "content" && x.content?.type === "text" && x.content.text) body.push(`<div class="${c.kind === "execute" ? "term" : "bubble"}">${esc(x.content.text.slice(0, 6000))}</div>`);
  }
  if (!body.length && c.rawInput && Object.keys(c.rawInput).length) body.push(`<div class="mono">${esc(JSON.stringify(c.rawInput).slice(0, 800))}</div>`);
  for (const l of c.locations || []) body.push(`<div class="chip"><i class="ti ti-file"></i>${esc(l.path)}${l.line ? ":" + l.line : ""}</div>`);
  const ap = c.approval || {};
  let apHtml = "";
  if (ap.decision === "pending" && ap.request) {
    apHtml = `<div class="approval"><div class="q"><i class="ti ti-shield-question"></i> ${esc(t("approvals.question"))}</div>
      ${(ap.options || []).map(o => `<button class="btn sm ${String(o.kind).startsWith("allow") ? "primary" : ""}" data-approve="${esc(ap.request)}" data-option="${esc(o.optionId)}">${esc(optName(o))}</button>`).join("")}</div>`;
  } else if (ap.decision) {
    apHtml = `<div class="approval"><span class="chip ${ap.decision === "allow" ? "ok" : "bad"}"><i class="ti ti-${ap.decision === "allow" ? "check" : "x"}"></i>${esc(t("approvals." + ap.decision))}</span><small>${esc(ap.by ? t("approvals.by", ap.by === "rule" ? t("approvals.by_rule") : ap.by === "human" ? t("origin.person") : ap.by) : "")}</small></div>`;
  }
  const collapsed = st === "completed" && !(c.content || []).some(x => x.type === "diff") && ap.decision !== "pending";
  return `<div class="card ${collapsed ? "collapsed" : ""}"><div class="card-head"><span class="ico"><i class="ti ti-${KIND_ICON[c.kind] || "tool"}"></i></span>
    <span class="t">${esc(c.title || c.kind || t("chat.tool"))}</span>${mach}<span class="st ${esc(st)}">${statusIcon(st)}${esc(t("status." + st))}</span></div>
    ${body.length ? `<div class="card-body">${body.join("")}</div>` : ""}${apHtml}</div>`;
}
function optName(o) {
  const k = { allow_once: "approvals.allow_once", allow_always: "approvals.allow_always", reject_once: "approvals.deny", reject_always: "approvals.deny_always" }[o.kind];
  return k ? t(k) : (o.name || o.optionId);
}
function statusIcon(st) { return `<i class="ti ti-${{ completed: "circle-check", failed: "circle-x", in_progress: "loader-2", pending: "clock" }[st] || "circle"}"></i>`; }
function renderDiff(x) {
  const oldL = (x.oldText || "").split("\n"); const newL = (x.newText || "").split("\n");
  const rows = [`<div class="hdr">${esc(x.path)}</div>`];
  // 简单逐行差异（LCS），文件大时退化为整体替换
  if (oldL.length * newL.length > 400000) { oldL.forEach(l => rows.push(`<div class="del">- ${esc(l)}</div>`)); newL.forEach(l => rows.push(`<div class="add">+ ${esc(l)}</div>`)); }
  else {
    const n = oldL.length, mm = newL.length; const dp = Array.from({ length: n + 1 }, () => new Uint32Array(mm + 1));
    for (let i = n - 1; i >= 0; i--) for (let j = mm - 1; j >= 0; j--) dp[i][j] = oldL[i] === newL[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
    let i = 0, j = 0; const out = [];
    while (i < n || j < mm) {
      if (i < n && j < mm && oldL[i] === newL[j]) { out.push([" ", oldL[i]]); i++; j++; }
      else if (j < mm && (i >= n || dp[i][j + 1] >= dp[i + 1][j])) { out.push(["+", newL[j]]); j++; }
      else { out.push(["-", oldL[i]]); i++; }
    }
    if (x.oldText == null) out.splice(0, out.length, ...newL.map(l => ["+", l]));
    // 只显示改动附近 3 行
    const keep = out.map((r, k) => r[0] !== " " ? k : -1).filter(k => k >= 0);
    let last = -10;
    out.forEach((r, k) => {
      const near = keep.some(q => Math.abs(q - k) <= 3);
      if (!near) { if (last === k - 1) rows.push(`<div class="hdr">…</div>`); return; }
      last = k; rows.push(`<div class="${r[0] === "+" ? "add" : r[0] === "-" ? "del" : ""}">${r[0]} ${esc(r[1])}</div>`);
    });
  }
  return `<div class="diff">${rows.join("")}</div>`;
}
function renderDelegation(c) {
  const to = botById(c.to); const st = c.status || "in_progress";
  const live = to && S.live[to.id];
  const progress = st === "in_progress" && live ? `<div class="skills-used">${live.order.slice(-3).map(id => `<span class="chip"><i class="ti ti-${KIND_ICON[live.cards[id].kind] || "tool"}"></i>${esc(live.cards[id].title || "")}</span>`).join("")}</div>
     ${live.text ? `<div class="bubble caret">${md(live.text.slice(-800))}</div>` : ""}` : st === "in_progress" ? `<div class="progress"><div></div></div>` : "";
  return `<div class="card deleg"><div class="card-head"><span class="ico"><i class="ti ti-arrow-forward-up"></i></span>
    <span class="t">${esc(t("chat.delegated_to", to?.name || c.to_name || c.to || "?"))}</span>
    ${to ? `<button class="btn sm ghost" data-open-bot="${esc(to.id)}">${avatar(to, "sm")}${esc(t("chat.open"))}</button>` : ""}
    <span class="st ${esc(st)}">${statusIcon(st)}${esc(c.refused ? t("chat.refused") : t("status." + st))}</span></div>
    <div class="card-body">${c.task ? `<div><b>${esc(t("chat.task"))}</b> ${esc(c.task)}</div>` : ""}${progress}
    ${c.answer ? `<div class="answer">${md(c.answer)}</div>` : ""}
    ${(c.skills_used || []).length ? `<div class="skills-used"><i class="ti ti-books"></i>${c.skills_used.map(s => `<span class="chip accent">${esc(s)}</span>`).join("")}</div>` : ""}</div></div>`;
}
async function answerApproval(req, option) {
  await guard(() => api("POST", `approvals/${encodeURIComponent(req)}`, option ? { option } : {}));
  refreshApprovals();
}

// ------------------------------------------------------------------ 设置（与 OpenBot 的 Bot 设置分页对应）
const TABS = [["setup", "settings"], ["skills", "books"], ["memory", "brain"], ["approvals", "shield-check"], ["routines", "repeat"],
  ["delegation", "arrow-forward-up"], ["machines", "devices-pc"], ["channels", "message-share"], ["manage", "adjustments"]];
async function openSettings(id, tab = "setup") {
  S.view = "settings"; renderSidebar();
  const [cfg, sk, ag, cn] = await Promise.all([api("GET", `bots/${id}/config`), api("GET", "skills"), loadAgents(), api("GET", "connectors")]);
  const b = cfg.config; const v = $("#view");
  const draft = JSON.parse(JSON.stringify(b)); draft.__rules = Object.fromEntries((b.approvals?.rules || []).map(r => [r.kind, r.decision]));
  v.innerHTML = `<div class="page"><div class="page-inner">
    <div class="chat-head" style="border:0;padding:0;background:transparent">
      <button class="icon-btn" id="back"><i class="ti ti-arrow-left"></i></button>${avatar(b, "lg")}
      <div class="title"><b>${esc(b.name)}</b><div class="sub">${esc(t("settings.title"))} · <span class="mono">bot:${esc(b.id)}</span></div></div></div>
    <div class="settings"><div class="tabs">${TABS.map(([k, ic]) => `<button class="tab ${k === tab ? "active" : ""}" data-tab="${k}"><i class="ti ti-${ic}"></i>${esc(t("settings.tab_" + k))}</button>`).join("")}</div>
    <div id="tab-body"></div></div></div></div>`;
  $("#back").onclick = () => openBot(id);
  const show = k => {
    $$(".tab", v).forEach(x => x.classList.toggle("active", x.dataset.tab === k));
    const body = $("#tab-body"); body.innerHTML = "";
    ({ setup: tabSetup, skills: tabSkills, memory: tabMemory, approvals: tabApprovals, routines: tabRoutines, delegation: tabDelegation,
       machines: tabMachines, channels: tabChannels, manage: tabManage })[k](body, draft, { sk: sk.skills, ag, cn });
    applyI18n(body);
  };
  $$(".tab", v).forEach(x => x.onclick = () => show(x.dataset.tab));
  show(tab);
}
function sw(id, checked, label, help) {
  return `<div class="switch-row"><div class="txt">${esc(label)}${help ? `<small>${esc(help)}</small>` : ""}</div>
    <label class="switch"><input type="checkbox" id="${id}" ${checked ? "checked" : ""}><span></span></label></div>`;
}
function saveBar(body, fn) {
  const bar = h(`<div class="save-bar"><button class="btn primary"><i class="ti ti-device-floppy"></i>${esc(t("common.save"))}</button></div>`);
  bar.firstElementChild.onclick = () => guard(async () => { await fn(); await refreshState(); toast(t("common.saved")); });
  body.append(bar);
}
function patchBot(id, p) { return api("PATCH", `bots/${encodeURIComponent(id)}`, p); }

function tabSetup(body, d, ctx) {
  const be = d.backend || {};
  const agents = [{ id: "foxos-local", name: t("agents.local") }, ...(ctx.ag.installed || []).filter(a => a.id !== "foxos-local")];
  body.innerHTML = `
  <div class="section"><h4><i class="ti ti-id"></i>${esc(t("settings.identity"))}</h4>
    <div class="two"><div class="field"><label>${esc(t("settings.name"))}</label><input id="f-name" value="${esc(d.name)}"></div>
    <div class="field"><label>${esc(t("settings.title_f"))}</label><input id="f-title" value="${esc(d.title || "")}"></div></div>
    <div class="field"><label>${esc(t("settings.role"))}</label><input id="f-role" value="${esc(d.role || "")}"><div class="help">${esc(t("settings.role_help"))}</div></div>
    <div class="field"><label>${esc(t("settings.instructions"))}</label><textarea id="f-instr">${esc(d.instructions || "")}</textarea><div class="help">${esc(t("settings.instructions_help"))}</div></div></div>
  <div class="section"><h4><i class="ti ti-photo"></i>${esc(t("settings.avatar"))}</h4>
    <div class="icon-pick" id="f-icons">${ICONS.map(i => `<button data-icon="${i}" class="${(d.avatar?.icon || "robot") === i && !d.avatar?.image ? "sel" : ""}"><i class="ti ti-${i}"></i></button>`).join("")}</div>
    <div class="color-pick" id="f-colors">${COLORS.map(c => `<button data-color="${c}" style="background:${c}" class="${(d.avatar?.color || "").toUpperCase() === c ? "sel" : ""}"></button>`).join("")}</div>
    <div class="two"><div class="field"><label>${esc(t("settings.image"))}</label><input id="f-image" value="${esc(d.avatar?.image || "")}" placeholder="attachments/…/avatar.png"></div>
    <div class="field"><label>&nbsp;</label><button class="btn" id="f-upload"><i class="ti ti-upload"></i>${esc(t("settings.upload_image"))}</button><input type="file" id="f-img-file" accept="image/*" class="hidden"></div></div></div>
  <div class="section"><h4><i class="ti ti-plug"></i>${esc(t("settings.connection"))}</h4>
    <div class="seg" id="f-kind"><button data-k="acp" class="${be.kind !== "model" ? "sel" : ""}">${esc(t("settings.backend_acp"))}</button><button data-k="model" class="${be.kind === "model" ? "sel" : ""}">${esc(t("settings.backend_model"))}</button></div>
    <div id="f-acp" class="${be.kind === "model" ? "hidden" : ""}"><div class="field"><label>${esc(t("settings.agent"))}</label>
      <select id="f-agent">${agents.map(a => `<option value="${esc(a.id)}" ${a.id === (be.agent || "foxos-local") ? "selected" : ""}>${esc(a.name)} (${esc(a.id)})</option>`).join("")}</select>
      <div class="help">${esc(t("settings.agent_help"))} <a href="#" id="go-agents">${esc(t("nav.agents"))}</a></div></div>
      <div class="field"><label>${esc(t("settings.model_pref"))}</label><input id="f-model-pref" value="${esc(d.model || "")}" placeholder="${esc(t("settings.optional"))}"></div></div>
    <div id="f-model" class="${be.kind === "model" ? "" : "hidden"}"><div class="field"><label>${esc(t("settings.endpoint"))}</label><input id="f-base" value="${esc(be.base_url || "")}" placeholder="https://api.example.com/v1"></div>
      <div class="two"><div class="field"><label>${esc(t("settings.model"))}</label><input id="f-model-name" value="${esc(be.model || "")}"></div>
      <div class="field"><label>${esc(t("settings.api_key"))}${d.has_api_key ? ` <span class="chip ok">${esc(t("settings.saved_key"))}</span>` : ""}</label><input type="password" id="f-key" autocomplete="off" placeholder="${esc(d.has_api_key ? "••••••••" : "")}"></div></div>
      <div class="help">${esc(t("settings.model_help"))}</div></div></div>
  <div class="section"><h4><i class="ti ti-eye"></i>${esc(t("settings.visibility"))}</h4>
    <div class="seg" id="f-vis"><button data-v="private" class="${d.visibility !== "public" ? "sel" : ""}">${esc(t("settings.private"))}</button><button data-v="public" class="${d.visibility === "public" ? "sel" : ""}">${esc(t("settings.public"))}</button></div>
    ${sw("f-isolated", d.isolated, t("settings.isolated"), t("settings.isolated_help"))}
    <div class="field"><label>${esc(t("settings.scope"))}</label><input id="f-scope" value="${esc(d.scope || ".")}"><div class="help">${esc(t("settings.scope_help"))}</div></div></div>`;
  let icon = d.avatar?.image ? null : (d.avatar?.icon || "robot"), color = d.avatar?.color || COLORS[0], kind = be.kind || "acp", vis = d.visibility || "private";
  $$("#f-icons button", body).forEach(x => x.onclick = () => { icon = x.dataset.icon; $("#f-image").value = ""; $$("#f-icons button").forEach(y => y.classList.toggle("sel", y === x)); });
  $$("#f-colors button", body).forEach(x => x.onclick = () => { color = x.dataset.color; $$("#f-colors button").forEach(y => y.classList.toggle("sel", y === x)); });
  $$("#f-kind button", body).forEach(x => x.onclick = () => { kind = x.dataset.k; $$("#f-kind button").forEach(y => y.classList.toggle("sel", y === x)); $("#f-acp").classList.toggle("hidden", kind === "model"); $("#f-model").classList.toggle("hidden", kind !== "model"); });
  $$("#f-vis button", body).forEach(x => x.onclick = () => { vis = x.dataset.v; $$("#f-vis button").forEach(y => y.classList.toggle("sel", y === x)); });
  $("#go-agents").onclick = e => { e.preventDefault(); showView("agents"); };
  $("#f-upload").onclick = () => $("#f-img-file").click();
  $("#f-img-file").onchange = async e => { const f = e.target.files[0]; if (!f) return; const r = await guard(() => api("POST", "upload", undefined, { name: f.name, body: f })); $("#f-image").value = r.path; };
  saveBar(body, async () => {
    const p = { name: $("#f-name").value.trim(), title: $("#f-title").value, role: $("#f-role").value, instructions: $("#f-instr").value,
      color, visibility: vis, isolated: $("#f-isolated").checked, scope: $("#f-scope").value.trim() || "." };
    const img = $("#f-image").value.trim(); if (img) p.image = img; else if (icon) { p.icon = icon; p.image = ""; }
    if (kind === "model") { p.base_url = $("#f-base").value.trim(); p.model = $("#f-model-name").value.trim(); const k = $("#f-key").value; if (k) p.api_key = k; }
    else { p.agent = $("#f-agent").value; p.model = $("#f-model-pref").value.trim(); }
    await patchBot(d.id, p);
  });
}
function tabSkills(body, d, ctx) {
  const mode = d.skills?.mode || "all"; const en = new Set(d.skills?.enabled || []); const off = new Set(d.skills?.disabled || []);
  const groups = { skill: [], principle: [], subagent: [] }; for (const s of ctx.sk) (groups[s.kind] ||= []).push(s);
  const inst = ctx.cn.installed || [];
  body.innerHTML = `
  <div class="section"><h4><i class="ti ti-books"></i>${esc(t("settings.skills"))}</h4><p class="lead">${esc(t("settings.skills_help"))}</p>
    <div class="seg" id="s-mode"><button data-m="all" class="${mode === "all" ? "sel" : ""}">${esc(t("settings.skills_all"))}</button><button data-m="selected" class="${mode === "selected" ? "sel" : ""}">${esc(t("settings.skills_selected"))}</button></div>
    <div class="search"><i class="ti ti-search"></i><input id="s-q" placeholder="${esc(t("common.search"))}"></div>
    <div class="check-list" id="s-list">${Object.entries(groups).filter(([, a]) => a.length).map(([k, arr]) => `<div class="chip" style="margin:6px 4px 2px">${esc(t("skills.kind_" + k))} · ${arr.length}</div>` +
      arr.map(s => `<label data-q="${esc((s.name + " " + s.description).toLowerCase())}"><input type="checkbox" data-skill="${esc(s.name)}" ${(mode === "all" ? !off.has(s.name) : en.has(s.name)) ? "checked" : ""}>
        <div><b>${esc(s.name)}</b>${s.manual_only ? ` <span class="chip">${esc(t("skills.manual"))}</span>` : ""} <span class="chip">${esc(s.source)}</span><small>${esc(s.description)}</small></div></label>`).join("")).join("")}</div></div>
  <div class="section"><h4><i class="ti ti-plug-connected"></i>${esc(t("settings.apps"))}</h4><p class="lead">${esc(t("settings.apps_help"))}</p>
    ${inst.length ? `<div class="check-list">${inst.map(c => `<label><input type="checkbox" data-conn="${esc(c.id)}" ${(d.connectors || []).includes(c.id) ? "checked" : ""}>
      <div><b>${esc(c.title || c.id)}</b> ${c.connected ? `<span class="chip ok">${esc(t("connectors.connected"))}</span>` : `<span class="chip warn">${esc(t("connectors.not_connected"))}</span>`}<small>${esc(c.url || (c.command || []).join(" "))}</small></div></label>`).join("")}</div>`
      : `<div class="help">${esc(t("settings.no_connectors"))} <a href="#" id="go-conn">${esc(t("nav.connectors"))}</a></div>`}</div>`;
  let m = mode;
  $$("#s-mode button", body).forEach(x => x.onclick = () => { m = x.dataset.m; $$("#s-mode button").forEach(y => y.classList.toggle("sel", y === x)); });
  $("#s-q").oninput = e => { const q = e.target.value.toLowerCase(); $$("#s-list label").forEach(l => l.classList.toggle("hidden", q && !l.dataset.q.includes(q))); };
  $("#go-conn") && ($("#go-conn").onclick = e => { e.preventDefault(); showView("connectors"); });
  saveBar(body, async () => {
    const checked = $$("[data-skill]", body).filter(x => x.checked).map(x => x.dataset.skill);
    const unchecked = $$("[data-skill]", body).filter(x => !x.checked).map(x => x.dataset.skill);
    const p = { skills_mode: m, connectors: $$("[data-conn]", body).filter(x => x.checked).map(x => x.dataset.conn) };
    if (m === "selected") { p.skills = checked; p.skills_off = []; } else { p.skills_off = unchecked; }
    await patchBot(d.id, p);
  });
}
async function tabMemory(body, d) {
  const mem = (await api("GET", `bots/${d.id}/memory`)).memory;
  body.innerHTML = `<div class="section"><h4><i class="ti ti-brain"></i>${esc(t("settings.memory"))}</h4><p class="lead">${esc(t("settings.memory_help"))}</p>
    <div style="display:flex;gap:8px"><input class="inp" id="m-text" placeholder="${esc(t("settings.memory_add_ph"))}"><button class="btn primary" id="m-add"><i class="ti ti-plus"></i>${esc(t("common.add"))}</button></div>
    <div class="row-list">${mem.length ? mem.slice().reverse().map(x => `<div class="r"><i class="ti ti-point"></i><div class="grow">${esc(x.text)}<small>${esc(fmtTime(x.ts || x.created))} · ${esc(x.source || "")}</small></div>
      <button class="icon-btn" data-forget="${esc(x.id)}"><i class="ti ti-trash"></i></button></div>`).join("") : `<div class="r"><span class="help">${esc(t("settings.memory_empty"))}</span></div>`}</div></div>`;
  $("#m-add").onclick = () => guard(async () => { const v = $("#m-text").value.trim(); if (!v) return; await api("POST", `bots/${d.id}/memory`, { text: v }); tabMemory(body, d); });
  $$("[data-forget]", body).forEach(x => x.onclick = () => guard(async () => { await api("DELETE", `bots/${d.id}/memory/${x.dataset.forget}`); tabMemory(body, d); }));
}
function tabApprovals(body, d) {
  const mode = d.approvals?.mode || "ask"; const rules = d.__rules;
  body.innerHTML = `<div class="section"><h4><i class="ti ti-shield-check"></i>${esc(t("settings.approval_rules"))}</h4><p class="lead">${esc(t("settings.approval_help"))}</p>
    <div class="seg" id="a-mode">${["ask", "allow_reads", "allow_all"].map(k => `<button data-m="${k}" class="${mode === k ? "sel" : ""}">${esc(t("settings.mode_" + k))}</button>`).join("")}</div>
    <h4>${esc(t("settings.rules_by_kind"))}</h4>
    <div class="rules">${ACP_KINDS.map(k => `<div><i class="ti ti-${KIND_ICON[k]}"></i> ${esc(t("kind." + k))}</div>
      <div class="seg" data-rule="${k}">${["default", "allow", "ask", "deny"].map(v => `<button data-v="${v}" class="${(rules[k] || "default") === v ? "sel" : ""}">${esc(t("settings.rule_" + v))}</button>`).join("")}</div>`).join("")}</div>
    <div class="help">${esc(t("settings.rules_note"))}</div></div>`;
  let m = mode;
  $$("#a-mode button", body).forEach(x => x.onclick = () => { m = x.dataset.m; $$("#a-mode button").forEach(y => y.classList.toggle("sel", y === x)); });
  $$("[data-rule]", body).forEach(g => $$("button", g).forEach(x => x.onclick = () => { rules[g.dataset.rule] = x.dataset.v; $$("button", g).forEach(y => y.classList.toggle("sel", y === x)); }));
  saveBar(body, () => patchBot(d.id, { approval_mode: m, rules: Object.fromEntries(ACP_KINDS.map(k => [k, rules[k] || "default"])) }));
}
async function tabRoutines(body, d) {
  const rs = (await api("GET", "routines")).routines.filter(r => r.bot === d.id);
  body.innerHTML = `<div class="section"><h4><i class="ti ti-repeat"></i>${esc(t("settings.routines"))}</h4><p class="lead">${esc(t("settings.routines_help"))}</p>
    <div class="two"><div class="field"><label>${esc(t("settings.routine_instruction"))}</label><input id="r-ins"></div>
    <div class="field"><label>${esc(t("settings.routine_every"))}</label><input type="number" id="r-every" value="60" min="15"></div></div>
    <div><button class="btn primary" id="r-add"><i class="ti ti-plus"></i>${esc(t("common.add"))}</button></div>
    <div class="row-list">${rs.length ? rs.map(r => routineRow(r)).join("") : `<div class="r"><span class="help">${esc(t("settings.routines_empty"))}</span></div>`}</div></div>`;
  $("#r-add").onclick = () => guard(async () => { await api("POST", "routines", { bot: d.id, instruction: $("#r-ins").value, every_minutes: +$("#r-every").value }); tabRoutines(body, d); });
  bindRoutineRows(body, () => tabRoutines(body, d));
}
function routineRow(r) {
  const b = botById(r.bot);
  return `<div class="r">${avatar(b, "sm")}<div class="grow">${esc(r.title || r.instruction)}<small>${esc(t("routines.every", r.every_minutes))} · ${esc(r.last_run ? t("routines.last", fmtTime(r.last_run)) : t("routines.never"))}${r.last_status ? " · " + esc(r.last_status) : ""}</small></div>
    <label class="switch"><input type="checkbox" data-rt-toggle="${esc(r.id)}" ${r.enabled ? "checked" : ""}><span></span></label>
    <button class="btn sm" data-rt-run="${esc(r.id)}"><i class="ti ti-player-play"></i>${esc(t("routines.run_now"))}</button>
    <button class="icon-btn" data-rt-del="${esc(r.id)}"><i class="ti ti-trash"></i></button></div>`;
}
function bindRoutineRows(root, again) {
  $$("[data-rt-toggle]", root).forEach(x => x.onchange = () => guard(async () => { await api("PATCH", `routines/${x.dataset.rtToggle}`, { enabled: x.checked }); again(); }));
  $$("[data-rt-run]", root).forEach(x => x.onclick = () => guard(async () => { x.disabled = true; await api("POST", "routines/run", { routine: x.dataset.rtRun }); toast(t("routines.ran")); again(); }));
  $$("[data-rt-del]", root).forEach(x => x.onclick = () => guard(async () => { await api("DELETE", `routines/${x.dataset.rtDel}`); again(); }));
}
function tabDelegation(body, d) {
  const dl = d.delegation || {}; const allowed = new Set(dl.allowed || ["*"]);
  const others = S.bots.filter(b => b.id !== d.id);
  body.innerHTML = `<div class="section"><h4><i class="ti ti-arrow-forward-up"></i>${esc(t("settings.delegation"))}</h4><p class="lead">${esc(t("settings.delegation_help"))}</p>
    ${sw("d-all", allowed.has("*"), t("settings.delegate_all"))}
    <div class="check-list ${allowed.has("*") ? "hidden" : ""}" id="d-list">${others.map(b => `<label><input type="checkbox" data-deleg="${esc(b.id)}" ${allowed.has(b.id) ? "checked" : ""}>${avatar(b, "sm")}<div><b>${esc(b.name)}</b><small>${esc(b.title || b.role || "")}</small></div></label>`).join("")}</div>
    <div class="two"><div class="field"><label>${esc(t("settings.max_depth"))}</label><input type="number" id="d-depth" min="0" max="5" value="${dl.max_depth ?? 3}"></div>
    <div class="field"><label>${esc(t("settings.max_per_turn"))}</label><input type="number" id="d-turn" min="0" max="10" value="${dl.max_per_turn ?? 5}"></div></div></div>`;
  $("#d-all").onchange = e => $("#d-list").classList.toggle("hidden", e.target.checked);
  saveBar(body, () => patchBot(d.id, { delegate_to: $("#d-all").checked ? ["*"] : $$("[data-deleg]", body).filter(x => x.checked).map(x => x.dataset.deleg),
    max_depth: +$("#d-depth").value, max_per_turn: +$("#d-turn").value }));
}
function tabMachines(body, d) {
  const m = d.machines || {}; const allowed = new Set(m.allowed || ["local"]);
  body.innerHTML = `<div class="section"><h4><i class="ti ti-devices-pc"></i>${esc(t("settings.machines"))}</h4><p class="lead">${esc(t("settings.machines_help"))}</p>
    <div class="check-list">${S.machines.map(x => `<label><input type="checkbox" data-mach="${esc(x)}" ${allowed.has(x) ? "checked" : ""}><div><b>${esc(x === "local" ? t("machines.local") : x)}</b></div>
      <input type="radio" name="defm" value="${esc(x)}" ${x === (m.default || "local") ? "checked" : ""} title="${esc(t("settings.default_machine"))}" style="margin-left:auto"></label>`).join("")}</div>
    <div class="help">${esc(t("settings.machines_note"))} <a href="#" id="go-mach">${esc(t("nav.machines"))}</a></div></div>`;
  $("#go-mach").onclick = e => { e.preventDefault(); showView("machines"); };
  saveBar(body, () => patchBot(d.id, { machines: $$("[data-mach]", body).filter(x => x.checked).map(x => x.dataset.mach), default_machine: $("input[name=defm]:checked", body)?.value || "local" }));
}
function tabChannels(body, d) {
  const ch = d.channels || {};
  body.innerHTML = `<div class="section"><h4><i class="ti ti-brand-telegram"></i>Telegram</h4><p class="lead">${esc(t("settings.telegram_help"))}</p>
    ${ch.telegram ? `<div class="chip ok"><i class="ti ti-check"></i>@${esc(ch.telegram.username || "")}${ch.telegram.chat ? " · chat " + esc(ch.telegram.chat) : ""}</div><div><button class="btn danger sm" id="tg-rm">${esc(t("common.remove"))}</button></div>` :
      `<div class="two"><div class="field"><label>${esc(t("settings.telegram_token"))}</label><input type="password" id="tg-token" autocomplete="off"></div><div class="field"><label>${esc(t("settings.telegram_chat"))}</label><input id="tg-chat" placeholder="${esc(t("settings.optional"))}"></div></div>
      <div><button class="btn primary" id="tg-save">${esc(t("common.connect"))}</button></div>`}</div>
  <div class="section"><h4><i class="ti ti-webhook"></i>Webhook</h4><p class="lead">${esc(t("settings.webhook_help"))}</p>
    ${ch.webhook ? `<div class="chip ok"><i class="ti ti-check"></i>${esc(ch.webhook.path)}…</div>` : ""}<div id="wh-out"></div>
    <div style="display:flex;gap:8px"><button class="btn" id="wh-new">${esc(ch.webhook ? t("settings.webhook_rotate") : t("settings.webhook_create"))}</button>${ch.webhook ? `<button class="btn danger sm" id="wh-rm">${esc(t("common.remove"))}</button>` : ""}</div></div>
  <div class="section"><h4><i class="ti ti-bell"></i>${esc(t("settings.notifications"))}</h4>${sw("c-notify", d.notifications, t("settings.notify_desktop"), t("settings.notify_help"))}</div>`;
  $("#tg-save") && ($("#tg-save").onclick = () => guard(async () => { await api("POST", `bots/${d.id}/channel`, { kind: "telegram", token: $("#tg-token").value, chat: $("#tg-chat").value || null }); openSettings(d.id, "channels"); }));
  $("#tg-rm") && ($("#tg-rm").onclick = () => guard(async () => { await api("DELETE", `bots/${d.id}/channel`, { kind: "telegram" }); openSettings(d.id, "channels"); }));
  $("#wh-rm") && ($("#wh-rm").onclick = () => guard(async () => { await api("DELETE", `bots/${d.id}/channel`, { kind: "webhook" }); openSettings(d.id, "channels"); }));
  $("#wh-new").onclick = () => guard(async () => { const r = await api("POST", `bots/${d.id}/channel`, { kind: "webhook" });
    $("#wh-out").innerHTML = `<div class="field"><label>${esc(t("settings.webhook_url"))}</label><input readonly value="${esc(location.origin + r.path)}"><div class="help">${esc(t("settings.webhook_once"))}</div></div>`; });
  $("#c-notify").onchange = e => guard(() => patchBot(d.id, { notifications: e.target.checked }));
}
function tabManage(body, d) {
  body.innerHTML = `<div class="section"><h4><i class="ti ti-adjustments"></i>${esc(t("settings.tab_manage"))}</h4>
    ${sw("g-active", d.active !== false, t("settings.active"), d.main ? t("settings.main_always_active") : t("settings.active_help"))}
    ${sw("g-pinned", d.pinned, t("settings.pinned"))}
    ${sw("g-hidden", d.hidden, t("settings.hidden"), t("settings.hidden_help"))}</div>
  <div class="section"><h4><i class="ti ti-copy"></i>${esc(t("settings.duplicate"))}</h4><div style="display:flex;gap:8px"><input class="inp" id="g-dup" value="${esc(d.name)} 2"><button class="btn" id="g-dup-go">${esc(t("settings.duplicate"))}</button></div></div>
  <div class="section"><h4><i class="ti ti-refresh"></i>${esc(t("settings.reset"))}</h4><p class="lead">${esc(t("settings.reset_help"))}</p><div><button class="btn" id="g-reset">${esc(t("settings.reset"))}</button></div></div>
  ${d.main ? "" : `<div class="section"><h4 style="color:var(--bad)"><i class="ti ti-trash"></i>${esc(t("settings.delete"))}</h4><div><button class="btn danger" id="g-del">${esc(t("settings.delete"))}</button></div></div>`}`;
  if (d.main) $("#g-active").disabled = true;
  for (const [id, f] of [["g-active", "active"], ["g-pinned", "pinned"], ["g-hidden", "hidden"]]) $("#" + id).onchange = e => guard(async () => { await patchBot(d.id, { [f]: e.target.checked }); await refreshState(); });
  $("#g-dup-go").onclick = () => guard(async () => { const r = await api("POST", `bots/${d.id}/duplicate`, { name: $("#g-dup").value }); await refreshState(); openSettings(r.bot.id); });
  $("#g-reset").onclick = () => confirmModal(t("settings.reset"), t("settings.reset_confirm", d.name), async () => { await api("POST", `bots/${d.id}/reset`, {}); S.messages[d.id] = []; toast(t("common.done")); });
  $("#g-del") && ($("#g-del").onclick = () => confirmModal(t("settings.delete"), t("settings.delete_confirm", d.name), async () => { await api("DELETE", `bots/${d.id}`); await refreshState(); openBot(S.bots.find(b => b.main).id); }));
}

// ------------------------------------------------------------------ 其它页面
function showView(name) {
  S.view = name; $("#app").classList.remove("side-open");
  $$(".nav-item").forEach(n => n.classList.toggle("active", n.dataset.view === name));
  renderSidebar();
  ({ approvals: renderApprovals, connectors: renderConnectors, agents: renderAgents, machines: renderMachines, skills: renderSkills, routines: renderRoutines, runtime: renderRuntime })[name]();
}
function page(title, icon, lead, inner) {
  $("#view").innerHTML = `<div class="page"><div class="page-inner"><h2><button class="icon-btn only-narrow" id="btn-side2"><i class="ti ti-menu-2"></i></button><i class="ti ti-${icon}"></i>${esc(title)}</h2>${lead ? `<p class="lead">${esc(lead)}</p>` : ""}${inner}</div></div>`;
  $("#btn-side2").onclick = () => $("#app").classList.toggle("side-open");
}
async function renderApprovals() {
  if (S.view !== "approvals") return;
  const a = S.approvals;
  page(t("nav.approvals"), "shield-check", t("approvals.lead"), `<div class="row-list">${a.length ? a.map(x => { const b = botById(x.bot);
    return `<div class="r">${avatar(b)}<div class="grow"><b>${esc(x.bot_name || x.bot)}</b> · ${esc(x.toolCall?.title || x.toolCall?.kind || "")}
      <small>${esc(t("kind." + (x.toolCall?.kind || "other")))} · ${esc(x.machine || "local")} · ${esc(fmtTime(x.created))}</small></div>
      ${(x.options || []).map(o => `<button class="btn sm ${String(o.kind).startsWith("allow") ? "primary" : ""}" data-approve="${esc(x.id)}" data-option="${esc(o.optionId)}">${esc(optName(o))}</button>`).join("")}</div>`; }).join("")
    : `<div class="r"><span class="help">${esc(t("approvals.none"))}</span></div>`}</div>`);
  $$("[data-approve]").forEach(x => x.onclick = () => answerApproval(x.dataset.approve, x.dataset.option));
}
async function loadAgents(force) { if (!S.agents || force) S.agents = await api("GET", "agents"); return S.agents; }
async function renderConnectors() {
  const c = S.connectors = await api("GET", "connectors");
  const inst = c.installed;
  page(t("nav.connectors"), "plug-connected", t("connectors.lead"), `
    <h3>${esc(t("connectors.added"))}</h3>
    <div class="row-list">${inst.length ? inst.map(x => `<div class="r"><span class="avatar sm" style="background:var(--soft);color:var(--text)"><i class="ti ti-${esc(x.icon || "plug")}"></i></span>
      <div class="grow"><b>${esc(x.title || x.id)}</b> ${x.connected ? `<span class="chip ok">${esc(t("connectors.connected"))}</span>` : `<span class="chip warn">${esc(t("connectors.not_connected"))}</span>`}
      <span class="chip">${esc(t("connectors.auth_" + ((x.auth || {}).kind || "none")))}</span> ${x.tool_count ? `<span class="chip">${esc(t("connectors.tools", x.tool_count))}</span>` : ""}
      <small>${esc(x.url || (x.command || []).join(" "))} · ${esc(t("connectors.used_by", S.bots.filter(b => (b.connectors || []).includes(x.id)).map(b => b.name).join(", ") || "—"))}</small></div>
      ${(x.auth || {}).kind !== "none" ? `<button class="btn sm ${x.connected ? "" : "primary"}" data-cconnect="${esc(x.id)}">${esc(x.connected ? t("connectors.reconnect") : t("common.connect"))}</button>` : ""}
      <button class="btn sm" data-ctools="${esc(x.id)}">${esc(t("connectors.tools_btn"))}</button>
      ${x.connected && (x.auth || {}).kind !== "none" ? `<button class="btn sm ghost" data-cdisc="${esc(x.id)}">${esc(t("connectors.disconnect"))}</button>` : ""}
      <button class="icon-btn" data-crm="${esc(x.id)}"><i class="ti ti-trash"></i></button></div>`).join("") : `<div class="r"><span class="help">${esc(t("connectors.none"))}</span></div>`}</div>
    <h3>${esc(t("connectors.catalog"))}</h3>
    <div class="grid">${c.catalog.map(x => `<div class="tile"><div class="top"><span class="logo"><i class="ti ti-${esc(x.icon || "plug")}"></i></span><div><b>${esc(x.title)}</b><small>${esc(x.vendor)} · ${esc(t("connectors.auth_" + x.auth.kind))}</small></div></div>
      <div class="desc">${esc(x.summary)}</div><div class="acts">${x.installed ? `<span class="chip ok"><i class="ti ti-check"></i>${esc(t("connectors.added_chip"))}</span>` : `<button class="btn sm primary" data-cadd="${esc(x.key)}"><i class="ti ti-plus"></i>${esc(t("common.add"))}</button>`}
      <a class="btn sm ghost" href="${esc(x.docs)}" target="_blank" rel="noopener"><i class="ti ti-external-link"></i>${esc(t("common.docs"))}</a></div></div>`).join("")}
      <div class="tile"><div class="top"><span class="logo"><i class="ti ti-link-plus"></i></span><div><b>${esc(t("connectors.custom"))}</b><small>MCP · HTTP / stdio</small></div></div>
      <div class="desc">${esc(t("connectors.custom_help"))}</div><div class="acts"><button class="btn sm" id="c-custom"><i class="ti ti-plus"></i>${esc(t("common.add"))}</button></div></div></div>`);
  $$("[data-cadd]").forEach(x => x.onclick = () => guard(async () => { await api("POST", "connectors", { key: x.dataset.cadd }); renderConnectors(); }));
  $$("[data-crm]").forEach(x => x.onclick = () => confirmModal(t("common.remove"), t("connectors.remove_confirm", x.dataset.crm), async () => { await api("DELETE", `connectors/${x.dataset.crm}`); renderConnectors(); }));
  $$("[data-cdisc]").forEach(x => x.onclick = () => guard(async () => { await api("POST", `connectors/${x.dataset.cdisc}/disconnect`, {}); renderConnectors(); }));
  $$("[data-ctools]").forEach(x => x.onclick = () => connectorTools(x.dataset.ctools));
  $$("[data-cconnect]").forEach(x => x.onclick = () => connectConnector(inst.find(i => i.id === x.dataset.cconnect)));
  $("#c-custom").onclick = customConnector;
}
function connectConnector(c) {
  const kind = (c.auth || {}).kind;
  if (kind === "bearer") {
    modal(`<h3><i class="ti ti-key"></i>${esc(t("connectors.connect_title", c.title || c.id))}</h3>
      <div class="field"><label>${esc(t("connectors.token"))}</label><input type="password" id="mc-token" autocomplete="off"><div class="help">${esc(t("connectors.token_help"))}</div></div>`,
      async () => { await api("POST", `connectors/${c.id}/connect`, { token: $("#mc-token").value }); renderConnectors(); toast(t("connectors.connected")); });
  } else {
    modal(`<h3><i class="ti ti-login"></i>${esc(t("connectors.connect_title", c.title || c.id))}</h3><p class="lead">${esc(t("connectors.oauth_help"))}</p>
      ${(c.auth || {}).client_required || (c.auth || {}).registration_url == null ? `<div class="two"><div class="field"><label>Client ID</label><input id="mc-cid"></div><div class="field"><label>Client secret</label><input type="password" id="mc-cs" placeholder="${esc(t("settings.optional"))}"></div></div>` : ""}
      <div id="mc-status"></div>`, async () => {
      const r = await api("POST", `connectors/${c.id}/connect`, { client_id: $("#mc-cid")?.value || null, client_secret: $("#mc-cs")?.value || null });
      if (r.error) throw Object.assign(new Error(r.error.message), r.error);
      if (r.authorize_url) window.open(r.authorize_url, "_blank", "noopener");
      toast(t("connectors.oauth_wait"));
      pollJob(r.job, () => renderConnectors());
    });
  }
}
async function pollJob(id, done) {
  for (let i = 0; i < 400; i++) {
    const j = await api("GET", `jobs/${id}`); S.jobs[id] = j; renderJobs();
    if (j.status !== "running") { j.status === "done" ? toast(t("jobs.done", t("jobs." + j.kind))) : toast(j.error?.message || "failed", true); done && done(j); return j; }
    await new Promise(r => setTimeout(r, 1000));
  }
}
function renderJobs() {
  for (const j of Object.values(S.jobs)) {
    const el = $(`[data-job-for="${CSS.escape(j.agent || j.tool || j.connector || "")}"]`);
    if (el) el.innerHTML = j.status === "running" ? `<div class="progress"><div></div></div>` : j.status === "failed" ? `<span class="chip bad">${esc(j.error?.message || "")}</span>` : "";
  }
}
async function connectorTools(id) {
  const r = await guard(() => api("GET", `connectors/${id}/tools?refresh=1`));
  modal(`<h3><i class="ti ti-tool"></i>${esc(t("connectors.tools_of", id))}</h3><div class="row-list">${(r.tools || []).map(x => `<div class="r"><div class="grow"><b class="mono">${esc(x.name)}</b>
    ${x.annotations?.readOnlyHint ? `<span class="chip ok">${esc(t("connectors.read_only"))}</span>` : `<span class="chip warn">${esc(t("connectors.may_write"))}</span>`}<small>${esc((x.description || "").slice(0, 240))}</small></div></div>`).join("") || `<div class="r">${esc(t("connectors.no_tools"))}</div>`}</div>`);
}
function customConnector() {
  modal(`<h3><i class="ti ti-link-plus"></i>${esc(t("connectors.custom"))}</h3>
    <div class="two"><div class="field"><label>ID</label><input id="cc-id" placeholder="my-server"></div><div class="field"><label>${esc(t("connectors.title_f"))}</label><input id="cc-title"></div></div>
    <div class="field"><label>URL</label><input id="cc-url" placeholder="https://example.com/mcp"></div>
    <div class="field"><label>${esc(t("connectors.or_command"))}</label><input id="cc-cmd" placeholder="npx -y @modelcontextprotocol/server-filesystem /home/foxos"></div>
    <div class="two"><div class="field"><label>${esc(t("connectors.auth"))}</label><select id="cc-auth"><option value="none">${esc(t("connectors.auth_none"))}</option><option value="bearer">${esc(t("connectors.auth_bearer"))}</option><option value="oauth">${esc(t("connectors.auth_oauth"))}</option></select></div>
    <div class="field"><label>${esc(t("connectors.header"))}</label><input id="cc-header" placeholder="Authorization"></div></div>`, async () => {
    const cmd = $("#cc-cmd").value.trim();
    await api("POST", "connectors", { id: $("#cc-id").value.trim(), title: $("#cc-title").value || null, url: $("#cc-url").value.trim() || null,
      command: cmd ? cmd.split(/\s+/) : null, auth: $("#cc-auth").value, header: $("#cc-header").value || null });
    renderConnectors();
  });
}
async function renderAgents() {
  page(t("nav.agents"), "terminal-2", t("agents.lead"), `<div class="progress"><div></div></div>`);
  const a = await loadAgents(true);
  const inst = new Map(a.installed.map(x => [x.id, x]));
  const keys = a.keys || [];
  const reg = [...a.registry].sort((x, y) => (inst.has(y.id) - inst.has(x.id)) || ((["claude-acp", "codex-acp", "gemini", "qwen-code", "opencode"].indexOf(x.id) + 1 || 99) - (["claude-acp", "codex-acp", "gemini", "qwen-code", "opencode"].indexOf(y.id) + 1 || 99)) || x.name.localeCompare(y.name));
  const tile = x => { const i = inst.get(x.id); const k = keys.filter(z => z.agent === x.id);
    return `<div class="tile"><div class="top"><span class="logo">${agentIcon(x.id).replace("<img", '<img class="mono"')}</span><div><b>${esc(x.name)}</b><small>${esc(x.version || "")} · ${esc(x.license || "?")}${x.redistributable === false ? " · " + esc(t("agents.proprietary")) : ""}</small></div></div>
      <div class="desc">${esc(x.description || "")}</div>
      <div class="acts">${i ? `<span class="chip ok"><i class="ti ti-check"></i>${esc(i.system ? t("agents.preinstalled") : t("agents.installed", i.version || ""))}</span>
          <button class="btn sm" data-probe="${esc(x.id)}"><i class="ti ti-plug-connected"></i>${esc(t("agents.probe"))}</button>
          <button class="btn sm" data-keys="${esc(x.id)}"><i class="ti ti-key"></i>${esc(t("agents.keys"))}${k.length ? " · " + k.length : ""}</button>
          ${i.system ? "" : `<button class="icon-btn" data-uninst="${esc(x.id)}"><i class="ti ti-trash"></i></button>`}`
        : `<button class="btn sm primary" data-install="${esc(x.id)}" ${x.methods?.length ? "" : "disabled"}><i class="ti ti-download"></i>${esc(x.methods?.length ? t("agents.install") : t("agents.unavailable"))}</button>`}
        ${x.repository ? `<a class="btn sm ghost" href="${esc(x.repository)}" target="_blank" rel="noopener"><i class="ti ti-external-link"></i></a>` : ""}</div>
      <div data-job-for="${esc(x.id)}"></div></div>`; };
  page(t("nav.agents"), "terminal-2", t("agents.lead"), `
    <div class="tile"><div class="top"><span class="logo"><i class="ti ti-sparkles"></i></span><div><b>${esc(t("agents.local"))}</b><small>foxos-local · ${esc(t("agents.builtin"))}</small></div></div><div class="desc">${esc(t("agents.local_help"))}</div></div>
    <h3>${esc(t("agents.registry", reg.length))}</h3><p class="lead">${esc(t("agents.registry_help"))} <span class="mono">${esc(a.source || "")}</span></p>
    <div class="grid">${reg.map(tile).join("")}</div>`);
  $$("[data-install]").forEach(x => x.onclick = () => guard(async () => {
    const ag = reg.find(r => r.id === x.dataset.install);
    const go = async () => { x.disabled = true; const r = await api("POST", `agents/${ag.id}/install`, {}); S.jobs[r.job] = { id: r.job, kind: "install", status: "running", agent: ag.id }; renderJobs(); pollJob(r.job, () => { S.agents = null; renderAgents(); }); };
    if (ag.redistributable === false) confirmModal(t("agents.license_title"), t("agents.license_confirm", ag.name, ag.license), go); else go();
  }));
  $$("[data-probe]").forEach(x => x.onclick = () => guard(async () => { const r = await api("POST", `agents/${x.dataset.probe}/probe`, {}); const j = await pollJob(r.job);
    if (j?.status === "done") { const p = j.result; modal(`<h3><i class="ti ti-plug-connected"></i>${esc(t("agents.probe_result", x.dataset.probe))}</h3><div class="kv">
      <span>agentInfo</span><span class="mono">${esc(JSON.stringify(p.agentInfo || p.agent_info || {}))}</span>
      <span>protocol</span><span class="mono">${esc(p.protocolVersion ?? p.protocol_version ?? "")}</span>
      <span>session/new</span><span class="mono">${esc(p.session ? (p.session.ok ? p.session.sessionId : (p.session.auth_required ? t("agents.needs_login") + " · " : "") + p.session.message) : "—")}</span>
      <span>ms</span><span class="mono">${esc(p.ms)}</span>
      <span>authMethods</span><span class="mono">${esc((p.authMethods || p.auth_methods || []).map(m => m.id).join(", ") || "—")}</span></div>
      ${(p.authMethods || p.auth_methods || []).length ? `<div class="acts" style="justify-content:flex-start">${(p.authMethods || p.auth_methods).map(m => `<button class="btn sm" data-login="${esc(m.id)}">${esc(t("agents.sign_in_with", m.name || m.id))}</button>`).join("")}</div>` : ""}`);
      $$("[data-login]").forEach(b => b.onclick = () => guard(async () => { const r2 = await api("POST", `agents/${x.dataset.probe}/login`, { method: b.dataset.login }); pollJob(r2.job); })); } }));
  $$("[data-keys]").forEach(x => x.onclick = () => agentKeys(reg.find(r => r.id === x.dataset.keys) || { id: x.dataset.keys, name: x.dataset.keys }));
  $$("[data-uninst]").forEach(x => x.onclick = () => confirmModal(t("agents.uninstall"), t("agents.uninstall_confirm", x.dataset.uninst), async () => { await api("POST", `agents/${x.dataset.uninst}/uninstall`, {}); S.agents = null; renderAgents(); }));
}
function agentKeys(ag) {
  const ks = (S.agents.keys || []).filter(k => k.agent === ag.id);
  const envs = [...new Set([...(ag.key_env || []), ...ks.map(k => k.name)])];
  modal(`<h3><i class="ti ti-key"></i>${esc(t("agents.keys_of", ag.name))}</h3><p class="lead">${esc(t("agents.keys_help"))}</p>
    <div class="row-list">${ks.length ? ks.map(k => `<div class="r"><div class="grow"><b class="mono">${esc(k.name)}</b><small>…${esc(k.hint)} · ${esc(fmtTime(k.updated))}</small></div><button class="icon-btn" data-krm="${esc(k.name)}"><i class="ti ti-trash"></i></button></div>`).join("") : `<div class="r"><span class="help">${esc(t("agents.no_keys"))}</span></div>`}</div>
    <div class="two"><div class="field"><label>${esc(t("agents.env_name"))}</label><input id="k-name" list="k-envs" value="${esc(envs[0] || "")}"><datalist id="k-envs">${envs.map(e => `<option value="${esc(e)}">`).join("")}</datalist></div>
    <div class="field"><label>${esc(t("agents.key_value"))}</label><input type="password" id="k-val" autocomplete="off"></div></div>`, async () => {
    await api("POST", `agents/${ag.id}/key`, { name: $("#k-name").value.trim(), value: $("#k-val").value }); S.agents = null; toast(t("agents.key_saved")); renderAgents(); });
  $$("[data-krm]").forEach(x => x.onclick = () => guard(async () => { await api("DELETE", `agents/${ag.id}/key`, { name: x.dataset.krm }); closeModal(); S.agents = null; renderAgents(); }));
}
async function renderMachines() {
  page(t("nav.machines"), "devices-pc", t("machines.lead"), `<div class="progress"><div></div></div>`);
  const r = await api("GET", "machines?check=1");
  const host = r.host || {};
  page(t("nav.machines"), "devices-pc", t("machines.lead"), `
    <h3>${esc(t("machines.controlled"))}</h3>
    <div class="row-list">${r.machines.map(m => `<div class="r"><span class="avatar sm" style="background:${m.local ? "var(--accent)" : m.online ? "var(--ok)" : "#9aa0a9"}"><i class="ti ti-device-desktop"></i></span>
      <div class="grow"><b>${esc(m.local ? t("machines.local") : m.name)}</b> ${m.local ? "" : m.online ? `<span class="chip ok">${esc(t("machines.online"))}${m.ms ? " · " + m.ms + "ms" : ""}</span>` : `<span class="chip bad">${esc(t("machines.offline"))}</span>`}
      <small>${esc(m.local ? m.workspace : `${m.url} · ${m.host || ""} · ${t("machines.as_client", m.client || "")}`)}</small>
      ${m.fingerprint ? `<small class="mono">sha256 ${esc(m.fingerprint)}</small>` : ""}
      ${m.grants ? `<small>${esc(t("machines.grants_here"))} ${esc(Object.entries(m.grants).map(([b, g]) => `${b}: ${(g.permissions || []).join("/")}${g.apps?.length ? " [" + g.apps.join(",") + "]" : ""} ${g.scope || "."}`).join("; ") || "—")}</small>` : ""}
      ${m.acting?.length ? `<small>${esc(t("machines.acting_there"))} ${esc(m.acting.map(a => a.agent + " · " + a.command).join("; "))}</small>` : ""}
      <small>${esc(t("machines.bots_using", S.bots.filter(b => (b.machines?.allowed || ["local"]).includes(m.name)).map(b => b.name).join(", ") || "—"))}</small></div>
      ${m.local ? "" : `<button class="icon-btn" data-mrm="${esc(m.name)}"><i class="ti ti-trash"></i></button>`}</div>`).join("")}</div>
    <div class="section"><h4><i class="ti ti-link"></i>${esc(t("machines.pair"))}</h4><p class="lead">${esc(t("machines.pair_help"))}</p>
      <div class="two"><div class="field"><label>${esc(t("machines.name"))}</label><input id="p-name" placeholder="vm1"></div><div class="field"><label>URL</label><input id="p-url" placeholder="https://192.168.1.20:7443"></div></div>
      <div class="two"><div class="field"><label>${esc(t("machines.code"))}</label><input id="p-code" placeholder="XXXX-XXXX-XXXX" autocomplete="off"></div><div class="field"><label>${esc(t("machines.fingerprint"))}</label><input id="p-fp" placeholder="sha256…"></div></div>
      <div><button class="btn primary" id="p-go"><i class="ti ti-link"></i>${esc(t("machines.pair_btn"))}</button></div></div>
    <div class="section"><h4><i class="ti ti-server"></i>${esc(t("machines.this_host"))}</h4><p class="lead">${esc(t("machines.host_help"))}</p>
      <div class="kv"><span>${esc(t("machines.fingerprint"))}</span><span class="mono">${esc(host.fingerprint || t("machines.no_cert"))}</span></div>
      <div><button class="btn" id="h-code"><i class="ti ti-key"></i>${esc(t("machines.new_code"))}</button></div><div id="h-code-out"></div>
      <h4>${esc(t("machines.clients"))}</h4>
      <div class="row-list">${(host.clients || []).length ? host.clients.map(c => `<div class="r"><i class="ti ti-device-laptop"></i><div class="grow"><b>${esc(c.client)}</b><small>${esc(fmtTime(c.paired_at))}</small>
        <small>${esc(Object.entries(c.grants || {}).map(([b, g]) => `${b}: ${(g.permissions || []).join("/")}${g.apps?.length ? " [" + g.apps.join(",") + "]" : ""} ${g.scope || "."}`).join("; ") || t("machines.no_grants"))}</small></div>
        <button class="btn sm" data-grant="${esc(c.client)}">${esc(t("machines.grant"))}</button><button class="btn sm ghost" data-revoke="${esc(c.client)}">${esc(t("machines.revoke_all"))}</button>
        <button class="icon-btn" data-unpair="${esc(c.client)}"><i class="ti ti-unlink"></i></button></div>`).join("") : `<div class="r"><span class="help">${esc(t("machines.no_clients"))}</span></div>`}</div></div>`);
  $("#p-go").onclick = () => guard(async () => { const x = await api("POST", "machines/pair", { name: $("#p-name").value.trim(), url: $("#p-url").value.trim(), code: $("#p-code").value.trim(), fingerprint: $("#p-fp").value.trim() || null });
    toast(x.message); await refreshState(); renderMachines(); });
  $$("[data-mrm]").forEach(x => x.onclick = () => confirmModal(t("common.remove"), t("machines.remove_confirm", x.dataset.mrm), async () => { await api("DELETE", `machines/${x.dataset.mrm}`); await refreshState(); renderMachines(); }));
  $("#h-code").onclick = () => guard(async () => { const c = await api("POST", "machines/host/code", { ttl: 600 });
    $("#h-code-out").innerHTML = `<div class="kv"><span>${esc(t("machines.code"))}</span><b class="mono" style="font-size:16px">${esc(c.code)}</b><span>${esc(t("machines.fingerprint"))}</span><span class="mono">${esc(c.fingerprint || host.fingerprint || "")}</span><span>${esc(t("machines.expires"))}</span><span>${esc(t("machines.expires_in", Math.round(c.expires_in / 60)))}</span></div>
      <div class="help">${esc(t("machines.code_help"))}</div>`; });
  $$("[data-grant]").forEach(x => x.onclick = () => grantModal(x.dataset.grant));
  $$("[data-revoke]").forEach(x => x.onclick = () => guard(async () => { await api("POST", "machines/host/revoke", { client: x.dataset.revoke }); renderMachines(); }));
  $$("[data-unpair]").forEach(x => x.onclick = () => confirmModal(t("machines.unpair"), t("machines.unpair_confirm", x.dataset.unpair), async () => { await api("POST", "machines/host/unpair", { client: x.dataset.unpair }); renderMachines(); }));
}
function grantModal(client) {
  const perms = ["read", "create", "modify", "delete", "run"];
  modal(`<h3><i class="ti ti-shield-lock"></i>${esc(t("machines.grant_title", client))}</h3><p class="lead">${esc(t("machines.grant_help"))}</p>
    <div class="field"><label>${esc(t("machines.bot_id"))}</label><input id="g-bot" placeholder="coder"></div>
    <div class="field"><label>${esc(t("machines.permissions"))}</label><div style="display:flex;gap:12px;flex-wrap:wrap">${perms.map(p => `<label><input type="checkbox" data-perm="${p}" ${p === "read" ? "checked" : ""}> ${esc(t("perm." + p))}</label>`).join("")}</div></div>
    <div class="two"><div class="field"><label>${esc(t("machines.apps"))}</label><input id="g-apps" placeholder="files,desktop"></div><div class="field"><label>${esc(t("machines.scope"))}</label><input id="g-scope" value="."></div></div>`,
    async () => { await api("POST", "machines/host/grant", { client, bot: $("#g-bot").value.trim(), permissions: $$("[data-perm]").filter(x => x.checked).map(x => x.dataset.perm),
      apps: $("#g-apps").value.split(",").map(s => s.trim()).filter(Boolean), scope: $("#g-scope").value.trim() || "." }); renderMachines(); });
}
async function renderSkills() {
  const r = await api("GET", "skills");
  const groups = {}; for (const s of r.skills) (groups[s.kind] ||= []).push(s);
  page(t("nav.skills"), "books", t("skills.lead"), `<div class="search"><i class="ti ti-search"></i><input id="sk-q" placeholder="${esc(t("common.search"))}"></div>
    ${Object.entries(groups).map(([k, arr]) => `<h3>${esc(t("skills.kind_" + k))} · ${arr.length}</h3><div class="grid">${arr.map(s => `<div class="tile" data-skq="${esc((s.name + " " + s.description).toLowerCase())}">
      <div class="top"><span class="logo"><i class="ti ti-${k === "principle" ? "compass" : k === "subagent" ? "users" : "book"}"></i></span><div><b>${esc(s.name)}</b><small>${esc(s.source)}${s.manual_only ? " · " + esc(t("skills.manual")) : ""}</small></div></div>
      <div class="desc">${esc(s.description)}</div><div class="acts"><button class="btn sm" data-skshow="${esc(s.name)}">${esc(t("skills.view"))}</button></div></div>`).join("")}</div>`).join("")}
    <p class="help">${esc(t("skills.notice"))}</p>`);
  $("#sk-q").oninput = e => { const q = e.target.value.toLowerCase(); $$("[data-skq]").forEach(x => x.classList.toggle("hidden", q && !x.dataset.skq.includes(q))); };
  $$("[data-skshow]").forEach(x => x.onclick = async () => { const s = (await api("GET", `skills/${encodeURIComponent(x.dataset.skshow)}`)).skill;
    modal(`<h3><i class="ti ti-book"></i>${esc(s.name)}</h3><div class="mono">${esc(s.path)}</div><div class="md-view">${esc(s.content)}</div>`); });
}
async function renderRoutines() {
  const rs = (await api("GET", "routines")).routines;
  page(t("nav.routines"), "repeat", t("routines.lead"), `<div class="row-list">${rs.length ? rs.map(routineRow).join("") : `<div class="r"><span class="help">${esc(t("settings.routines_empty"))}</span></div>`}</div>`);
  bindRoutineRows($("#view"), renderRoutines);
}
async function renderRuntime() {
  page(t("nav.runtime"), "stack-2", t("runtime.lead"), `<div class="progress"><div></div></div>`);
  const r = await api("GET", "runtime");
  const groups = {}; for (const x of r.tools) (groups[x.group] ||= []).push(x);
  page(t("nav.runtime"), "stack-2", t("runtime.lead"), Object.entries(groups).map(([g, arr]) => `<h3>${esc(t("runtime.group_" + g))}</h3><div class="row-list">${arr.map(x => `<div class="r">
    <i class="ti ti-${x.ok ? "circle-check" : "circle-dashed"}" style="color:${x.ok ? "var(--ok)" : "var(--muted)"}"></i>
    <div class="grow"><b>${esc(x.title)}</b> <span class="chip">${esc(x.version)}</span> <span class="chip">${esc(t("runtime.phase_" + x.phase))}</span> <span class="chip">${esc(x.license)}</span>
    <small>${esc(x.ok ? (x.found || "") + (x.path ? " · " + x.path : "") : (x.why_not_iso || x.source || ""))}</small><div data-job-for="${esc(x.name)}"></div></div>
    ${x.ok || ["apt", "bundled"].includes(x.kind) ? "" : `<button class="btn sm" data-rtinst="${esc(x.name)}" data-redis="${x.redistributable ? 1 : 0}" data-lic="${esc(x.license)}"><i class="ti ti-download"></i>${esc(t("agents.install"))}</button>`}</div>`).join("")}</div>`).join(""));
  $$("[data-rtinst]").forEach(x => x.onclick = () => {
    const go = async () => { const j = await api("POST", `runtime/${x.dataset.rtinst}/install`, { accept_license: x.dataset.redis === "0" }); S.jobs[j.job] = { id: j.job, kind: "runtime", status: "running", tool: x.dataset.rtinst }; renderJobs(); pollJob(j.job, renderRuntime); };
    x.dataset.redis === "0" ? confirmModal(t("agents.license_title"), t("agents.license_confirm", x.dataset.rtinst, x.dataset.lic), go) : guard(go);
  });
}

// ------------------------------------------------------------------ 新建智能体、对话框
async function newBot() {
  const ag = await loadAgents();
  const agents = [{ id: "foxos-local", name: t("agents.local") }, ...(ag.installed || []).filter(a => a.id !== "foxos-local")];
  let icon = "robot", color = COLORS[1];
  modal(`<h3><i class="ti ti-plus"></i>${esc(t("bots.new"))}</h3>
    <div class="two"><div class="field"><label>${esc(t("settings.name"))}</label><input id="n-name"></div><div class="field"><label>${esc(t("settings.title_f"))}</label><input id="n-title"></div></div>
    <div class="field"><label>${esc(t("settings.role"))}</label><input id="n-role"></div>
    <div class="field"><label>${esc(t("settings.agent"))}</label><select id="n-agent">${agents.map(a => `<option value="${esc(a.id)}">${esc(a.name)} (${esc(a.id)})</option>`).join("")}</select></div>
    <div class="icon-pick" id="n-icons">${ICONS.slice(0, 16).map(i => `<button data-icon="${i}" class="${i === icon ? "sel" : ""}"><i class="ti ti-${i}"></i></button>`).join("")}</div>
    <div class="color-pick" id="n-colors">${COLORS.map(c => `<button data-color="${c}" style="background:${c}" class="${c === color ? "sel" : ""}"></button>`).join("")}</div>
    ${sw("n-iso", false, t("settings.isolated"), t("settings.isolated_help"))}`, async () => {
    const r = await api("POST", "bots", { name: $("#n-name").value.trim(), title: $("#n-title").value, role: $("#n-role").value, agent: $("#n-agent").value, icon, color, isolated: $("#n-iso").checked });
    await refreshState(); openBot(r.bot.id);
  });
  $$("#n-icons button").forEach(x => x.onclick = () => { icon = x.dataset.icon; $$("#n-icons button").forEach(y => y.classList.toggle("sel", y === x)); });
  $$("#n-colors button").forEach(x => x.onclick = () => { color = x.dataset.color; $$("#n-colors button").forEach(y => y.classList.toggle("sel", y === x)); });
  $("#n-name").focus();
}
function modal(inner, onOk) {
  closeModal();
  const el = h(`<div class="modal-bg"><div class="modal">${inner}<div class="acts"><button class="btn" data-x>${esc(onOk ? t("common.cancel") : t("common.close"))}</button>${onOk ? `<button class="btn primary" data-ok>${esc(t("common.ok"))}</button>` : ""}</div></div></div>`);
  el.onclick = e => { if (e.target === el || e.target.closest("[data-x]")) closeModal(); };
  const ok = $("[data-ok]", el);
  if (ok) ok.onclick = async () => { ok.disabled = true; try { await onOk(); closeModal(); } catch (e) { toast(e.message + (e.hint ? " — " + e.hint : ""), true); ok.disabled = false; } };
  $("#modal-root").append(el);
  el.onkeydown = e => { if (e.key === "Escape") closeModal(); if (e.key === "Enter" && ok && e.target.tagName === "INPUT") ok.click(); };
}
function closeModal() { $("#modal-root").innerHTML = ""; }
function confirmModal(title, text, fn) { modal(`<h3>${esc(title)}</h3><p>${esc(text)}</p>`, fn); }

// ------------------------------------------------------------------ 启动
function layout() { $("#app").classList.toggle("narrow", innerWidth < 760); }
async function init() {
  const st0 = await api("GET", "state").catch(() => null);
  await loadLang(S.lang || st0?.lang || "zh-CN");
  $("#lang").onchange = e => { loadLang(e.target.value).then(() => { renderSidebar(); S.view === "chat" ? (renderChat(), renderMessages(true)) : S.view === "settings" ? openSettings(S.current) : showView(S.view); }); };
  $("#bot-search").oninput = renderSidebar;
  $("#btn-new-bot").onclick = newBot;
  $$(".nav-item").forEach(n => n.onclick = () => showView(n.dataset.view));
  $("#btn-takeover").onclick = () => guard(async () => { await api("POST", S.control?.paused ? "control/resume" : "control/pause", { reason: "ui" }); await refreshState(); renderTakeover(); });
  $("#btn-dock").onclick = () => guard(async () => { const r = await api("PUT", "prefs", { dock: !S.prefs.dock }); S.prefs = r.prefs; renderDock(); toast(S.prefs.dock ? t("app.docked") : t("app.undocked")); });
  addEventListener("resize", layout); layout();
  await refreshState(); renderTakeover(); renderDock();
  loadAgents().catch(() => {});
  connectEvents();
  // #approvals、#bot/<id>、#settings/<id>/<tab>
  const [h0, h1, h2] = decodeURIComponent(location.hash.slice(1)).split("/");
  if (["approvals", "connectors", "agents", "machines", "skills", "routines", "runtime"].includes(h0)) showView(h0);
  else if (h0 === "settings" && botById(h1)) { openBot(h1); openSettings(h1, h2); }
  else { const id = h0 === "bot" ? h1 : h0; openBot(id && botById(id) ? id : S.current); }
}
function renderDock() { $("#btn-dock").innerHTML = `<i class="ti ti-${S.prefs.dock ? "app-window" : "layout-sidebar-right"}"></i>`; $("#btn-dock").title = S.prefs.dock ? t("app.undock") : t("app.dock"); }
// 图片加载失败时换成图标（CSP 不允许内联 onerror）
document.addEventListener("error", e => {
  const el = e.target;
  if (el && el.tagName === "IMG" && el.dataset.fallback) el.replaceWith(Object.assign(document.createElement("i"), { className: "ti ti-" + el.dataset.fallback }));
}, true);
init();
