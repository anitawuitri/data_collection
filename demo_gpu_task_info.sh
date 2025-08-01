#!/bin/bash

echo "=== GPU 使用者任務資訊功能演示 ==="
echo
echo "1. 顯示 GPU 使用者任務報告 (2025-07-22):"
echo "-------------------------------------------"
python3 python/daily_gpu_log.py --user-report 2025-07-22 | head -50
echo
echo "2. 可用的命令列選項:"
echo "-------------------"
echo "# 正常數據收集 (包含使用者資訊)"
echo "python3 python/daily_gpu_log.py 2025-07-22"
echo
echo "# 只顯示使用者任務報告"
echo "python3 python/daily_gpu_log.py --user-report 2025-07-22"
echo
echo "# 跳過使用者任務資訊"
echo "python3 python/daily_gpu_log.py --skip-task-info 2025-07-22"
echo
echo "3. 檢查說明文件:"
echo "---------------"
echo "詳細說明請參考:"
echo "- GPU_TASK_INFO_INTEGRATION.md"
echo "- GPU_MAPPING_INTEGRATION_REPORT.md"
echo
echo "4. 測試功能:"
echo "----------"
echo "執行 'python3 test_gpu_task_info.py' 進行完整功能測試"
