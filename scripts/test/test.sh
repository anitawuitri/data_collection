#!/bin/bash
NETDATA_HOST="http://192.168.10.103:19999"
GPU_ID=1

DATE="2025-06-11"

echo "$DATE 的時間戳記計算..."
TIMESTAMP_START=$(TZ=UTC date -d "$DATE 00:00:00" +%s)
echo "計算時間戳記: $TIMESTAMP_START (UTC)"
# 計算當天結束時間戳記 (23:59:59)
TIMESTAMP_END=$(TZ=UTC date -d "$DATE 23:59:59" +%s)
# 設定數據點間隔為10分鐘，一天共144個點
POINTS=144



GPU_UTIL_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_utilization_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
        # 第二步：擷取 VRAM 使用率數據
#VRAM_USAGE_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
 
        