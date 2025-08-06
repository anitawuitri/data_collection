# AMD GPU 數據收集工具 - Python 版本

> 🔥 **重大更新 (2025-08-01)**: GPU 使用者追蹤系統已整合！現在可以顯示每個 GPU 的使用者資訊。

這是原本 `scripts/daily_gpu_log.sh` 的 Python 重寫版本，提供相同的功能但使用 Python 實現，具有更好的錯誤處理、數據處理能力和可擴展性。現在還包含了完整的 GPU 使用者追蹤功能。

## 🚀 功能特色

### 🔥 新增功能（2025-08-01）
- **GPU 使用者追蹤**: 即時顯示哪些使用者正在使用哪些 GPU
- **硬體對應表**: 自動建立 GPU Card ID 到 GPU Index 的對應關係
- **管理 API 整合**: 透過 JWT 認證從管理系統獲取使用者任務資訊
- **增強報表格式**: CSV 檔案和摘要報告包含詳細使用者資訊

### 完全相容
- **輸出格式相容**: 生成與原 shell 腳本相同的 CSV 和報告格式（並增強功能）
- **目錄結構相容**: 使用相同的數據目錄結構
- **功能對等**: 提供所有原腳本的功能，並新增使用者追蹤

### Python 優勢  
- **🔥 GPU 使用者追蹤**: 整合管理 API，自動顯示 GPU 使用者資訊
- **硬體對應系統**: 自動建立 GPU Card ID 到 GPU Index 對應表
- **增強數據格式**: CSV 檔案包含使用者欄位，摘要報告顯示詳細任務資訊
- **更好的錯誤處理**: 詳細的異常處理和錯誤訊息
- **數據處理能力**: 使用 pandas 進行高效的數據操作
- **HTTP 請求**: 使用 requests 庫提供穩定的網路請求
- **模組化設計**: 面向對象的程式設計，易於維護和擴展

## 📋 需求

### Python 環境
- Python 3.7+
- requests >= 2.25.0  
- pandas >= 1.3.0

### 系統需求
- 網路連線到各 GPU 節點 (192.168.10.103-106)
- 各節點 Netdata 服務運行在端口 19999
- **🔥 管理系統連線**: 連線到管理 API (192.168.10.100) 以獲取使用者資訊
- **JWT Token**: 管理 API 的有效 Bearer Token

## 🛠️ 安裝

### 1. 安裝 Python 依賴

```bash
# 切換到 python 目錄
cd /path/to/data_collection/python

# 安裝依賴套件
pip3 install -r requirements.txt

# 或者使用虛擬環境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 設定執行權限

```bash
chmod +x run_daily_gpu_log.sh
```

## 📖 使用方法

### 🔥 快速體驗使用者追蹤功能

```bash
# 測試使用者欄位功能
python3 test_user_column.py

# 收集包含使用者資訊的今日數據
./python/run_daily_gpu_log.sh

# 查看使用者資訊（CSV 格式）
head -10 data/colab-gpu4/$(date +%Y-%m-%d)/average_$(date +%Y-%m-%d).csv

# 查看詳細使用者任務資訊
cat data/colab-gpu4/$(date +%Y-%m-%d)/summary_$(date +%Y-%m-%d).txt
```

### 基本用法

```bash
# 收集今天的數據（包含使用者資訊）
./python/run_daily_gpu_log.sh

# 收集指定日期的數據  
./python/run_daily_gpu_log.sh 2025-08-01

# 顯示說明
./python/run_daily_gpu_log.sh --help
```

### 直接使用 Python 腳本

```bash
# 收集今天的數據
python3 python/daily_gpu_log.py

# 收集指定日期的數據
python3 python/daily_gpu_log.py 2025-08-01

# 自訂數據目錄
python3 python/daily_gpu_log.py --data-dir /custom/path

# 顯示完整說明
python3 python/daily_gpu_log.py --help
```

## 📊 輸出格式

### 🔥 新增使用者資訊格式

#### GPU 硬體對應表
系統自動建立以下對應關係：
```
GPU[0] -> Card 1    GPU[4] -> Card 33
GPU[1] -> Card 9    GPU[5] -> Card 41  
GPU[2] -> Card 17   GPU[6] -> Card 49
GPU[3] -> Card 25   GPU[7] -> Card 57
```

#### 使用者任務資訊來源
- **管理 API 端點**: `http://192.168.10.100/api/v2/consumption/task`
- **認證方式**: JWT Bearer Token
- **功能**: 獲取 GPU 使用者任務資訊，包含使用者名稱、任務類型、GPU UUID 等

### 數據結構

輸出的數據結構與原 shell 腳本完全相同，但增加了使用者資訊：

```
data/
├── colab-gpu1/
│   └── 2025-08-01/
│       ├── gpu1_2025-08-01.csv        # 各 GPU 的詳細數據
│       ├── gpu9_2025-08-01.csv        # ...
│       ├── ...
│       ├── average_2025-08-01.csv     # 🔥 平均使用率統計（含使用者欄位）
│       └── summary_2025-08-01.txt     # 🔥 摘要報告（含詳細使用者任務資訊）
├── colab-gpu2/
├── colab-gpu3/
└── colab-gpu4/
```

### CSV 檔案格式

每個 GPU 的 CSV 檔案包含：
```csv
時間戳,日期時間,GPU使用率(%),VRAM使用率(%)
1722470400,"2025-08-01 00:00:00",1.23,45.67
1722471000,"2025-08-01 00:10:00",2.45,47.89
...
```

### CSV 檔案格式

每個 GPU 的 CSV 檔案包含：
```csv
時間戳,日期時間,GPU使用率(%),VRAM使用率(%)
1722470400,"2025-08-01 00:00:00",1.23,45.67
1722471000,"2025-08-01 00:10:00",2.45,47.89
...
```

### 🔥 平均值 CSV 格式（包含使用者資訊）

**新格式**（包含使用者欄位）：
```csv
GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者
GPU[0],0.00,0.14,未使用
GPU[1],0.00,0.14,未使用
GPU[2],20.28,83.38,未使用
GPU[3],18.17,82.27,nycubme
GPU[4],0.00,0.14,未使用
GPU[5],0.00,0.14,未使用
GPU[6],0.00,0.14,未使用
GPU[7],0.00,0.14,未使用
全部平均,4.81,20.81,所有使用者
```

**舊格式對比**：
```csv
GPU卡號,平均GPU使用率(%),平均VRAM使用率(%)
gpu1,12.34,56.78
gpu9,23.45,67.89
...
全部平均,18.75,62.33
```

### 🔥 摘要報告格式（包含使用者任務資訊）

**範例摘要報告**：
```
================================
AMD GPU 與 VRAM 每日使用率統計
日期: 2025-08-01
節點: colab-gpu4
================================

GPU 硬體對應表:
GPU[0] -> Card 1
GPU[1] -> Card 9
GPU[2] -> Card 17
GPU[3] -> Card 25
GPU[4] -> Card 33
GPU[5] -> Card 41
GPU[6] -> Card 49
GPU[7] -> Card 57

GPU 使用者任務資訊:
--------------------------------------------------
colab-gpu4 GPU 任務資訊:
  GPU 25: nycubme
    - GPU 型號: AMD Instinct MI300X
    - GPU 記憶體: 196592 MB
    - 任務類型: LAB
    - 專案 UUID: pd6ce655
    - 映像檔: myelintek/labu1f682d9:1750235191
    - 開始時間: Mon, 14 Jul 2025 14:22:00 GMT
    - 狀態: 執行中
    - 使用時長: 86399.0 秒
    - GPU UUID: APU-70cb99ce3e214bda

各 GPU 使用率與 VRAM 使用率:
GPU[0]: GPU使用率 = 0.0%, VRAM使用率 = 0.14% (使用者: 未使用)
GPU[1]: GPU使用率 = 0.0%, VRAM使用率 = 0.14% (使用者: 未使用)
GPU[2]: GPU使用率 = 20.28%, VRAM使用率 = 83.38% (使用者: 未使用)
GPU[3]: GPU使用率 = 18.17%, VRAM使用率 = 82.27% (使用者: nycubme)
GPU[4]: GPU使用率 = 0.0%, VRAM使用率 = 0.14% (使用者: 未使用)
GPU[5]: GPU使用率 = 0.0%, VRAM使用率 = 0.14% (使用者: 未使用)
GPU[6]: GPU使用率 = 0.0%, VRAM使用率 = 0.14% (使用者: 未使用)
GPU[7]: GPU使用率 = 0.0%, VRAM使用率 = 0.14% (使用者: 未使用)

整體平均 GPU 使用率: 4.81%
整體平均 VRAM 使用率: 20.81%
================================
```

## 🔧 技術實現

### 🔥 新增功能實現

#### GPU 使用者追蹤系統
```python
def fetch_gpu_task_info(self):
    """從管理 API 獲取 GPU 使用者任務資訊"""
    # JWT Bearer Token 認證
    # 解析 GPU UUID 與使用者名稱對應
    # 建立 GPU Card ID 到使用者的映射

def get_gpu_user_mapping(self, node_tasks):
    """建立 GPU ID 到使用者名稱的對應"""
    # 根據 Card ID 對應到 GPU Index
    # 返回 {gpu_index: username} 映射

def calculate_averages(self, date_str):
    """計算平均值並包含使用者資訊"""
    # 生成包含使用者欄位的 CSV
    # 創建詳細的摘要報告
```

#### GPU 硬體對應表
```python
# GPU Card ID 到 GPU Index 的對應
self.gpu_card_mapping = {
    1: 0, 9: 1, 17: 2, 25: 3, 
    33: 4, 41: 5, 49: 6, 57: 7
}
```

### 類別架構

```python
class GPUDataCollector:
    """主要的數據收集器類別"""
    
    def __init__(self, data_dir="./data"):
        # 初始化配置
        # 🔥 新增：管理 API 設定和 GPU 對應表
    
    def collect_data(self, date_str=None):
        # 主要收集流程
        # 🔥 新增：整合使用者任務資訊收集
    
    def fetch_netdata_data(self, host, chart, start, end):
        # 從 Netdata API 獲取數據
    
    def fetch_gpu_task_info(self):
        # 🔥 新增：從管理 API 獲取使用者任務資訊
    
    def process_gpu_data(self, ip, name, date, start, end):
        # 處理單一節點的數據
    
    def calculate_averages(self, date_str):
        # 計算平均值和生成報告
        # 🔥 新增：包含使用者資訊的報告生成
    
    def get_gpu_user_mapping(self, node_tasks):
        # 🔥 新增：建立 GPU ID 到使用者名稱的對應
    
    def generate_summary_report(self, node, date_str, averages_df, gpu_user_mapping):
        # 🔥 新增：生成包含使用者任務資訊的詳細摘要
```

### 關鍵特性

1. **穩定的網路請求**: 使用 requests 庫處理 HTTP 請求，包含超時和錯誤處理
2. **🔥 管理 API 整合**: 透過 JWT Bearer Token 從管理系統獲取使用者任務資訊
3. **高效數據處理**: 使用 pandas 進行數據操作和統計計算
4. **🔥 智能使用者對應**: 自動建立 GPU Card ID 到 GPU Index 到使用者名稱的完整對應
5. **時間戳處理**: 正確處理 UTC 時間戳轉換
6. **錯誤恢復**: 單一節點失敗不會影響其他節點的數據收集
7. **🔥 增強報表格式**: 生成包含使用者資訊的 CSV 和詳細摘要報告

## 🆚 與原 Shell 腳本的比較

| 特性 | Shell 腳本 | Python 版本 |
|------|------------|--------------|
| 執行速度 | 較快 | 稍慢（但差異不大） |
| 錯誤處理 | 基本 | 詳細且精確 |
| 數據處理 | 基本（awk/sed） | 強大（pandas） |
| **🔥 GPU 使用者追蹤** | ❌ 無 | ✅ 完整支援 |
| **硬體對應表** | ❌ 無 | ✅ 自動建立 |
| **使用者欄位報表** | ❌ 無 | ✅ CSV 和摘要 |
| **管理 API 整合** | ❌ 無 | ✅ JWT 認證 |
| 維護性 | 中等 | 高 |
| 可擴展性 | 有限 | 優秀 |
| 依賴 | 系統工具 | Python 套件 |
| 記憶體使用 | 低 | 中等 |

## 🐛 常見問題

### 🔥 使用者追蹤相關問題

#### 1. 管理 API 連線問題
```
錯誤：無法從管理 API 獲取數據
```
**解決方案**: 
- 檢查管理系統是否運行：`ping 192.168.10.100`
- 確認 API 端點：`curl http://192.168.10.100/api/v2/consumption/task`
- 檢查 JWT Bearer Token 是否有效

#### 2. 使用者資訊顯示為空
```
CSV 檔案中使用者欄位顯示為 "未使用"
```
**解決方案**: 
- 檢查 GPU 是否真的有人使用
- 驗證 GPU UUID 對應是否正確
- 測試使用者欄位功能：`python3 test_user_column.py`

#### 3. GPU 硬體對應錯誤
```
GPU Index 對應到錯誤的 Card ID
```
**解決方案**: 
- 檢查摘要報告中的硬體對應表
- 確認對應關係：`GPU[0] -> Card 1`, `GPU[1] -> Card 9`, 等等

### 網路和系統問題

#### 4. 網路連線問題
```
錯誤：無法從 http://192.168.10.103:19999 獲取數據
```
**解決方案**: 檢查節點的 Netdata 服務是否運行，確認網路連線

#### 5. Python 套件缺失
```
ModuleNotFoundError: No module named 'requests'
```
**解決方案**: 執行 `pip3 install -r requirements.txt`

#### 6. 權限問題
```
Permission denied: ./run_daily_gpu_log.sh
```
**解決方案**: 執行 `chmod +x run_daily_gpu_log.sh`

#### 7. 數據目錄權限
```
PermissionError: [Errno 13] Permission denied: './data/colab-gpu1'
```
**解決方案**: 確認對數據目錄有寫入權限

## 🔄 遷移指南

從原 shell 腳本遷移到 Python 版本：

1. **安裝依賴**: `pip3 install -r python/requirements.txt`
2. **測試執行**: `./python/run_daily_gpu_log.sh`
3. **驗證輸出**: 確認生成的檔案格式正確
4. **更新 cron**: 修改定時任務指向新的 Python 腳本

### 更新 crontab 範例

```bash
# 原來的設定
45 23 * * * /bin/bash /path/to/data_collection/scripts/daily_gpu_log.sh

# 新的設定
45 23 * * * /bin/bash /path/to/data_collection/python/run_daily_gpu_log.sh
```

## 🚀 未來擴展

Python 版本為未來功能擴展提供了良好的基礎：

### 🔥 已實現功能（2025-08-01）
- ✅ **GPU 使用者追蹤系統** - 完整的使用者任務資訊整合
- ✅ **硬體對應表** - 自動建立 GPU Card ID 到 GPU Index 對應
- ✅ **管理 API 整合** - JWT 認證和 API 數據解析
- ✅ **增強報表格式** - 包含使用者資訊的 CSV 和摘要報告

### 計劃中的功能
- **並行處理**: 可使用多執行緒同時收集多個節點的數據
- **數據驗證**: 更複雜的數據品質檢查
- **通知系統**: 收集失敗時的自動通知
- **配置檔案**: 支援外部配置檔案
- **日誌系統**: 詳細的日誌記錄和分析
- **數據庫支援**: 直接寫入數據庫而非檔案
- **🔥 使用者告警**: GPU 使用率異常時通知使用者
- **🔥 資源衝突檢測**: 檢測多使用者 GPU 衝突情況

## 📝 開發建議

在此 Python 版本基礎上進行開發時，建議：

1. **保持相容性**: 確保輸出格式與現有視覺化工具相容
2. **🔥 使用者隱私**: 處理使用者資訊時注意隱私保護
3. **🔥 API 穩定性**: 管理 API 變更時確保向後相容
4. **錯誤處理**: 加強網路異常和數據異常的處理
5. **效能優化**: 考慮使用異步請求提升收集速度
6. **測試覆蓋**: 為關鍵功能編寫單元測試
7. **文檔更新**: 保持程式碼註解和使用文檔的同步更新
8. **🔥 使用者體驗**: 優化使用者資訊的展示和查詢功能

### 🔥 使用者追蹤功能最佳實踐

1. **資料驗證**: 確認 GPU UUID 對應的正確性
2. **錯誤處理**: 管理 API 不可用時的優雅降級
3. **快取機制**: 考慮快取使用者資訊以提升效能
4. **日誌記錄**: 記錄 API 呼叫和使用者對應的詳細日誌

---

💡 **提示**: 現在 Python 版本已包含完整的 GPU 使用者追蹤功能，建議所有新部署都使用此版本以獲得最佳的監控體驗！
