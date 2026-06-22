// Static checks against the repo-root /index.html, which is the Pages entry
// point. Confirms the meta-refresh redirect to site/facet.html exists and
// that a clickable fallback link is also present (for users with
// meta-refresh disabled).

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

import { REPO_ROOT } from '../helpers/dom.mjs';

const INDEX_PATH = path.join(REPO_ROOT, 'index.html');

describe('index.html (root) — redirect', () => {
  it('root_index_redirects_to_facet', async () => {
    const html = await readFile(INDEX_PATH, 'utf8');
    // Meta-refresh with site/facet.html target. Be tolerant of attribute
    // ordering and quote style.
    assert.match(
      html,
      /<meta\s+http-equiv=["']refresh["'][^>]*content=["'][^"']*site\/facet\.html[^"']*["']/i,
      'expected <meta http-equiv="refresh" content="...site/facet.html">',
    );
  });

  it('root_index_has_fallback_link', async () => {
    const html = await readFile(INDEX_PATH, 'utf8');
    assert.match(
      html,
      /<a\s+href=["']site\/facet\.html["'][^>]*>/i,
      'expected fallback <a href="site/facet.html">',
    );
  });
});
