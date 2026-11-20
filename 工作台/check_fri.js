// 五上 L05 週五版：檢查各班學生的作答狀況（唯讀，只讀不寫）。
// 用 Firebase 服務帳號（金鑰在老師電腦 D:\keys\，不進 git）讀 Firestore 的 submissions，
// 依學習單自己的判定規則（engine_L05_fri.js）算每位學生每一欄有沒有拿到星星，列出沒完成的座號與差多少，
// 統計大家最常卡的地方，並為每班寫一則給學生看的公告草稿。
//
// 用法（專案根目錄）：
//   工作台\runtime\node\node.exe 工作台\check_fri.js 501 505 510
//   工作台\runtime\node\node.exe 工作台\check_fri.js 501 505 510 --n 501=26,505=25,510=27   ← 給各班人數，才找得出完全沒交的座號
//   選項：--ws g5-L05-fri（學習單 id，預設就是週五版）  --out 資料夾（預設 課程進度/_本機）
//
// 班級代碼＝年級＋兩位班號：501＝五年 1 班、510＝五年 10 班。
// 隱私：報告與公告只出現「班級＋座號」，不出現姓名（繳交資料本來就只有年級／班級／座號）。
// 輸出檔放在 課程進度/_本機/（已被 .gitignore 排除，不會進 git）。
'use strict';
const fs = require('fs');
const path = require('path');

// ───────────── 判定規則：與 engine_L05_fri.js 完全一致 ─────────────
const STAR_MIN = 5;                                   // 要寫的字「超過 5 個字」（空白不算）就給星星
const URL_RE = /^https?:\/\/[^\s]+$/i;
const OK_HOST = /(^|\.)(tfc-taiwan\.org\.tw|mygopen\.com)$/i;
const JUDGE = /假的|不是真|謠言|不實|造謠|錯誤|誤導|詐騙|騙人|不可信|不要相信|別相信/;
const RE_WHERE = /流傳|LINE|Line|臉書|FB|IG|Threads|YouTube|TikTok|抖音|網路|群組|轉傳|社群|傳/;
const RE_WHO_SAID = /根據|說|表示|指出|MyGoPen|查核中心|警方|165|衛福|專家|機構|官方|消防|氣象/;
const RE_FEEL = /怕|擔心|緊張|恐慌|好奇|驚奇|厲害|神奇|想幫|幫忙|關心|家人|救人|好康|免費|便宜|搶|相信|信任|朋友|親友|感動|生氣|有趣/;
const RE_WHO = /有人|我|大家|家人|別人|老人|長輩|學生|小孩|同學|朋友|民眾|他們|人們|陌生人|消費者|媽媽|爸爸|阿公|阿嬤/;

const FIELDS = [   // 與學習單 7 欄同順序
  { qid: 'url', name: '查核網址' }, { qid: 'tool', name: '搜尋工具' }, { qid: 'desc', name: '原始內容描述' },
  { qid: 'res', name: '查核結果' }, { qid: 'fact', name: '正確資訊' }, { qid: 'why', name: '為什麼會流傳' }, { qid: 'risk', name: '相信的後果' },
];

const tr = v => String(v == null ? '' : v).trim();
const len = v => tr(v).replace(/\s/g, '').length;
const hasKw = s => (s.toolKinds || []).indexOf('關鍵字搜尋') >= 0;

// 一欄的狀態：{star, state:'star'|'short'|'empty', short?:要再多寫幾個字, why?:原因}
function fieldStatus(qid, s) {
  const need = n => Math.max(0, STAR_MIN + 1 - n);          // 超過 5 個字 → 至少 6 個字
  switch (qid) {
    case 'url': {
      const u = tr(s.url);
      if (!u) return { star: false, state: 'empty', why: '沒貼網址' };
      if (!URL_RE.test(u)) return { star: false, state: 'short', why: '不是網址（要 https:// 開頭、只有網址）' };
      return { star: true, state: 'star' };
    }
    case 'tool': {
      if (!(s.toolKinds || []).length) return { star: false, state: 'empty', why: '沒選工具' };
      if (hasKw(s)) {
        const n = len(s.toolB);
        if (!n) return { star: false, state: 'empty', why: '選了關鍵字搜尋，沒寫「我輸入的是」' };
        if (n <= STAR_MIN) return { star: false, state: 'short', short: need(n), why: '「我輸入的是」太短' };
      }
      return { star: true, state: 'star' };
    }
    case 'res': {
      const miss = [];
      if (!tr(s.resOrg)) miss.push('哪一家'); if (!tr(s.resLabel)) miss.push('標籤');
      const n = len(s.resNote);
      if (miss.length || !n) return { star: false, state: (miss.length === 2 && !n) ? 'empty' : 'short', why: '還沒選或沒寫：' + miss.concat(n ? [] : ['一句重點']).join('、') };
      if (n <= STAR_MIN) return { star: false, state: 'short', short: need(n), why: '「一句重點」太短' };
      return { star: true, state: 'star' };
    }
    default: {
      const t = { desc: s.desc, fact: s.fact, why: s.whyText, risk: s.riskText }[qid];
      const n = len(t);
      if (!n) return { star: false, state: 'empty', why: '沒寫' };
      if (n <= STAR_MIN) return { star: false, state: 'short', short: need(n), why: '字數不夠' };
      return { star: true, state: 'star' };
    }
  }
}

// 「品質提醒」：不影響星星，但是老師口頭提醒的重點（對應學習單檢查表）
function qualityNotes(s) {
  const out = [];
  const u = tr(s.url);
  if (URL_RE.test(u)) {
    let host = ''; try { host = new URL(u).hostname; } catch (e) {}
    if (!OK_HOST.test(host)) out.push({ key: 'url_host', qid: 'url', text: '網址不是查核機構自己的網站（要 mygopen.com 或 tfc-taiwan.org.tw，轉載不算）' });
    if (!/^https:\/\//i.test(u)) out.push({ key: 'url_https', qid: 'url', text: '網址開頭不是 https://' });
  }
  if (hasKw(s) && len(s.toolB) && !/查核/.test(s.toolB)) out.push({ key: 'tool_chahe', qid: 'tool', text: '用關鍵字搜尋，輸入的字最後沒有加「查核」' });
  const d = tr(s.desc);
  if (d) {
    if (len(d) < 30) out.push({ key: 'desc_short', qid: 'desc', text: '原始內容描述太短（建議 30 字以上，寫出什麼事、會怎樣、在哪裡流傳）' });
    if (!RE_WHERE.test(d)) out.push({ key: 'desc_where', qid: 'desc', text: '原始內容描述沒說在哪裡流傳' });
    const m = d.match(JUDGE); if (m) out.push({ key: 'desc_judge', qid: 'desc', text: '原始內容描述寫了真假判斷（例如「' + m[0] + '」），描述只寫看到什麼' });
  }
  const f = tr(s.fact);
  if (f) {
    if (len(f) < 20) out.push({ key: 'fact_short', qid: 'fact', text: '正確資訊太短（建議 20 字以上）' });
    if (!RE_WHO_SAID.test(f)) out.push({ key: 'fact_who', qid: 'fact', text: '正確資訊沒寫是誰說的（根據○○／○○說）' });
    if (f.split(/\n+/).some(x => x.trim().length > 110)) out.push({ key: 'fact_copy', qid: 'fact', text: '正確資訊有一句太長，可能是整段複製，要改成自己的話' });
  }
  const w = tr(s.whyText);
  if (w) { if (len(w) < 15) out.push({ key: 'why_short', qid: 'why', text: '為什麼會流傳太短（建議 15 字以上）' }); if (!RE_FEEL.test(w)) out.push({ key: 'why_feel', qid: 'why', text: '為什麼會流傳沒說讓人有什麼感覺（怕？好奇？想幫忙？）' }); }
  const r = tr(s.riskText);
  if (r) { if (!RE_WHO.test(r)) out.push({ key: 'risk_who', qid: 'risk', text: '相信的後果沒寫「誰」' }); if (len(r) < 15) out.push({ key: 'risk_short', qid: 'risk', text: '相信的後果太短，要寫出「誰會怎樣」' }); }
  const n = tr(s.resNote);
  if (n && len(n) < 10) out.push({ key: 'res_short', qid: 'res', text: '查核結果的一句重點太短（建議 10 字以上）' });
  return out;
}

// ───────────── 分析：subs＝Firestore 讀回的 submissions（已轉成一般物件） ─────────────
function analyze(subs, classes, rosterN) {
  const res = {};
  classes.forEach(c => { res[c] = { code: c, students: {}, n: rosterN[c] || null }; });
  subs.forEach(sub => {
    const code = String(Number(sub.grade) * 100 + Number(sub.className)).padStart(3, '0');
    if (!res[code]) return;
    const seat = Number(sub.studentId);
    const s = sub.parts || {};
    const ck = sub.checkpoint || {};
    const fields = {}; let stars = 0;
    FIELDS.forEach(f => { fields[f.qid] = fieldStatus(f.qid, s); if (fields[f.qid].star) stars++; });
    const row = { seat, stars, fields, notes: qualityNotes(s), final: ck.final !== false, step: ck.stepName || '', sel: s.sel || '' };
    const old = res[code].students[seat];
    if (!old || stars >= old.stars) res[code].students[seat] = row;     // 同座號重複（共用電腦）取較完整的一筆
  });
  return res;
}

function summarize(cls) {
  const seats = Object.keys(cls.students).map(Number).sort((a, b) => a - b);
  const done = seats.filter(s => cls.students[s].stars === FIELDS.length);
  const todo = seats.filter(s => cls.students[s].stars < FIELDS.length);
  const notSubmitted = cls.n ? Array.from({ length: cls.n }, (_, i) => i + 1).filter(s => !cls.students[s]) : null;
  const dist = {}; seats.forEach(s => { dist[cls.students[s].stars] = (dist[cls.students[s].stars] || 0) + 1; });
  // 各欄沒拿到星的人數
  const fieldMiss = {}; FIELDS.forEach(f => { fieldMiss[f.qid] = seats.filter(s => !cls.students[s].fields[f.qid].star); });
  // 品質提醒統計（各種提醒各幾人）
  const noteCount = {}; seats.forEach(s => cls.students[s].notes.forEach(n => { (noteCount[n.key] = noteCount[n.key] || { text: n.text, qid: n.qid, seats: [] }).seats.push(s); }));
  return { seats, done, todo, notSubmitted, dist, fieldMiss, noteCount };
}

const fname = q => FIELDS.find(f => f.qid === q).name;
const seatList = a => a.length ? a.join('、') : '（無）';
const pct = (a, b) => b ? Math.round(a / b * 100) + '%' : '-';

function gapText(row) {
  const parts = [];
  FIELDS.forEach(f => {
    const st = row.fields[f.qid];
    if (st.star) return;
    parts.push(f.name + (st.state === 'empty' ? '（沒寫）' : st.short ? `（再多寫 ${st.short} 個字）` : `（${st.why}）`));
  });
  return parts.join('、');
}

function reportFor(cls) {
  const sm = summarize(cls);
  const total = sm.seats.length;
  const L = [];
  L.push(`## ${cls.code} 班（${cls.code[0]}年${Number(cls.code.slice(1))}班）`);
  L.push('');
  L.push(`- 有繳交（含先存檔）：${total} 人${cls.n ? ` ／ 全班 ${cls.n} 人` : '（沒給全班人數，看不出誰完全沒交）'}`);
  L.push(`- **7 顆星全收集（完成）：${sm.done.length} 人**（${pct(sm.done.length, cls.n || total)}）`);
  L.push(`- 還沒完成：${sm.todo.length} 人` + (sm.notSubmitted ? `；完全沒交：${sm.notSubmitted.length} 人` : ''));
  L.push(`- 星星分布：` + [7, 6, 5, 4, 3, 2, 1, 0].filter(k => sm.dist[k]).map(k => `${k} 顆 ${sm.dist[k]} 人`).join('，'));
  L.push('');
  L.push('### 沒完成的座號（差多少）');
  L.push('');
  if (!sm.todo.length && !(sm.notSubmitted || []).length) L.push('全部完成。');
  else {
    L.push('| 座號 | 星星 | 差幾顆 | 還缺什麼 | 狀態 |', '|---|---|---|---|---|');
    sm.todo.sort((a, b) => cls.students[b].stars - cls.students[a].stars || a - b).forEach(s => {
      const r = cls.students[s];
      L.push(`| ${s} | ${r.stars}／7 | ${7 - r.stars} | ${gapText(r)} | ${r.final ? '已繳交' : '先存檔，停在「' + r.step + '」'} |`);
    });
    if (sm.notSubmitted && sm.notSubmitted.length) L.push('', `完全沒交（沒有任何存檔）：${seatList(sm.notSubmitted)}`);
  }
  L.push('');
  L.push('### 各欄還沒拿到星的人數');
  L.push('');
  L.push('| 欄位 | 人數 | 座號 |', '|---|---|---|');
  FIELDS.forEach(f => L.push(`| ${f.name} | ${sm.fieldMiss[f.qid].length} | ${seatList(sm.fieldMiss[f.qid])} |`));
  L.push('');
  L.push('### 寫得怎麼樣：常見的問題（不影響星星，是口頭提醒的重點）');
  L.push('');
  const ranked = Object.values(sm.noteCount).sort((a, b) => b.seats.length - a.seats.length);
  if (!ranked.length) L.push('沒有明顯問題。');
  else { L.push('| 問題 | 人數 | 佔有繳交的 |', '|---|---|---|'); ranked.forEach(n => L.push(`| ${n.text} | ${n.seats.length} | ${pct(n.seats.length, total)} |`)); }
  L.push('');
  return { text: L.join('\n'), sm };
}

// 給學生看的公告：不點名座號（公開列出誰沒完成會讓同學難堪）；座號清單只在給老師的報告裡
const TIPS = {
  url_host: '貼的網址要是「查核機構自己」的網站（網址裡有 mygopen 或 tfc-taiwan），新聞或臉書轉載的不算。',
  tool_chahe: '用關鍵字搜尋時，搜尋的字最後要加「查核」。',
  desc_judge: '「原始內容描述」只寫看到什麼，不寫「是假的」「不要相信」，真假留到下一欄。',
  desc_where: '「原始內容描述」最後要說這則訊息在哪裡流傳（LINE、臉書…），看不出來就寫「網路上」。',
  desc_short: '「原始內容描述」多寫一點：說了什麼事、說會怎樣、在哪裡流傳。',
  fact_who: '「正確資訊」每一點要寫出是誰說的，例如「根據 MyGoPen，…」「警方說，…」。',
  fact_copy: '「正確資訊」不要整段複製，用自己的話寫成一句。',
  why_feel: '「為什麼會流傳」要寫出這句話讓人有什麼感覺（怕？好奇？想幫忙？），再看 5 種原因對照。',
  risk_who: '「相信的後果」要寫出「誰」會怎樣，例如「有人相信以後，會…」。',
  risk_short: '「相信的後果」要寫完整：誰會怎樣。',
};
function announcementFor(cls, sm) {
  const total = sm.seats.length, ranked = Object.entries(sm.noteCount).filter(([k]) => TIPS[k]).sort((a, b) => b[1].seats.length - a[1].seats.length).slice(0, 3);
  const L = [];
  L.push(`【訊息查證小偵探】${cls.code} 班進度`);
  L.push('');
  const left = sm.todo.length + ((sm.notSubmitted || []).length);
  L.push(`目前有 ${sm.done.length} 位同學收集了 7 顆 ★，很棒！${left ? `還有同學還沒收集完，請找時間補完。` : '全班都完成了！'}`);
  if (left) {
    const missMost = FIELDS.map(f => ({ f, n: sm.fieldMiss[f.qid].length })).filter(x => x.n).sort((a, b) => b.n - a.n).slice(0, 3);
    L.push('');
    L.push('怎麼補：');
    L.push('1. 打開學習單，填好年級、班級、座號，按「拿回我上次存的進度」。');
    L.push('2. 看上面的星星：☆ 是還沒拿到的欄位，點進去寫超過 5 個字就會拿到 ★。');
    if (missMost.length) L.push(`3. 最多同學還缺的是：${missMost.map(x => x.f.name).join('、')}。`);
    L.push('4. 全部寫完，到最後一步按「繳交學習單」。');
  }
  if (ranked.length) {
    L.push('');
    L.push('寫的時候要注意（很多同學都犯過）：');
    ranked.forEach(([k], i) => L.push(`${i + 1}. ${TIPS[k]}`));
  }
  L.push('');
  L.push('不會的地方，每一欄都有「看老師怎麼做」的示範影片，可以按「再看一次示範」。');
  return L.join('\n');
}

// ───────────── Firestore 讀取（服務帳號，只讀） ─────────────
function firestoreClient() {
  const crypto = require('crypto'), https = require('https');
  const KEYDIR = process.env.FIREBASE_KEYDIR || 'D:\\keys';
  const keyFile = fs.readdirSync(KEYDIR).find(n => n.startsWith('pcclass-94300-firebase-adminsdk'));
  if (!keyFile) throw new Error('找不到 pcclass-94300 的服務帳號金鑰（' + KEYDIR + '）');
  const sa = JSON.parse(fs.readFileSync(path.join(KEYDIR, keyFile), 'utf8'));
  const b64u = b => Buffer.from(b).toString('base64').replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  const req = (method, url, headers, body) => new Promise((res, rej) => {
    const u = new URL(url);
    const r = https.request({ method, hostname: u.hostname, path: u.pathname + u.search, headers }, resp => {
      let d = ''; resp.on('data', c => d += c); resp.on('end', () => {
        let j; try { j = JSON.parse(d); } catch (e) { j = d; }
        if (resp.statusCode >= 300) rej(new Error(resp.statusCode + ' ' + (typeof j === 'string' ? j : JSON.stringify(j)).slice(0, 300))); else res(j);
      });
    }); r.on('error', rej); if (body) r.write(body); r.end();
  });
  const dec = v => {
    if (v == null) return null;
    if ('stringValue' in v) return v.stringValue; if ('integerValue' in v) return Number(v.integerValue);
    if ('doubleValue' in v) return v.doubleValue; if ('booleanValue' in v) return v.booleanValue; if ('nullValue' in v) return null;
    if ('timestampValue' in v) return v.timestampValue;
    if ('arrayValue' in v) return (v.arrayValue.values || []).map(dec);
    if ('mapValue' in v) { const o = {}; for (const k in (v.mapValue.fields || {})) o[k] = dec(v.mapValue.fields[k]); return o; }
    return null;
  };
  async function token() {
    const now = Math.floor(Date.now() / 1000);
    const head = b64u(JSON.stringify({ alg: 'RS256', typ: 'JWT' }));
    const claim = b64u(JSON.stringify({ iss: sa.client_email, scope: 'https://www.googleapis.com/auth/datastore', aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3000 }));
    const sig = crypto.createSign('RSA-SHA256').update(head + '.' + claim).sign(sa.private_key);
    const body = 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + head + '.' + claim + '.' + b64u(sig);
    return (await req('POST', 'https://oauth2.googleapis.com/token', { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) }, body)).access_token;
  }
  return {
    async submissions(ws) {                        // 只做 runQuery（讀），沒有任何寫入
      const tk = await token();
      const url = `https://firestore.googleapis.com/v1/projects/${sa.project_id}/databases/(default)/documents:runQuery`;
      const body = JSON.stringify({ structuredQuery: { from: [{ collectionId: 'submissions' }], where: { fieldFilter: { field: { fieldPath: 'worksheetId' }, op: 'EQUAL', value: { stringValue: ws } } } } });
      const rows = await req('POST', url, { Authorization: 'Bearer ' + tk, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }, body);
      return rows.filter(r => r.document).map(r => { const o = {}; for (const k in r.document.fields) o[k] = dec(r.document.fields[k]); return o; });
    },
  };
}

async function main() {
  const argv = process.argv.slice(2), classes = [], opt = { ws: 'g5-L05-fri', n: {}, out: path.join(__dirname, '..', '課程進度', '_本機') };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--ws') opt.ws = argv[++i];
    else if (argv[i] === '--out') opt.out = argv[++i];
    else if (argv[i] === '--n') argv[++i].split(',').forEach(p => { const [c, n] = p.split('='); opt.n[c.trim()] = Number(n); });
    else if (/^\d{3}$/.test(argv[i])) classes.push(argv[i]);
    else { console.error('看不懂的參數：' + argv[i] + '\n用法：node check_fri.js 501 505 510 [--n 501=26,505=25] [--ws g5-L05-fri] [--out 資料夾]'); process.exit(2); }
  }
  if (!classes.length) { console.error('請至少給一個班級代碼，例如：node check_fri.js 501 505 510'); process.exit(2); }
  const subs = await firestoreClient().submissions(opt.ws);
  console.log(`讀到 ${opt.ws} 共 ${subs.length} 筆繳交`);
  const res = analyze(subs, classes, opt.n);
  fs.mkdirSync(opt.out, { recursive: true });
  const all = [`# 五上 L05 週五版：作答檢查（${opt.ws}）`, '', `產生時間：${new Date().toLocaleString('zh-TW', { hour12: false })}`, '',
    `判定規則：一欄必填的都有寫、要寫的文字超過 ${STAR_MIN} 個字（空白不算）才拿到 ★；7 欄都有 ★ ＝ 完成。`, '只出現班級與座號，不含姓名。', ''];
  classes.forEach(c => {
    const { text, sm } = reportFor(res[c]);
    all.push(text);
    fs.writeFileSync(path.join(opt.out, `公告_${c}.txt`), announcementFor(res[c], sm) + '\n', 'utf8');
    console.log(`${c}：有繳交 ${sm.seats.length} 人，完成 ${sm.done.length} 人，沒完成 ${sm.todo.length} 人` + (sm.notSubmitted ? `，完全沒交 ${sm.notSubmitted.length} 人` : ''));
  });
  const rp = path.join(opt.out, 'fri_報告.md'); fs.writeFileSync(rp, all.join('\n'), 'utf8');
  console.log('\n報告：' + rp + '\n公告草稿：' + path.join(opt.out, '公告_<班級>.txt') + '（給學生看，不點名座號）');
}

module.exports = { fieldStatus, qualityNotes, analyze, summarize, reportFor, announcementFor, FIELDS, STAR_MIN };
if (require.main === module) main().catch(e => { console.error('失敗：', e.message); process.exit(1); });
