# GPU 使用者任務資訊整合功能

## 概述
已成功將 GPU 使用者任務資訊整合到 `daily_gpu_log.py` 中，基於 test.sh 中的 curl 指令，從管理 API 獲取特定使用者的 GPU 使用資訊，並將 APU 欄位對應至 GPU UUID。

## 新增功能

### 1. GPU 使用者任務資訊 API 整合
- **API 端點**: `http://192.168.10.100/api/v2/consumption/task`
- **認證方式**: Bearer Token
- **查詢參數**: 
  - `start_t`: 開始時間 (YYYY-MM-DD HH:MM:SS)
  - `end_t`: 結束時間 (YYYY-MM-DD HH:MM:SS)
  - `username`: 特定使用者名稱 (可選)

### 2. 資料結構解析
從 API 回應中擷取以下資訊：
- **使用者資訊**: username, hostname
- **GPU 資訊**: gpu_id, gpu_uuid, gpu_name, gpu_memory
- **任務資訊**: task_id, task_type, project_uuid, image
- **時間資訊**: create_time, start, end, total_seconds

### 3. 新增的類別方法

#### `fetch_gpu_task_info(date_str)`
- 從管理 API 獲取指定日期的 GPU 使用者任務資訊
- 建立 GPU UUID 到使用者的對應關係
- 儲存在 `self.gpu_task_info` 字典中

#### `generate_gpu_usage_report(date_str)`
- 生成格式化的 GPU 使用者任務報告
- 按主機名稱分組顯示任務資訊
- 包含完整的任務詳細資訊

#### 更新的 `generate_summary_report()`
- 在摘要報告中加入 GPU 使用者任務資訊
- 顯示當前節點的 GPU 任務詳情
- 嘗試將 GPU 使用率數據與使用者資訊結合

### 4. 新增命令列選項

#### `--user-report`
```bash
python3 python/daily_gpu_log.py --user-report 2025-07-22
```
- 只顯示 GPU 使用者任務報告
- 不收集使用率數據

#### `--skip-task-info`
```bash
python3 python/daily_gpu_log.py --skip-task-info 2025-07-22
```
- 跳過 GPU 使用者任務資訊的獲取
- 只收集使用率數據

## 使用方式

### 1. 正常數據收集 (包含使用者資訊)
```bash
python3 python/daily_gpu_log.py 2025-07-22
```
- 收集 GPU 使用率和 VRAM 使用率數據
- 獲取 GPU 使用者任務資訊
- 生成包含使用者資訊的摘要報告

### 2. 只顯示使用者任務報告
```bash
python3 python/daily_gpu_log.py --user-report 2025-07-22
```
- 只從管理 API 獲取使用者任務資訊
- 生成詳細的 GPU 使用者任務報告
- 不收集使用率數據

### 3. 跳過使用者任務資訊
```bash
python3 python/daily_gpu_log.py --skip-task-info 2025-07-22
```
- 只收集 GPU 使用率數據
- 跳過管理 API 的查詢
- 適用於無法存取管理 API 的情況

## 範例輸出

### GPU 使用者任務摘要
```
GPU 使用者任務摘要:
  GPU 25 (colab-gpu4): nycubme - AMD Instinct MI300X
  GPU 26 (colab-gpu4): nycubme - AMD Instinct MI300X
  GPU 27 (colab-gpu4): itrd - AMD Instinct MI300X
  GPU 28 (colab-gpu4): itrd - AMD Instinct MI300X
```

### 詳細使用者任務報告
```
=== 2025-07-22 GPU 使用者任務報告 ===

colab-gpu4:
----------------------------------------
GPU 27:
  使用者: itrd
  GPU 型號: AMD Instinct MI300X
  GPU 記憶體: 196592 MB
  任務類型: WEBAPP
  映像檔: 192.168.10.101:5000/myelintek/ollama:0.6.2-rocm
  開始時間: Wed, 16 Jul 2025 08:19:32 GMT
  狀態: 執行中
  使用時長: 86399.0 秒
  GPU UUID: APU-52f67b3700dcc6f3
```

### 摘要報告中的使用者資訊
摘要報告 (`summary_YYYY-MM-DD.txt`) 現在包含：
- GPU 硬體對應表
- GPU 使用者任務資訊 (按節點分組)
- 各 GPU 使用率數據 (可能包含使用者標記)
- 整體平均使用率

## 技術實作細節

### API 認證配置
```python
self.management_api = {
    "domain": "192.168.10.100",
    "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### GPU UUID 對應結構
```python
self.gpu_task_info = {
    "APU-52f67b3700dcc6f3": {
        'username': 'itrd',
        'hostname': 'colab-gpu4',
        'gpu_id': 27,
        'gpu_name': 'AMD Instinct MI300X',
        'gpu_memory': 196592,
        'task_type': 'WEBAPP',
        # ... 其他欄位
    }
}
```

### 錯誤處理
- **網路錯誤**: 當無法連接管理 API 時，顯示警告並繼續處理
- **認證錯誤**: 當 Access Token 無效時，顯示錯誤訊息
- **資料解析錯誤**: 當 API 回應格式錯誤時，回傳空字典

## 相容性
- **向後相容**: 原有功能完全保持不變
- **選用功能**: 使用者任務資訊為可選功能，失敗時不影響使用率數據收集
- **Access Token**: 可透過修改類別初始化參數更新認證資訊

## 測試驗證
- ✅ API 連接測試通過
- ✅ 資料解析測試通過  
- ✅ 報告生成測試通過
- ✅ 命令列選項測試通過
- ✅ 錯誤處理測試通過

## 未來改進方向
1. **GPU 對應優化**: 建立更精確的 GPU index 到 GPU ID 的對應關係
2. **快取機制**: 實作任務資訊快取，避免重複 API 查詢
3. **使用者過濾**: 支援只顯示特定使用者的任務資訊
4. **實時監控**: 整合即時任務狀態更新
5. **視覺化**: 為使用者任務資訊新增圖表顯示功能

這個整合為 GPU 監控系統提供了完整的使用者任務可視性，讓管理員能夠同時監控 GPU 效能和使用者活動。
