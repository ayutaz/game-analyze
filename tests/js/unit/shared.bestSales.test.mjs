// Unit tests for site/shared.js → bestSales(g)
//
//   return parseSalesToM(g.sales_world) ?? parseSalesToM(g.sales_jp);
//
// Worldwide preferred when it parses; falls back to JP otherwise; null if
// neither parses. ?? is nullish-coalescing so 0 would be preserved, but the
// regex never yields 0 in practice (M/B suffix is required).

import { test, describe, before } from 'node:test';
import assert from 'node:assert/strict';
import { loadShared } from '../helpers/shared.mjs';

let bestSales;

before(async () => {
  ({ bestSales } = await loadShared());
});

describe('bestSales', () => {
  test('prefers_world_over_jp', () => {
    assert.equal(bestSales({ sales_world: '47M+', sales_jp: '11.91M' }), 47);
  });

  test('falls_back_to_jp_when_world_null', () => {
    assert.equal(bestSales({ sales_world: null, sales_jp: '11.91M' }), 11.91);
  });

  test('falls_back_to_jp_when_world_missing', () => {
    assert.equal(bestSales({ sales_jp: '5M' }), 5);
  });

  test('falls_back_to_jp_when_world_unparseable', () => {
    // parseSalesToM('—') → null → ?? takes the right operand
    assert.equal(bestSales({ sales_world: '—', sales_jp: '11M' }), 11);
  });

  test('returns_null_when_both_missing', () => {
    assert.equal(bestSales({}), null);
  });

  test('returns_null_when_both_unparseable', () => {
    assert.equal(bestSales({ sales_world: '—', sales_jp: '未公開' }), null);
  });

  test('world_billions_preferred', () => {
    assert.equal(
      bestSales({ sales_world: '1.5B+ DL', sales_jp: '10M' }),
      1500,
    );
  });

  test('world_zero_value_preserved', { skip: 'parseSalesToM cannot produce 0 today (requires M/B suffix; bare 0 yields null). Re-enable if parser is extended.' }, () => {
    // Hypothetical: if parseSalesToM('0M') ever returned 0, ?? would still
    // return 0 (not fall through). Documented but not exercisable.
  });

  test('handles_undefined_argument_safely', () => {
    // Current impl does `g.sales_world` first — accessing a property on
    // undefined throws TypeError. Asserted to document the limitation.
    //
    // Note: bestSales runs inside the JSDOM realm so the thrown TypeError is
    // an instance of JSDOM-window.TypeError, not Node's. We match on name.
    assert.throws(() => bestSales(undefined), (err) => {
      assert.equal(err.name, 'TypeError');
      return true;
    });
  });
});
