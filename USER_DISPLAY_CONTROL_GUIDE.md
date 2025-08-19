# 使用者資訊顯示控制功能總覽

## 📋 功能概述

GPU 監控系統現在支援在多個圖表類型中控制使用者資訊的顯示，提供更靈活的視覺化選項。

## 🎯 支援的命令

### 1. `quick` 命令 - 快速生成所有圖表 🔥
```bash
# 語法
./run_gpu_visualization.sh quick [開始日期] [結束日期] [顯示使用者]

# 使用範例
./run_gpu_visualization.sh quick 2025-08-11 2025-08-17           # 預設顯示使用者（8張圖表）
./run_gpu_visualization.sh quick 2025-08-11 2025-08-17 true      # 明確顯示使用者（8張圖表）
./run_gpu_visualization.sh quick 2025-08-11 2025-08-17 false     # 不顯示使用者（6張圖表）
```

### 2. `nodes` 命令 - 節點對比趨勢圖
```bash
# 語法
./run_gpu_visualization.sh nodes [開始日期] [結束日期] [顯示使用者]

# 使用範例
./run_gpu_visualization.sh nodes 2025-08-11 2025-08-17           # 預設顯示使用者
./run_gpu_visualization.sh nodes 2025-08-11 2025-08-17 true      # 明確顯示使用者
./run_gpu_visualization.sh nodes 2025-08-11 2025-08-17 false     # 不顯示使用者
```

### 3. `vram-stacked` 命令 - VRAM 堆疊區域圖
```bash
# 語法  
./run_gpu_visualization.sh vram-stacked [開始日期] [結束日期] [顯示使用者]

# 使用範例
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17           # 預設顯示使用者
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17 true      # 明確顯示使用者
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17 false     # 不顯示使用者
```

## 📊 參數說明

### `show_users` 參數（第三個參數）
- **類型**: 布林值
- **預設值**: `true` (顯示使用者資訊)
- **支援格式**:
  - 顯示使用者: `true`, `True`, `1`, `yes`
  - 隱藏使用者: `false`, `False`, `0`, `no`
- **省略行為**: 當省略第三個參數時，預設為 `true`

### 通用特性
- ✅ **向後相容**: 現有腳本無需修改
- ✅ **一致介面**: 所有支援的命令使用相同的參數格式
- ✅ **智慧檔名**: 自動根據設定生成描述性檔名

## 📁 檔案命名規則

### 模式
- **包含使用者**: `[圖表類型]_[日期範圍]_with_users.png`
- **不含使用者**: `[圖表類型]_[日期範圍]_without_users.png`

### 實際範例
```
# quick 命令生成的檔案
nodes_trend_2025-08-11_to_2025-08-17_with_users.png
nodes_trend_2025-08-11_to_2025-08-17_without_users.png
heatmap_2025-08-11_to_2025-08-17_with_users.png
heatmap_2025-08-11_to_2025-08-17.png
vram_nodes_comparison_all_gpus_2025-08-11_to_2025-08-17_with_users.png
vram_nodes_comparison_all_gpus_2025-08-11_to_2025-08-17.png
user_activity_summary_2025-08-11_to_2025-08-17.png (僅 show_users=true)
vram_user_activity_summary_2025-08-11_to_2025-08-17.png (僅 show_users=true)

# nodes 命令生成的檔案
nodes_trend_2025-08-11_to_2025-08-17_with_users.png
nodes_trend_2025-08-11_to_2025-08-17_without_users.png

# vram-stacked 命令生成的檔案
nodes_vram_stacked_utilization_2025-08-11_to_2025-08-17_with_users.png
nodes_vram_stacked_utilization_2025-08-11_to_2025-08-17_without_users.png
```

## 🎨 視覺化差異比較

### 顯示使用者資訊 (show_users=true)

#### quick 命令 (批量生成)
- ✅ **生成 8 張完整圖表**，包含所有使用者資訊
- ✅ 圖表標題、圖例包含使用者統計
- ✅ 包含專門的使用者活動摘要圖表
- ✅ 部分圖表使用 `_with_users` 檔名後綴

#### nodes 命令
- ✅ 圖表標題包含使用者資訊統計
- ✅ 圖表高度增加 (10)，為使用者資訊留出空間
- ✅ 顯示最後一天的使用者活動資訊

#### vram-stacked 命令
- ✅ 圖例標籤包含使用者名稱: `colab-gpu1 (user1, user2)`
- ✅ 圖表標題顯示總活躍使用者數統計
- ✅ 智慧使用者標籤處理（1-2人/3人/4+人不同顯示）

### 隱藏使用者資訊 (show_users=false)

#### quick 命令 (批量生成)
- ❌ **生成 6 張圖表**，跳過使用者相關圖表
- ❌ 圖表專注於硬體效能數據
- ❌ 不包含使用者活動摘要圖表
- ❌ 使用標準檔名或 `_without_users` 後綴

#### nodes 命令
- ❌ 圖表標題僅顯示時間範圍和節點資訊
- ❌ 標準圖表高度 (8)
- ❌ 專注於硬體效能數據

#### vram-stacked 命令
- ❌ 圖例僅顯示節點名稱: `colab-gpu1`
- ❌ 圖表標題不包含使用者統計
- ❌ 純硬體資源使用率分析

## 🔧 Python API 使用

### 函數調用
```python
from quick_gpu_trend_plots import quick_nodes_trend, quick_nodes_vram_stacked_utilization

# nodes 命令對應的函數
quick_nodes_trend("2025-08-11", "2025-08-17", show_users=True)   # 顯示使用者
quick_nodes_trend("2025-08-11", "2025-08-17", show_users=False)  # 隱藏使用者

# vram-stacked 命令對應的函數
quick_nodes_vram_stacked_utilization("2025-08-11", "2025-08-17", show_users=True)   # 顯示使用者
quick_nodes_vram_stacked_utilization("2025-08-11", "2025-08-17", show_users=False)  # 隱藏使用者
```

## 🧪 測試和驗證

### 自動化測試腳本
```bash
# 測試 quick 命令
python3 test_quick_show_users.py

# 測試 nodes 命令
python3 test_nodes_show_users.py

# 測試 vram-stacked 命令  
python3 test_show_users_parameter.py
```

### 手動驗證步驟
1. 分別生成顯示和隱藏使用者資訊的圖表
2. 檢查檔名後綴是否正確（`_with_users` vs `_without_users`）
3. 比較檔案大小差異（顯示使用者的圖表通常較大）
4. 視覺檢查圖表內容差異

## 💡 使用場景建議

### 何時顯示使用者資訊
- 📊 **管理報告**: 需要了解資源分配和使用者活動
- 🔍 **使用分析**: 追蹤特定使用者的資源使用模式
- 📈 **使用率審核**: 監控資源使用合理性
- 👥 **團隊協調**: 了解 GPU 資源被哪些團隊成員使用

### 何時隱藏使用者資訊
- 🎯 **效能分析**: 專注於硬體效能和系統表現
- 📋 **簡化報告**: 減少圖表複雜度，專注核心數據
- 🔒 **隱私保護**: 不希望暴露使用者身份的場合
- 📊 **純技術分析**: 系統容量規劃和硬體評估

## 🚀 版本歷史

- **v2.5 (2025-12-05)**: quick 命令支援使用者顯示控制，批量圖表生成
- **v2.4 (2025-12-05)**: nodes 命令支援使用者顯示控制
- **v2.3 (2025-12-05)**: vram-stacked 命令支援使用者顯示控制
- **v2.2 (2025-12-05)**: 基礎 VRAM 堆疊圖功能實現
- **v2.1 (2025-08-06)**: 熱力圖使用者資訊整合
- **v2.0 (2025-08-06)**: 使用者資訊整合系統

## 🔮 未來計劃

計劃將使用者顯示控制功能擴展到更多圖表類型：
- [ ] `stacked` - GPU 使用率堆疊圖
- [ ] `gpu` - 特定 GPU 跨節點對比圖
- [ ] `heatmap` - 熱力圖
- [ ] `node` - 單節點詳細分析圖
- [ ] `vram-nodes` - VRAM 節點對比圖

## 📚 相關文檔

- [VRAM_SHOW_USERS_GUIDE.md](./VRAM_SHOW_USERS_GUIDE.md) - VRAM 堆疊圖使用者控制詳細說明
- [CHANGELOG.md](./CHANGELOG.md) - 完整版本更新記錄  
- [USER_INFO_GUIDE.md](./USER_INFO_GUIDE.md) - 使用者追蹤系統說明
- [VISUALIZATION_QUICK_START.md](./VISUALIZATION_QUICK_START.md) - 視覺化功能快速上手