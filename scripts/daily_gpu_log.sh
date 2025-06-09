#!/bin/bash

# 顯示使用方法
usage() {
    echo "使用方法: $0 [日期]"
    echo "日期格式: YYYY-MM-DD (例如: 2025-05-22)"
    echo "如不指定日期，預設使用今天日期"
    exit 1
}

# 解析命令行參數
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# 設定日期：如果有提供參數就使用參數的日期，否則使用今天的日期
if [ -n "$1" ]; then
    # 驗證日期格式
    date -d "$1" > /dev/null 2>&1 || { echo "錯誤: 日期格式無效"; usage; }
    DATE="$1"
else
    DATE=$(date +%Y-%m-%d)
fi

echo "使用日期: $DATE"

outdir_prefix="./data/"
OUTDIR="${outdir_prefix}${DATE}"

# 修改為你的 Netdata 主機或 Docker IP
#NETDATA_HOST="http://localhost:19999"


# 固定 GPU ID 列表
GPU_IDS=(1 9 17 25 33 41 49 57)
echo "使用固定 GPU ID: ${GPU_IDS[@]}"

# 為指定日期計算時間戳記
echo "$DATE 的時間戳記計算..."
TIMESTAMP_START=$(TZ=UTC date -d "$DATE 00:00:00" +%s)
echo "計算時間戳記: $TIMESTAMP_START (UTC)"
# 計算當天結束時間戳記 (23:59:59)
TIMESTAMP_END=$(TZ=UTC date -d "$DATE 23:59:59" +%s)
# 設定數據點間隔為10分鐘，一天共144個點
POINTS=144


# 從多個 IP 擷取 GPU 使用率圖表與資料
# 192.168.10.103: colab-gpu1 , 192.168.10.104: colab-gpu2 , 192.168.10.105: colab-gpu3 , 192.168.10.106: colab-gpu4
IP_LIST=("192.168.10.103" "192.168.10.104" "192.168.10.105" "192.168.10.106")
declare -A IP_NAME_MAP=(
    ["192.168.10.103"]="colab-gpu1"
    ["192.168.10.104"]="colab-gpu2"
    ["192.168.10.105"]="colab-gpu3"
    ["192.168.10.106"]="colab-gpu4"
)
for IP in "${IP_LIST[@]}"; do
    NAME="${IP_NAME_MAP[$IP]}"
    IP_OUTDIR="${outdir_prefix}${NAME}/$DATE"
    mkdir -p "$IP_OUTDIR"
    NETDATA_HOST="http://$IP:19999"

    echo "正在處理 $NAME ($IP)..."
    echo "輸出目錄: $IP_OUTDIR"
    # for GPU_ID in "${GPU_IDS[@]}"; do
    #     # 擷取 SVG 圖表，確保覆蓋整天資料
    #     curl -s "$NETDATA_HOST/api/v1/badge.svg?chart=amdgpu.gpu_utilization_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&format=svg" \
    #         -o "$IP_OUTDIR/gpu${GPU_ID}_$DATE.svg"
    # done
    for GPU_ID in "${GPU_IDS[@]}"; do
        TMP_CSV="$IP_OUTDIR/gpu${GPU_ID}_$DATE.csv.tmp"
        FINAL_CSV="$IP_OUTDIR/gpu${GPU_ID}_$DATE.csv"
        # 擷取一天資料，每10分鐘一個點 (共144點)
        # 第一步：擷取 GPU 使用率數據
        GPU_UTIL_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_utilization_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
        # 第二步：擷取 VRAM 使用率數據
        VRAM_USAGE_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card${GPU_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
        
        # 創建包含時間戳、日期時間、GPU使用率和VRAM使用率的CSV
        echo "時間戳,日期時間,GPU使用率(%),VRAM使用率(%)" > "$TMP_CSV"
        
        # 解析 GPU 使用率數據並存入臨時文件
        GPU_UTIL_DATA=$(echo "$GPU_UTIL_JSON" | jq -r '.data[] | [.[] | if . == null then 0 else . | tonumber end] | [.[0], (.[0] | strftime("%Y-%m-%d %H:%M:%S")), .[1]] | @csv')
        TIMESTAMPS=$(echo "$GPU_UTIL_DATA" | awk -F, '{print $1}' | sed 's/"//g')
        
        # 對每個時間戳，獲取對應的 VRAM 使用率數據
        for TS in $TIMESTAMPS; do
            # 從 GPU 使用率數據中提取此時間戳的行
            GPU_LINE=$(echo "$GPU_UTIL_DATA" | grep "$TS")
            GPU_TIME=$(echo "$GPU_LINE" | awk -F, '{print $2}' | sed 's/"//g')
            GPU_UTIL=$(echo "$GPU_LINE" | awk -F, '{print $3}')
            
            # 從 VRAM 使用率數據中提取此時間戳的值，將 null 處理為 0
            VRAM_USAGE=$(echo "$VRAM_USAGE_JSON" | jq -r --arg ts "$TS" '.data[] | map(if . == null then 0 else . | tonumber end) | select(.[0] == ($ts | tonumber)) | .[1]')
            
            # 若沒有對應的 VRAM 數據，則設為 0
            VRAM_USAGE=${VRAM_USAGE:-0}
            
            # 寫入合併的數據行
            echo "$TS,\"$GPU_TIME\",$GPU_UTIL,$VRAM_USAGE" >> "$TMP_CSV"
        done
        
        # 依照第二欄（時間字串）排序，並保留 header
        { head -n1 "$TMP_CSV"; tail -n +2 "$TMP_CSV" | sort -t, -k2; } > "$FINAL_CSV"
        rm -f "$TMP_CSV"
    done
done


# 依據不同 colab 資料夾計算平均 GPU 使用率
for NAME in colab-gpu1 colab-gpu2 colab-gpu3 colab-gpu4; do
    COLAB_OUTDIR="${outdir_prefix}${NAME}/$DATE"
    echo "計算 $DATE $NAME 的 GPU 平均使用率..."
    echo "GPU卡號,平均GPU使用率(%),平均VRAM使用率(%)" > "$COLAB_OUTDIR/average_$DATE.csv"
    for GPU_ID in "${GPU_IDS[@]}"; do
        CSV_FILE="$COLAB_OUTDIR/gpu${GPU_ID}_$DATE.csv"
        if [ -f "$CSV_FILE" ]; then
            # 計算 GPU 使用率平均值 (第三欄)
            AVG_USAGE=$(awk -F, 'NR>1 {sum+=$3; count++} END {if (count > 0) print sum/count; else print "N/A"}' "$CSV_FILE")
            # 計算 VRAM 使用率平均值 (第四欄)
            AVG_VRAM=$(awk -F, 'NR>1 {sum+=$4; count++} END {if (count > 0) print sum/count; else print "N/A"}' "$CSV_FILE")
            
            # 格式化數值
            if [ "$AVG_USAGE" != "N/A" ]; then
                FORMATTED_AVG_USAGE=$(awk -v avg="$AVG_USAGE" 'BEGIN {printf "%.2f", avg}')
            else
                FORMATTED_AVG_USAGE="N/A"
            fi
            if [ "$AVG_VRAM" != "N/A" ]; then
                FORMATTED_AVG_VRAM=$(awk -v avg="$AVG_VRAM" 'BEGIN {printf "%.2f", avg}')
            else
                FORMATTED_AVG_VRAM="N/A"
            fi
            
            echo "GPU $GPU_ID: 平均使用率 = $FORMATTED_AVG_USAGE%, 平均VRAM使用率 = $FORMATTED_AVG_VRAM%"
            echo "gpu${GPU_ID},$FORMATTED_AVG_USAGE,$FORMATTED_AVG_VRAM" >> "$COLAB_OUTDIR/average_$DATE.csv"
        else
            echo "警告: 找不到 $CSV_FILE 檔案"
            echo "gpu${GPU_ID},N/A,N/A" >> "$COLAB_OUTDIR/average_$DATE.csv"
        fi
    done
    # 計算所有 GPU 的整體平均使用率
    OVERALL_AVG=$(awk -F, 'NR>1 {if ($2 != "N/A") {sum+=$2; count++}} END {if (count > 0) print sum/count; else print "N/A"}' "$COLAB_OUTDIR/average_$DATE.csv")
    # 計算所有 GPU 的整體平均 VRAM 使用率
    OVERALL_VRAM_AVG=$(awk -F, 'NR>1 {if ($3 != "N/A") {sum+=$3; count++}} END {if (count > 0) print sum/count; else print "N/A"}' "$COLAB_OUTDIR/average_$DATE.csv")
    
    # 格式化數值
    if [ "$OVERALL_AVG" != "N/A" ]; then
        FORMATTED_OVERALL_AVG=$(awk -v avg="$OVERALL_AVG" 'BEGIN {printf "%.2f", avg}')
    else
        FORMATTED_OVERALL_AVG="N/A"
    fi
    if [ "$OVERALL_VRAM_AVG" != "N/A" ]; then
        FORMATTED_OVERALL_VRAM_AVG=$(awk -v avg="$OVERALL_VRAM_AVG" 'BEGIN {printf "%.2f", avg}')
    else
        FORMATTED_OVERALL_VRAM_AVG="N/A"
    fi
    
    echo "===========================================" 
    echo "$NAME 所有 GPU 的整體平均使用率: $FORMATTED_OVERALL_AVG%"
    echo "$NAME 所有 GPU 的整體平均 VRAM 使用率: $FORMATTED_OVERALL_VRAM_AVG%"
    echo "===========================================" 
    echo "全部平均,$FORMATTED_OVERALL_AVG,$FORMATTED_OVERALL_VRAM_AVG" >> "$COLAB_OUTDIR/average_$DATE.csv"
    echo "結果已保存至 $COLAB_OUTDIR/average_$DATE.csv"
    # 生成帶有每日平均值的摘要報告
    cat > "$COLAB_OUTDIR/summary_$DATE.txt" << EOL
================================
AMD GPU 與 VRAM 每日使用率統計
日期: $DATE
================================

偵測到的 GPU 卡: ${GPU_IDS[@]}

各 GPU 卡使用率與 VRAM 使用率:



$(awk -F, 'NR>1 {printf "GPU %s: GPU使用率 = %s%%, VRAM使用率 = %s%%\n", $1, $2, $3}' "$COLAB_OUTDIR/average_$DATE.csv")

整體平均 GPU 使用率: $FORMATTED_OVERALL_AVG%
整體平均 VRAM 使用率: $FORMATTED_OVERALL_VRAM_AVG%
================================
EOL
    echo "摘要報告已保存至 $COLAB_OUTDIR/summary_$DATE.txt"
done


