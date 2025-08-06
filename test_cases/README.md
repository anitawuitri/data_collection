# GPU 監控系統測試套件

本資料夾包含 GPU 監控系統的所有測試腳本和驗證工具。

## 📁 測試檔案結構

```
test_cases/
├── run_all_tests.py              # 主要測試執行器
├── README.md                     # 本說明檔案
│
├── 基礎功能測試/
│   ├── test_chinese_font.py      # 中文字體支援測試
│   ├── test_fonts.py             # 字體配置測試
│   ├── test_gpu_mapping.py       # GPU ID 映射邏輯測試
│   ├── test_gpu_task_info.py     # GPU 任務資訊 API 測試
│   ├── test_user_column.py       # CSV 使用者欄位測試
│   └── test_gpu_collector.py     # GPU 資料收集器測試
│
├── 視覺化功能測試/
│   ├── test_user_info.py         # 使用者資訊視覺化測試
│   └── test_heatmap_users.py     # Heatmap 使用者資訊測試
│
└── 系統驗證測試/
    ├── chart_verification.py     # 圖表檔案完整性驗證
    └── final_verification.py     # 最終系統功能驗證
```

## 🚀 快速開始

### 執行所有測試
```bash
# 在 data_collection 根目錄下執行
cd test_cases
python3 run_all_tests.py
```

### 執行特定測試
```bash
# 執行特定測試檔案
python3 test_user_info.py
python3 test_heatmap_users.py
python3 final_verification.py
```

## 📝 測試類別說明

### 1. 基礎功能測試

#### `test_chinese_font.py`
- **目的**: 驗證中文字體支援
- **測試內容**: 字體檔案存在性、字體載入、中文字元顯示

#### `test_fonts.py`
- **目的**: 測試字體配置模組
- **測試內容**: font_config.py 模組功能驗證

#### `test_gpu_mapping.py`
- **目的**: 驗證 GPU ID 映射邏輯
- **測試內容**: API 絕對 ID 到硬體 Card ID 的對應關係

#### `test_gpu_task_info.py`
- **目的**: 測試 GPU 任務資訊 API
- **測試內容**: Management API 連線、JWT 認證、使用者資訊提取

#### `test_user_column.py`
- **目的**: 驗證 CSV 使用者欄位功能
- **測試內容**: CSV 格式、使用者資訊寫入、資料完整性

#### `test_gpu_collector.py`
- **目的**: 測試 GPU 資料收集器
- **測試內容**: Netdata API 整合、資料收集邏輯

### 2. 視覺化功能測試

#### `test_user_info.py`
- **目的**: 驗證使用者資訊視覺化功能
- **測試內容**: 
  - 資料讀取功能
  - 使用者資訊提取
  - 圖表生成（包含使用者資訊）
  - 使用者活動摘要

#### `test_heatmap_users.py`
- **目的**: 專門測試 Heatmap 使用者資訊功能
- **測試內容**:
  - 包含/不包含使用者資訊的熱力圖生成
  - 檔案命名規則驗證
  - 使用者標籤顯示功能

### 3. 系統驗證測試

#### `chart_verification.py`
- **目的**: 驗證圖表檔案完整性
- **測試內容**:
  - 圖表檔案存在性檢查
  - 檔案大小驗證
  - 資料準確性測試

#### `final_verification.py`
- **目的**: 最終系統功能綜合驗證
- **測試內容**:
  - 所有功能清單檢查
  - 技術實現驗證
  - 使用範例確認

## 🔧 測試環境要求

### Python 依賴
```bash
pip install pandas matplotlib seaborn requests
```

### 系統要求
- Python 3.7+
- 中文字體支援 (Noto Sans CJK)
- 網路連線 (用於 API 測試)

### 資料要求
- 測試資料位於 `../data/` 目錄
- 包含 2025-08-04, 2025-08-05 的 GPU 使用資料

## 📊 測試報告

測試執行後會產生詳細報告，包括：

- ✅ **通過的測試**: 功能正常
- ❌ **失敗的測試**: 需要修復
- ⚠️  **警告**: 部分功能異常
- 📈 **成功率**: 整體測試通過率

### 成功率評級
- **90%+**: 🎉 優秀 - 系統已準備就緒
- **70-89%**: ⚠️ 良好 - 部分功能需檢查
- **<70%**: ❌ 需改進 - 請修復失敗項目

## 🐛 故障排除

### 常見問題

1. **字體相關錯誤**
   ```bash
   sudo apt-get install fonts-noto-cjk
   ```

2. **模組導入錯誤**
   - 確保在正確的目錄執行測試
   - 檢查 Python 路徑設定

3. **API 連線失敗**
   - 確認 Management API 服務可用
   - 檢查網路連線

4. **資料檔案不存在**
   - 執行資料收集: `python3 python/daily_gpu_log.py 2025-08-04`
   - 確認 `../data/` 目錄存在相關資料

### 除錯模式

單獨執行失敗的測試並查看詳細錯誤訊息：

```bash
python3 -v test_user_info.py
python3 -v test_heatmap_users.py
```

## 🔄 持續整合

建議在以下情況執行完整測試套件：

1. **程式碼變更後**
2. **新功能開發完成**
3. **部署前驗證**
4. **定期系統檢查**

## 📚 相關文件

- [USER_INFO_GUIDE.md](../USER_INFO_GUIDE.md) - 使用者資訊功能說明
- [CHANGELOG.md](../CHANGELOG.md) - 版本更新記錄
- [README.md](../README.md) - 專案主要說明
