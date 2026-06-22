// Helper: load site/shared.js into a fresh JSDOM window and return the
// functions/constants it defines as globals.
//
// shared.js is a classic browser script (no exports). It declares the
// following names at script-evaluation time:
//   PRIMARY_LABEL, SOCIAL_AXES,
//   loadIndex, loadGame, parseSalesToM, bestSales, topbarNav, cardHTML
//
// JSDOM with runScripts:'dangerously' evaluates <script> tags in the page,
// and `const`/`function` declarations at the top level of those scripts are
// attached to the window's global record. We grab them off the window.

import { fileURLToPath } from 'node:url';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { JSDOM } from 'jsdom';

const HELPERS_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(HELPERS_DIR, '..', '..', '..');
const SHARED_JS = path.join(REPO_ROOT, 'site', 'shared.js');

/**
 * Load site/shared.js into a JSDOM window and return the named exports.
 * Optionally, a `fetchImpl` can be installed on the window before the script
 * runs (used by loader tests to stub fetch).
 *
 * @param {object} [opts]
 * @param {Function} [opts.fetchImpl]  function to use as window.fetch
 * @returns {Promise<{
 *   window: import('jsdom').DOMWindow,
 *   PRIMARY_LABEL: any,
 *   SOCIAL_AXES: any,
 *   parseSalesToM: Function,
 *   bestSales: Function,
 *   topbarNav: Function,
 *   cardHTML: Function,
 *   loadIndex: Function,
 *   loadGame: Function,
 * }>}
 */
export async function loadShared(opts = {}) {
  const source = await readFile(SHARED_JS, 'utf8');
  // Minimal HTML host; no external resources needed.
  const dom = new JSDOM('<!doctype html><html><head></head><body></body></html>', {
    runScripts: 'dangerously',
    pretendToBeVisual: true,
  });
  const win = dom.window;

  if (typeof opts.fetchImpl === 'function') {
    win.fetch = opts.fetchImpl;
  }

  // Evaluate shared.js in the JSDOM realm so its `const`/`function`
  // declarations end up on the window.
  //
  // Note: top-level `function` declarations in a classic script become
  // window properties, but top-level `const` declarations do NOT (they are
  // lexically scoped to the script). We append a trailer that copies the
  // const names onto window so tests can read them through the JSDOM realm.
  const trailer = `
;try { window.PRIMARY_LABEL = PRIMARY_LABEL; } catch (e) {}
;try { window.SOCIAL_AXES = SOCIAL_AXES; } catch (e) {}
`;
  const scriptEl = win.document.createElement('script');
  scriptEl.textContent = source + trailer;
  win.document.head.appendChild(scriptEl);

  return {
    window: win,
    PRIMARY_LABEL: win.PRIMARY_LABEL,
    SOCIAL_AXES: win.SOCIAL_AXES,
    parseSalesToM: win.parseSalesToM,
    bestSales: win.bestSales,
    topbarNav: win.topbarNav,
    cardHTML: win.cardHTML,
    loadIndex: win.loadIndex,
    loadGame: win.loadGame,
  };
}
