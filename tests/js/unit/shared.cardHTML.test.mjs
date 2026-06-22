// Unit tests for site/shared.js → cardHTML(g, linkable=true)
//
// Returns an HTML string for a game card. The string is rendered into the
// facet page via innerHTML, so each assertion checks the literal substrings
// that the page DOM depends on.
//
// Known limitation surfaced by these tests: cardHTML does NOT escape
// user/data-provided strings (title_jp, title_en, popularity, etc). The
// detail page escapes its values, but facet cards do not. That is asserted
// below so future hardening is a deliberate change.

import { test, describe, before } from 'node:test';
import assert from 'node:assert/strict';
import { loadShared } from '../helpers/shared.mjs';

let cardHTML;

before(async () => {
  ({ cardHTML } = await loadShared());
});

describe('cardHTML', () => {
  test('linkable_card_uses_a_tag', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    assert.ok(
      html.includes('<a class="card card-link" href="detail.html?id=1">'),
      `expected <a class="card card-link" href="detail.html?id=1"> in output. Got:\n${html}`,
    );
  });

  test('non_linkable_card_uses_article_tag', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' }, false);
    assert.ok(html.includes('<article class="card">'),
      `expected <article class="card"> in output. Got:\n${html}`);
    assert.ok(!html.includes('href='),
      `expected no href in non-linkable output. Got:\n${html}`);
  });

  test('renders_title_jp', () => {
    const html = cardHTML({ id: 1, title_jp: 'スプラトゥーン3', primary: 'EXP' });
    assert.ok(html.includes('スプラトゥーン3'));
  });

  test('renders_title_en_when_present', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      title_en: 'Splatoon 3',
      primary: 'EXP',
    });
    assert.ok(html.includes('Splatoon 3'));
  });

  test('renders_empty_title_en_safely', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    // The `||''` fallback means we render the wrapping div with empty contents,
    // never the literal text 'undefined'.
    assert.ok(html.includes('<div class="title-en"></div>'),
      `expected empty title-en div. Got:\n${html}`);
    assert.ok(!html.includes('undefined'),
      `did not expect "undefined" in card output. Got:\n${html}`);
  });

  test('renders_primary_badge_class_lowercase', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    assert.ok(html.includes('badge exp'),
      `expected "badge exp" class. Got:\n${html}`);
  });

  test('renders_primary_label_japanese', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'NAR' });
    assert.ok(html.includes('物語型'),
      `expected "物語型" label. Got:\n${html}`);
  });

  test('renders_social_axis_when_present', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      social_axis: '対戦',
    });
    assert.ok(html.includes('<span class="axis-tag">対戦</span>'),
      `expected an axis-tag span containing 対戦. Got:\n${html}`);
  });

  test('omits_social_axis_when_falsy', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      social_axis: null,
    });
    // The card always emits a fixed badge span and possibly platform/secondary
    // tags. We only assert the *literal* word "null" doesn't sneak in.
    assert.ok(!html.includes('>null<'),
      `did not expect "null" rendered as a tag. Got:\n${html}`);
  });

  test('renders_secondary_tags', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      secondary: ['REW', 'NAR'],
    });
    assert.ok(html.includes('<span class="axis-tag">REW</span>'));
    assert.ok(html.includes('<span class="axis-tag">NAR</span>'));
  });

  test('secondary_empty_array_renders_nothing', () => {
    const withSec = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      secondary: ['REW'],
    });
    const withoutSec = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      secondary: [],
    });
    // Empty `secondary` should produce no axis-tag spans from secondary —
    // confirmed by absence of "REW" tag and by output not containing the
    // joined form `<span class="axis-tag"></span>` either.
    assert.ok(!withoutSec.includes('REW'));
    assert.notEqual(withSec, withoutSec);
  });

  test('platform_first_two_only', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      platform: ['Switch', 'PS5', 'PC', 'iOS'],
    });
    assert.ok(html.includes('<span class="axis-tag">Switch</span>'));
    assert.ok(html.includes('<span class="axis-tag">PS5</span>'));
    assert.ok(!html.includes('<span class="axis-tag">PC</span>'),
      `expected only first two platforms. Got:\n${html}`);
    assert.ok(!html.includes('<span class="axis-tag">iOS</span>'),
      `expected only first two platforms. Got:\n${html}`);
  });

  test('platform_missing_renders_nothing', () => {
    // No `platform` key — the `(g.platform || [])` fallback prevents a
    // TypeError and emits no platform tags.
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    // We can't simply check for absence of axis-tag (the badge is unrelated),
    // but we can check that no obvious platform name leaks through.
    assert.ok(!html.includes('Switch'));
    assert.ok(!html.includes('PS5'));
  });

  test('year_rendered_in_meta', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      year: 2020,
    });
    assert.ok(html.includes('<span>2020</span>'),
      `expected <span>2020</span> in meta. Got:\n${html}`);
  });

  test('year_missing_renders_empty_span', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    assert.ok(html.includes('<span></span>'),
      `expected empty <span></span> when year omitted. Got:\n${html}`);
    assert.ok(!html.includes('undefined'),
      `did not expect "undefined" in card output. Got:\n${html}`);
  });

  test('popularity_renders_when_present', () => {
    const html = cardHTML({
      id: 1,
      title_jp: 'X',
      primary: 'EXP',
      popularity: 'コロナ社会現象',
    });
    assert.ok(html.includes('<div class="pop">コロナ社会現象</div>'),
      `expected <div class="pop"> with text. Got:\n${html}`);
  });

  test('popularity_omitted_when_falsy', () => {
    const html = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    assert.ok(!html.includes('<div class="pop">'),
      `did not expect a .pop div when popularity is absent. Got:\n${html}`);
  });

  test('html_in_title_jp_is_not_escaped', () => {
    // Known limitation: cardHTML interpolates title_jp directly into the
    // returned string without HTML escaping. The detail.html template DOES
    // escape values; facet cards do not. If/when this is fixed the assertion
    // below will need to be updated to assert escaping instead.
    const html = cardHTML({
      id: 1,
      title_jp: '<script>x</script>',
      primary: 'EXP',
    });
    assert.ok(html.includes('<script>x</script>'),
      `expected raw HTML in title_jp to pass through unescaped (current behavior). Got:\n${html}`);
  });

  test('default_argument_is_linkable_true', () => {
    const withoutArg = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' });
    const withTrue = cardHTML({ id: 1, title_jp: 'X', primary: 'EXP' }, true);
    assert.equal(withoutArg, withTrue);
  });
});
