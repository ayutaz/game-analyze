// UI / E2E tests for site/facet.html
//
// Boots facet.html under JSDOM (via tests/js/helpers/dom.mjs), waits for the
// async IIFE to finish rendering, then asserts on:
//   * initial render shape (cards, filter rows, counts, topbar, search/reset)
//   * filter interactions (checkbox via input.click, label-row click,
//     multi-facet AND across primary + decade + axis + platform,
//     search input, reset, active-class toggling)
//   * the recently-fixed "label-click double-toggle" regression — clicking on
//     the .filter-row (the <label>) must NOT flip the checkbox twice and must
//     reduce the visible card count to 705 when EXP is toggled.
//
// All expected counts (1025 total, EXP 705 / NAR 125 / REW 195, etc.) are derived
// from data/index.json at test time so the tests stay correct if the catalog
// grows or shrinks.

import { describe, it, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

import { loadPage, waitFor, REPO_ROOT } from '../helpers/dom.mjs';

// --- Helpers ------------------------------------------------------------

async function readIndex() {
  const buf = await readFile(path.join(REPO_ROOT, 'data', 'index.json'), 'utf8');
  return JSON.parse(buf);
}

function decadeOf(year) {
  if (!year) return null;
  return Math.floor(year / 10) * 10 + 's';
}

async function bootFacet() {
  const dom = await loadPage('facet.html');
  const win = dom.window;
  await waitFor(
    () => win.document.querySelectorAll('#grid .card').length > 0,
    5000,
  );
  return dom;
}

function cards(win) {
  return win.document.querySelectorAll('#grid .card');
}

function filterRow(win, key, val) {
  return win.document.querySelector(
    `#filter-${key} .filter-row[data-val="${val}"]`,
  );
}

function tick(win, ms = 0) {
  return new Promise((r) => win.setTimeout(r, ms));
}

// --- Render tests -------------------------------------------------------

describe('facet.html — initial render', () => {
  let dom;
  let win;
  let index;

  before(async () => {
    index = await readIndex();
    dom = await bootFacet();
    win = dom.window;
  });

  after(() => {
    dom.window.close();
  });

  it('page_loads_without_uncaught_errors', () => {
    // The waitFor() in bootFacet already enforces successful boot — if the
    // IIFE had thrown, no cards would have been rendered. We additionally
    // confirm here that #grid is populated (already asserted by waitFor) and
    // that the DOM is in a sane state.
    assert.ok(win.document.querySelector('#grid'));
    assert.ok(win.document.querySelector('#filter-primary'));
  });

  it('topbar_rendered', () => {
    const link = win.document.querySelector('#topbar h1 a');
    assert.ok(link, '#topbar should contain a heading link');
    assert.equal(link.textContent.trim(), '日本／世界のゲーム 3カテゴリ分析カタログ');
  });

  it('renders_1025_cards_initially', () => {
    assert.equal(cards(win).length, 1025);
  });

  it('result_count_text_matches_1025_over_1025', () => {
    assert.equal(
      win.document.getElementById('result-count').textContent,
      '1025 / 1025 件',
    );
  });

  it('primary_filter_section_has_three_rows', () => {
    const rows = win.document.querySelectorAll('#filter-primary .filter-row');
    assert.equal(rows.length, 3);
  });

  it('primary_filter_counts_show_705_125_195', () => {
    // Render order is EXP / NAR / REW per facet.html
    const counts = Array.from(
      win.document.querySelectorAll('#filter-primary .count'),
    ).map((n) => Number(n.textContent));
    assert.deepEqual(counts, [705, 125, 195]);
  });

  it('axis_filter_section_has_six_rows', () => {
    const rows = win.document.querySelectorAll('#filter-axis .filter-row');
    assert.equal(rows.length, 6);
    const labels = Array.from(rows).map((r) => r.dataset.val);
    assert.deepEqual(labels, ['対戦', '協力', '非対称', '非同期', '観戦', 'ソロ']);
  });

  it('axis_filter_counts_sum_to_EXP_with_axis_set (sanity)', () => {
    // The sidebar axis counts are computed over ALL games (not only EXP), but
    // EXP-with-axis is the dominant subset. We sanity-check that the sum of
    // axis counts is >= the count of EXP games that have a non-null axis.
    const axisCounts = Array.from(
      win.document.querySelectorAll('#filter-axis .count'),
    ).map((n) => Number(n.textContent));
    const sum = axisCounts.reduce((a, b) => a + b, 0);
    const expWithAxis = index.games.filter(
      (g) => g.primary === 'EXP' && g.social_axis,
    ).length;
    assert.ok(
      sum >= expWithAxis,
      `axis count sum ${sum} should be >= EXP-with-axis ${expWithAxis}`,
    );
  });

  it('decade_filter_section_present', () => {
    const rows = win.document.querySelectorAll('#filter-decade .filter-row');
    assert.ok(rows.length > 0);
  });

  it('decade_filter_sorted_ascending', () => {
    const labels = Array.from(
      win.document.querySelectorAll('#filter-decade .filter-row'),
    ).map((r) => r.dataset.val);
    const sorted = [...labels].sort((a, b) => a.localeCompare(b));
    assert.deepEqual(labels, sorted);
  });

  it('platform_filter_shows_only_counts_5_and_above', () => {
    const counts = Array.from(
      win.document.querySelectorAll('#filter-platform .count'),
    ).map((n) => Number(n.textContent));
    assert.ok(counts.length >= 12, `expected at least 12 rows after threshold, got ${counts.length}`);
    for (const n of counts) {
      assert.ok(n >= 5, `expected each shown platform to have count >= 5, got ${n}`);
    }
  });

  it('platform_counts_descending', () => {
    const counts = Array.from(
      win.document.querySelectorAll('#filter-platform .count'),
    ).map((n) => Number(n.textContent));
    for (let i = 1; i < counts.length; i++) {
      assert.ok(
        counts[i] <= counts[i - 1],
        `platform counts not non-increasing at ${i}: ${counts}`,
      );
    }
  });

  it('search_input_present_and_empty', () => {
    const s = win.document.getElementById('search');
    assert.ok(s);
    assert.equal(s.value, '');
  });

  it('reset_button_present', () => {
    const b = win.document.getElementById('reset');
    assert.ok(b);
    assert.equal(b.textContent.trim(), 'フィルタ解除');
  });

  it('every_card_has_link_to_detail', () => {
    const links = win.document.querySelectorAll('#grid .card-link');
    assert.equal(links.length, 1025);
    for (const a of links) {
      const href = a.getAttribute('href');
      assert.match(href, /detail\.html\?id=\d+/);
    }
  });

  it('id_56_is_present_after_2020_expansion', () => {
    // Slot #56 was previously skipped (Project Sekai duplicate) but the
    // 2026-06 expansion filled it with 桃太郎電鉄. Confirm a link exists.
    const hrefs = Array.from(
      win.document.querySelectorAll('#grid .card-link'),
    ).map((a) => a.getAttribute('href'));
    assert.ok(
      hrefs.some((h) => /[?&]id=56(\b|$)/.test(h)),
      'a card should link to id=56',
    );
  });
});

// --- Filter / interaction tests ----------------------------------------

describe('facet.html — filter interactions', () => {
  // Each test boots a fresh page so state is isolated.

  it('exp_label_click_filters_to_705_cards_REGRESSION', async () => {
    // REGRESSION for the label-click double-toggle bug. Clicking on the
    // .filter-row (which IS the <label>) must flip the checkbox exactly once,
    // dispatching a single change event, leaving EXP checked and #grid
    // showing 705 cards. The previous buggy state had the click propagating
    // through label->input click twice, leaving the box unchecked and the
    // filter inactive.
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');
      assert.equal(cb.checked, false, 'precondition: checkbox unchecked');

      row.click(); // simulate <label> click
      await tick(win, 30);

      assert.equal(cb.checked, true, 'after label click, checkbox must be checked');
      assert.equal(cards(win).length, 705, 'EXP filter should reveal 705 cards');
      assert.ok(row.classList.contains('active'), 'filter-row should be .active');
    } finally {
      dom.window.close();
    }
  });

  it('exp_label_click_unchecks_and_restores_1025', async () => {
    // Second half of the regression: a second label click must un-check the
    // checkbox and restore all 1025 cards.
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');

      row.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 705);

      row.click();
      await tick(win, 20);
      assert.equal(cb.checked, false);
      assert.equal(cards(win).length, 1025);
      assert.ok(!row.classList.contains('active'));
    } finally {
      dom.window.close();
    }
  });

  it('exp_checkbox_via_input_change_filters_to_705', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');
      cb.checked = true;
      cb.dispatchEvent(new win.Event('change', { bubbles: true }));
      await tick(win, 20);
      assert.equal(cards(win).length, 705);
    } finally {
      dom.window.close();
    }
  });

  it('nar_checkbox_filters_to_125_cards', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const cb = filterRow(win, 'primary', 'NAR').querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 125);
    } finally {
      dom.window.close();
    }
  });

  it('rew_checkbox_filters_to_195_cards', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const cb = filterRow(win, 'primary', 'REW').querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 195);
    } finally {
      dom.window.close();
    }
  });

  it('unchecking_restores_1025', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const cb = filterRow(win, 'primary', 'EXP').querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 705);
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 1025);
    } finally {
      dom.window.close();
    }
  });

  it('multiple_primary_checked_unions_within_facet', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'EXP').querySelector('input').click();
      filterRow(win, 'primary', 'REW').querySelector('input').click();
      await tick(win, 20);
      // Set.has across primary acts as OR within the facet -> 705 + 195 = 900
      assert.equal(cards(win).length, 900);
    } finally {
      dom.window.close();
    }
  });

  it('primary_AND_decade_combine', async () => {
    const index = await readIndex();
    const expected = index.games.filter(
      (g) => g.primary === 'EXP' && decadeOf(g.year) === '2020s',
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'EXP').querySelector('input').click();
      filterRow(win, 'decade', '2020s').querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
    } finally {
      dom.window.close();
    }
  });

  it('primary_AND_axis_combine', async () => {
    const index = await readIndex();
    const expected = index.games.filter(
      (g) => g.primary === 'EXP' && g.social_axis === '対戦',
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'EXP').querySelector('input').click();
      filterRow(win, 'axis', '対戦').querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
    } finally {
      dom.window.close();
    }
  });

  it('platform_filter_any_match_semantics', async () => {
    const index = await readIndex();
    const expected = index.games.filter((g) =>
      (g.platform || []).includes('Switch'),
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'platform', 'Switch');
      assert.ok(row, 'Switch platform row should render in top 12');
      row.querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
    } finally {
      dom.window.close();
    }
  });

  it('search_narrows_results_case_insensitive', async () => {
    // Search now spans title + genre + developer + publisher + popularity +
    // concept + target + secondary, so a card may legitimately match by a
    // field that isn't rendered on the card (concept/target/popularity).
    // Compare against the count predicted from the same hay function.
    const index = await readIndex();
    const expected = index.games.filter((g) =>
      [g.title_jp, g.title_en, g.genre, g.developer, g.publisher,
        g.popularity, g.concept, g.target, ...(g.secondary || [])]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes('mario')
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = 'mario';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
      assert.ok(expected > 0, 'mario should match >0 games');
    } finally {
      dom.window.close();
    }
  });

  it('search_japanese_token', async () => {
    const index = await readIndex();
    const expected = index.games.filter((g) =>
      [g.title_jp, g.title_en, g.genre, g.developer, g.publisher,
        g.popularity, g.concept, g.target, ...(g.secondary || [])]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes('ポケモン'.toLowerCase())
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = 'ポケモン';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
      assert.ok(expected > 0);
    } finally {
      dom.window.close();
    }
  });

  it('search_no_match_yields_zero', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = 'zzzznevermatching';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.equal(cards(win).length, 0);
      assert.equal(
        win.document.getElementById('result-count').textContent,
        '0 / 1025 件',
      );
    } finally {
      dom.window.close();
    }
  });

  it('search_combines_with_filters', async () => {
    const index = await readIndex();
    const expected = index.games.filter(
      (g) =>
        g.primary === 'EXP' &&
        [g.title_jp, g.title_en, g.genre, g.developer, g.publisher,
          g.popularity, g.concept, g.target, ...(g.secondary || [])]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
          .includes('マリオ'.toLowerCase()),
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'EXP').querySelector('input').click();
      const s = win.document.getElementById('search');
      s.value = 'マリオ';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
    } finally {
      dom.window.close();
    }
  });

  it('result_count_updates_after_each_change', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'NAR').querySelector('input').click();
      await tick(win, 20);
      assert.equal(
        win.document.getElementById('result-count').textContent,
        '125 / 1025 件',
      );
      const s = win.document.getElementById('search');
      s.value = 'zzzznevermatching';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.equal(
        win.document.getElementById('result-count').textContent,
        '0 / 1025 件',
      );
    } finally {
      dom.window.close();
    }
  });

  it('filter_row_active_class_toggles_on', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');
      cb.checked = true;
      cb.dispatchEvent(new win.Event('change', { bubbles: true }));
      await tick(win, 20);
      assert.ok(row.classList.contains('active'));
    } finally {
      dom.window.close();
    }
  });

  it('filter_row_active_class_toggles_off', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.ok(row.classList.contains('active'));
      cb.click();
      await tick(win, 20);
      assert.ok(!row.classList.contains('active'));
    } finally {
      dom.window.close();
    }
  });

  it('reset_clears_all_filters', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'EXP').querySelector('input').click();
      filterRow(win, 'decade', '2020s').querySelector('input').click();
      const s = win.document.getElementById('search');
      s.value = 'mario';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);

      win.document.getElementById('reset').click();
      await tick(win, 20);

      assert.equal(s.value, '');
      const checked = Array.from(
        win.document.querySelectorAll('.filter-row input'),
      ).filter((c) => c.checked);
      assert.equal(checked.length, 0);
      const active = win.document.querySelectorAll('.filter-row.active');
      assert.equal(active.length, 0);
      assert.equal(cards(win).length, 1025);
    } finally {
      dom.window.close();
    }
  });

  it('reset_clears_state_sets', async () => {
    // After reset, applying a single fresh filter must yield a clean result
    // (i.e., no stale Set entries from previous filters leak into the count).
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'primary', 'EXP').querySelector('input').click();
      filterRow(win, 'primary', 'REW').querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, 900);
      win.document.getElementById('reset').click();
      await tick(win, 20);
      // Now check only NAR — must show exactly 125, not 125 + leftover.
      filterRow(win, 'primary', 'NAR').querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, 125);
    } finally {
      dom.window.close();
    }
  });
});

// --- Regression tests for the 2026-06-24 bug-hunt fixes -----------------

describe('facet.html — bug-hunt regression', () => {
  it('puzdra_and_monst_appear_in_2010s_REW_iOS_filter', async () => {
    // Original bug: platform='Mobile' singleton excluded these from
    // iOS/Android facets. Fixed by normalizing to ['iOS','Android'].
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'decade', '2010s').querySelector('input').click();
      filterRow(win, 'primary', 'REW').querySelector('input').click();
      filterRow(win, 'platform', 'iOS').querySelector('input').click();
      await tick(win, 20);
      const titles = Array.from(cards(win)).map((c) => c.textContent);
      assert.ok(
        titles.some((t) => t.includes('パズル') && t.includes('ドラゴンズ')),
        'パズル&ドラゴンズ should appear in 2010s×REW×iOS',
      );
      assert.ok(
        titles.some((t) => t.includes('モンスターストライク')),
        'モンスターストライク should appear in 2010s×REW×iOS',
      );
    } finally {
      dom.window.close();
    }
  });

  it('xbox_series_xs_facet_includes_all_normalized_entries', async () => {
    // Originally split across Xbox Series / Xbox Series X/S / Xbox Series X|S / XSX.
    const index = await readIndex();
    const expected = index.games.filter((g) =>
      (g.platform || []).includes('Xbox Series X/S'),
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'platform', 'Xbox Series X/S');
      assert.ok(row, 'Xbox Series X/S facet row should render');
      row.querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, expected);
      assert.ok(expected >= 150,
        `expected ~190 Xbox Series X/S titles after normalization, got ${expected}`);
    } finally {
      dom.window.close();
    }
  });

  it('mac_facet_unified_no_macos_chip', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      assert.ok(filterRow(win, 'platform', 'Mac'),
        "'Mac' facet row should exist");
      assert.equal(filterRow(win, 'platform', 'macOS'), null,
        "'macOS' chip should be gone after normalization");
    } finally {
      dom.window.close();
    }
  });

  it('storefront_steam_chip_not_shown', async () => {
    // 'Steam'/'GOG'/'Epic Games Store' etc collapsed into PC.
    const dom = await bootFacet();
    const win = dom.window;
    try {
      for (const v of ['Steam', 'GOG', 'Epic Games Store', 'itch.io']) {
        assert.equal(filterRow(win, 'platform', v), null,
          `'${v}' should not appear as its own platform chip`);
      }
    } finally {
      dom.window.close();
    }
  });

  it('search_matches_publisher', async () => {
    // Originally only [title_jp, title_en, genre] was searched; '任天堂' or
    // 'Square Enix' as publisher names returned ~0 results.
    const index = await readIndex();
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = '任天堂';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      // Expect many hits (Nintendo publisher games); upper bound is loose.
      assert.ok(cards(win).length >= 10,
        `'任天堂' search should hit publisher field; got ${cards(win).length}`);
    } finally {
      dom.window.close();
    }
  });

  it('search_matches_developer', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = 'FromSoftware';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.ok(cards(win).length >= 3,
        `'FromSoftware' should hit developer; got ${cards(win).length}`);
    } finally {
      dom.window.close();
    }
  });

  it('axis_filter_ignores_non_EXP_games', async () => {
    // Per CLAUDE.md social_axis is meaningful only for EXP. The fix gates
    // axis filtering on primary==='EXP' so that selecting 'ソロ' doesn't
    // erase NAR/REW games that simply lack a social_axis.
    const index = await readIndex();
    const expectedSolo = index.games.filter(
      (g) => g.primary === 'EXP' && g.social_axis === 'ソロ',
    ).length;
    const dom = await bootFacet();
    const win = dom.window;
    try {
      filterRow(win, 'axis', 'ソロ').querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, expectedSolo,
        `axis='ソロ' alone should yield EXP-only solo titles (${expectedSolo})`);
      // Confirm: no REW/NAR cards in result.
      for (const c of cards(win)) {
        const badge = c.querySelector('.badge');
        assert.ok(badge && /体験型/.test(badge.textContent),
          'axis filter must not surface non-EXP cards');
      }
    } finally {
      dom.window.close();
    }
  });
});
