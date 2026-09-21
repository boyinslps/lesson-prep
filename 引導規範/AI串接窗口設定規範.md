# AI 串接窗口設定規範

> 這份文件定義本專案**所有 AI 呼叫的統一串接方式**（聊天補全介面／反向代理／模型偵測），
> 作為工作台生成、評分平台 AI 評分，以及日後任何新 AI 功能的共同規範。
>
> **檔案位置**：`引導規範/AI串接窗口設定規範.md`（就是本檔）。

---

## 1. 一句話原則
所有 AI 一律走 **OpenAI 相容的「聊天補全」介面**（`POST {endpoint}/chat/completions`），
`endpoint` 是使用者自填的**反向代理 URL**（通常結尾 `/v1`），金鑰用 `Authorization: Bearer <key>`。
**金鑰只存在後端 `工作台/config.json`，前端絕不內嵌。**

## 2. 兩個獨立的 AI 窗口
| 窗口 | 用途 | config.json 欄位 |
|---|---|---|
| **主 AI**（生成） | 工作台的鷹架／關鍵字／教學流程等生成 | `provider` `endpoint` `key` `model` |
| **評分 AI** | 評分平台開放題 AI 評分 | `grade_provider` `grade_endpoint` `grade_key` `grade_model` |
- 兩窗口**各自可填不同反向代理與模型**。
- **回退**：評分 AI 沒填 `grade_key` 時，自動改用主 AI（同一把設定）。

## 3. 三個標準動作（每個窗口都一樣）
1. **填端點與金鑰**：`endpoint`（反向代理，結尾通常 `/v1`）＋ `key`。
2. **偵測並列出可用模型**：`GET {endpoint}/models`（帶 `Authorization: Bearer`）→ 取 `data[].id` → 下拉選單。
   - Gemini 原生模式：改打 `GET {base}/models?key=...`，取支援 `generateContent` 的 `models[].name`。
3. **選模型並儲存**：`model` 存進 config；之後呼叫 `chat/completions` 帶這個 `model`。

## 4. 後端實作（工作台/server.py）
- `_llm_call(provider, key, model, endpoint, prompt)`：底層呼叫（openai 相容或 gemini 原生），回 `{ok, text}`。
- `_llm_models(provider, key, endpoint)`：列模型，回 `{ok, models[]}`。
- 對外包裝：
  - 主 AI：`gemini_call()` / `gemini_models()`（讀 `provider/endpoint/key/model`）。
  - 評分 AI：`grade_call()` / `grade_models()`（讀 `grade_*`，未設則回退主 AI）。
- API 路由：
  - `POST /api/gemini`、`GET /api/gemini-models`（主 AI）。
  - `POST /api/grade`（用 `grade_call`）、`GET /api/grade-models`（評分 AI 列模型）。
  - 設定讀寫走 `GET/POST /api/settings`（合併寫入 config.json，含 `grade_*`）。

## 5. 前端串接規範（任何要用 AI 的頁面照做）
1. 設定面板提供：**反向代理 URL**、**API Key**、**「測試並列出模型」按鈕**、**模型下拉**。
2. 「測試並列出模型」：先 `POST /api/settings` 存目前輸入 → 再 `GET /api/grade-models`（或 `/api/gemini-models`）→ 用回傳的清單填下拉。**偵測連結是否可用＝這一步成功與否。**
3. 呼叫 AI 一律打後端 API（`/api/grade`、`/api/gemini`），**不要在前端直接呼叫代理或放金鑰**。
4. 跨來源呼叫工作台（`http://127.0.0.1:8770`）已開 CORS；金鑰仍只在後端。

## 6. config.json 範例（僅示意，勿把真金鑰寫進版本庫）
```json
{
  "provider": "openai",
  "endpoint": "https://你的反向代理/v1",
  "key": "sk-...",
  "model": "gpt-4o-mini",

  "grade_provider": "openai",
  "grade_endpoint": "https://你的反向代理/v1",
  "grade_key": "sk-...",
  "grade_model": "gpt-4o-mini"
}
```

## 7. 錯誤處理與安全
- 端點錯／金鑰錯／模型不存在 → 後端回 `{ok:false,error}`，前端顯示，不要吞掉。
- `config.json` 含金鑰，**已被 `.gitignore` 排除**（`*.json` 類憑證），不進發布庫。
- 反向代理由使用者自負責；本專案只負責「填 URL → 列模型 → 用模型」的統一流程。

---

### 延伸
- 工作台介面與 API → `工作流介面規劃.md`
- 評分平台規格 → `../評分平台/SPEC.md`
