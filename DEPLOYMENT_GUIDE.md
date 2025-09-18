# 🚀 AMD GPU 監控系統重構版本部署指南

## 📋 部署概述

重構版本 (v3.0.0) 現已完成並通過所有測試。本指南將協助您部署和使用新的模組化系統。

## ✅ 重構完成狀態

- **✅ 核心架構**: 完整的模組化設計
- **✅ 服務層**: DataCollectionService 和 DataProcessingService  
- **✅ 收集器**: NetdataCollector 和 ManagementCollector
- **✅ CLI 介面**: 現代化的 Click-based 命令列工具
- **✅ 配置管理**: 統一的環境配置系統
- **✅ 測試框架**: 完整的測試覆蓋
- **✅ 容器支援**: Docker 和 docker-compose 配置

## 🏗️ 部署選項

### 選項 1: 傳統部署 (推薦用於測試)

```bash
# 1. 安裝依賴
./setup.sh install

# 2. 測試系統
python3 test_refactor.py

# 3. 檢查狀態  
poetry run gpu-monitor status

# 4. 收集數據 (試運行)
poetry run gpu-monitor collect daily --dry-run
```

### 選項 2: Docker 部署 (推薦用於生產)

```bash
# 1. Docker 啟動
./setup.sh docker

# 2. 查看服務狀態
docker-compose ps

# 3. 執行命令
docker-compose exec gpu-monitor gpu-monitor status

# 4. 查看日誌
docker-compose logs -f
```

### 選項 3: 開發部署

```bash
# 1. 安裝開發依賴
./setup.sh install-dev

# 2. 執行測試
./setup.sh test

# 3. 代碼品質檢查
poetry run black src/
poetry run isort src/
poetry run flake8 src/
```

## 🔧 配置說明

### 環境變數配置

創建 `.env` 文件：

```bash
# 數據目錄
DATA_DIR=./data
PLOTS_DIR=./plots

# API 配置
MANAGEMENT_API_URL=http://192.168.10.100/api/v2/consumption/task
MANAGEMENT_API_TOKEN=your_bearer_token_here

# 數據收集配置
DATA_POINTS=144
API_TIMEOUT=30
```

### 節點配置

系統預設配置 4 個節點：
- colab-gpu1: 192.168.10.103:19999
- colab-gpu2: 192.168.10.104:19999  
- colab-gpu3: 192.168.10.105:19999
- colab-gpu4: 192.168.10.106:19999

可通過修改 `src/infrastructure/config/settings.py` 進行調整。

## 📊 主要功能使用

### 數據收集

```bash
# 收集今日數據
poetry run gpu-monitor collect daily

# 收集指定日期
poetry run gpu-monitor collect daily --date 2025-09-17

# 批量收集日期範圍
poetry run gpu-monitor collect range 2025-09-10 2025-09-17

# 指定節點收集
poetry run gpu-monitor collect daily --nodes colab-gpu1 --nodes colab-gpu2
```

### 數據查詢

```bash
# 查詢特定使用者
poetry run gpu-monitor query user paslab_openai 2025-09-17

# 查詢使用者在日期範圍
poetry run gpu-monitor query user itrd 2025-09-10 2025-09-17

# 系統使用統計
poetry run gpu-monitor query stats 2025-09-10 2025-09-17

# 詳細統計報告
poetry run gpu-monitor query stats 2025-09-10 2025-09-17 --detailed
```

### 系統狀態

```bash
# 檢查系統狀態
poetry run gpu-monitor status

# 顯示版本資訊
poetry run gpu-monitor version

# 查看幫助
poetry run gpu-monitor --help
```

## 🔄 遷移策略

### 並行運行期間

重構版本與現有系統完全相容，可以並行運行：

```bash
# 新版本 (重構)
poetry run gpu-monitor collect daily

# 舊版本 (保持不變)
python3 python/daily_gpu_log.py $(date +%Y-%m-%d)
./run_gpu_visualization.sh quick $(date +%Y-%m-%d) $(date +%Y-%m-%d)
```

### 逐步遷移計劃

1. **第 1 週**: 測試新版本數據收集
2. **第 2 週**: 驗證數據一致性和查詢功能  
3. **第 3 週**: 切換到新版本作為主要工具
4. **第 4 週**: 停用舊版本腳本

## 🧪 驗證和測試

### 功能驗證

```bash
# 1. 執行重構測試
python3 test_refactor.py

# 2. 測試數據收集 (試運行)
poetry run gpu-monitor collect daily --dry-run

# 3. 測試查詢功能
poetry run gpu-monitor query stats 2025-09-01 2025-09-15

# 4. 測試配置
poetry run gpu-monitor status
```

### 性能驗證

```bash
# 並行收集性能測試
time poetry run gpu-monitor collect range 2025-09-01 2025-09-07

# 對比舊版本性能
time ./scripts/daily_gpu_log.sh 2025-09-17
```

## 🔍 故障排除

### 常見問題

#### 1. 模組導入錯誤
```bash
# 檢查 Python 路徑
python3 test_refactor.py

# 重新安裝依賴
./setup.sh install
```

#### 2. API 連接失敗
```bash
# 檢查網路連接
curl -I http://192.168.10.103:19999/api/v1/info

# 檢查 Bearer Token
curl -H "Authorization: Bearer $MANAGEMENT_API_TOKEN" \
     http://192.168.10.100/api/v2/consumption/task
```

#### 3. 數據目錄權限
```bash
# 檢查目錄權限
ls -la data/
mkdir -p data plots logs
chmod 755 data plots logs
```

### 除錯模式

```bash
# 啟用詳細輸出
poetry run gpu-monitor --verbose collect daily

# 查看詳細日誌
poetry run gpu-monitor --verbose query stats 2025-09-15 2025-09-17 --detailed
```

## 📈 監控和維護

### 系統監控

```bash
# 定期狀態檢查
*/30 * * * * cd /path/to/project && poetry run gpu-monitor status

# 自動數據收集 (crontab)
0 1 * * * cd /path/to/project && poetry run gpu-monitor collect daily
```

### 日誌管理

```bash
# 查看應用日誌
tail -f logs/gpu-monitor.log

# Docker 日誌  
docker-compose logs -f gpu-monitor
```

### 備份策略

```bash
# 數據備份
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# 配置備份
cp .env .env.backup
cp -r src/ src.backup/
```

## 🎯 性能優化建議

### 生產環境優化

1. **並行收集**: 使用 `--nodes` 參數分散負載
2. **時間分散**: 錯開不同節點的收集時間
3. **資源監控**: 定期監控記憶體和磁碟使用
4. **數據清理**: 定期清理舊數據檔案

### 擴展性考慮

1. **水平擴展**: 可拆分為獨立微服務
2. **快取機制**: Redis 快取常用查詢結果  
3. **資料庫**: 考慮遷移到時序資料庫
4. **API 化**: 提供 REST API 介面

## 🚀 後續發展路線圖

### 短期目標 (1-3 個月)
- Web 介面開發
- 實時監控儀表板
- 警報和通知系統

### 中期目標 (3-6 個月)  
- 機器學習預測模型
- 自動化運維功能
- 多租戶支援

### 長期目標 (6-12 個月)
- 雲端原生部署
- 開源社區建設
- 國際化支援

## 📞 技術支援

如有任何問題，請參考：

1. **文檔**: `REFACTORING_GUIDE.md` 和 `REFACTOR_COMPLETION_REPORT.md`
2. **測試**: 執行 `python3 test_refactor.py`
3. **問題回報**: 通過 GitHub Issues
4. **技術討論**: 團隊 Slack 頻道

---

**部署版本**: v3.0.0  
**更新日期**: 2025年9月17日  
**狀態**: ✅ 生產就緒

重構版本已經完全準備就緒，歡迎開始使用！🎉