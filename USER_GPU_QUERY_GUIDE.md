# GPU 使用者查詢工具使用說明

## 概述

`get_user_gpu_usage.py` 是一個專門用來查詢特定使用者 GPU 使用情況的工具。它可以幫助您：

- 🔍 查詢特定使用者的 GPU 使用率和 VRAM 使用量
- 📅 分析單日或多日的使用情況
- 📋 列出指定日期的所有 GPU 使用者  
- 📊 提供詳細的統計分析
- 📈 生成使用趨勢圖（需要安裝 matplotlib）

## 安裝需求

### 基本功能（必需）
```bash
# 無需額外套件，使用內建 csv 模組
```

### 完整功能（推薦）
```bash
pip3 install pandas matplotlib seaborn
```

## 使用方法

### 1. 查詢特定使用者單日 GPU 使用情況

```bash
# 基本格式
python3 get_user_gpu_usage.py <使用者名稱> <日期>

# 實際範例
python3 get_user_gpu_usage.py paslab_openai 2025-09-15
python3 get_user_gpu_usage.py itrd 2025-07-22
```

**輸出範例：**
```
🔍 查詢使用者 'itrd' 的 GPU 使用情況...
📅 日期範圍: 2025-07-22 至 2025-07-22
============================================================

📈 找到 2 筆使用記錄:
------------------------------------------------------------
🟢 2025-07-22 | colab-gpu4 | GPU[2]
   GPU使用率: 20.28%
   VRAM使用率: 83.38%

🟢 2025-07-22 | colab-gpu4 | GPU[3]
   GPU使用率: 18.17%
   VRAM使用率: 82.27%

📊 統計摘要:
   總記錄數: 2
   有活動記錄數: 2 (100.0%)
   平均 GPU 使用率: 19.23%
   平均 VRAM 使用率: 82.82%
   最大 GPU 使用率: 20.28%
   最大 VRAM 使用率: 83.38%
   使用的節點: colab-gpu4
   使用的 GPU: 2 個
```

### 2. 查詢特定使用者多日 GPU 使用情況

```bash
# 基本格式
python3 get_user_gpu_usage.py <使用者名稱> <開始日期> <結束日期>

# 實際範例
python3 get_user_gpu_usage.py paslab_openai 2025-08-11 2025-08-15
python3 get_user_gpu_usage.py itrd 2025-07-20 2025-07-25
```

### 3. 列出指定日期的所有 GPU 使用者

```bash
# 基本格式
python3 get_user_gpu_usage.py --list-users <日期>

# 實際範例
python3 get_user_gpu_usage.py --list-users 2025-07-22
```

**輸出範例：**
```
📋 2025-07-22 的所有 GPU 使用者:
==================================================

👤 itrd:
   📍 colab-gpu4:GPU[2] - GPU: 20.3%, VRAM: 83.4%
   📍 colab-gpu4:GPU[3] - GPU: 18.2%, VRAM: 82.3%
   📊 平均: GPU 19.2%, VRAM 82.8% (2 GPU)

📈 總共找到 1 位使用者
```

### 4. 生成使用趨勢圖

```bash
# 添加 --plot 參數生成圖表
python3 get_user_gpu_usage.py paslab_openai 2025-08-10 2025-08-15 --plot
```

## 透過 run_user_monitor.sh 使用

為了更方便使用，這些功能已經整合到 `run_user_monitor.sh` 中：

```bash
# 查詢特定使用者單日使用情況
./run_user_monitor.sh query-user paslab_openai 2025-08-15

# 查詢特定使用者多日使用情況  
./run_user_monitor.sh query-user itrd 2025-07-20 2025-07-25

# 列出指定日期的所有使用者
./run_user_monitor.sh list-users 2025-08-15
```

## 進階技巧

### 1. 搜尋包含特定使用者的所有日期

```bash
# 搜尋所有包含 'paslab_openai' 的日期
grep -r 'paslab_openai' data/*/*/average_*.csv | cut -d/ -f3 | sort -u

# 搜尋特定使用者並顯示使用情況
grep -r 'paslab_openai' data/*/*/average_*.csv | grep -v '未使用'
```

### 2. 批量查詢多個使用者

```bash
# 先列出某日的所有使用者，然後逐一查詢
users=$(python3 get_user_gpu_usage.py --list-users 2025-07-22 2>/dev/null | grep "👤" | cut -d' ' -f2 | tr -d ':')

for user in $users; do
    echo "=== 查詢使用者: $user ==="
    python3 get_user_gpu_usage.py "$user" 2025-07-22
    echo
done
```

### 3. 自訂輸出目錄

```bash
# 指定自訂的資料和圖表目錄
python3 get_user_gpu_usage.py paslab_openai 2025-08-15 \
    --data-dir /custom/data/path \
    --plots-dir /custom/plots/path \
    --plot
```

## 輸出說明

### 狀態符號
- 🟢：高活動（GPU 使用率 > 1%）
- 🟡：低活動（GPU 使用率 ≤ 1%）
- 📍：節點和 GPU 位置
- 📊：統計摘要
- 👤：使用者名稱

### 統計指標
- **總記錄數**：找到的 GPU 使用記錄總數
- **有活動記錄數**：GPU 使用率 > 1% 的記錄數和比例
- **平均 GPU 使用率**：所有記錄的平均 GPU 使用率
- **平均 VRAM 使用率**：所有記錄的平均 VRAM 使用率
- **最大使用率**：期間內的最大 GPU 和 VRAM 使用率
- **使用的節點**：涉及的 GPU 節點
- **使用的 GPU**：使用的 GPU 總數

## 故障排除

### 1. 找不到使用者資料
```
❌ 未找到任何使用記錄
```

**可能原因：**
- 使用者名稱拼寫錯誤
- 指定日期沒有該使用者的使用記錄
- 資料檔案不存在或格式不正確

**解決方法：**
```bash
# 1. 檢查使用者名稱是否正確
./run_user_monitor.sh list-users 2025-07-22

# 2. 搜尋使用者的使用記錄
grep -r 'paslab_openai' data/*/*/average_*.csv

# 3. 檢查資料檔案是否存在
ls data/colab-gpu*/2025-07-22/average_2025-07-22.csv
```

### 2. 沒有使用者欄位
```
KeyError: 'user' 或 KeyError: '使用者'
```

**原因：** CSV 檔案缺少使用者欄位（可能是舊版本的資料）

**解決方法：** 使用 Python 版本的資料收集器重新收集資料
```bash
./python/run_daily_gpu_log.sh 2025-09-15
```

### 3. 無法生成圖表
```
⚠️ 未安裝 matplotlib/seaborn，無法生成圖表
```

**解決方法：** 安裝繪圖套件
```bash
pip3 install matplotlib seaborn
```

## 範例腳本

查看 `demo_user_gpu_query.sh` 獲取完整的使用範例：

```bash
./demo_user_gpu_query.sh
```

此腳本包含：
- 列出使用者的範例
- 查詢單一使用者的範例  
- 查詢多日使用情況的範例
- 搜尋技巧示範

## 相關文件

- [USER_INFO_GUIDE.md](USER_INFO_GUIDE.md) - GPU 使用者資訊功能完整說明
- [README.md](README.md) - 專案總覽
- [CHANGELOG.md](CHANGELOG.md) - 版本更新記錄

---

💡 **提示：** 這個工具設計為與現有的 GPU 監控系統完全整合，可以方便地查詢任何使用者的 GPU 使用情況。如果您需要查詢特定使用者如 `paslab_openai`，只需要按照上述格式執行命令即可。