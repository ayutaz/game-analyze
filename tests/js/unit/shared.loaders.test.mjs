// Unit tests for site/shared.js → loadIndex() and loadGame(file)
//
// Both helpers are thin wrappers around `fetch`:
//   loadIndex()        -> fetch('../data/index.json')
//   loadGame(file)     -> fetch('../' + file)
// They return res.json() on res.ok, else throw.
//
// We stub the JSDOM window's `fetch` (which is the binding the wrapped
// functions resolve at call time) and inspect the recorded calls.

import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { loadShared } from '../helpers/shared.mjs';

/**
 * Build a fake fetch that records calls and returns a configurable response.
 * @param {(url:string) => {ok:boolean, json?: any}} respond
 */
function makeFakeFetch(respond) {
  const calls = [];
  const fakeFetch = async (input /*, init */) => {
    const url = typeof input === 'string' ? input : (input && input.url) || String(input);
    calls.push(url);
    const r = respond(url) || { ok: true };
    return {
      ok: r.ok,
      status: r.ok ? 200 : 500,
      statusText: r.ok ? 'OK' : 'Server Error',
      async json() {
        return r.json;
      },
      async text() {
        return JSON.stringify(r.json ?? null);
      },
    };
  };
  fakeFetch.calls = calls;
  return fakeFetch;
}

describe('loadIndex', () => {
  let loadIndex;
  let fakeFetch;

  beforeEach(async () => {
    fakeFetch = makeFakeFetch(() => ({ ok: true, json: { games: [{ id: 1 }] } }));
    ({ loadIndex } = await loadShared({ fetchImpl: fakeFetch }));
  });

  test('loadIndex_fetches_relative_path', async () => {
    await loadIndex();
    assert.equal(fakeFetch.calls.length, 1);
    assert.equal(fakeFetch.calls[0], '../data/index.json');
  });

  test('loadIndex_returns_parsed_json', async () => {
    const result = await loadIndex();
    assert.deepEqual(result, { games: [{ id: 1 }] });
  });

  test('loadIndex_throws_on_non_ok', async () => {
    const fail = makeFakeFetch(() => ({ ok: false }));
    const { loadIndex: failLoad } = await loadShared({ fetchImpl: fail });
    await assert.rejects(
      () => failLoad(),
      /failed to load data\/index\.json/,
    );
  });
});

describe('loadGame', () => {
  let loadGame;
  let fakeFetch;

  beforeEach(async () => {
    fakeFetch = makeFakeFetch(() => ({ ok: true, json: { id: 1, title_jp: 'X' } }));
    ({ loadGame } = await loadShared({ fetchImpl: fakeFetch }));
  });

  test('loadGame_fetches_relative_to_parent', async () => {
    await loadGame('data/games/001-x.json');
    assert.equal(fakeFetch.calls.length, 1);
    assert.equal(fakeFetch.calls[0], '../data/games/001-x.json');
  });

  test('loadGame_returns_parsed_json', async () => {
    const result = await loadGame('data/games/001-x.json');
    assert.deepEqual(result, { id: 1, title_jp: 'X' });
  });

  test('loadGame_throws_on_non_ok_with_path_in_message', async () => {
    const fail = makeFakeFetch(() => ({ ok: false }));
    const { loadGame: failLoad } = await loadShared({ fetchImpl: fail });
    await assert.rejects(
      () => failLoad('data/games/001-x.json'),
      /data\/games\/001-x\.json/,
    );
  });
});
