// 用 Firebase 服務帳號憑證（D:\keys\worksheet-f47f3-firebase-adminsdk*.json）把「去姓名版」aiHistory 寫進 Firestore aiHistory/{年-班-座}。
// 規則：和網頁「匯入 aiHistory.json」一樣——不動學生挑的 picks；老師在網頁改過標記（marksEdited）的人保留標記，除非加 --overwrite-marks。
// 另外多寫 guide（說明書提示）、modes（各模式發言次數）、cands（老師預選的輪次，第 4 步左右切換著看），學生端要靠它們（網頁匯入目前不會寫這兩個欄位）。
// 用法（專案根目錄）：
//   工作台\runtime\node\node.exe materials\競賽專區\C04_檢查標記與排版\_歷程工具\上傳aiHistory.js inspect   只看雲端現況，不改資料
//   工作台\runtime\node\node.exe materials\競賽專區\C04_檢查標記與排版\_歷程工具\上傳aiHistory.js upload    寫入（加 --overwrite-marks 才覆蓋已改過的標記）
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const https = require('https');

const KEYDIR = 'D:\\keys';
const DATA = path.join(__dirname, '..', '學生對話紀錄', 'aiHistory_去姓名.json');
const keyFile = fs.readdirSync(KEYDIR).find(n => n.startsWith('worksheet-f47f3-firebase-adminsdk'));
if (!keyFile) throw new Error('找不到 worksheet-f47f3 的服務帳號金鑰（D:\\keys）');
const sa = JSON.parse(fs.readFileSync(path.join(KEYDIR, keyFile), 'utf8'));
const PROJECT = sa.project_id;
const BASE = `https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents`;

function b64u(b) { return Buffer.from(b).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_'); }
function req(method, url, headers, body) {
  return new Promise((res, rej) => {
    const u = new URL(url);
    const r = https.request({ method, hostname: u.hostname, path: u.pathname + u.search, headers }, resp => {
      const ch = []; resp.on('data', c => ch.push(c)); resp.on('end', () => { const d = Buffer.concat(ch).toString('utf8');
        let j; try { j = JSON.parse(d); } catch (e) { j = d; }
        if (resp.statusCode >= 300) rej(new Error(resp.statusCode + ' ' + (typeof j === 'string' ? j : JSON.stringify(j)).slice(0, 400)));
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

// JS 值 → Firestore REST 的型別值
function enc(v) {
  if (v === null || v === undefined) return { nullValue: null };
  if (typeof v === 'boolean') return { booleanValue: v };
  if (typeof v === 'number') return Number.isInteger(v) ? { integerValue: String(v) } : { doubleValue: v };
  if (typeof v === 'string') return { stringValue: v };
  if (Array.isArray(v)) return { arrayValue: { values: v.map(enc) } };
  const fields = {}; Object.keys(v).forEach(k => { fields[k] = enc(v[k]); });
  return { mapValue: { fields } };
}

async function listExisting(tk) {
  const out = {}; let page = '';
  do {
    const j = await req('GET', `${BASE}/aiHistory?pageSize=100${page ? '&pageToken=' + page : ''}`, { Authorization: 'Bearer ' + tk });
    (j.documents || []).forEach(d => { out[d.name.split('/').pop()] = d.fields || {}; });
    page = j.nextPageToken || '';
  } while (page);
  return out;
}

(async () => {
  const cmd = process.argv[2] || 'inspect', overwrite = process.argv.includes('--overwrite-marks');
  const data = JSON.parse(fs.readFileSync(DATA, 'utf8')).students;
  const tk = await token();
  console.log('專案：' + PROJECT + '　憑證：' + sa.client_email.replace(/^[^@]*/, '…'));
  const ex = await listExisting(tk);
  const exIds = Object.keys(ex);
  console.log('雲端 aiHistory 現有 ' + exIds.length + ' 份：' + (exIds.join('、') || '（空）'));
  exIds.forEach(id => {
    const f = ex[id];
    console.log('  ' + id + '　sessions=' + ((f.sessions && f.sessions.arrayValue.values || []).length) + '　marks=' + ((f.marks && f.marks.arrayValue.values || []).length)
      + '　picks=' + ((f.picks && f.picks.arrayValue.values || []).length) + '　marksEdited=' + !!(f.marksEdited && f.marksEdited.booleanValue));
  });
  if (cmd !== 'upload') { console.log('（inspect：沒有改任何資料）'); return; }
  let n = 0;
  for (const id of Object.keys(data)) {
    const s = data[id], cur = ex[id] || {};
    const body = { grade: s.grade, className: s.className, studentId: s.studentId, sessions: s.sessions, guide: s.guide || {}, modes: s.modes || {}, cands: s.cands || [], importedAt: Date.now() };
    const keepMarks = !overwrite && cur.marksEdited && cur.marksEdited.booleanValue;
    if (!keepMarks) { body.marks = s.marks || []; if (overwrite) body.marksEdited = false; }
    const keys = Object.keys(body);
    const fields = {}; keys.forEach(k => { fields[k] = enc(body[k]); });
    const q = keys.map(k => 'updateMask.fieldPaths=' + encodeURIComponent(k)).join('&');
    const payload = JSON.stringify({ fields });
    await req('PATCH', `${BASE}/aiHistory/${id}?${q}`, { Authorization: 'Bearer ' + tk, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }, payload);
    n++; console.log('✓ ' + id + '　' + (keepMarks ? '（保留網頁上改過的標記）' : '') + '　' + Math.round(payload.length / 1024) + ' KB');
  }
  console.log('已寫入 ' + n + ' 位學生。picks（學生挑的內容）沒有動。');
})().catch(e => { console.error('失敗：', e.message); process.exit(1); });
