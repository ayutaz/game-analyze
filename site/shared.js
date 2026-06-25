// 共通: data/index.json と data/games/*.json を読み込むヘルパ
const PRIMARY_LABEL = { EXP: '体験型', NAR: '物語型', REW: '報酬型' };
const SOCIAL_AXES = ['対戦', '協力', '非対称', '非同期', '観戦', 'ソロ'];
const TAG_LABEL = { indie: 'インディーズ' };

async function loadIndex() {
  const res = await fetch('../data/index.json');
  if (!res.ok) throw new Error('failed to load data/index.json');
  return res.json();
}

async function loadGame(file) {
  const res = await fetch('../' + file);
  if (!res.ok) throw new Error('failed to load ' + file);
  return res.json();
}

// 売上文字列 "11.91M" "47M+" "5B+ DL" などから百万単位の数値を抽出
function parseSalesToM(s) {
  if (!s) return null;
  const m = s.match(/([\d.]+)\s*([MB])/i);
  if (!m) return null;
  let n = parseFloat(m[1]);
  if (m[2].toUpperCase() === 'B') n *= 1000;
  return n;
}

function bestSales(g) {
  return parseSalesToM(g.sales_world) ?? parseSalesToM(g.sales_jp);
}

function topbarNav(active) {
  return `
    <h1><a href="facet.html" style="text-decoration:none;color:inherit;">日本／世界のゲーム 3カテゴリ分析カタログ</a></h1>
    <nav>
      <a href="facet.html" class="${active==='facet'?'active':''}">一覧</a>
      <a href="https://github.com/ayutaz/game-analyze" target="_blank">GitHub</a>
    </nav>
  `;
}

function cardHTML(g, linkable = true) {
  const subs = (g.secondary || []).map(s => `<span class="axis-tag">${s}</span>`).join('');
  const axis = g.social_axis ? `<span class="axis-tag">${g.social_axis}</span>` : '';
  const platforms = (g.platform || []).slice(0, 2).map(p => `<span class="axis-tag">${p}</span>`).join('');
  const tags = (g.tags || []).map(t => `<span class="axis-tag tag-${t}">${TAG_LABEL[t] || t}</span>`).join('');
  const pop = g.popularity ? `<div class="pop">${g.popularity}</div>` : '';
  const wrapper = linkable
    ? `<a class="card card-link" href="detail.html?id=${g.id}">`
    : `<article class="card">`;
  const close = linkable ? `</a>` : `</article>`;
  return `
    ${wrapper}
      <div>
        <div class="title-jp">${g.title_jp}</div>
        <div class="title-en">${g.title_en || ''}</div>
      </div>
      <div class="meta">
        <span class="badge ${g.primary.toLowerCase()}">${PRIMARY_LABEL[g.primary]}</span>
        ${axis}
        ${tags}
        ${subs}
        ${platforms}
        <span>${g.year || ''}</span>
      </div>
      ${pop}
    ${close}
  `;
}
