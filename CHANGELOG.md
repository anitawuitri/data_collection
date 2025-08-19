# GPU 監控系統更新記錄

## [2.6] - 2025-01-XX
### Added
- vram-all 命令添加 show_users 參數，完成所有主要命令的使用者資訊控制
- 完整的 VRAM 監控使用者顯示控制系統
- 智能 VRAM 圖表生成，支援 5/4 圖表變化模式

### Changed
- vram-all 命令現在支援第三個參數控制使用者資訊顯示
- generate_all_vram_plots 函數支援 show_users 參數
- 統一所有主要命令的使用者資訊控制介面

### Technical Details
- 實現 5/4 圖表變化系統（show_users=True: 5張圖，show_users=False: 4張圖）
- VRAM 使用者活動摘要圖僅在 show_users=True 時生成
- 完成使用者顯示控制系統的全面實現

## [2.5] - 2025-01-XX
### Added
- quick 命令添加 show_users 參數，允許批次控制使用者資訊顯示
- 彈性圖表生成系統，支援條件性圖表建立
- 智能使用者資訊檔案命名，包含 _with_users 和 _without_users 後綴

### Changed
- quick 命令現在支援第三個參數控制使用者資訊顯示
- generate_all_quick_plots 函數支援 show_users 參數
- 優化批次圖表生成邏輯，提高生成效率

### Technical Details
- 實現 8/6 圖表變化系統（show_users=True: 8張圖，show_users=False: 6張圖）
- 使用者活動摘要圖和時段分布圖僅在 show_users=True 時生成

---

## 🎉 版本 v2.4 - 節點趨勢圖使用者顯示控制參數 (2025-12-05)

### 🆕 新增功能
- **nodes 命令增強**: 節點對比趨勢圖新增 `show_users` 參數支援
- **統一使用者控制**: nodes 和 vram-stacked 命令均支援使用者資訊顯示開關
- **靈活檔案命名**: nodes 命令根據使用者顯示設定自動產生描述性檔名
- **一致的使用體驗**: 與 VRAM 堆疊圖相同的參數格式和行為

### 🔧 技術改進
- **`quick_nodes_trend()` 函數增強**: 支援 `show_users` 參數和智慧檔名生成
- **命令行參數統一**: 支援 `true/false`, `1/0`, `yes/no` 等多種布林值格式
- **向後相容性**: 預設顯示使用者資訊，維持現有行為
- **圖表高度自適應**: 根據是否顯示使用者資訊調整圖表高度

### 🎯 使用範例
```bash
# 預設顯示使用者資訊
./run_gpu_visualization.sh nodes 2025-08-11 2025-08-17

# 明確顯示使用者資訊  
./run_gpu_visualization.sh nodes 2025-08-11 2025-08-17 true

# 不顯示使用者資訊
./run_gpu_visualization.sh nodes 2025-08-11 2025-08-17 false
```

### 📊 生成檔案命名規則
- **包含使用者**: `nodes_trend_[日期範圍]_with_users.png`
- **不含使用者**: `nodes_trend_[日期範圍]_without_users.png`

### 📈 視覺化差異
- **顯示使用者模式**: 圖表標題包含使用者資訊，圖表高度增加至 10
- **隱藏使用者模式**: 純節點比較圖，專注硬體效能數據，圖表高度 8

### 🧪 測試驗證
- ✅ nodes 命令參數正確傳遞
- ✅ 檔名後綴自動生成（_with_users / _without_users）
- ✅ 圖表內容根據參數正確顯示/隱藏使用者資訊
- ✅ 向後相容性維持
- ✅ 與 vram-stacked 命令行為一致

### 🔄 功能統一
現在以下命令都支援使用者資訊控制：
- `nodes` - 節點對比趨勢圖
- `vram-stacked` - VRAM 堆疊區域圖

---

## 🎉 版本 v2.3 - VRAM 堆疊圖使用者顯示控制參數 (2025-12-05)

### 🆕 新增功能
- **使用者顯示控制**: VRAM 堆疊區域圖新增 `show_users` 參數
- **靈活圖表生成**: 可選擇顯示或隱藏使用者資訊
- **智慧檔名命名**: 根據使用者顯示設定自動產生描述性檔名
- **命令行參數支援**: 透過命令行第三個參數控制使用者顯示

### 🔧 技術改進
- **參數驗證**: 支援多種布林值格式（true/false, 1/0, yes/no）
- **預設行為**: 預設顯示使用者資訊，保持向後相容性
- **檔名後綴**: 自動添加 `_with_users` 或 `_without_users` 後綴
- **使用說明更新**: 詳細的命令行使用範例和參數說明

### 🎯 使用範例
```bash
# 預設顯示使用者資訊
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17

# 顯示使用者資訊
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17 true

# 不顯示使用者資訊
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17 false
```

### 📊 生成檔案命名規則
- **包含使用者**: `nodes_vram_stacked_utilization_[日期範圍]_with_users.png`
- **不含使用者**: `nodes_vram_stacked_utilization_[日期範圍]_without_users.png`

### 🧪 測試驗證
- ✅ 參數正確傳遞到 Python 函數
- ✅ 布林值轉換正確處理
- ✅ 檔名後綴正確生成
- ✅ 圖表內容根據參數正確顯示/隱藏使用者資訊
- ✅ 向後相容性維持（預設顯示使用者）

---

## 🎉 版本 v2.2 - VRAM 堆疊區域圖視覺化 (2025-12-05)

### 🆕 新增功能
- **VRAM 堆疊區域圖**: 新增各節點 VRAM 使用率累積堆疊視圖功能
- **使用者標籤整合**: VRAM 堆疊圖包含智慧型使用者資訊顯示
- **多時間區間支援**: 支援任意時間範圍的 VRAM 使用率分析
- **累積視覺化**: 清晰顯示各節點 VRAM 使用率的累積分佈情況

### 🔧 技術改進
- **quick_gpu_trend_plots.py**: 新增 `quick_nodes_vram_stacked_utilization()` 函數
- **run_gpu_visualization.sh**: 新增 `vram-stacked` 命令選項
- **Y軸範圍修正**: 修正負數顯示問題，確保 Y 軸從 0 開始
- **資料處理優化**: 改進 VRAM 資料提取和處理邏輯

### 📊 增強的視覺化功能
- **堆疊區域圖**: 使用 `stackplot` 顯示各節點 VRAM 使用率累積
- **智慧使用者標籤**: 根據使用者數量調整標籤顯示格式
  - 1-2 個使用者：顯示完整使用者名稱
  - 3 個使用者：顯示前 2 個 + "等"
  - 4+ 個使用者：顯示第一個 + "等N人"
- **中文字體支援**: 完整支援中文標籤和圖表文字
- **檔案命名**: 自動生成描述性檔名，包含時間範圍資訊

### 🎯 使用範例
```bash
# 生成 VRAM 堆疊區域圖
./run_gpu_visualization.sh vram-stacked 2025-08-04 2025-08-05

# 測試特定時間範圍
./run_gpu_visualization.sh vram-stacked 2025-07-16 2025-08-04
```

### 🐛 修復的問題
- ✅ 修復 Y 軸負數顯示問題
- ✅ 修復 VRAM 資料提取錯誤（之前顯示 0.0%）
- ✅ 正確處理 CSV 欄位名稱對應（'平均VRAM使用率(%)' → 'vram'）
- ✅ 改善使用者資訊收集邏輯

### 📈 效果展示
- **之前**: 無 VRAM 堆疊視覺化功能
- **現在**: 完整的 VRAM 使用率累積分析，包含使用者資訊和智慧標籤顯示

---

## 🎉 版本 v2.1 - Heatmap 使用者資訊整合 (2025-08-06)

### 🆕 新增功能
- **GPU 使用率熱力圖**: 新增包含使用者資訊的熱力圖功能
- **多日期視覺化**: 熱力圖支援多日期範圍的 GPU 使用率分佈
- **使用者標籤顯示**: 熱力圖 Y 軸標籤包含節點、GPU 編號和使用者資訊
- **靈活參數控制**: `show_users` 參數控制是否在熱力圖中顯示使用者資訊

### 🔧 技術改進
- **advanced_gpu_trend_analyzer.py**: 增強 `plot_heatmap` 函數支援使用者資訊
- **quick_gpu_trend_plots.py**: 新增 `quick_gpu_heatmap` 快速生成函數
- **run_user_monitor.sh**: 新增 `heatmap` 命令支援
- **檔案命名**: 包含使用者資訊的熱力圖使用 `_with_users` 後綴

### 📊 增強的圖表功能
- 熱力圖標題包含使用者摘要統計
- Y 軸標籤格式: `節點 GPU編號 (使用者名稱)`
- 自動調整圖表大小適應多日期和多節點
- 支援生成有/無使用者資訊的兩種版本

### 🎯 使用範例
```bash
# 生成包含使用者資訊的熱力圖
./run_user_monitor.sh heatmap 2025-08-04 2025-08-05

# 快速生成所有圖表（現在包含熱力圖）
./run_user_monitor.sh quick 2025-08-04 2025-08-05
```

---

## 🎉 版本 v2.0 - 使用者資訊整合版本 (2025-08-06)

### 🚀 重大功能更新

#### ✅ 修復重大 Bug
- **問題**: CSV 檔案中所有 GPU 顯示 "未使用"，但終端輸出顯示正確使用者名稱
- **根本原因**: API 返回的絕對 GPU ID (0-31) 與硬體 Card ID (1,9,17,25,33,41,49,57) 對應錯誤
- **解決方案**: 實現 `map_absolute_gpu_to_card_id()` 函數，正確對應 GPU ID
- **影響**: 所有 CSV 報告現在正確顯示使用者資訊

#### 🆕 全新功能
1. **使用者資訊整合**
   - CSV 報告新增 "使用者" 欄位
   - 視覺化圖表包含使用者資訊
   - 使用者活動摘要圖表

2. **增強的視覺化系統**
   - 圖表標題包含使用者資訊摘要
   - `show_users` 參數控制使用者資訊顯示
   - 4 種不同類型的使用者資訊圖表

3. **便捷執行腳本**
   - `run_user_monitor.sh` 統一管理腳本
   - 命令列介面，支援所有功能
   - 自動環境檢查和錯誤處理

#### 🔧 技術改進
- **GPU ID 映射邏輯**: 精確對應 API ID 和硬體 ID
- **字體配置**: 完整的中文字體支援
- **錯誤處理**: 增強的異常處理和日誌記錄
- **代碼重構**: 模組化設計，便於維護

### 📁 新增檔案
- `visualization/quick_gpu_trend_plots.py` (大幅增強)
- `visualization/font_config.py`
- `visualization/test_user_info.py`
- `visualization/chart_verification.py`
- `run_user_monitor.sh`
- `USER_INFO_GUIDE.md`

### 📊 測試驗證
- ✅ 功能完整性測試
- ✅ 資料準確性驗證
- ✅ 圖表生成測試
- ✅ 使用者資訊顯示驗證
- ✅ 多節點環境測試

### 🎯 使用範例
```bash
# 收集今日資料（包含使用者資訊）
./run_user_monitor.sh collect

# 生成包含使用者資訊的圖表
./run_user_monitor.sh quick 2025-08-04 2025-08-05

# 運行完整功能測試
./run_user_monitor.sh test
```

### 📈 效果展示
- **之前**: CSV 顯示 "未使用"，圖表無使用者資訊
- **現在**: CSV 正確顯示使用者名稱，圖表包含詳細使用者資訊

---

## 版本 v1.0 - 基礎版本 (2025-05-xx)

### ✅ 基礎功能
- GPU 使用率監控
- CSV 報告生成
- 基本視覺化圖表
- 多節點支援

### 📁 核心檔案
- `python/daily_gpu_log.py`
- `scripts/` 目錄下的各種腳本
- 基礎圖表生成功能

---

## 🔮 未來規劃 (v3.0)
- [ ] 實時監控面板
- [ ] 使用者使用時間統計
- [ ] 效能基準測試
- [ ] 告警系統
- [ ] Web 介面
