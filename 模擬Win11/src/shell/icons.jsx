// 內建向量圖示（自繪，不需外部圖檔）。用法：<Ico name="folder" size={20} />
// 名稱以 "img:" 開頭＝用 public/ 底下的圖檔（例：img:images/apps/edge.png）。
import React from "react";
import { extOf } from "../kernel/vfs";

export const asset = (p) => `${process.env.PUBLIC_URL || "."}/${String(p).replace(/^\//, "")}`;

const Page = ({ color, label, extra }) => (
  <>
    <path d="M7 2h13l6 6v20a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" fill="#f4f6f8" stroke="#aeb7c2" strokeWidth="1" />
    <path d="M20 2v4a2 2 0 0 0 2 2h4z" fill="#d6dbe1" />
    {label && (
      <>
        <rect x="3" y="14" width="16" height="11" rx="2" fill={color} />
        <text x="11" y="22.6" fontSize="8.5" fontWeight="700" fill="#fff" textAnchor="middle" fontFamily="Segoe UI, Arial">{label}</text>
      </>
    )}
    {extra}
  </>
);

const Folder = ({ glyph }) => (
  <>
    <path d="M2 8a3 3 0 0 1 3-3h7l3 3h12a3 3 0 0 1 3 3v2H2z" fill="#E3A93A" />
    <path d="M2 12a2 2 0 0 1 2-2h24a2 2 0 0 1 2 2v13a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3z" fill="#FFD067" />
    {glyph}
  </>
);

const ICONS = {
  folder: () => <Folder />,
  "folder-desktop": () => <Folder glyph={<rect x="9" y="14" width="14" height="9" rx="1.5" fill="#3b82f6" stroke="#fff" strokeWidth="1" />} />,
  "folder-downloads": () => <Folder glyph={<path d="M16 14v8m-4-4l4 4 4-4" stroke="#16a34a" strokeWidth="2.4" fill="none" strokeLinecap="round" strokeLinejoin="round" />} />,
  "folder-documents": () => <Folder glyph={<g><rect x="10" y="13" width="12" height="11" rx="1" fill="#fff" /><path d="M12 17h8M12 20h8" stroke="#9aa5b1" strokeWidth="1.2" /></g>} />,
  "folder-pictures": () => <Folder glyph={<g><rect x="9" y="13" width="14" height="11" rx="1.5" fill="#fff" /><circle cx="13" cy="17" r="1.4" fill="#f59e0b" /><path d="M10 23l4-4 3 3 2-2 4 4z" fill="#16a34a" /></g>} />,
  "folder-music": () => <Folder glyph={<path d="M19 14v7.5a2.3 2.3 0 1 1-1.4-2.1V16l-4 1v5a2.3 2.3 0 1 1-1.4-2.1V15z" fill="#e11d48" />} />,
  "folder-videos": () => <Folder glyph={<g><rect x="9" y="14" width="14" height="9" rx="1.5" fill="#7c3aed" /><path d="M15 16.5l4 2-4 2z" fill="#fff" /></g>} />,
  "folder-user": () => <Folder glyph={<g><circle cx="16" cy="16.5" r="2.6" fill="#fff" /><path d="M10.5 24c.6-3 2.7-4.4 5.5-4.4s4.9 1.4 5.5 4.4z" fill="#fff" /></g>} />,
  file: () => <Page />,
  "file-txt": () => <Page extra={<path d="M9 13h10M9 16.5h14M9 20h14M9 23.5h9" stroke="#8b96a3" strokeWidth="1.3" strokeLinecap="round" />} />,
  "file-docx": () => <Page color="#2b6cd9" label="W" />,
  "file-xlsx": () => <Page color="#1f8f4e" label="X" />,
  "file-pptx": () => <Page color="#d1511f" label="P" />,
  "file-pdf": () => <Page color="#d63a3a" label="PDF" />,
  "file-zip": () => <Page color="#d19b1f" label="ZIP" />,
  "file-mp3": () => <Page color="#e11d48" label="♪" />,
  "file-mp4": () => <Page color="#7c3aed" label="▶" />,
  "file-html": () => <Page color="#0ea5e9" label="</>" />,
  "file-exe": () => <Page color="#475569" label="EXE" />,
  "file-img": () => (
    <g>
      <rect x="3" y="5" width="26" height="22" rx="2.5" fill="#fff" stroke="#aeb7c2" />
      <rect x="5" y="7" width="22" height="18" rx="1.5" fill="#bfe3ff" />
      <circle cx="21" cy="12" r="2.4" fill="#fbbf24" />
      <path d="M5 25l8-9 5 5 3-3 6 7z" fill="#34a853" />
    </g>
  ),
  drive: () => (
    <g>
      <rect x="2" y="9" width="28" height="14" rx="3" fill="#cfd6df" stroke="#9aa5b1" />
      <rect x="4" y="11" width="24" height="7" rx="1.5" fill="#eef1f5" />
      <circle cx="25" cy="20.5" r="1.3" fill="#22c55e" />
      <path d="M6 20.5h8" stroke="#9aa5b1" strokeWidth="1.5" strokeLinecap="round" />
    </g>
  ),
  thisPC: () => (
    <g>
      <rect x="3" y="5" width="26" height="17" rx="2" fill="#2a2f3a" />
      <rect x="4.6" y="6.6" width="22.8" height="13.8" rx="1" fill="#4aa3ff" />
      <path d="M4.6 6.6h22.8v6.5L4.6 18z" fill="#7cc0ff" />
      <rect x="12" y="23" width="8" height="2.5" fill="#8a94a1" />
      <rect x="8" y="25.5" width="16" height="2" rx="1" fill="#aab3be" />
    </g>
  ),
  recycle: () => (
    <g>
      <path d="M8 9h16l-1.5 18a2 2 0 0 1-2 1.8h-9a2 2 0 0 1-2-1.8z" fill="#dfe6ee" stroke="#9aa5b1" />
      <rect x="6" y="6" width="20" height="3.4" rx="1.4" fill="#c4ccd6" stroke="#9aa5b1" />
      <path d="M12 12v13M16 12v13M20 12v13" stroke="#aab3be" strokeWidth="1.4" />
      <path d="M12.5 15.5l1.6-2.4 1.5 1.6m-1.5-1.6 3 1m3.5 4.2l-1.6 2.4-1.5-1.6" stroke="#2f9e44" strokeWidth="1.3" fill="none" strokeLinecap="round" opacity=".0" />
    </g>
  ),
  "recycle-full": () => (
    <g>
      <path d="M8 9h16l-1.5 18a2 2 0 0 1-2 1.8h-9a2 2 0 0 1-2-1.8z" fill="#dfe6ee" stroke="#9aa5b1" />
      <rect x="6" y="6" width="20" height="3.4" rx="1.4" fill="#c4ccd6" stroke="#9aa5b1" />
      <path d="M10 8l3-4 3 3 3-3 3 4z" fill="#fff" stroke="#c0c8d2" />
      <path d="M12 12v13M16 12v13M20 12v13" stroke="#aab3be" strokeWidth="1.4" />
    </g>
  ),
  notepad: () => (
    <g>
      <rect x="6" y="3" width="20" height="26" rx="3" fill="#3aa0e8" />
      <rect x="8" y="7" width="16" height="20" rx="1.5" fill="#fff" />
      <path d="M10.5 11h11M10.5 14.5h11M10.5 18h11M10.5 21.5h7" stroke="#8aa0b8" strokeWidth="1.3" strokeLinecap="round" />
      <rect x="9" y="1.8" width="3" height="5" rx="1.2" fill="#fff" stroke="#3aa0e8" />
      <rect x="14.5" y="1.8" width="3" height="5" rx="1.2" fill="#fff" stroke="#3aa0e8" />
      <rect x="20" y="1.8" width="3" height="5" rx="1.2" fill="#fff" stroke="#3aa0e8" />
    </g>
  ),
  photos: () => (
    <g>
      <rect x="3" y="4" width="26" height="24" rx="4" fill="#fff" />
      <path d="M16 16V6a10 10 0 0 1 8.7 5z" fill="#f59e0b" /><path d="M16 16l8.7-5A10 10 0 0 1 26 16z" fill="#ef4444" />
      <path d="M16 16h10a10 10 0 0 1-5 8.7z" fill="#3b82f6" /><path d="M16 16l5 8.7A10 10 0 0 1 11 24.7z" fill="#22c55e" />
      <path d="M16 16l-5 8.7A10 10 0 0 1 6 16z" fill="#06b6d4" /><path d="M16 16H6a10 10 0 0 1 5-8.7z" fill="#a855f7" />
    </g>
  ),
  settings: () => (
    <g>
      <circle cx="16" cy="16" r="5" fill="none" stroke="#8da0b6" strokeWidth="3.5" />
      <path d="M16 3v4M16 25v4M3 16h4M25 16h4M6.8 6.8l2.8 2.8M22.4 22.4l2.8 2.8M25.2 6.8l-2.8 2.8M9.6 22.4l-2.8 2.8" stroke="#8da0b6" strokeWidth="3.4" strokeLinecap="round" />
    </g>
  ),
  calculator: () => (
    <g>
      <rect x="6" y="2.5" width="20" height="27" rx="3" fill="#475569" />
      <rect x="9" y="5.5" width="14" height="5.5" rx="1" fill="#bfe3ff" />
      {[0, 1, 2].flatMap((r) => [0, 1, 2].map((c) => <rect key={r + "" + c} x={9 + c * 5.2} y={13.5 + r * 5} width="3.6" height="3.6" rx=".8" fill="#e5e7eb" />))}
    </g>
  ),
  word: () => (
    <g>
      <rect x="9" y="4" width="20" height="24" rx="2.5" fill="#dbe7fb" /><path d="M16 9h10M16 13h10M16 17h10M16 21h10" stroke="#2b6cd9" strokeWidth="1.5" />
      <rect x="2" y="9" width="15" height="15" rx="2.5" fill="#2b6cd9" />
      <text x="9.5" y="21" fontSize="11" fontWeight="700" fill="#fff" textAnchor="middle" fontFamily="Segoe UI, Arial">W</text>
    </g>
  ),
  excel: () => (
    <g>
      <rect x="9" y="4" width="20" height="24" rx="2.5" fill="#d6f1e1" /><path d="M16 9h10M16 13h10M16 17h10M16 21h10" stroke="#1f8f4e" strokeWidth="1.5" />
      <rect x="2" y="9" width="15" height="15" rx="2.5" fill="#1f8f4e" />
      <text x="9.5" y="21" fontSize="11" fontWeight="700" fill="#fff" textAnchor="middle" fontFamily="Segoe UI, Arial">X</text>
    </g>
  ),
  powerpoint: () => (
    <g>
      <rect x="9" y="4" width="20" height="24" rx="2.5" fill="#fbe3d8" /><circle cx="21" cy="16" r="5.5" fill="none" stroke="#d1511f" strokeWidth="2" />
      <rect x="2" y="9" width="15" height="15" rx="2.5" fill="#d1511f" />
      <text x="9.5" y="21" fontSize="11" fontWeight="700" fill="#fff" textAnchor="middle" fontFamily="Segoe UI, Arial">P</text>
    </g>
  ),
  search: () => (<g><circle cx="14" cy="14" r="8" fill="none" stroke="#9aa5b1" strokeWidth="3" /><path d="M20 20l8 8" stroke="#9aa5b1" strokeWidth="3.4" strokeLinecap="round" /></g>),
  globe: () => (<g><circle cx="16" cy="16" r="12" fill="#3b82f6" /><path d="M4 16h24M16 4c-5 4-5 20 0 24M16 4c5 4 5 20 0 24" stroke="#fff" strokeWidth="1.4" fill="none" /></g>),
  windows: () => (<g><path d="M3 5.5l12-1.7v11H3z" fill="#4cc2ff" /><path d="M17 3.5L29 2v13H17z" fill="#4cc2ff" /><path d="M3 17h12v11L3 26.5z" fill="#4cc2ff" /><path d="M17 17h12v13l-12-1.7z" fill="#4cc2ff" /></g>),
  user: () => (<g><circle cx="16" cy="12" r="6" fill="#cbd5e1" /><path d="M4 29c1-7 6-10 12-10s11 3 12 10z" fill="#cbd5e1" /></g>),
  warn: () => (<g><path d="M16 3L30 28H2z" fill="#fbbf24" stroke="#b45309" strokeWidth="1" strokeLinejoin="round" /><path d="M16 12v8" stroke="#1f2937" strokeWidth="2.6" strokeLinecap="round" /><circle cx="16" cy="23.5" r="1.6" fill="#1f2937" /></g>),
  error: () => (<g><circle cx="16" cy="16" r="13" fill="#dc2626" /><path d="M10.5 10.5l11 11M21.5 10.5l-11 11" stroke="#fff" strokeWidth="3" strokeLinecap="round" /></g>),
  info: () => (<g><circle cx="16" cy="16" r="13" fill="#2563eb" /><path d="M16 14v8" stroke="#fff" strokeWidth="3" strokeLinecap="round" /><circle cx="16" cy="9.5" r="1.8" fill="#fff" /></g>),
  question: () => (<g><circle cx="16" cy="16" r="13" fill="#2563eb" /><path d="M11.5 12.5a4.5 4.5 0 1 1 6.2 4.2c-1.2.6-1.7 1.3-1.7 2.8" stroke="#fff" strokeWidth="2.6" fill="none" strokeLinecap="round" /><circle cx="16" cy="24" r="1.7" fill="#fff" /></g>),
  shield: () => (<g><path d="M16 3l11 4v8c0 7-5 11-11 14C10 26 5 22 5 15V7z" fill="#2563eb" /><path d="M10.5 16l4 4 7-8" stroke="#fff" strokeWidth="2.6" fill="none" strokeLinecap="round" strokeLinejoin="round" /></g>),
};

const IMG_EXT = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg", "ico"];
export function iconForFile(name, type = "file") {
  if (type === "dir") return "folder";
  const e = extOf(name);
  if (IMG_EXT.includes(e)) return "file-img";
  if (["txt", "md", "log", "rtf"].includes(e)) return "file-txt";
  if (["doc", "docx"].includes(e)) return "file-docx";
  if (["xls", "xlsx", "csv"].includes(e)) return "file-xlsx";
  if (["ppt", "pptx"].includes(e)) return "file-pptx";
  if (["zip", "rar", "7z"].includes(e)) return "file-zip";
  if (["mp3", "wav", "m4a"].includes(e)) return "file-mp3";
  if (["mp4", "mov", "avi"].includes(e)) return "file-mp4";
  const known = { pdf: "file-pdf", html: "file-html", htm: "file-html", exe: "file-exe" };
  return known[e] || "file";
}

export function Ico({ name, size = 20, className = "", style, title }) {
  if (!name) return null;
  if (name.startsWith("img:")) {
    return <img className={"ico " + className} src={asset(name.slice(4))} width={size} height={size} alt="" draggable="false" style={style} title={title} />;
  }
  const draw = ICONS[name] || ICONS.file;
  return (
    <svg className={"ico " + className} width={size} height={size} viewBox="0 0 32 32" style={style} aria-hidden="true" focusable="false">
      {title && <title>{title}</title>}
      {draw()}
    </svg>
  );
}

export function FileIco({ name, type, size = 20, thumb }) {
  if (thumb) return <img className="ico thumb" src={thumb} width={size} height={size} alt="" draggable="false" style={{ objectFit: "cover", borderRadius: 3 }} />;
  return <Ico name={iconForFile(name, type)} size={size} />;
}
