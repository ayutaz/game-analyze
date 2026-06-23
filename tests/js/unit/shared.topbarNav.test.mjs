// Unit tests for site/shared.js → topbarNav(active)
//
// Renders the shared header used by both facet.html and detail.html. The
// `active` argument receives the page identifier; if it equals 'facet' the
// facet anchor gets the `active` CSS class.

import { test, describe, before } from 'node:test';
import assert from 'node:assert/strict';
import { loadShared } from '../helpers/shared.mjs';

let topbarNav;

before(async () => {
  ({ topbarNav } = await loadShared());
});

describe('topbarNav', () => {
  test('always_includes_title_link', () => {
    const html = topbarNav('');
    assert.ok(html.includes('<h1><a href="facet.html"'),
      `expected <h1><a href="facet.html" in output. Got:\n${html}`);
  });

  test('always_includes_github_link', () => {
    const html = topbarNav('facet');
    assert.ok(html.includes('href="https://github.com/ayutaz/game-analyze"'),
      `expected GitHub href. Got:\n${html}`);
    assert.ok(html.includes('target="_blank"'),
      `expected target="_blank" on the GitHub link. Got:\n${html}`);
  });

  test('marks_facet_active_when_arg_facet', () => {
    const html = topbarNav('facet');
    assert.ok(html.includes('class="active"'),
      `expected class="active" when active==='facet'. Got:\n${html}`);
    // And that active class is on the facet anchor, not the GitHub one.
    // We can identify by checking that the active class appears between the
    // facet anchor's `href="facet.html"` and the following closing `>`.
    const facetAnchorMatch = html.match(/<a href="facet\.html" class="([^"]*)"/);
    assert.ok(facetAnchorMatch, `expected facet nav anchor in output. Got:\n${html}`);
    assert.equal(facetAnchorMatch[1], 'active');
  });

  test('no_active_class_for_other_args', () => {
    for (const arg of ['detail', '', undefined]) {
      const html = topbarNav(arg);
      assert.ok(!html.includes('class="active"'),
        `did not expect class="active" for active=${JSON.stringify(arg)}. Got:\n${html}`);
    }
  });

  test('title_text_says_803', () => {
    const html = topbarNav('');
    assert.ok(html.includes('日本／世界のゲーム803本'),
      `expected "日本／世界のゲーム803本" in header. Got:\n${html}`);
  });
});
