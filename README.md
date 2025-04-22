# 自然語言轉 SQL 查詢系統

## 專案說明

本專案旨在建立一個使用 Gemini API 的自然語言轉 SQL 查詢系統。使用者可以透過 Streamlit 前端介面輸入自然語言的資料庫查詢請求，系統後端會呼叫 Gemini API，結合從 Word 文件讀取的資料庫 Schema 資訊，來理解使用者需求並生成對應的 SQL 查詢語句。最終生成的 SQL 語句會被執行，並將結果以口語化的方式呈現給使用者。

## 執行步驟

1.  **設定環境變數：**
    *   請先申請 Google Gemini API 金鑰，並將其設定為環境變數 `GEMINI_API_KEY`。
    *   在終端機中執行以下指令：
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY"
        ```
        (請將 `YOUR_API_KEY` 替換為您的實際金鑰)
    *   或者，您也可以將金鑰儲存在 `.env` 檔案中，並確保 `app.py` 能夠正確讀取。

2.  **安裝相依套件：**
    *   在終端機中執行以下指令，以安裝專案所需的 Python 套件：
        ```bash
        pip install streamlit python-docx google-generativeai python-dotenv
        ```

3.  **建立 SQLite 資料庫：**
    *   執行 `src/create_db.py` 檔案，以建立 SQLite 資料庫並填入假資料：
        ```bash
        python src/create_db.py
        ```
    *   此步驟會建立一個名為 `data.db` 的 SQLite 資料庫檔案，並在其中建立 `員工薪資` 和 `部門資訊` 兩個表格。

4.  **執行 Streamlit 應用程式：**
   * 每次執行streamlit前都要先執行 python src/create_db.py
    *   在終端機中執行以下指令，以啟動 Streamlit 應用程式：
        ```bash
        streamlit run src/app.py
        ```

5.  **在瀏覽器中開啟應用程式：**
    *   Streamlit 應用程式啟動後，會在終端機中顯示一個網址。請在瀏覽器中開啟該網址，以使用自然語言轉 SQL 查詢系統。

## 專案結構

```
.
├── README.md
├── data.db
├── output.txt
├── src
│   ├── app.py
│   ├── config.py
│   ├── create_db.py
│   ├── fake_schema1.py
│   ├── fake_schema2.py
│   ├── gemini_client.py
│   └── schema_parser.py
└── DB_Schema
    ├── TWDETAILTMPL 臺幣付款交易範本明細檔.docx
    └── TWMASTER臺幣交易主檔.docx
```

## 檔案說明

*   `README.md`: 本檔案，包含專案說明和執行步驟。
*   `data.db`: SQLite 資料庫檔案，儲存員工薪資和部門資訊。
*   `output.txt`: 儲存生成的 SQL 查詢語句。
*   `src/app.py`: Streamlit 應用程式的主要邏輯。
*   `src/config.py`: 儲存設定檔，例如 `COMPANYKEY`。
*   `src/create_db.py`: 建立 SQLite 資料庫並填入假資料的腳本。
*   `src/fake_schema1.py`: 定義 `員工薪資` 表格的結構。
*   `src/fake_schema2.py`: 定義 `部門資訊` 表格的結構。 員工薪資表格的「部門」欄位與部門資訊表格的「部門編號」欄位之間存在外鍵關聯。
*   `src/gemini_client.py`: 與 Google Gemini API 互動的模組。
*   `src/schema_parser.py`: 解析 Word 文件中的資料庫 Schema 資訊。
*   `DB_Schema/`: 包含資料庫 Schema 資訊的 Word 文件。

## 系統架構

1.  使用者在 Streamlit 介面輸入自然語言查詢。
2.  系統將查詢傳送給 Gemini API，並提供資料庫 Schema 資訊。
3.  Gemini API 根據查詢和 Schema 產生 SQL 查詢語句。
4.  系統執行 SQL 查詢語句，從 SQLite 資料庫中取得結果。
5.  系統將查詢結果傳送給 Gemini API，要求生成口語化的摘要。
6.  Gemini API 生成口語化的摘要，並將其顯示在 Streamlit 介面上。
7.  生成的 SQL 查詢語句會儲存到 `output.txt` 檔案中。

## 資料檢視

*   資料庫資訊儲存在 `data.db` 檔案中，您可以使用 SQLite 瀏覽器開啟檢視。
*   您也可以將資料庫內容匯出為 CSV 檔案，方法是執行 `src/create_db.py` 檔案。匯出後的 CSV 檔案會儲存在專案目錄下。

## 資訊呈現

*   **Streamlit 介面：** 僅顯示 Gemini API 生成的口語化摘要，不包含 SQL 查詢語句或其他技術細節。
*   **終端機：** 顯示程式執行過程中的除錯訊息，例如 SQL 查詢語句、資料庫連線狀態等。
*   **output.txt：** 儲存每次查詢所生成的 SQL 查詢語句。

## 系統價值

本系統可為 永豐銀行 寰宇金融網 (B2B) 的企業客戶帶來以下價值：

*   **降低資料查詢門檻：** 讓不熟悉 SQL 語法的企業客戶也能輕鬆查詢其交易資訊、員工薪資等資料。
*   **提升查詢效率：** 透過自然語言查詢，客戶可以快速找到所需的資訊，無需耗時撰寫複雜的 SQL 語句。
*   **強化資料分析能力：** 系統生成的口語化摘要，有助於客戶快速理解查詢結果，並從中發掘有價值的資訊。
*   **降低管理成本：** 對於擁有大量交易資訊和員工的企業客戶，本系統可大幅降低資料查詢和管理的負擔，提升整體營運效率。

## 注意事項

*   請確保已正確設定 `GEMINI_API_KEY` 環境變數。
*   如果遇到任何錯誤，請檢查終端機輸出的錯誤訊息，並根據訊息內容進行調整。
*   本專案僅為概念驗證，生成的 SQL 查詢語句可能不完全準確.

## Security Measures

This system implements the following security measures to mitigate the risks of Prompt Injection and SQL Injection attacks:

*   **Input Layer Protection:** Implements natural language filtering to prevent dangerous keywords (e.g., "ignore", "delete", "other companies") from being used in the user's query.
*   **Prompt Engineering:** Enhances the system prompt template to include constraints that prevent the generation of DELETE/UPDATE statements and enforce the inclusion of a WHERE clause with the COMPANYKEY.
