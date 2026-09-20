/* convertmask web UI — no framework, no build step at runtime */

const METHODS = {
  mask2json: "mask images -> labelme JSON (needs masks)",
  mask2xml: "mask images -> VOC XML (needs masks)",
  json2mask: "labelme JSON -> mask images",
  json2xml: "labelme JSON -> VOC XML",
  xml2json: "VOC XML -> labelme JSON (needs images)",
  xml2yolo: "VOC XML -> YOLO txt",
  yolo2xml: "YOLO txt -> VOC XML (needs images + classes)",
  xml2mask: "VOC XML -> mask images",
};
const AUG_METHODS = ["flip", "rotation", "translation", "zoom", "noise", "crop",
  "distort", "inpaint", "perspective", "resize"];

const state = { session: null, files: null, previewPath: null };

const $ = (sel) => document.querySelector(sel);

// ---------------------------------------------------------------- helpers
async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return res.json();
}

function setStatus(text, kind = "info") {
  const el = $("#status");
  el.className = "text-sm rounded-lg px-3 py-2 " + (
    kind === "error" ? "bg-red-50 text-red-700"
    : kind === "ok" ? "bg-emerald-50 text-emerald-700"
    : "bg-slate-200 text-slate-700");
  el.textContent = text;
  el.classList.remove("hidden");
}

async function ensureSession() {
  if (state.session) return state.session;
  const { session } = await api("/api/session", { method: "POST" });
  state.session = session;
  return session;
}

// ---------------------------------------------------------------- upload
async function uploadFiles(fileList) {
  const session = await ensureSession();
  const asMask = $("#upload-as-mask").checked;
  const fd = new FormData();
  for (const f of fileList) fd.append("files", f);
  setStatus(`Uploading ${fileList.length} file(s)…`);
  try {
    const res = await api(`/api/upload/${session}${asMask ? "?as=mask" : ""}`, {
      method: "POST", body: fd,
    });
    setStatus(`Uploaded: ${res.images.length} image(s), ${res.masks.length} mask(s), ` +
      `${res.labels.length} label(s), ${res.classes.length} class file(s)`, "ok");
    await refreshFiles();
  } catch (e) {
    setStatus(e.message, "error");
  }
}

function initDropzone() {
  const dz = $("#dropzone"), input = $("#file-input");
  dz.addEventListener("click", () => input.click());
  input.addEventListener("change", () => uploadFiles([...input.files]));
  ["dragover", "dragenter"].forEach(ev => dz.addEventListener(ev, e => {
    e.preventDefault(); dz.classList.add("border-indigo-400", "bg-indigo-50");
  }));
  ["dragleave", "drop"].forEach(ev => dz.addEventListener(ev, e => {
    e.preventDefault(); dz.classList.remove("border-indigo-400", "bg-indigo-50");
  }));
  dz.addEventListener("drop", e => uploadFiles([...e.dataTransfer.files]));
}

// ---------------------------------------------------------------- file tree
async function refreshFiles() {
  if (!state.session) return;
  state.files = await api(`/api/files/${state.session}`);
  const tree = $("#file-tree");
  const groups = [["images", "Images"], ["masks", "Masks"], ["labels", "Labels"],
    ["classes", "Classes"], ["outputs", "Outputs"], ["analysis", "Analysis"]];
  tree.innerHTML = "";
  let any = false;
  for (const [key, title] of groups) {
    const items = state.files[key] || [];
    if (!items.length) continue;
    any = true;
    const div = document.createElement("div");
    const head = document.createElement("div");
    head.className = "font-medium text-slate-500 uppercase tracking-wide text-[10px] mb-1";
    head.textContent = `${title} (${items.length})`;
    div.appendChild(head);
    for (const path of items.slice(0, 50)) {
      const row = document.createElement("button");
      row.className = "block w-full text-left px-1.5 py-0.5 rounded hover:bg-slate-100 truncate" +
        (isImage(path) ? " text-indigo-700" : "");
      row.textContent = path;
      row.title = path;
      if (isImage(path)) row.addEventListener("click", () => setPreview(path));
      div.appendChild(row);
    }
    if (items.length > 50) {
      const more = document.createElement("div");
      more.className = "text-slate-400";
      more.textContent = `… ${items.length - 50} more`;
      div.appendChild(more);
    }
    tree.appendChild(div);
  }
  if (!any) tree.innerHTML = '<div class="text-slate-400">nothing uploaded yet</div>';
}

const isImage = (p) => /\.(jpe?g|png|bmp)$/i.test(p);

// ---------------------------------------------------------------- preview
async function setPreview(path) {
  state.previewPath = path;
  await drawPreview();
}

async function drawPreview() {
  const path = state.previewPath;
  const canvas = $("#preview-canvas");
  if (!path || !state.session) { canvas.width = 0; canvas.height = 0; return; }
  $("#preview-title").textContent = `Preview — ${path.split("/").pop()}`;

  const img = new Image();
  img.src = `/api/file/${state.session}?path=${encodeURIComponent(path)}`;
  await img.decode();

  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);

  if (!$("#overlay-toggle").checked) return;

  const shapes = await loadShapesFor(path);
  for (const s of shapes) {
    const color = colorFor(s.label);
    if (s.points.length > 2) {
      ctx.beginPath();
      s.points.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y));
      ctx.closePath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = color + "33";
      ctx.fill();
    } else if (s.points.length === 2) {
      const [[x1, y1], [x2, y2]] = s.points;
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(Math.min(x1, x2), Math.min(y1, y2), Math.abs(x2 - x1), Math.abs(y2 - y1));
    }
    const xs = s.points.map(p => p[0]), ys = s.points.map(p => p[1]);
    const tx = Math.min(...xs), ty = Math.max(...ys);
    ctx.font = "12px sans-serif";
    ctx.fillStyle = color;
    ctx.fillText(s.label, Math.max(0, tx), Math.max(10, Math.min(canvas.height, ty - 3)));
  }
}

async function loadShapesFor(imagePath) {
  if (!state.files) return [];
  const stem = imagePath.split("/").pop().replace(/\.[^.]+$/, "");
  const label = (state.files.labels || []).find(l =>
    l.split("/").pop().replace(/\.[^.]+$/, "") === stem);
  if (!label) return [];
  try {
    const url = `/api/file/${state.session}?path=${encodeURIComponent(label)}`;
    if (label.endsWith(".json")) {
      const data = await (await fetch(url)).json();
      return (data.shapes || []).map(s => ({ label: s.label, points: s.points }));
    }
    if (label.endsWith(".xml")) {
      const text = await (await fetch(url)).text();
      const doc = new DOMParser().parseFromString(text, "text/xml");
      const W = +doc.querySelector("size width")?.textContent || 1;
      const H = +doc.querySelector("size height")?.textContent || 1;
      return [...doc.querySelectorAll("object")].map(o => {
        const b = o.querySelector("bndbox");
        const xmin = +b.querySelector("xmin").textContent, ymin = +b.querySelector("ymin").textContent;
        const xmax = +b.querySelector("xmax").textContent, ymax = +b.querySelector("ymax").textContent;
        return { label: o.querySelector("name").textContent,
                 points: [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]] };
      });
    }
  } catch { /* label unreadable: preview without overlay */ }
  return [];
}

const PALETTE = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6",
  "#ec4899", "#14b8a6", "#f97316"];
function colorFor(label) {
  let h = 0;
  for (const c of label) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return PALETTE[h % PALETTE.length];
}

// ---------------------------------------------------------------- tabs
function initTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => {
      const active = b === btn;
      b.classList.toggle("border-indigo-500", active);
      b.classList.toggle("text-indigo-600", active);
      b.classList.toggle("border-transparent", !active);
      b.classList.toggle("text-slate-500", !active);
    });
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.add("hidden"));
    $(`#tab-${btn.dataset.tab}`).classList.remove("hidden");
  }));
}

// ---------------------------------------------------------------- convert
function initConvert() {
  const sel = $("#conv-method");
  for (const [method, hint] of Object.entries(METHODS)) {
    const opt = document.createElement("option");
    opt.value = method;
    opt.textContent = method;
    sel.appendChild(opt);
  }
  const hint = () => { $("#conv-hint").textContent = METHODS[sel.value]; };
  sel.addEventListener("change", hint);
  hint();

  $("#run-convert").addEventListener("click", async () => {
    const session = await ensureSession();
    const f = state.files || {};
    const req = {
      method: sel.value,
      imgs: (f.images || []).length ? "imgs" : undefined,
      masks: (f.masks || []).length ? "masks" : undefined,
      jsons: "labels", xmls: "labels", txts: "labels",
      classes: (f.classes || [])[0],
    };
    setStatus("Converting…");
    try {
      const res = await api(`/api/convert/${session}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      setStatus(`Conversion done: ${res.outputs.length} file(s)`, "ok");
      await refreshFiles();
    } catch (e) {
      setStatus(e.message, "error");
    }
  });
}

// ---------------------------------------------------------------- augment
function initAugment() {
  const box = $("#aug-methods");
  for (const m of AUG_METHODS) {
    const label = document.createElement("label");
    label.className = "flex items-center gap-1.5";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.value = m;
    if (["flip", "rotation", "noise"].includes(m)) cb.checked = true;
    label.append(cb, document.createTextNode(m));
    box.appendChild(label);
  }
  $("#run-augment").addEventListener("click", async () => {
    const session = await ensureSession();
    const methods = [...box.querySelectorAll("input:checked")].map(i => i.value);
    const seedVal = $("#aug-seed").value;
    const body = {
      imgs: "imgs",
      labels: (state.files?.labels || []).length ? "labels" : null,
      methods,
      number: +$("#aug-number").value || 1,
      seed: seedVal === "" ? null : +seedVal,
      save_mask: $("#aug-mask").checked,
    };
    setStatus("Augmenting…");
    try {
      const res = await api(`/api/augment/${session}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setStatus(`Augmentation done: ${res.outputs.length} file(s)`, "ok");
      await refreshFiles();
    } catch (e) {
      setStatus(e.message, "error");
    }
  });
}

// ---------------------------------------------------------------- analyze
function initAnalyze() {
  $("#run-analyze").addEventListener("click", async () => {
    const session = await ensureSession();
    setStatus("Analyzing…");
    try {
      const report = await api(`/api/analyze/${session}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          annos: "labels",
          imgs: (state.files?.images || []).length ? "imgs" : null,
          classes: (state.files?.classes || [])[0],
        }),
      });
      setStatus("Analysis ready", "ok");
      renderReport(report);
      await refreshFiles();
    } catch (e) {
      setStatus(e.message, "error");
    }
  });
}

function renderReport(report) {
  const panel = $("#report-panel");
  panel.classList.remove("hidden");
  const s = report.summary;
  const maxCount = Math.max(1, ...Object.values(s.class_distribution || {}));

  const chip = (val, label, cls) =>
    `<div class="rounded-lg px-3 py-2 text-center ${cls}">
       <div class="text-xl font-semibold">${val}</div>
       <div class="text-[11px] opacity-70">${label}</div></div>`;

  let html = `<div class="px-4 py-3 border-b border-slate-100 text-sm font-medium">Analysis report</div>
    <div class="grid grid-cols-4 gap-3 p-4">
      ${chip(s.annotations, "annotations", "bg-slate-100")}
      ${chip(s.images, "images", "bg-slate-100")}
      ${chip(s.errors, "errors", s.errors ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700")}
      ${chip(s.warnings, "warnings", s.warnings ? "bg-amber-100 text-amber-700" : "bg-slate-100")}
    </div>`;

  if (Object.keys(s.class_distribution || {}).length) {
    html += `<div class="px-4 pb-3"><div class="text-xs font-medium text-slate-500 uppercase mb-2">Class distribution</div>`;
    for (const [name, count] of Object.entries(s.class_distribution)) {
      html += `<div class="flex items-center gap-2 text-xs mb-1">
        <span class="w-24 truncate" title="${name}">${name}</span>
        <div class="flex-1 h-3 bg-slate-100 rounded">
          <div class="h-3 bg-indigo-400 rounded" style="width:${100 * count / maxCount}%"></div>
        </div>
        <span class="w-8 text-right">${count}</span></div>`;
    }
    html += `</div>`;
  }

  const filesWithIssues = report.files.filter(f => f.issues.length);
  if (filesWithIssues.length) {
    html += `<div class="px-4 pb-4"><div class="text-xs font-medium text-slate-500 uppercase mb-2">Issues</div>
      <div class="overflow-auto max-h-64 border border-slate-100 rounded-lg text-xs">`;
    html += `<table class="w-full"><thead class="bg-slate-50 text-left">
      <tr><th class="px-2 py-1">file</th><th class="px-2 py-1">severity</th>
      <th class="px-2 py-1">code</th><th class="px-2 py-1">detail</th></tr></thead><tbody>`;
    for (const f of filesWithIssues) {
      for (const i of f.issues) {
        html += `<tr class="border-t border-slate-100">
          <td class="px-2 py-1 truncate max-w-[12rem]" title="${f.file}">${f.file}</td>
          <td class="px-2 py-1 ${i.severity === "error" ? "text-red-600" : "text-amber-600"}">${i.severity}</td>
          <td class="px-2 py-1">${i.code}</td>
          <td class="px-2 py-1 text-slate-500">${i.detail}</td></tr>`;
      }
    }
    html += `</tbody></table></div></div>`;
  }
  panel.innerHTML = html;
}

// ---------------------------------------------------------------- misc
function initDownloads() {
  document.querySelectorAll(".dl-btn").forEach(btn => btn.addEventListener("click", () => {
    if (!state.session) return setStatus("upload something first", "error");
    window.location.href = `/api/download/${state.session}?which=${btn.dataset.dl}`;
  }));
}

document.addEventListener("DOMContentLoaded", () => {
  initDropzone();
  initTabs();
  initConvert();
  initAugment();
  initAnalyze();
  initDownloads();
  $("#refresh-files").addEventListener("click", refreshFiles);
  $("#overlay-toggle").addEventListener("change", drawPreview);
});
