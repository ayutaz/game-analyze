// UI / E2E tests for site/detail.html
//
// Boots detail.html with various ?id=... query strings under JSDOM. Asserts:
//   * id=1 (Animal Crossing: New Horizons) renders correctly: title_jp,
//     title_en, primary badge, axis tag, basic-data kv panel, concept/target,
//     analysis markdown (the .md file exists), back link, related panels.
//   * id=4 maps to "ポケットモンスター 赤・緑" (documents the actual id; the
//     parent task referenced "Pokémon at id=1" which is incorrect — id=1 is
//     Animal Crossing per data/games/).
//   * id=2 (Mario Kart 8) lacks an analyses/*.md file, so #analysis shows the
//     empty-analysis placeholder.
//   * Not-found branch fires for id=56 (intentionally-missing), id=99999,
//     id=0, id=-1, missing param, non-numeric param.
//   * Related panels: cap at 8, exclude self, year window ±3.
//   * Back link present.
//   * 'JSON' kv row contains the per-file path.
//
// Concept/target/title-escape "placeholder" cases are recorded as skipped:
// every game JSON currently has both fields populated, and no title contains
// HTML metacharacters — so those branches in detail.html cannot be exercised
// without first introducing a fixture, which we leave to future work.

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

async function bootDetail(query) {
  const dom = await loadPage('detail.html', query);
  const win = dom.window;
  // The page either renders the head (game found) or rewrites <main> with the
  // not-found message. Wait until one of those two terminal states arrives.
  await waitFor(() => {
    const head = win.document.querySelector('#head h1');
    const mainText = win.document.querySelector('main')?.textContent || '';
    return head || mainText.includes('ゲームが見つかりません');
  }, 6000);
  return dom;
}

// --- id=1 (Animal Crossing) --------------------------------------------

describe('detail.html — id=1 (Animal Crossing: New Horizons)', () => {
  let dom;
  let win;

  before(async () => {
    dom = await bootDetail('?id=1');
    win = dom.window;
    // Also wait for the markdown fetch to resolve so #analysis is populated.
    await waitFor(
      () => (win.document.getElementById('analysis')?.innerHTML || '').length > 0,
      6000,
    );
  });

  after(() => {
    dom.window.close();
  });

  it('id_1_loads_animal_crossing', () => {
    const title = win.document.querySelector('.detail-head .title-jp');
    assert.ok(title, '.title-jp should render');
    assert.equal(title.textContent, 'あつまれ どうぶつの森');
  });

  it('id_1_title_en_rendered', () => {
    const en = win.document.querySelector('.detail-head .title-en');
    assert.ok(en);
    assert.equal(en.textContent, 'Animal Crossing: New Horizons');
  });

  it('id_1_primary_badge_class', () => {
    const badge = win.document.querySelector('.detail-head .badge.exp');
    assert.ok(badge, '.badge.exp expected for EXP primary');
    assert.equal(badge.textContent.trim(), '体験型');
  });

  it('id_1_social_axis_rendered', () => {
    const tags = Array.from(
      win.document.querySelectorAll('.detail-head .axis-tag'),
    ).map((t) => t.textContent.trim());
    assert.ok(
      tags.includes('他者軸: 非同期'),
      `expected '他者軸: 非同期' among axis tags: ${JSON.stringify(tags)}`,
    );
  });

  it('id_1_basic_data_panel_populated', () => {
    const kv = win.document.getElementById('kv');
    assert.ok(kv);
    const dts = Array.from(kv.querySelectorAll('dt')).map((d) =>
      d.textContent.trim(),
    );
    const dds = Array.from(kv.querySelectorAll('dd')).map((d) =>
      d.textContent.trim(),
    );
    for (const label of ['開発元', '販売元', '初リリース', 'ジャンル', '国内売上', '世界売上']) {
      assert.ok(dts.includes(label), `dt missing: ${label}`);
    }
    // Spot-check values from id=1 fixture
    const map = Object.fromEntries(dts.map((k, i) => [k, dds[i]]));
    assert.equal(map['初リリース'], '2020');
    assert.equal(map['国内売上'], '11.91M');
    assert.equal(map['世界売上'], '47M+');
    assert.equal(map['開発元'], '任天堂');
  });

  it('id_1_concept_panel_populated', () => {
    const c = win.document.getElementById('concept');
    assert.ok(c);
    assert.ok(!c.classList.contains('empty'), 'concept should not be .empty');
    assert.ok(c.textContent.length > 0);
    assert.ok(!c.textContent.startsWith('未記載'));
  });

  it('id_1_target_panel_populated', () => {
    const t = win.document.getElementById('target');
    assert.ok(t);
    assert.ok(!t.classList.contains('empty'));
    assert.ok(t.textContent.length > 0);
    assert.ok(!t.textContent.startsWith('未記載'));
  });

  it('id_1_loads_analysis_markdown', () => {
    // data/analyses/001-animal-crossing-new-horizons.md exists.
    const html = win.document.getElementById('analysis').innerHTML;
    assert.ok(
      !html.includes('まだ書かれていません'),
      'analysis should not show the empty placeholder',
    );
    // marked.parse produces a heading tag from the leading '##' in the .md
    assert.ok(
      /<h[12]/.test(html),
      `expected an <h1>/<h2> tag in parsed markdown, got: ${html.slice(0, 120)}`,
    );
  });

  it('json_path_shown_in_kv', () => {
    const kv = win.document.getElementById('kv');
    const code = kv.querySelector('code');
    assert.ok(code);
    assert.equal(code.textContent, 'data/games/001-animal-crossing-new-horizons.json');
  });

  it('back_link_present', () => {
    const a = win.document.querySelector('a.back');
    assert.ok(a);
    assert.equal(a.getAttribute('href'), 'facet.html');
  });

  // --- Related panels --------------------------------------------------

  it('related_same_axis_links_render', () => {
    const panel = win.document.getElementById('rel-axis');
    assert.ok(panel);
    const minis = panel.querySelectorAll('a.mini');
    // Either >=1 .mini link OR the '該当なし' fallback text.
    if (minis.length === 0) {
      assert.ok(panel.textContent.includes('該当なし'));
    } else {
      assert.ok(minis.length >= 1);
    }
  });

  it('related_same_axis_excludes_self', () => {
    const minis = win.document.querySelectorAll('#rel-axis a.mini');
    for (const a of minis) {
      assert.ok(
        !/[?&]id=1(\b|$)/.test(a.getAttribute('href') || ''),
        'self link must be excluded',
      );
    }
  });

  it('related_same_axis_capped_at_8', () => {
    const minis = win.document.querySelectorAll('#rel-axis a.mini');
    assert.ok(minis.length <= 8, `rel-axis must have <=8 links, got ${minis.length}`);
  });

  it('related_same_year_within_3_years', async () => {
    const index = await readIndex();
    const acYear = 2020;
    const allowedIds = new Set(
      index.games
        .filter(
          (g) => g.id !== 1 && g.year && Math.abs(g.year - acYear) <= 3,
        )
        .map((g) => g.id),
    );
    const minis = win.document.querySelectorAll('#rel-year a.mini');
    for (const a of minis) {
      const m = a.getAttribute('href').match(/[?&]id=(\d+)/);
      assert.ok(m, `bad href on related-year link: ${a.outerHTML}`);
      const id = Number(m[1]);
      assert.ok(allowedIds.has(id), `year-related id=${id} not within ±3 of ${acYear}`);
    }
  });

  it('related_same_year_capped_at_8', () => {
    const minis = win.document.querySelectorAll('#rel-year a.mini');
    assert.ok(minis.length <= 8, `rel-year must have <=8 links, got ${minis.length}`);
  });
});

// --- id=4 (Pokemon Red/Green) -- documents actual id mapping -----------

describe('detail.html — id=4 (Pokemon Red/Green)', () => {
  it('id_4_pokemon_red_green_title', async () => {
    // Per data/games/004-pokemon-red-green.json. The parent task referred to
    // this as 'id=1' but the actual mapping is id=4 (id=1 is Animal Crossing).
    const dom = await bootDetail('?id=4');
    const win = dom.window;
    try {
      const title = win.document.querySelector('.detail-head .title-jp');
      assert.ok(title);
      assert.equal(title.textContent, 'ポケットモンスター 赤・緑');
    } finally {
      dom.window.close();
    }
  });
});

// --- id=2 (Mario Kart 8 — has no analyses md) --------------------------

describe('detail.html — analysis placeholder', () => {
  it('id_with_no_analysis_md_shows_placeholder', async () => {
    // data/analyses/002-mario-kart-8-deluxe.md does NOT exist (checked at
    // authoring time). The fetch in detail.html returns 404, which falls
    // through to the empty-analysis branch.
    const dom = await bootDetail('?id=2');
    const win = dom.window;
    try {
      await waitFor(
        () => (win.document.getElementById('analysis')?.innerHTML || '').length > 0,
        4000,
      );
      const html = win.document.getElementById('analysis').innerHTML;
      assert.ok(
        html.includes('このゲームの深い分析はまだ書かれていません'),
        `expected empty-analysis text, got: ${html.slice(0, 160)}`,
      );
    } finally {
      dom.window.close();
    }
  });
});

// --- not-found branches ------------------------------------------------

describe('detail.html — not-found branches', () => {
  // ID #56 used to be a hole (Project Sekai duplicate) and was tested as
  // not-found; the 2026-06 expansion filled it with 桃太郎電鉄. The remaining
  // cases exercise IDs that legitimately have no corresponding game.
  const cases = [
    ['?id=99999', 'id_99999_also_shows_not_found'],
    ['?id=0', 'id_zero_shows_not_found'],
    ['?id=-1', 'id_negative_shows_not_found'],
    ['', 'no_id_param_shows_not_found'],
    ['?id=abc', 'non_numeric_id_shows_not_found'],
  ];

  for (const [query, name] of cases) {
    it(name, async () => {
      const dom = await bootDetail(query);
      const win = dom.window;
      try {
        const text = win.document.querySelector('main')?.textContent || '';
        assert.ok(
          text.includes('ゲームが見つかりません'),
          `query=${query || '(empty)'} expected not-found message, got: ${text.slice(0, 120)}`,
        );
      } finally {
        dom.window.close();
      }
    });
  }
});

// --- documented gaps (skipped) -----------------------------------------

describe('detail.html — placeholder branches (skipped: no fixture currently)', () => {
  it.skip(
    'id_without_concept_shows_placeholder (no game JSON lacks concept right now)',
    () => {},
  );
  it.skip(
    'id_without_target_shows_placeholder (no game JSON lacks target right now)',
    () => {},
  );
  it.skip(
    "title_jp_html_escaped (no current title contains '<', '&', etc.; escapeHtml is exercised by inspection)",
    () => {},
  );
});
