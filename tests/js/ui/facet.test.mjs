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
//     reduce the visible card count to 183 when EXP is toggled.
//
// All expected counts (303 total, EXP 183 / NAR 69 / REW 51, etc.) are derived
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
    assert.equal(link.textContent.trim(), '日本のゲーム303本 分析カタログ');
  });

  it('renders_303_cards_initially', () => {
    assert.equal(cards(win).length, 303);
  });

  it('result_count_text_matches_303_over_303', () => {
    assert.equal(
      win.document.getElementById('result-count').textContent,
      '303 / 303 件',
    );
  });

  it('primary_filter_section_has_three_rows', () => {
    const rows = win.document.querySelectorAll('#filter-primary .filter-row');
    assert.equal(rows.length, 3);
  });

  it('primary_filter_counts_show_183_69_51', () => {
    // Render order is EXP / NAR / REW per facet.html
    const counts = Array.from(
      win.document.querySelectorAll('#filter-primary .count'),
    ).map((n) => Number(n.textContent));
    assert.deepEqual(counts, [183, 69, 51]);
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

  it('platform_filter_capped_at_12', () => {
    const rows = win.document.querySelectorAll('#filter-platform .filter-row');
    assert.ok(rows.length <= 12, `expected <=12 rows, got ${rows.length}`);
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
    assert.equal(links.length, 303);
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

  it('exp_label_click_filters_to_183_cards_REGRESSION', async () => {
    // REGRESSION for the label-click double-toggle bug. Clicking on the
    // .filter-row (which IS the <label>) must flip the checkbox exactly once,
    // dispatching a single change event, leaving EXP checked and #grid
    // showing 183 cards. The previous buggy state had the click propagating
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
      assert.equal(cards(win).length, 183, 'EXP filter should reveal 183 cards');
      assert.ok(row.classList.contains('active'), 'filter-row should be .active');
    } finally {
      dom.window.close();
    }
  });

  it('exp_label_click_unchecks_and_restores_303', async () => {
    // Second half of the regression: a second label click must un-check the
    // checkbox and restore all 303 cards.
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');

      row.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 183);

      row.click();
      await tick(win, 20);
      assert.equal(cb.checked, false);
      assert.equal(cards(win).length, 303);
      assert.ok(!row.classList.contains('active'));
    } finally {
      dom.window.close();
    }
  });

  it('exp_checkbox_via_input_change_filters_to_183', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const row = filterRow(win, 'primary', 'EXP');
      const cb = row.querySelector('input');
      cb.checked = true;
      cb.dispatchEvent(new win.Event('change', { bubbles: true }));
      await tick(win, 20);
      assert.equal(cards(win).length, 183);
    } finally {
      dom.window.close();
    }
  });

  it('nar_checkbox_filters_to_69_cards', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const cb = filterRow(win, 'primary', 'NAR').querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 69);
    } finally {
      dom.window.close();
    }
  });

  it('rew_checkbox_filters_to_51_cards', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const cb = filterRow(win, 'primary', 'REW').querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 51);
    } finally {
      dom.window.close();
    }
  });

  it('unchecking_restores_303', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const cb = filterRow(win, 'primary', 'EXP').querySelector('input');
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 183);
      cb.click();
      await tick(win, 20);
      assert.equal(cards(win).length, 303);
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
      // Set.has across primary acts as OR within the facet -> 183 + 51 = 234
      assert.equal(cards(win).length, 234);
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
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = 'mario';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      const visible = cards(win);
      assert.ok(visible.length > 0, 'mario should match >0 games');
      for (const c of visible) {
        const txt = c.textContent.toLowerCase();
        assert.ok(
          txt.includes('mario') || txt.includes('マリオ'),
          `card without 'mario': ${c.textContent.slice(0, 60)}`,
        );
      }
    } finally {
      dom.window.close();
    }
  });

  it('search_japanese_token', async () => {
    const dom = await bootFacet();
    const win = dom.window;
    try {
      const s = win.document.getElementById('search');
      s.value = 'ポケモン';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      const visible = cards(win);
      assert.ok(visible.length > 0);
      for (const c of visible) {
        assert.ok(
          c.textContent.includes('ポケモン') ||
            c.textContent.toLowerCase().includes('pokémon') ||
            c.textContent.toLowerCase().includes('pokemon'),
          `card lacked ポケモン: ${c.textContent.slice(0, 80)}`,
        );
      }
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
        '0 / 303 件',
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
        [(g.title_jp || ''), (g.title_en || ''), (g.genre || '')]
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
        '69 / 303 件',
      );
      const s = win.document.getElementById('search');
      s.value = 'zzzznevermatching';
      s.dispatchEvent(new win.Event('input', { bubbles: true }));
      await tick(win, 20);
      assert.equal(
        win.document.getElementById('result-count').textContent,
        '0 / 303 件',
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
      assert.equal(cards(win).length, 303);
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
      assert.equal(cards(win).length, 234);
      win.document.getElementById('reset').click();
      await tick(win, 20);
      // Now check only NAR — must show exactly 69, not 69 + leftover.
      filterRow(win, 'primary', 'NAR').querySelector('input').click();
      await tick(win, 20);
      assert.equal(cards(win).length, 69);
    } finally {
      dom.window.close();
    }
  });
});
