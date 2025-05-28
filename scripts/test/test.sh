#!/bin/bash
#IP_OUTDIR="
NETDATA_HOST="http://192.168.10.105:19999"
GPU_ID=1
POINTS=3
#Date=$(date +%Y-%m-%d)
Date="2025-05-26"

# 為指定日期計算時間戳記
TIMESTAMP_START=$(TZ=UTC date -d "$DATE 00:00:00" +%s)
# 計算當天結束時間戳記 (23:59:59)
TIMESTAMP_END=$(TZ=UTC date -d "$DATE 00:30:00" +%s)


TMP_CSV="test.csv.tmp"
        FINAL_CSV="test.csv"
        # 擷取一天資料，每10分鐘一個點 (共144點)
        curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_utilization_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json" \
            | jq -r '.data[] | [.[] | tonumber] | [.[0], (.[0] | strftime("%Y-%m-%d %H:%M:%S")), .[1]] | @csv' > "$TMP_CSV"
        # 依照第二欄（時間字串）排序，並保留 header
        (head -n1 "$TMP_CSV" && tail -n +2 "$TMP_CSV" | sort -t, -k2) > "$FINAL_CSV"
        rm -f "$TMP_CSV"
        