// 用服務帳號憑證（D:\keys\worksheet-f47f3-firebase-adminsdk*.json）把學生的作答（cardWork）和對話（aiHistory）整份下載成 JSON，
// 給「匯出參賽資料.py」用。含學生姓名與完整對話，只存在本機，已列入 .gitignore，不要 commit。
// 用法：工作台\runtime\node\node.exe 下載雲端資料.js 輸出檔.json
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const https = require('https');

const KEYDIR = 'D:\\keys';
const OUT = process.argv[2] || path.join(__dirname, '..', '學生對話紀錄', '_輸出', '雲端資料.json');
const keyFile = fs.readdirSync(KEYDIR).find(n => n.startsWith('worksheet-f47f3-firebase-adminsdk'));
if (!keyFile) { console.error('找不到 worksheet-f47f3 的服務帳號金鑰（D:\\keys）'); process.exit(1); }
const sa = JSON.parse(fs.readFileSync(path.join(KEYDIR, keyFile), 'utf8'));
const BASE = `https://firestore.googleapis.com/v1/projects/${sa.project_id}/databases/(default)/documents`;

function b64u(b) { return Buffer.from(b).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_'); }
function req(method, url, headers, body) {
  return new Promise((res, rej) => {
    const u = new URL(url);
    const r = https.request({ method, hostname: u.hostname, path: u.pathname + u.search, headers }, resp => {
      const ch = []; resp.on('data', c => ch.push(c)); resp.on('end', () => { const d = Buffer.concat(ch).toString('utf8');
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
  const body = 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + head + '.' + claim + '.' + b64u(sig);
  const j = await req('POST', 'https://oauth2.googleapis.com/token', { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) }, body);
  return j.access_token;
}
// Firestore REST 的型別值 → 一般 JS 值
function dec(v) {
  if ('stringValue' in v) return v.stringValue;
  if ('integerValue' in v) return Number(v.integerValue);
  if ('doubleValue' in v) return v.doubleValue;
  if ('booleanValue' in v) return v.booleanValue;
  if ('nullValue' in v) return null;
  if ('timestampValue' in v) return v.timestampValue;
  if ('arrayValue' in v) return (v.arrayValue.values || []).map(dec);
  if ('mapValue' in v) { const o = {}; const f = v.mapValue.fields || {}; Object.keys(f).forEach(k => { o[k] = dec(f[k]); }); return o; }
  return null;
}
async function all(tk, coll) {
  const out = {}; let page = '';
  do {
    const j = await req('GET', `${BASE}/${coll}?pageSize=100${page ? '&pageToken=' + page : ''}`, { Authorization: 'Bearer ' + tk });
    (j.documents || []).forEach(d => {
      const o = {}; Object.keys(d.fields || {}).forEach(k => { o[k] = dec(d.fields[k]); });
      out[d.name.split('/').pop()] = o;
    });
    page = j.nextPageToken || '';
  } while (page);
  return out;
}
(async () => {
  const tk = await token();
  const cardWork = await all(tk, 'cardWork'), aiHistory = await all(tk, 'aiHistory');
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify({ downloadedAt: new Date().toISOString(), cardWork, aiHistory }), 'utf8');
  console.log('已下載：cardWork ' + Object.keys(cardWork).length + ' 份、aiHistory ' + Object.keys(aiHistory).length + ' 份 → ' + OUT);
})().catch(e => { console.error('下載失敗：', e.message); process.exit(1); });
