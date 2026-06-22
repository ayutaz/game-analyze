// 共通: data/index.json と data/games/*.json を読み込むヘルパ
const PRIMARY_LABEL = { EXP: '体験型', NAR: '物語型', REW: '報酬型' };
const SOCIAL_AXES = ['対戦', '協力', '非対称', '非同期', '観戦', 'ソロ'];

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
    <h1>日本のゲーム99本 分析カタログ</h1>
    <span class="mock-label">MOCK</span>
    <nav>
      <a href="index.html" class="${active==='index'?'active':''}">モック選択</a>
      <a href="matrix.html" class="${active==='matrix'?'active':''}">A: マトリクス</a>
      <a href="facet.html" class="${active==='facet'?'active':''}">B: ファセット</a>
      <a href="scatter.html" class="${active==='scatter'?'active':''}">C: 散布図</a>
      <a href="dashboard.html" class="${active==='dashboard'?'active':''}">D: ダッシュボード</a>
    </nav>
  `;
}

function cardHTML(g, linkable = true) {
  const subs = (g.secondary || []).map(s => `<span class="axis-tag">${s}</span>`).join('');
  const axis = g.social_axis ? `<span class="axis-tag">${g.social_axis}</span>` : '';
  const platforms = (g.platform || []).slice(0, 2).map(p => `<span class="axis-tag">${p}</span>`).join('');
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
        ${subs}
        ${platforms}
        <span>${g.year || ''}</span>
      </div>
      ${pop}
    ${close}
  `;
}
