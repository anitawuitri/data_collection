# 🔑 管理 API 配置指南

## 📋 概述

重構版本支援從管理 API 收集使用者任務資訊，以提供更完整的 GPU 使用監控。此功能是**可選的** - 系統在沒有管理 API 配置時仍能正常收集 Netdata 數據。

## ⚙️ 配置步驟

### 1. 獲取 Bearer Token

聯繫系統管理員獲取管理 API 的 Bearer Token。Token 格式通常如下：

```
eyJhbGciOiJIUzI1NiIsImFwaV9hZGRyZXNzIjoiaHR0cDovLzE5Mi4xNjgu...
```

### 2. 設定環境變數

#### 方法 A: 臨時設定 (單次使用)

```bash
export MANAGEMENT_API_TOKEN="your_bearer_token_here"
```

#### 方法 B: 永久設定 (.bashrc)

```bash
echo 'export MANAGEMENT_API_TOKEN="your_bearer_token_here"' >> ~/.bashrc
source ~/.bashrc
```

#### 方法 C: 使用 .env 文件

創建或編輯 `.env` 文件：

```bash
# 管理 API 配置
MANAGEMENT_API_URL=http://192.168.10.100/api/v2/consumption/task
MANAGEMENT_API_TOKEN=your_bearer_token_here
API_TIMEOUT=30
```

### 3. 驗證配置

檢查系統狀態確認配置：

```bash
python3 -m src status
```

應該看到：

```
🔗 API 配置:
   ✅ Bearer Token: eyJhbGci... (已設定)
   📋 功能: Netdata + 使用者資訊收集
```

## 🧪 測試 API 連接

使用調試腳本測試 API 連接：

```bash
python3 debug_management_api.py
```

## ✅ 功能差異

### 沒有 Bearer Token (預設)
- ✅ 收集 Netdata GPU 使用率和 VRAM 數據
- ✅ 生成完整的 CSV 文件
- ❌ 使用者欄位顯示為 "unknown"
- ✅ 系統正常運行，無錯誤

### 有 Bearer Token
- ✅ 收集 Netdata GPU 使用率和 VRAM 數據  
- ✅ 收集使用者任務資訊
- ✅ 使用者欄位顯示實際使用者名稱
- ✅ 支援使用者查詢和統計功能

## 🔧 故障排除

### 常見問題

#### 1. HTTP 422 錯誤
```
管理 API 請求失敗: HTTP 422
```

**解決方法:**
- 檢查 Bearer Token 是否正確
- 確認 Token 沒有過期
- 檢查時間參數格式

#### 2. HTTP 401 錯誤
```
管理 API 請求失敗: HTTP 401
```

**解決方法:**
- Token 無效或過期
- 重新獲取新的 Bearer Token

#### 3. 網路連接錯誤
```
網路請求錯誤: Cannot connect to host
```

**解決方法:**
- 檢查管理服務器是否可達
- 確認 API URL 是否正確
- 檢查網路連接

### 調試步驟

1. **檢查環境變數:**
   ```bash
   echo $MANAGEMENT_API_TOKEN
   ```

2. **測試 API 連接:**
   ```bash
   python3 debug_management_api.py
   ```

3. **查看詳細日誌:**
   ```bash
   python3 -m src --verbose collect daily --dry-run
   ```

## 📊 數據格式

### 無管理 API 數據
```csv
gpu,usage,vram,user
gpu0,25.5,60.2,unknown
gpu1,0.0,0.1,unknown
```

### 有管理 API 數據
```csv
gpu,usage,vram,user
gpu0,25.5,60.2,paslab_openai
gpu1,0.0,0.1,unused
```

## 🚀 最佳實踐

### 1. 分階段部署
1. 先使用無管理 API 模式驗證系統穩定性
2. 取得 Bearer Token 後再啟用使用者資訊收集
3. 對比數據確認一致性

### 2. Token 安全
- 不要在日誌或代碼中洩漏完整 Token
- 定期更新 Token
- 使用環境變數而非硬編碼

### 3. 監控 API 狀態
- 定期檢查 API 連接狀態
- 監控 Token 過期時間
- 設定 API 錯誤警報

---

**注意**: 管理 API 功能是完全可選的。系統在沒有管理 API 配置時仍能提供完整的 GPU 監控功能。