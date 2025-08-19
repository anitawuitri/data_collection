# VRAM 堆疊圖使用者顯示控制參數說明

## 📋 功能概述

VRAM 堆疊區域圖現在支援控制是否在圖表中顯示使用者資訊，提供更靈活的視覺化選項。

## 🎯 使用方式

### 命令行接口
```bash
# 語法
./run_gpu_visualization.sh vram-stacked [開始日期] [結束日期] [顯示使用者]

# 預設行為 - 顯示使用者資訊
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17

# 明確顯示使用者資訊
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17 true

# 不顯示使用者資訊
./run_gpu_visualization.sh vram-stacked 2025-08-11 2025-08-17 false
```

### Python API
```python
from quick_gpu_trend_plots import quick_nodes_vram_stacked_utilization

# 顯示使用者資訊（預設）
quick_nodes_vram_stacked_utilization("2025-08-11", "2025-08-17", show_users=True)

# 不顯示使用者資訊
quick_nodes_vram_stacked_utilization("2025-08-11", "2025-08-17", show_users=False)
```

## 📊 參數說明

### `show_users` 參數
- **類型**: 布林值 (boolean)
- **預設值**: `True`
- **支援格式**:
  - `true`, `True`, `1`, `yes` → 顯示使用者資訊
  - `false`, `False`, `0`, `no` → 不顯示使用者資訊

### 影響範圍
1. **圖表標題**: 包含或排除使用者統計資訊
2. **圖例標籤**: 節點名稱是否附帶使用者名稱
3. **檔案命名**: 自動添加相應後綴

## 📁 生成檔案

### 檔案命名規則
- **包含使用者**: `nodes_vram_stacked_utilization_[開始日期]_to_[結束日期]_with_users.png`
- **不含使用者**: `nodes_vram_stacked_utilization_[開始日期]_to_[結束日期]_without_users.png`

### 範例檔名
```
nodes_vram_stacked_utilization_2025-08-11_to_2025-08-17_with_users.png
nodes_vram_stacked_utilization_2025-08-11_to_2025-08-17_without_users.png
```

## 🎨 視覺差異

### 顯示使用者資訊 (show_users=True)
- ✅ 圖表標題包含總活躍使用者數統計
- ✅ 圖例顯示: `colab-gpu1 (user1, user2)`
- ✅ 智慧標籤處理:
  - 1-2個使用者: 顯示完整名稱
  - 3個使用者: 顯示所有名稱
  - 4+個使用者: 顯示前2個 + "等N人"

### 不顯示使用者資訊 (show_users=False)
- ❌ 圖表標題僅顯示時間範圍
- ❌ 圖例僅顯示: `colab-gpu1`
- ❌ 無使用者相關統計資訊

## 🧪 測試驗證

### 自動化測試
```bash
# 運行測試腳本
cd /home/amditri/data_collection
python3 test_show_users_parameter.py
```

### 手動驗證步驟
1. 生成兩個版本的圖表
2. 比較檔案大小差異
3. 檢查檔名後綴是否正確
4. 視覺檢查圖表內容差異

## 🔄 向後相容性

- ✅ 現有腳本無需修改，預設行為保持不變
- ✅ 所有現有 API 呼叫繼續正常工作
- ✅ 舊版本生成的圖表檔案不受影響

## 💡 使用建議

### 何時顯示使用者資訊
- 📊 **管理報告**: 需要了解資源使用者身份
- 🔍 **使用率分析**: 分析特定使用者的資源消耗
- 📈 **趨勢追蹤**: 監控使用者活動變化

### 何時隱藏使用者資訊
- 🎯 **系統效能**: 專注於硬體效能分析
- 📋 **簡化報告**: 減少圖表複雜度
- 🔒 **隱私考量**: 不希望暴露使用者身份

## 🚀 未來擴展

計劃將此功能擴展到其他圖表類型：
- [ ] GPU 使用率圖表
- [ ] 熱力圖
- [ ] 節點比較圖
- [ ] 時間序列圖

## 📚 相關文檔

- [VRAM_STACKED_VIEW_GUIDE.md](./VRAM_STACKED_VIEW_GUIDE.md) - VRAM 堆疊圖基礎功能
- [CHANGELOG.md](./CHANGELOG.md) - 版本更新記錄
- [USER_INFO_GUIDE.md](./USER_INFO_GUIDE.md) - 使用者追蹤功能說明