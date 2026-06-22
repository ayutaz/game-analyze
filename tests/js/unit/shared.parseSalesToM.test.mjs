// Unit tests for site/shared.js → parseSalesToM(s)
//
// The function extracts a leading-ish number followed by an "M" or "B" suffix
// (case-insensitive) and returns it in millions. "B" multiplies by 1000.
// Anything that doesn't have a M/B suffix, or is falsy, yields null.
// Number inputs currently throw because the function calls `s.match(...)`.

import { test, describe, before } from 'node:test';
import assert from 'node:assert/strict';
import { loadShared } from '../helpers/shared.mjs';

let parseSalesToM;

before(async () => {
  ({ parseSalesToM } = await loadShared());
});

describe('parseSalesToM', () => {
  test('parses_plain_millions', () => {
    assert.equal(parseSalesToM('11.91M'), 11.91);
  });

  test('parses_integer_millions', () => {
    assert.equal(parseSalesToM('47M'), 47);
  });

  test('parses_millions_with_plus', () => {
    assert.equal(parseSalesToM('47M+'), 47);
  });

  test('parses_billions_to_millions', () => {
    assert.equal(parseSalesToM('5B+'), 5000);
  });

  test('parses_decimal_billions', () => {
    assert.equal(parseSalesToM('1.5B+ DL'), 1500);
  });

  test('parses_lowercase_m', () => {
    // The regex uses /i so lowercase 'm' is also a unit.
    assert.equal(parseSalesToM('3.2m'), 3.2);
  });

  test('parses_lowercase_b', () => {
    assert.equal(parseSalesToM('2b+'), 2000);
  });

  test('ignores_leading_whitespace_in_number', () => {
    // The regex tolerates surrounding text — only the number+unit submatch
    // matters.
    assert.equal(parseSalesToM('  11.91M '), 11.91);
  });

  test('extracts_first_match_when_multiple', () => {
    // Default regex match returns the first occurrence.
    assert.equal(parseSalesToM('11M / 47M+'), 11);
  });

  test('handles_suffix_words', () => {
    assert.equal(parseSalesToM('250M downloads'), 250);
  });

  test('returns_null_for_null_input', () => {
    assert.equal(parseSalesToM(null), null);
  });

  test('returns_null_for_undefined_input', () => {
    assert.equal(parseSalesToM(undefined), null);
  });

  test('returns_null_for_empty_string', () => {
    // The `if (!s)` falsy guard returns null up front.
    assert.equal(parseSalesToM(''), null);
  });

  test('returns_null_for_zero_string', () => {
    // '0' has no M/B suffix so the regex fails and the function returns null.
    // Documents current behavior — a bare digit with no unit is not a sale.
    assert.equal(parseSalesToM('0'), null);
  });

  test('returns_null_for_garbage', () => {
    assert.equal(parseSalesToM('garbage'), null);
  });

  test('returns_null_for_number_without_suffix', () => {
    assert.equal(parseSalesToM('1500000'), null);
  });

  test('returns_null_for_currency_only', () => {
    assert.equal(parseSalesToM('$50'), null);
  });

  test('handles_dash_placeholder', () => {
    assert.equal(parseSalesToM('—'), null);
  });

  test('handles_japanese_unit_chars_as_null', () => {
    // The regex only knows M/B; "万" is not understood.
    assert.equal(parseSalesToM('100万本'), null);
  });

  test('preserves_float_precision', () => {
    // parseFloat semantics: '11.91' becomes exactly the IEEE-754 representation
    // of 11.91, and JavaScript === compares that to the same literal in the test.
    assert.equal(parseSalesToM('11.91M') === 11.91, true);
  });

  test('billion_multiplication_exact', () => {
    assert.equal(parseSalesToM('1B'), 1000);
  });

  test('does_not_throw_on_number_input', () => {
    // Current implementation invokes `s.match(...)` which throws TypeError
    // for a Number argument. We assert this behavior so a future fix (e.g.
    // coercing to String first) deliberately updates this test.
    //
    // Note: the function runs inside the JSDOM realm, so the thrown
    // TypeError is an instance of JSDOM-window.TypeError, not Node's. We
    // match on `name` and `message` instead of constructor identity.
    assert.throws(() => parseSalesToM(47), (err) => {
      assert.equal(err.name, 'TypeError');
      assert.match(err.message, /match is not a function/);
      return true;
    });
  });
});
