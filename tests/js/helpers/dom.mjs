// Shared JSDOM bootstrap for UI tests.
//
// `loadPage(relativePath, query)` returns a Promise<JSDOM> whose window has:
//   * the requested HTML page loaded from site/<relativePath>
//   * runScripts: 'dangerously' + resources: 'usable' so <script src="shared.js">
//     and the inline IIFE in facet.html / detail.html actually execute
//   * a `fetch` polyfill installed on the window that resolves relative URLs
//     (e.g. '../data/index.json', `../data/games/${file}`) against the page's
//     file:// URL and reads from the local filesystem with Node's fs.promises
//
// `waitFor(predicate, timeoutMs)` polls until `predicate()` returns truthy or
// times out. Useful for waiting on the page's async IIFE to render cards.
//
// Both helpers are intentionally framework-agnostic so individual test files
// can opt into whichever shape (node:test, mocha, etc.) they prefer.

import { fileURLToPath, pathToFileURL, URL as NodeURL } from 'node:url';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { JSDOM } from 'jsdom';

const HELPERS_DIR = path.dirname(fileURLToPath(import.meta.url));
// tests/js/helpers -> repo root
export const REPO_ROOT = path.resolve(HELPERS_DIR, '..', '..', '..');
export const SITE_DIR = path.join(REPO_ROOT, 'site');

/**
 * Sleep for `ms` milliseconds. Promise-based.
 * @param {number} ms
 */
export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Poll `predicate` until it returns a truthy value or `timeoutMs` elapses.
 * Resolves with the truthy value, or rejects with a timeout Error.
 *
 * @template T
 * @param {() => (T | Promise<T>)} predicate
 * @param {number} [timeoutMs=2000]
 * @param {number} [intervalMs=20]
 * @returns {Promise<T>}
 */
export async function waitFor(predicate, timeoutMs = 2000, intervalMs = 20) {
  const start = Date.now();
  // First fast attempt before any waiting
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      const v = await predicate();
      if (v) return v;
    } catch {
      // swallow and retry until timeout
    }
    if (Date.now() - start >= timeoutMs) {
      throw new Error(`waitFor: timed out after ${timeoutMs}ms`);
    }
    await sleep(intervalMs);
  }
}

/**
 * Build a minimal Response-like object from a Buffer payload and content type.
 * Mirrors only the surface that shared.js / page scripts use:
 *   .ok, .status, .statusText, .url, .text(), .json()
 *
 * @param {Buffer} buffer
 * @param {string} url
 * @param {number} [status=200]
 * @param {string} [statusText='OK']
 */
function makeResponse(buffer, url, status = 200, statusText = 'OK') {
  const text = buffer.toString('utf8');
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText,
    url,
    async text() {
      return text;
    },
    async json() {
      return JSON.parse(text);
    },
  };
}

function makeErrorResponse(url, status, statusText) {
  return {
    ok: false,
    status,
    statusText,
    url,
    async text() {
      return '';
    },
    async json() {
      throw new Error(`No JSON body (status ${status})`);
    },
  };
}

/**
 * Install a `fetch` polyfill on the JSDOM window that resolves relative URLs
 * against the page's own document URL and reads matching files from disk.
 *
 * @param {import('jsdom').DOMWindow} win
 */
function installFetchPolyfill(win) {
  const baseHref = win.document.URL; // file:///.../site/facet.html?...

  async function localFetch(input /*, init */) {
    // Accept string, URL, or Request-like objects
    const raw =
      typeof input === 'string'
        ? input
        : input && typeof input.url === 'string'
        ? input.url
        : String(input);

    let resolved;
    try {
      resolved = new NodeURL(raw, baseHref);
    } catch (err) {
      throw new TypeError(`fetch polyfill: cannot resolve URL '${raw}' against '${baseHref}': ${err.message}`);
    }

    if (resolved.protocol !== 'file:') {
      // For tests we never want to hit the network. Surface a clear error.
      return makeErrorResponse(resolved.toString(), 599, `non-file URL blocked: ${resolved.protocol}`);
    }

    const fsPath = fileURLToPath(resolved);
    try {
      const buf = await readFile(fsPath);
      return makeResponse(buf, resolved.toString());
    } catch (err) {
      if (err && err.code === 'ENOENT') {
        return makeErrorResponse(resolved.toString(), 404, 'Not Found');
      }
      throw err;
    }
  }

  win.fetch = localFetch;
}

/**
 * Load an HTML page from the site/ directory under JSDOM.
 *
 * @param {string} relativePath  e.g. 'facet.html' or 'detail.html'
 * @param {string} [query='']    query string, with or without leading '?'
 * @param {object} [opts]
 * @param {boolean} [opts.waitForReady=true]  if true, await DOMContentLoaded
 * @returns {Promise<JSDOM>}
 */
export async function loadPage(relativePath, query = '', opts = {}) {
  const { waitForReady = true } = opts;

  const absHtml = path.join(SITE_DIR, relativePath);
  const html = await readFile(absHtml, 'utf8');

  const baseUrl = pathToFileURL(absHtml);
  if (query) {
    baseUrl.search = query.startsWith('?') ? query.slice(1) : query;
  }

  const dom = new JSDOM(html, {
    url: baseUrl.toString(),
    runScripts: 'dangerously',
    resources: 'usable',
    pretendToBeVisual: true,
  });

  installFetchPolyfill(dom.window);

  if (waitForReady) {
    await new Promise((resolve) => {
      const w = dom.window;
      if (w.document.readyState === 'complete') {
        resolve();
        return;
      }
      w.addEventListener('load', () => resolve(), { once: true });
    });
  }

  return dom;
}

/**
 * Convenience: wait until at least one ".card" (or supplied selector) has been
 * rendered into the document. Useful because the page scripts are async IIFEs
 * that resolve after `load`.
 *
 * @param {import('jsdom').DOMWindow} win
 * @param {string} [selector='.card']
 * @param {number} [timeoutMs=3000]
 */
export function waitForCards(win, selector = '.card', timeoutMs = 3000) {
  return waitFor(() => {
    const nodes = win.document.querySelectorAll(selector);
    return nodes.length > 0 ? nodes : null;
  }, timeoutMs);
}
