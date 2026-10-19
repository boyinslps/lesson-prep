// 用 Firebase 服務帳號憑證（D:\keys\pcclass-94300-*.json）直接打 Firestore REST，不需要安裝任何套件。
// 用途：把學生「繳交紀錄 submissions」裡學生端讀不到的內容，複製到學生讀得到的「暫存區 studentWork」（規範 §3-c）。
// 用法（專案根目錄）：
//   工作台\runtime\node\node.exe 工作台\firebase_admin_rest.js inspect g5-L05          只看筆數與欄位，不改資料
//   工作台\runtime\node\node.exe 工作台\firebase_admin_rest.js backfill-factcheck g5-L05   寫進 studentWork（kind=factcheck）
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const https = require('https');

const KEYDIR = 'D:\\keys';
const keyFile = fs.readdirSync(KEYDIR).find(n => n.startsWith('pcclass-94300-firebase-adminsdk'));
if (!keyFile) throw new Error('找不到 pcclass-94300 的服務帳號金鑰');
const sa = JSON.parse(fs.readFileSync(path.join(KEYDIR, keyFile), 'utf8'));
const PROJECT = sa.project_id;

function b64u(b) { return Buffer.from(b).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_'); }
function req(method, url, headers, body) {
  return new Promise((res, rej) => {
    const u = new URL(url);
    const r = https.request({ method, hostname: u.hostname, path: u.pathname + u.search, headers }, resp => {
      let d = ''; resp.on('data', c => d += c); resp.on('end', () => {
        let j; try { j = JSON.parse(d); } catch (e) { j = d; }
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
  const jwt = head + '.' + claim + '.' + b64u(sig);
  const body = 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + jwt;
  const j = await req('POST', 'https://oauth2.googleapis.com/token', { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) }, body);
  return j.access_token;
}
// Firestore REST 的值 ↔ 一般值
function dec(v) {
  if (v == null) return null;
  if ('stringValue' in v) return v.stringValue;
  if ('integerValue' in v) return Number(v.integerValue);
  if ('doubleValue' in v) return v.doubleValue;
  if ('booleanValue' in v) return v.booleanValue;
  if ('nullValue' in v) return null;
  if ('timestampValue' in v) return v.timestampValue;
  if ('arrayValue' in v) return (v.arrayValue.values || []).map(dec);
  if ('mapValue' in v) { const o = {}; for (const k in (v.mapValue.fields || {})) o[k] = dec(v.mapValue.fields[k]); return o; }
  return null;
}
function enc(x) {
  if (x == null) return { nullValue: null };
  if (typeof x === 'string') return { stringValue: x };
  if (typeof x === 'number') return Number.isInteger(x) ? { integerValue: String(x) } : { doubleValue: x };
  if (typeof x === 'boolean') return { booleanValue: x };
  if (Array.isArray(x)) return { arrayValue: { values: x.map(enc) } };
  const f = {}; for (const k in x) f[k] = enc(x[k]); return { mapValue: { fields: f } };
}
async function querySubmissions(tk, ws) {
  const url = `https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents:runQuery`;
  const body = JSON.stringify({ structuredQuery: { from: [{ collectionId: 'submissions' }], where: { fieldFilter: { field: { fieldPath: 'worksheetId' }, op: 'EQUAL', value: { stringValue: ws } } } } });
  const rows = await req('POST', url, { Authorization: 'Bearer ' + tk, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }, body);
  return rows.filter(r => r.document).map(r => { const o = {}; for (const k in r.document.fields) o[k] = dec(r.document.fields[k]); o._id = r.document.name.split('/').pop(); return o; });
}
async function setWork(tk, id, obj) {
  const url = `https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/(default)/documents/studentWork/${encodeURIComponent(id)}`;
  const f = {}; for (const k in obj) f[k] = enc(obj[k]);
  const body = JSON.stringify({ fields: f });
  return req('PATCH', url, { Authorization: 'Bearer ' + tk, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }, body);
}

// 學生當時選的訊息 → 老師準備的那篇查核文章（頁面的 CARDS；學生自己貼過網址就用自己的）
const CARD_URL = {
  C: 'https://www.mygopen.com/2026/08/vote-scam.html',
  D: 'https://tfc-taiwan.org.tw/?p=109294',
  E: 'https://tfc-taiwan.org.tw/fact-check-reports/migration-7854',
  G: 'https://www.mygopen.com/2026/09/india-ai.html',
  H: 'https://www.mygopen.com/2022/01/Charging-Phone.html',
  K: 'https://tfc-taiwan.org.tw/fact-check-reports/migration-4806',
};

(async () => {
  const [cmd, ws] = process.argv.slice(2);
  const tk = await token();
  const subs = await querySubmissions(tk, ws);
  console.log('筆數', subs.length);
  const keyCount = {};
  subs.forEach(s => { Object.keys(s.parts || {}).forEach(k => keyCount[k] = (keyCount[k] || 0) + 1); Object.keys(s.answers || {}).forEach(k => keyCount['answers.' + k] = (keyCount['answers.' + k] || 0) + 1); });
  console.log('欄位出現次數', JSON.stringify(keyCount));
  if (cmd === 'inspect') return;
  if (cmd === 'backfill-factcheck') {
    let n = 0, withUrl = 0, noSel = 0;
    for (const s of subs) {
      const p = s.parts || {}, a = s.answers || {};
      const sel = p.sel || a.sel || null;
      const own = String(p.url || a.url || '').trim();
      if (!sel && !own) { noSel++; continue; }
      const url = own || (CARD_URL[sel] || '');
      if (own) withUrl++;
      const id = `${ws}__${s.grade}-${s.className}-${s.studentId}__factcheck`;
      await setWork(tk, id, {
        worksheetId: ws, kind: 'factcheck', grade: s.grade, className: s.className, studentId: s.studentId,
        data: { sel: sel || '', url, own: !!own, label: String(p.label || a.label || '') },
        text: url,
      });
      n++;
    }
    console.log('已寫入 studentWork', n, '筆（學生自己貼過網址', withUrl, '、沒選訊息略過', noSel, '）');
  }
})().catch(e => { console.error('失敗：', e.message); process.exit(1); });
