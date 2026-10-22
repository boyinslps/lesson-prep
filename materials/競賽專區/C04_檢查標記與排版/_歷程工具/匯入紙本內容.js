// 把「學生紙本寫的內容」（照片轉打好的字）寫進 Firestore cardWork/{年-班-座}.L4，之後匯出參賽資料時就會一起放進說明書。
// 用服務帳號憑證（D:\keys\worksheet-f47f3-firebase-adminsdk*.json）。
//
// 內容檔（預設 學生對話紀錄\紙本內容.json，含學生寫的字，已列入 .gitignore，不要 commit）：
//   { "5-9-11": { "idea": "創作理念…", "disclose": "查證揭露的簡單說明…", "learned": "學習反思…" }, ... }
//   可用欄位：idea（創作理念）、chapters（["第二章","第四章"]）、chapDesc、err（"有"／"沒有"）、found、eUse、
//            eUse（你在哪些地方使用到 e度；紙本「查證揭露」的說明寫在這裡，寫 disclose 也會自動轉成 eUse）、tools（["因材網 e度","Canva"]）、toolsOther、learned、
//            mTitle（作品名稱）、mName（參賽者姓名）、mGrade（年級）
//
// 用法（專案根目錄）：
//   工作台\runtime\node\node.exe materials\競賽專區\C04_檢查標記與排版\_歷程工具\匯入紙本內容.js            只預覽，不寫入
//   工作台\runtime\node\node.exe …\匯入紙本內容.js --go                                                    寫入（預設「合併補充」：欄位是空的就寫入；學生網頁上已經有字，就把紙本內容接在後面補充；已經包含的不重複；勾選項目取聯集）
//   加 --overwrite：欄位直接用紙本內容取代（連學生網頁上已經寫的字）
//   加 --skip：學生網頁上已經有內容的欄位一律不動
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const https = require('https');

const args = process.argv.slice(2);
const GO = args.includes('--go'), OVER = args.includes('--overwrite'), SKIP = args.includes('--skip');
const file = args.find(a => !a.startsWith('--')) || path.join(__dirname, '..', '學生對話紀錄', '紙本內容.json');
const STR = ['idea', 'chapDesc', 'err', 'found', 'eUse', 'disclose', 'toolsOther', 'learned', 'mTitle', 'mName', 'mGrade'];
const LST = ['chapters', 'tools'];

const KEYDIR = 'D:\\keys';
const keyFile = fs.readdirSync(KEYDIR).find(n => n.startsWith('worksheet-f47f3-firebase-adminsdk'));
if (!keyFile) { console.error('找不到 worksheet-f47f3 的服務帳號金鑰（D:\\keys）'); process.exit(1); }
const sa = JSON.parse(fs.readFileSync(path.join(KEYDIR, keyFile), 'utf8'));
const BASE = `https://firestore.googleapis.com/v1/projects/${sa.project_id}/databases/(default)/documents/cardWork`;

function b64u(b) { return Buffer.from(b).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_'); }
function req(method, url, headers, body, okNotFound) {
  return new Promise((res, rej) => {
    const u = new URL(url);
    const r = https.request({ method, hostname: u.hostname, path: u.pathname + u.search, headers }, resp => {
      const ch = []; resp.on('data', c => ch.push(c)); resp.on('end', () => { const d = Buffer.concat(ch).toString('utf8');
        let j; try { j = JSON.parse(d); } catch (e) { j = d; }
        if (resp.statusCode === 404 && okNotFound) return res(null);
        if (resp.statusCode >= 300) rej(new Error(resp.statusCode + ' ' + (typeof j === 'string' ? j : JSON.stringify(j)).slice(0, 300)));
        else res(j);
      });
    });
    r.on('error', rej); if (body) r.write(body); r.end();
  });
}
async function token() {
  const now = Math.floor(Date.now() / 1000);
  const head = b64u(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
  const claim = b64u(JSON.stringify({ iss: sa.client_email, scope: 'https://www.googleapis.com/auth/datastore', aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3000 }));
  const sig = crypto.createSign('RSA-SHA256').update(head + '.' + claim).sign(sa.private_key);
  const body = 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + head + '.' + claim + '.' + b64u(sig);
  const j = await req('POST', 'https://oauth2.googleapis.com/token', { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) }, body);
  return j.access_token;
}
const clip = s => String(s).replace(/\s+/g, ' ').slice(0, 40) + (String(s).length > 40 ? '…' : '');

(async () => {
  if (!fs.existsSync(file)) { console.error('找不到內容檔：' + file); process.exit(1); }
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const tk = await token(), H = { Authorization: 'Bearer ' + tk };
  let n = 0;
  for (const sid of Object.keys(data).filter(k => !k.startsWith('_'))) {
    const m = sid.match(/^(\d+)-(\d+)-(\d+)$/);
    if (!m) { console.log('✗ ' + sid + '：座號格式要是 年-班-座（例如 5-9-11）'); continue; }
    const D0 = data[sid];   // 查證揭露的文字說明已併入「你在哪些地方使用到 e度」（eUse）；說明書的查證揭露只放標記後的文章
    if ('disclose' in D0) { if (!D0.eUse) D0.eUse = D0.disclose; delete D0.disclose; }
    const cur = await req('GET', `${BASE}/${sid}`, H, null, true);
    const l4 = (cur && cur.fields && cur.fields.L4 && cur.fields.L4.mapValue && cur.fields.L4.mapValue.fields) || {};
    const have = k => { const v = l4[k]; return !!(v && ((v.stringValue || '').trim() || (v.arrayValue && (v.arrayValue.values || []).length))); };
    const fields = {}, paths = [], lines = [];
    for (const k of Object.keys(data[sid])) {
      const v = data[sid][k];
      if (!STR.includes(k) && !LST.includes(k)) { lines.push('  ⚠ 不認得的欄位「' + k + '」，略過'); continue; }
      const curStr = (l4[k] && l4[k].stringValue || '').trim(), curLst = (l4[k] && l4[k].arrayValue && (l4[k].arrayValue.values || []).map(x => x.stringValue)) || [];
      let val, note = '';
      if (LST.includes(k)) {
        const want = [].concat(v).map(String), merged = OVER ? want : Array.from(new Set(curLst.concat(want)));
        if (!OVER && merged.length === curLst.length && curLst.length) { lines.push('  － ' + k + '：已經包含，不動'); continue; }
        if (have(k) && SKIP && !OVER) { lines.push('  － ' + k + '：學生網頁上已經有內容，不動（--skip）'); continue; }
        val = { arrayValue: { values: merged.map(x => ({ stringValue: x })) } }; note = curLst.length && !OVER ? '（合併）' : '';
      } else {
        const want = String(v).trim();
        if (have(k) && !OVER) {
          if (SKIP) { lines.push('  － ' + k + '：學生網頁上已經有內容，不動（--skip）'); continue; }
          if (curStr.includes(want)) { lines.push('  － ' + k + '：已經包含，不動'); continue; }
          if (want.includes(curStr)) { val = { stringValue: want.slice(0, 3000) }; note = '（紙本內容更完整，取代學生打到一半的）'; fields[k] = val; paths.push('L4.' + k); lines.push('  ✓ ' + k + note + '：' + clip(v)); continue; }
          val = { stringValue: (curStr + '\n' + want).slice(0, 3000) }; note = '（接在學生原本寫的後面補充）';
        } else val = { stringValue: want.slice(0, 3000) };
      }
      fields[k] = val; paths.push('L4.' + k);
      lines.push('  ✓ ' + k + note + '：' + clip(Array.isArray(v) ? v.join('、') : v));
    }
    console.log((cur ? '' : '（雲端還沒有這位的資料，會新建）') + sid);
    lines.forEach(l => console.log(l));
    if (!GO || !paths.length) continue;
    const body = { fields: { L4: { mapValue: { fields } } } };
    let q = paths.map(p => 'updateMask.fieldPaths=' + encodeURIComponent(p)).join('&');
    if (!cur) {   // 新建時補上規則要求的欄位
      body.fields.grade = { integerValue: m[1] }; body.fields.className = { integerValue: m[2] }; body.fields.studentId = { integerValue: m[3] };
      q += '&updateMask.fieldPaths=grade&updateMask.fieldPaths=className&updateMask.fieldPaths=studentId';
    }
    body.fields.updatedAt = { timestampValue: new Date().toISOString() };
    q += '&updateMask.fieldPaths=updatedAt';
    const payload = JSON.stringify(body);
    await req('PATCH', `${BASE}/${sid}?${q}`, { ...H, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }, payload);
    n++;
  }
  console.log(GO ? '\n已寫入 ' + n + ' 位。' : '\n（只是預覽，沒有寫入。確認沒問題再加 --go）');
})().catch(e => { console.error('失敗：', e.message); process.exit(1); });
