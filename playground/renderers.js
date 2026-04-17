// Renderers — UI output helpers for the doql playground.
//
// This module handles all DOM rendering: diagnostics, AST view, env display,
// file list, and HTML escaping.

"use strict";

/**
 * Escape HTML special characters to prevent XSS.
 * @param {string} s
 * @returns {string}
 */
export function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

/**
 * Render a fatal error message in the diagnostics panel.
 * @param {HTMLElement} $diagnostics
 * @param {string} msg
 */
export function renderFatal($diagnostics, msg) {
  $diagnostics.innerHTML =
    `<div class="diagnostic sev-error"><span class="sev">fatal</span><span class="loc">parser</span><span class="msg">${escapeHtml(msg)}</span></div>`;
}

/**
 * Render diagnostics list in the diagnostics panel.
 * @param {HTMLElement} $diagnostics
 * @param {Array} list
 */
export function renderDiagnostics($diagnostics, list) {
  if (!list.length) {
    $diagnostics.innerHTML = `<div class="no-diagnostics">✓ No issues detected.</div>`;
    return;
  }
  $diagnostics.innerHTML = list
    .map((d) => {
      const loc = d.line ? `${d.path} (line ${d.line})` : d.path;
      return `<div class="diagnostic sev-${d.severity}">` +
        `<span class="sev">${d.severity}</span>` +
        `<span class="loc">${escapeHtml(loc)}</span>` +
        `<span class="msg">${escapeHtml(d.message)}</span>` +
        `</div>`;
    })
    .join("");
}

/**
 * Render AST/spec view as formatted JSON.
 * @param {HTMLElement} $astView
 * @param {object|null} spec
 */
export function renderAst($astView, spec) {
  if (!spec) { $astView.textContent = ""; return; }
  $astView.textContent = JSON.stringify(spec, null, 2);
}

/**
 * Render environment variables display.
 * @param {HTMLElement} $envView
 * @param {object|null} envVars
 * @param {Array} envRefs
 */
export function renderEnv($envView, envVars, envRefs) {
  if (!envVars) { $envView.textContent = ""; return; }
  const refs = new Set(envRefs || []);
  const lines = [
    "# Playground .env (auto-seeded with localhost defaults)",
    "# Referenced by spec: " + (envRefs && envRefs.length ? envRefs.join(", ") : "(none)"),
    "",
  ];
  const keys = Object.keys(envVars).sort();
  for (const k of keys) {
    const marker = refs.has(k) ? "  # ← referenced via env." + k : "";
    lines.push(`${k}=${envVars[k]}${marker}`);
  }
  $envView.textContent = lines.join("\n");
}

/**
 * Render generated files list.
 * @param {HTMLElement} $filesList
 * @param {Array} files
 */
export function renderFiles($filesList, files) {
  if (!files.length) { $filesList.innerHTML = "<li><em>no files</em></li>"; return; }
  $filesList.innerHTML = files
    .map((f) => `<li><span class="path">${escapeHtml(f.path)}</span><span class="size">${f.size} B</span></li>`)
    .join("");
}
