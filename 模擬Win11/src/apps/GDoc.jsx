// 線上文件（仿 Google 文件的「練習用」前端）：版面像、可做單一操作、每個動作都發事件供關卡判定。
// 刻意精簡：字型 2 種、文字顏色 3 種、字級 4 級、標題 3 級。版面概念參考 deeproop/google-doc-clone（程式為自寫）。
// 以 registerSite 掛在 https://docs.google.com/document/d/<id>/edit（見 apps/index.js）。
import React, { useEffect, useRef, useState } from "react";
import { MdUndo, MdRedo, MdPrint, MdFormatBold, MdFormatItalic, MdFormatUnderlined, MdFormatColorText, MdInsertLink, MdFormatAlignLeft, MdFormatAlignCenter, MdFormatAlignRight, MdFormatListBulleted, MdFormatListNumbered, MdFormatClear, MdAdd, MdRemove, MdArrowDropDown, MdStarBorder, MdStar, MdOutlineComment, MdLockOutline, MdPublic, MdCloudDone, MdOutlineFolder, MdCheck } from "react-icons/md";
import { sys, useSys } from "../kernel/store";
import { emit } from "../kernel/events";
import * as vfs from "../kernel/vfs";
import { known } from "../kernel/paths";
import { docUrl, ensureDoc, patchDoc, createDoc } from "../kernel/docs";

const FONTS = [["微軟正黑體", "Microsoft JhengHei"], ["標楷體", "DFKai-SB"]];
const COLORS = [["黑色", "#000000"], ["紅色", "#d93025"], ["藍色", "#1a73e8"]];
const SIZES = [11, 14, 18, 24];
const STYLES = [["一般文字", "p"], ["標題 1", "h1"], ["標題 2", "h2"], ["標題 3", "h3"]];

function Dropdown({ id, trigger, items, className = "", width }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    if (!open) return;
    const h = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", h, true);
    return () => document.removeEventListener("mousedown", h, true);
  }, [open]);
  return (
    <div className={"gd-dd " + className} ref={ref}>
      <button className={"gd-tbtn" + (open ? " on" : "")} data-sim-id={id} onMouseDown={(e) => e.preventDefault()} onClick={() => setOpen((v) => !v)}>{trigger}</button>
      {open && (
        <div className="gd-menu" style={width ? { minWidth: width } : null}>
          {items.map((it, i) => it.separator ? <div key={i} className="gd-msep" /> : (
            <div key={i} className={"gd-mitem" + (it.disabled ? " dis" : "")} data-sim-id={`${id}:${it.label}`} onMouseDown={(e) => e.preventDefault()}
              onClick={() => { if (it.disabled) return; setOpen(false); it.onClick && it.onClick(); }}>
              <span className="gd-mcheck">{it.checked ? <MdCheck /> : null}</span>
              {it.swatch && <i className="gd-swatch" style={{ background: it.swatch }} />}
              <span className="gd-mlabel" style={it.style}>{it.label}</span>
              {it.shortcut && <span className="gd-mshort">{it.shortcut}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// 工具列按鈕：mousedown 不取得焦點，編輯區的選取範圍才不會消失
function TB({ id, icon, label, on, onClick, disabled }) {
  return (
    <button className={"gd-tbtn" + (on ? " on" : "") + (disabled ? " dis" : "")} title={label} data-sim-id={"gdoc:tb:" + id} onMouseDown={(e) => e.preventDefault()} onClick={() => !disabled && onClick()}>{icon}</button>
  );
}

const Logo = () => (
  <svg width="30" height="40" viewBox="0 0 30 40" aria-hidden="true"><path d="M2 0h18l10 10v28a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2z" fill="#4285f4" /><path d="M20 0l10 10H22a2 2 0 0 1-2-2z" fill="#a1c2fa" /><path d="M7 20h16M7 25h16M7 30h11" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" /></svg>
);

export default function GDoc({ docId, nav }) {
  const doc = useSys((s) => s.docs[docId]);
  const page = useRef(null);
  const savedRange = useRef(null);
  const timer = useRef(null);
  const [status, setStatus] = useState("saved");
  const [fmt, setFmt] = useState({});
  const [starred, setStarred] = useState(false);
  const [share, setShare] = useState(false);
  const [linkBox, setLinkBox] = useState(null);
  const [email, setEmail] = useState("");
  const [titleEdit, setTitleEdit] = useState(null);
  const sid = (n) => "gdoc:" + n;

  useEffect(() => { ensureDoc(docId); }, [docId]);
  // 只在換文件時把內容灌進去（之後由編輯區自己維護，避免游標跳掉）
  useEffect(() => { if (page.current && doc) page.current.innerHTML = doc.html; /* eslint-disable-next-line */ }, [docId, !!doc]);
  useEffect(() => { document.addEventListener("selectionchange", readFmt); return () => document.removeEventListener("selectionchange", readFmt); }, []); // eslint-disable-line
  if (!doc) return null;

  const touch = () => {
    patchDoc(docId, { html: page.current.innerHTML });
    setStatus("saving");
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setStatus("saved"), 700);
  };
  const focusPage = () => { page.current.focus(); const r = savedRange.current; if (r && document.activeElement === page.current) { const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); } };
  const exec = (cmd, val, name = cmd) => {
    page.current.focus();
    document.execCommand(cmd, false, val);
    touch(); readFmt();
    emit("app:gdocs:format", { cmd: name, value: val ?? null });
  };
  const setSize = (pt) => {
    page.current.focus();
    document.execCommand("fontSize", false, "7");
    const fonts = Array.from(page.current.querySelectorAll('font[size="7"]'));
    fonts.forEach((f) => { f.removeAttribute("size"); f.style.fontSize = pt + "pt"; }); // 保留同一個 <font> 上的字型與顏色
    if (fonts.length) { const r = document.createRange(); r.setStartBefore(fonts[0]); r.setEndAfter(fonts[fonts.length - 1]); const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }
    touch(); readFmt();
    emit("app:gdocs:format", { cmd: "fontSize", value: pt });
  };

  // 讀目前選取範圍的格式，讓工具列按鈕顯示「按下」狀態
  function readFmt() {
    const s = window.getSelection();
    if (!s.rangeCount || !page.current || !page.current.contains(s.anchorNode)) return;
    const q = (c) => { try { return document.queryCommandState(c); } catch (e) { return false; } };
    const v = (c) => { try { return document.queryCommandValue(c); } catch (e) { return ""; } };
    const el = s.anchorNode.nodeType === 3 ? s.anchorNode.parentElement : s.anchorNode;
    const pt = Math.round(parseFloat(getComputedStyle(el).fontSize) * 0.75);
    const block = String(v("formatBlock")).toLowerCase().replace(/[<>]/g, "");
    const face = String(v("fontName")).replace(/["']/g, "");
    setFmt({
      bold: q("bold"), italic: q("italic"), underline: q("underline"), ul: q("insertUnorderedList"), ol: q("insertOrderedList"),
      left: q("justifyLeft"), center: q("justifyCenter"), right: q("justifyRight"),
      style: (STYLES.find(([, t]) => t === block) || STYLES[0])[0], size: pt,
      font: (FONTS.find(([n, e]) => face.includes(n) || face.includes(e)) || FONTS[0])[0],
    });
  }


  const download = (ext) => {
    const text = page.current.innerText;
    const name = `${doc.title}.${ext}`;
    let nm = name, n = 0;
    while (vfs.exists(vfs.join(known("downloads"), nm))) { n++; nm = `${doc.title} (${n}).${ext}`; }
    const p = vfs.create(known("downloads"), nm, "file", { content: text, auto: false });
    emit("app:gdocs:download", { id: docId, name: nm, path: p, ext });
  };
  const copy = () => { const t = window.getSelection().toString(); if (t) { sys.set((s) => ({ clipboard: { ...s.clipboard, text: t } })); emit("clipboard:text", { length: t.length }); } };
  const cut = () => { copy(); document.execCommand("delete"); touch(); };
  const paste = () => { const t = sys.get().clipboard.text; if (t) { page.current.focus(); document.execCommand("insertText", false, t); touch(); emit("app:gdocs:paste", { length: t.length }); } };
  const stub = (label) => ({ label, disabled: true });

  const onKeyDown = (e) => {
    const k = e.key.toLowerCase();
    if (e.ctrlKey && !e.altKey) {
      if (k === "z" && !e.shiftKey) { e.preventDefault(); exec("undo"); return; }
      if (k === "y" || (k === "z" && e.shiftKey)) { e.preventDefault(); exec("redo"); return; }
      if (k === "b") { e.preventDefault(); exec("bold"); return; }
      if (k === "i") { e.preventDefault(); exec("italic"); return; }
      if (k === "u") { e.preventDefault(); exec("underline"); return; }
      if (k === "a" && !e.isTrusted) { e.preventDefault(); document.execCommand("selectAll"); return; }
      if (!e.isTrusted) { // 自動操作送來的剪貼簿按鍵
        if (k === "c") { e.preventDefault(); copy(); return; }
        if (k === "x") { e.preventDefault(); cut(); return; }
        if (k === "v") { e.preventDefault(); paste(); return; }
      }
    }
  };

  const openLink = () => {
    const s = window.getSelection();
    savedRange.current = s.rangeCount ? s.getRangeAt(0).cloneRange() : null;
    setLinkBox({ url: "" });
  };
  const applyLink = () => {
    let url = (linkBox.url || "").trim();
    setLinkBox(null);
    if (!url) return;
    if (!/^https?:\/\//i.test(url)) url = "https://" + url;
    page.current.focus();
    const r = savedRange.current; if (r) { const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); }
    if (window.getSelection().isCollapsed) document.execCommand("insertHTML", false, `<a href="${url}">${url}</a>`);
    else document.execCommand("createLink", false, url);
    touch(); emit("app:gdocs:link", { url });
  };

  const menus = {
    "檔案": [
      { label: "新增", onClick: () => { const id = createDoc(); nav(docUrl(id)); } },
      { label: "開啟", disabled: true }, { label: "建立副本", disabled: true }, { separator: true },
      { label: "分享", onClick: () => setShare(true) },
      { label: "下載：Microsoft Word (.docx)", onClick: () => download("docx") },
      { label: "下載：純文字 (.txt)", onClick: () => download("txt") },
      { separator: true }, stub("列印"),
    ],
    "編輯": [
      { label: "復原", shortcut: "Ctrl+Z", onClick: () => exec("undo") }, { label: "重做", shortcut: "Ctrl+Y", onClick: () => exec("redo") }, { separator: true },
      { label: "剪下", shortcut: "Ctrl+X", onClick: cut }, { label: "複製", shortcut: "Ctrl+C", onClick: copy }, { label: "貼上", shortcut: "Ctrl+V", onClick: paste }, { separator: true },
      { label: "全選", shortcut: "Ctrl+A", onClick: () => { page.current.focus(); document.execCommand("selectAll"); } },
    ],
    "檢視": [stub("列印版面配置"), stub("顯示大綱"), stub("全螢幕")],
    "插入": [{ label: "連結", shortcut: "Ctrl+K", onClick: openLink }, stub("圖片"), stub("表格"), stub("分隔線")],
    "格式": [
      { label: "粗體", shortcut: "Ctrl+B", onClick: () => exec("bold") }, { label: "斜體", shortcut: "Ctrl+I", onClick: () => exec("italic") }, { label: "底線", shortcut: "Ctrl+U", onClick: () => exec("underline") },
      { separator: true }, { label: "清除格式", onClick: () => exec("removeFormat") },
    ],
    "工具": [stub("拼字及文法檢查"), stub("字數統計")],
    "說明": [stub("說明")],
  };

  const access = doc.share.access;
  const commitTitle = (v) => { setTitleEdit(null); const t = (v || "").trim() || "未命名文件"; if (t !== doc.title) { patchDoc(docId, { title: t }); emit("app:gdocs:title", { id: docId, title: t }); } };

  return (
    <div className="gd" data-sim-id={sid("root")}>
      <div className="gd-top">
        <div className="gd-logo"><Logo /></div>
        <div className="gd-titlewrap">
          <div className="gd-row1">
            {titleEdit != null ? (
              <input className="gd-title-input" autoFocus data-sim-id={sid("title:input")} value={titleEdit} onChange={(e) => setTitleEdit(e.target.value)} onFocus={(e) => e.target.select()} onBlur={() => commitTitle(titleEdit)}
                onKeyDown={(e) => { e.stopPropagation(); if (e.key === "Enter") commitTitle(titleEdit); else if (e.key === "Escape") setTitleEdit(null); }} />
            ) : <div className="gd-title" data-sim-id={sid("title")} onClick={() => setTitleEdit(doc.title)}>{doc.title}</div>}
            <button className="gd-ibtn" data-sim-id={sid("star")} onClick={() => { setStarred(!starred); emit("app:gdocs:star", { on: !starred }); }}>{starred ? <MdStar color="#f9ab00" /> : <MdStarBorder />}</button>
            <button className="gd-ibtn"><MdOutlineFolder /></button>
            <span className="gd-status" data-sim-id={sid("status")}><MdCloudDone />{status === "saved" ? "已儲存至雲端硬碟" : "儲存中…"}</span>
          </div>
          <div className="gd-menubar">
            {Object.entries(menus).map(([k, items]) => <Dropdown key={k} id={sid("menu:" + k)} className="gd-mb" trigger={k} items={items} width={240} />)}
          </div>
        </div>
        <button className="gd-ibtn big"><MdOutlineComment /></button>
        <button className="gd-share" data-sim-id={sid("share")} onClick={() => setShare(true)}>{access === "anyone" ? <MdPublic /> : <MdLockOutline />}分享</button>
        <div className="gd-avatar">學</div>
      </div>

      <div className="gd-toolbar" data-sim-id={sid("toolbar")}>
        <TB id="復原" icon={<MdUndo />} label="復原 (Ctrl+Z)" onClick={() => exec("undo")} />
        <TB id="重做" icon={<MdRedo />} label="重做 (Ctrl+Y)" onClick={() => exec("redo")} />
        <TB id="列印" icon={<MdPrint />} label="列印" disabled onClick={() => {}} />
        <span className="gd-tsep" />
        <Dropdown id={sid("tb:樣式")} className="gd-w110" trigger={<>{fmt.style || "一般文字"}<MdArrowDropDown /></>} items={STYLES.map(([n, t]) => ({ label: n, checked: fmt.style === n, onClick: () => exec("formatBlock", t, "style") }))} width={150} />
        <span className="gd-tsep" />
        <Dropdown id={sid("tb:字型")} className="gd-w110" trigger={<>{fmt.font || FONTS[0][0]}<MdArrowDropDown /></>} items={FONTS.map(([n, e]) => ({ label: n, checked: fmt.font === n, style: { fontFamily: `"${n}","${e}"` }, onClick: () => exec("fontName", n, "font") }))} width={150} />
        <span className="gd-tsep" />
        <TB id="縮小字級" icon={<MdRemove />} label="縮小字級" onClick={() => { const i = SIZES.indexOf(fmt.size); const cur = i < 0 ? SIZES.findIndex((x) => x >= (fmt.size || 11)) : i; setSize(SIZES[Math.max(0, (cur < 0 ? 0 : cur) - 1)]); }} />
        <div className="gd-size" data-sim-id={sid("tb:字級")}>{fmt.size || 11}</div>
        <TB id="放大字級" icon={<MdAdd />} label="放大字級" onClick={() => { const i = SIZES.indexOf(fmt.size); const cur = i < 0 ? SIZES.findIndex((x) => x >= (fmt.size || 11)) - 1 : i; setSize(SIZES[Math.min(SIZES.length - 1, Math.max(-1, cur) + 1)]); }} />
        <span className="gd-tsep" />
        <TB id="粗體" icon={<MdFormatBold />} label="粗體 (Ctrl+B)" on={fmt.bold} onClick={() => exec("bold")} />
        <TB id="斜體" icon={<MdFormatItalic />} label="斜體 (Ctrl+I)" on={fmt.italic} onClick={() => exec("italic")} />
        <TB id="底線" icon={<MdFormatUnderlined />} label="底線 (Ctrl+U)" on={fmt.underline} onClick={() => exec("underline")} />
        <Dropdown id={sid("tb:文字顏色")} trigger={<MdFormatColorText />} items={COLORS.map(([n, c]) => ({ label: n, swatch: c, onClick: () => exec("foreColor", c, "color") }))} width={150} />
        <span className="gd-tsep" />
        <TB id="連結" icon={<MdInsertLink />} label="插入連結 (Ctrl+K)" onClick={openLink} />
        <span className="gd-tsep" />
        <TB id="靠左對齊" icon={<MdFormatAlignLeft />} label="靠左對齊" on={fmt.left} onClick={() => exec("justifyLeft", null, "align")} />
        <TB id="置中對齊" icon={<MdFormatAlignCenter />} label="置中對齊" on={fmt.center} onClick={() => exec("justifyCenter", null, "align")} />
        <TB id="靠右對齊" icon={<MdFormatAlignRight />} label="靠右對齊" on={fmt.right} onClick={() => exec("justifyRight", null, "align")} />
        <span className="gd-tsep" />
        <TB id="項目符號清單" icon={<MdFormatListBulleted />} label="項目符號清單" on={fmt.ul} onClick={() => exec("insertUnorderedList", null, "bullets")} />
        <TB id="編號清單" icon={<MdFormatListNumbered />} label="編號清單" on={fmt.ol} onClick={() => exec("insertOrderedList", null, "numbered")} />
        <TB id="清除格式" icon={<MdFormatClear />} label="清除格式" onClick={() => exec("removeFormat")} />
      </div>

      <div className="gd-body">
        <div className="gd-scroll">
          <div className="gd-ruler" />
          <div className="gd-paper">
            <div ref={page} className="gd-page" contentEditable suppressContentEditableWarning spellCheck={false} data-sim-id={sid("page")}
              onInput={() => { touch(); emit("app:gdocs:edit", { id: docId }); }} onKeyDown={onKeyDown} onKeyUp={readFmt} onMouseUp={readFmt}
              onCopy={copy} onCut={() => { const t = window.getSelection().toString(); if (t) sys.set((s) => ({ clipboard: { ...s.clipboard, text: t } })); }} />
          </div>
        </div>
        <div className="gd-side"><i style={{ background: "#fbbc04" }} /><i style={{ background: "#34a853" }} /><i style={{ background: "#4285f4" }} /></div>
      </div>

      {linkBox && (
        <div className="gd-pop" data-sim-id={sid("link")}>
          <div className="gd-pop-h">連結</div>
          <input autoFocus placeholder="貼上或輸入連結" data-sim-id={sid("link:input")} value={linkBox.url} onChange={(e) => setLinkBox({ url: e.target.value })} onFocus={(e) => e.target.select()}
            onKeyDown={(e) => { e.stopPropagation(); if (e.key === "Enter") applyLink(); else if (e.key === "Escape") setLinkBox(null); }} />
          <div className="gd-pop-btns"><button data-sim-id={sid("link:cancel")} onClick={() => setLinkBox(null)}>取消</button><button className="p" data-sim-id={sid("link:apply")} onClick={applyLink}>套用</button></div>
        </div>
      )}

      {share && (
        <div className="gd-dim" onMouseDown={(e) => e.target === e.currentTarget && setShare(false)}>
          <div className="gd-dialog" data-sim-id={sid("share:dialog")}>
            <div className="gd-dialog-h">分享「{doc.title}」</div>
            <div className="gd-addrow">
              <input data-sim-id={sid("share:email")} placeholder="新增使用者和群組" value={email} onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => { e.stopPropagation(); if (e.key === "Enter" && email.trim()) { patchDoc(docId, { share: { ...doc.share, people: [...doc.share.people, email.trim()] } }); emit("app:gdocs:share-add", { email: email.trim() }); setEmail(""); } }} />
              <button className="gd-add" data-sim-id={sid("share:add")} onClick={() => { if (email.trim()) { patchDoc(docId, { share: { ...doc.share, people: [...doc.share.people, email.trim()] } }); emit("app:gdocs:share-add", { email: email.trim() }); setEmail(""); } }}>新增</button>
            </div>
            <div className="gd-sec">有權存取的使用者</div>
            <div className="gd-person"><div className="gd-avatar sm">學</div><div className="gd-pname">學生（你）<small>student@example.com</small></div><span className="gd-owner">擁有者</span></div>
            {doc.share.people.map((p, i) => <div key={i} className="gd-person" data-sim-id={sid("share:person:" + p)}><div className="gd-avatar sm g">{p[0].toUpperCase()}</div><div className="gd-pname">{p}</div><span className="gd-owner">檢視者</span></div>)}
            <div className="gd-sec">一般存取權</div>
            <div className="gd-person">
              <div className={"gd-avatar sm " + (access === "anyone" ? "gr" : "")}>{access === "anyone" ? <MdPublic /> : <MdLockOutline />}</div>
              <div className="gd-pname">
                <Dropdown id={sid("share:access")} className="gd-acc" trigger={<>{access === "anyone" ? "知道連結的任何人" : "受限"}<MdArrowDropDown /></>}
                  items={[{ label: "受限", checked: access === "restricted", onClick: () => { patchDoc(docId, { share: { ...doc.share, access: "restricted" } }); emit("app:gdocs:share-access", { access: "restricted" }); } }, { label: "知道連結的任何人", checked: access === "anyone", onClick: () => { patchDoc(docId, { share: { ...doc.share, access: "anyone" } }); emit("app:gdocs:share-access", { access: "anyone" }); } }]} width={190} />
                <small>{access === "anyone" ? "知道這個連結的任何人都可以檢視" : "只有具備存取權的使用者可以透過這個連結開啟"}</small>
              </div>
            </div>
            <div className="gd-dialog-f">
              <button className="gd-copy" data-sim-id={sid("share:copy")} onClick={() => { sys.set((s) => ({ clipboard: { ...s.clipboard, text: docUrl(docId) } })); emit("app:gdocs:copylink", { url: docUrl(docId) }); }}>🔗 複製連結</button>
              <button className="gd-done" data-sim-id={sid("share:done")} onClick={() => { setShare(false); emit("app:gdocs:share-done", { access, people: doc.share.people }); }}>完成</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
