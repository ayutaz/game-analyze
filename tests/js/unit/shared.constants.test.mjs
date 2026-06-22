// Unit tests for site/shared.js → PRIMARY_LABEL and SOCIAL_AXES
//
// These constants are part of the rendering contract: PRIMARY_LABEL backs the
// badge text in cardHTML, and SOCIAL_AXES drives the sidebar order on facet.
// The ordering of SOCIAL_AXES is rendered in the UI, so it's behavioral, not
// just data.

import { test, describe, before } from 'node:test';
import assert from 'node:assert/strict';
import { loadShared } from '../helpers/shared.mjs';

let PRIMARY_LABEL;
let SOCIAL_AXES;

before(async () => {
  ({ PRIMARY_LABEL, SOCIAL_AXES } = await loadShared());
});

// The constants live in the JSDOM realm, which has its own Object/Array
// prototypes distinct from Node's. assert.deepStrictEqual (the default
// `node:assert/strict` deepEqual) checks prototype identity, so we copy the
// values across the realm boundary into plain Node objects/arrays before
// comparing.
function toPlainObject(o) {
  return Object.assign(Object.create(null), o);
}
function toPlainArray(a) {
  return Array.prototype.slice.call(a);
}

describe('PRIMARY_LABEL', () => {
  test('primary_label_has_three_keys', () => {
    assert.deepEqual(toPlainArray(Object.keys(PRIMARY_LABEL)).sort(), ['EXP', 'NAR', 'REW']);
  });

  test('primary_label_japanese_values', () => {
    // Compare key-by-key to avoid cross-realm prototype identity mismatch.
    assert.equal(PRIMARY_LABEL.EXP, '体験型');
    assert.equal(PRIMARY_LABEL.NAR, '物語型');
    assert.equal(PRIMARY_LABEL.REW, '報酬型');
    // Also confirm no extra keys snuck in.
    assert.deepEqual(toPlainArray(Object.keys(PRIMARY_LABEL)).sort(), ['EXP', 'NAR', 'REW']);
  });
});

describe('SOCIAL_AXES', () => {
  test('social_axes_has_six_entries', () => {
    assert.equal(SOCIAL_AXES.length, 6);
  });

  test('social_axes_order_matches_spec', () => {
    // Copy across realm boundary so deepEqual's prototype check passes.
    assert.deepEqual(toPlainArray(SOCIAL_AXES), [
      '対戦',
      '協力',
      '非対称',
      '非同期',
      '観戦',
      'ソロ',
    ]);
  });
});
