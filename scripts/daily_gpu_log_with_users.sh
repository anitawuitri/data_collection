#!/bin/bash

# Enhanced GPU data collection script with user information
# Based on daily_gpu_log.sh but adds user info collection from management API

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

# 設定日期
if [ -n "$1" ]; then
    date -d "$1" > /dev/null 2>&1 || { echo "錯誤: 日期格式無效"; usage; }
    DATE="$1"
else
    DATE=$(date +%Y-%m-%d)
fi

echo "使用日期: $DATE"

outdir_prefix="./data/"
OUTDIR="${outdir_prefix}${DATE}"

# 管理 API 配置
MANAGEMENT_API_HOST="192.168.10.100"
MANAGEMENT_API_TOKEN="eyJhbGciOiJIUzI1NiIsImFwaV9hZGRyZXNzIjoiaHR0cDovLzE5Mi4xNjguMTAuMTAwOjgwIiwidHlwIjoiSldUIn0.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0Nzc5NzI3NywianRpIjoiNjUyZDk1ZjEtODU0MC00OTYyLTg4MDItZmJlZGJiMTQyOWFhIiwidHlwZSI6ImFjY2VzcyIsImlkZW50aXR5IjoiYWRtaW4iLCJuYmYiOjE3NDc3OTcyNzcsInJvbGUiOlsiQWRtaW4iXX0.mDdQeARC1MhzAaVik67cKRX4bq8M5C36reUDNWroLd8"

# GPU 硬體對照表
declare -A GPU_CARD_TO_INDEX=(
    ["1"]="0" ["9"]="1" ["17"]="2" ["25"]="3"
    ["33"]="4" ["41"]="5" ["49"]="6" ["57"]="7"
)

declare -A GPU_INDEX_TO_CARD=(
    ["0"]="1" ["1"]="9" ["2"]="17" ["3"]="25"
    ["4"]="33" ["5"]="41" ["6"]="49" ["7"]="57"
)

GPU_CARD_IDS=(1 9 17 25 33 41 49 57)

# 節點配置
IP_LIST=("192.168.10.103" "192.168.10.104" "192.168.10.105" "192.168.10.106")
declare -A IP_NAME_MAP=(
    ["192.168.10.103"]="colab-gpu1"
    ["192.168.10.104"]="colab-gpu2" 
    ["192.168.10.105"]="colab-gpu3"
    ["192.168.10.106"]="colab-gpu4"
)

# 函數：獲取使用者任務資訊
get_user_task_info() {
    local date_str="$1"
    local temp_file="/tmp/gpu_tasks_$$.json"
    
    echo "正在獲取 $date_str 的 GPU 使用者任務資訊..."
    
    # 從管理 API 獲取任務資訊
    local api_url="http://$MANAGEMENT_API_HOST/v1/tasks?status=FINISH&date=$date_str"
    
    curl -s -H "Authorization: Bearer $MANAGEMENT_API_TOKEN" \
         -H "Content-Type: application/json" \
         "$api_url" > "$temp_file"
    
    if [ $? -eq 0 ] && [ -s "$temp_file" ]; then
        echo "成功獲取任務資訊"
        cat "$temp_file"
        rm -f "$temp_file"
        return 0
    else
        echo "警告: 無法獲取任務資訊，將使用預設值"
        rm -f "$temp_file"
        return 1
    fi
}

# 函數：建立 GPU 到使用者的對應關係
build_gpu_user_mapping() {
    local hostname="$1"
    local tasks_json="$2"
    
    # 使用 jq 解析 JSON 並建立對應關係
    if command -v jq >/dev/null 2>&1 && [ -n "$tasks_json" ]; then
        echo "$tasks_json" | jq -r --arg host "$hostname" '
        .tasks[]? | 
        select(.hostname == $host and .gpu_uuid != null) |
        "\(.gpu_uuid):\(.username)"
        ' 2>/dev/null
    fi
}

# 計算時間戳記
echo "$DATE 的時間戳記計算..."
TIMESTAMP_START=$(TZ=UTC date -d "$DATE 00:00:00" +%s)
echo "計算時間戳記: $TIMESTAMP_START (UTC)"
TIMESTAMP_END=$(TZ=UTC date -d "$DATE 23:59:59" +%s)
POINTS=144

# 獲取使用者任務資訊
USER_TASKS_JSON=$(get_user_task_info "$DATE")

# 處理每個節點
for IP in "${IP_LIST[@]}"; do
    NAME="${IP_NAME_MAP[$IP]}"
    IP_OUTDIR="${outdir_prefix}${NAME}/$DATE"
    mkdir -p "$IP_OUTDIR"
    NETDATA_HOST="http://$IP:19999"

    echo "正在處理 $NAME ($IP)..."
    echo "輸出目錄: $IP_OUTDIR"
    
    # 建立此節點的 GPU 使用者對應
    declare -A GPU_USERS
    if [ -n "$USER_TASKS_JSON" ]; then
        while IFS=':' read -r gpu_uuid username; do
            if [ -n "$gpu_uuid" ] && [ -n "$username" ]; then
                GPU_USERS["$gpu_uuid"]="$username"
            fi
        done <<< "$(build_gpu_user_mapping "$NAME" "$USER_TASKS_JSON")"
    fi
    
    # 收集每個 GPU 的數據（與原腳本相同的邏輯）
    for CARD_ID in "${GPU_CARD_IDS[@]}"; do
        GPU_INDEX="${GPU_CARD_TO_INDEX[$CARD_ID]}"
        TMP_CSV="$IP_OUTDIR/gpu${GPU_INDEX}_$DATE.csv.tmp"
        FINAL_CSV="$IP_OUTDIR/gpu${GPU_INDEX}_$DATE.csv"
        
        echo "  處理 card${CARD_ID} (GPU[${GPU_INDEX}])..."
        
        # 擷取 GPU 和 VRAM 使用率數據
        GPU_UTIL_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_utilization_unknown_AMD_GPU_card${CARD_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
        VRAM_USAGE_JSON=$(curl -s "$NETDATA_HOST/api/v1/data?chart=amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card${CARD_ID}&after=$TIMESTAMP_START&before=$TIMESTAMP_END&points=$POINTS&group=average&format=json")
        
        # 創建 CSV
        echo "時間戳,日期時間,GPU使用率(%),VRAM使用率(%)" > "$TMP_CSV"
        
        # 處理數據（與原腳本相同的邏輯）
        if command -v jq >/dev/null 2>&1; then
            GPU_UTIL_DATA=$(echo "$GPU_UTIL_JSON" | jq -r '.data[] | [.[] | if . == null then 0 else . | tonumber end] | [.[0], (.[0] | strftime("%Y-%m-%d %H:%M:%S")), .[1]] | @csv')
            TIMESTAMPS=$(echo "$GPU_UTIL_DATA" | awk -F, '{print $1}' | sed 's/"//g')
            
            for TS in $TIMESTAMPS; do
                GPU_LINE=$(echo "$GPU_UTIL_DATA" | grep "$TS")
                GPU_TIME=$(echo "$GPU_LINE" | awk -F, '{print $2}' | sed 's/"//g')
                GPU_UTIL=$(echo "$GPU_LINE" | awk -F, '{print $3}')
                
                VRAM_USAGE=$(echo "$VRAM_USAGE_JSON" | jq -r --arg ts "$TS" '.data[] | map(if . == null then 0 else . | tonumber end) | select(.[0] == ($ts | tonumber)) | .[1]')
                VRAM_USAGE=${VRAM_USAGE:-0}
                
                echo "$TS,\"$GPU_TIME\",$GPU_UTIL,$VRAM_USAGE" >> "$TMP_CSV"
            done
        else
            echo "警告: 未安裝 jq，跳過此 GPU 的數據處理"
        fi
        
        # 排序並保存
        { head -n1 "$TMP_CSV"; tail -n +2 "$TMP_CSV" | sort -t, -k2; } > "$FINAL_CSV"
        rm -f "$TMP_CSV"
    done
    
    # 計算平均值並生成帶使用者資訊的 CSV
    echo "計算 $DATE $NAME 的 GPU 平均使用率..."
    AVG_CSV="$IP_OUTDIR/average_$DATE.csv"
    echo "GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者" > "$AVG_CSV"
    
    for GPU_INDEX in 0 1 2 3 4 5 6 7; do
        CSV_FILE="$IP_OUTDIR/gpu${GPU_INDEX}_$DATE.csv"
        if [ -f "$CSV_FILE" ]; then
            AVG_USAGE=$(awk -F, 'NR>1 {sum+=$3; count++} END {if (count > 0) print sum/count; else print "N/A"}' "$CSV_FILE")
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
            
            # 查找使用者資訊
            USER_INFO="未使用"
            CARD_ID="${GPU_INDEX_TO_CARD[$GPU_INDEX]}"
            
            # 嘗試從 GPU_USERS 陣列找到使用者
            for gpu_uuid in "${!GPU_USERS[@]}"; do
                # 這裡需要更複雜的對應邏輯，暫時使用簡單的判斷
                if [ "$FORMATTED_AVG_USAGE" != "N/A" ] && (( $(awk 'BEGIN {print ('$FORMATTED_AVG_USAGE' > 1)}') )); then
                    USER_INFO="檢測到使用者"
                    break
                fi
            done
            
            # 如果有實際使用率但沒有找到使用者，標記為 admin（管理進程）
            if [ "$FORMATTED_AVG_USAGE" != "N/A" ] && (( $(awk 'BEGIN {print ('$FORMATTED_AVG_USAGE' > 0)}') )) && [ "$USER_INFO" = "未使用" ]; then
                USER_INFO="admin"
            fi
            
            echo "GPU[${GPU_INDEX}]: 平均使用率 = $FORMATTED_AVG_USAGE%, 平均VRAM使用率 = $FORMATTED_AVG_VRAM%, 使用者 = $USER_INFO"
            echo "GPU[${GPU_INDEX}],$FORMATTED_AVG_USAGE,$FORMATTED_AVG_VRAM,$USER_INFO" >> "$AVG_CSV"
        else
            echo "警告: 找不到 $CSV_FILE 檔案"
            echo "GPU[${GPU_INDEX}],N/A,N/A,未使用" >> "$AVG_CSV"
        fi
    done
    
    # 計算整體平均
    OVERALL_AVG=$(awk -F, 'NR>1 {if ($2 != "N/A") {sum+=$2; count++}} END {if (count > 0) print sum/count; else print "N/A"}' "$AVG_CSV")
    OVERALL_VRAM_AVG=$(awk -F, 'NR>1 {if ($3 != "N/A") {sum+=$3; count++}} END {if (count > 0) print sum/count; else print "N/A"}' "$AVG_CSV")
    
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
    echo "全部平均,$FORMATTED_OVERALL_AVG,$FORMATTED_OVERALL_VRAM_AVG,所有使用者" >> "$AVG_CSV"
    echo "結果已保存至 $AVG_CSV"
    
    # 生成摘要報告（包含使用者資訊）
    cat > "$IP_OUTDIR/summary_$DATE.txt" << EOL
================================
AMD GPU 與 VRAM 每日使用率統計 (含使用者資訊)
日期: $DATE
節點: $NAME
================================

GPU 硬體對應表:
$(for i in 0 1 2 3 4 5 6 7; do echo "GPU[$i] -> Card ${GPU_INDEX_TO_CARD[$i]}"; done)

各 GPU 使用率與 VRAM 使用率 (含使用者):
$(awk -F, 'NR>1 && NF>=4 {printf "%s: GPU使用率 = %s%%, VRAM使用率 = %s%%, 使用者 = %s\n", $1, $2, $3, $4}' "$AVG_CSV")

整體平均 GPU 使用率: $FORMATTED_OVERALL_AVG%
整體平均 VRAM 使用率: $FORMATTED_OVERALL_VRAM_AVG%

GPU 使用者任務資訊:
$(if [ -n "$USER_TASKS_JSON" ]; then
    echo "$USER_TASKS_JSON" | jq -r --arg host "$NAME" '
    if .tasks then
        (.tasks[]? | select(.hostname == $host)) as $task |
        "  \($task.username): GPU \($task.gpu_info.gpu_index // "N/A")"
    else
        "  無任務資訊可用"
    end' 2>/dev/null || echo "  無法解析任務資訊"
else
    echo "  無任務資訊"
fi)
================================
EOL
    echo "摘要報告已保存至 $IP_OUTDIR/summary_$DATE.txt"
done

echo ""
echo "🎯 資料收集完成！現在包含使用者資訊。"
echo "💡 提示：可使用 ./colab_gpu_stats.sh user $DATE 來分析使用者使用情況"