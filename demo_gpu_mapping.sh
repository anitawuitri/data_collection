#!/bin/bash

echo "=== GPU 硬體對應表示範 ==="
echo
echo "1. 檢查 gpu_hardware_mapping.txt 內容:"
echo "------------------------------------"
cat gpu_hardware_mapping.txt
echo
echo "2. Shell 腳本中的對應表初始化:"
echo "--------------------------------"
grep -A 10 "declare -A GPU_CARD_TO_INDEX" scripts/daily_gpu_log.sh
echo
echo "3. Python 腳本中的對應表初始化:"
echo "-------------------------------"
grep -A 5 "gpu_card_to_index = {" python/daily_gpu_log.py
echo
echo "4. 新的檔案命名方式:"
echo "-------------------"
echo "舊方式: gpu1_2025-05-25.csv, gpu9_2025-05-25.csv, gpu17_2025-05-25.csv ..."
echo "新方式: gpu0_2025-05-25.csv, gpu1_2025-05-25.csv, gpu2_2025-05-25.csv ..."
echo
echo "5. 摘要報告中的硬體對應資訊:"
echo "---------------------------"
echo "報告將包含 GPU 硬體對應表，顯示 GPU[index] 與 Card ID 的對應關係"
echo
echo "6. 測試結果:"
echo "----------"
python3 test_gpu_mapping.py | grep "測試結果總結" -A 4
