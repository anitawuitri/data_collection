#!/bin/bash

# 時間轉換工具腳本 - 支援時區轉換
# 使用方法:
# 1. 將日期時間轉換為時間戳記: ./time_convert.sh date2ts "2025-05-27 00:00:00" [時區]
# 2. 將時間戳記轉換為日期時間: ./time_convert.sh ts2date 1748217600 [時區]

# 如果未指定時區，預設使用系統時區

# 顯示使用說明
usage() {
    echo "使用方法:"
    echo "  日期轉時間戳記: $0 date2ts \"YYYY-MM-DD HH:MM:SS\" [時區]"
    echo "  時間戳記轉日期: $0 ts2date TIMESTAMP [時區]"
    echo ""
    echo "時區範例: UTC, Asia/Taipei, Asia/Tokyo, America/New_York"
    echo "時區列表: timedatectl list-timezones"
    echo ""
    echo "範例:"
    echo "  $0 date2ts \"2025-05-27 00:00:00\" Asia/Taipei"
    echo "  $0 ts2date 1748217600 UTC"
    exit 1
}

# 檢查參數
if [ "$#" -lt 2 ]; then
    usage
fi

ACTION=$1
shift

case "$ACTION" in
    date2ts)
        DATE_TIME=$1
        TIMEZONE=${2:-$(timedatectl show --property=Timezone --value)}
        
        if [ -z "$DATE_TIME" ]; then
            echo "錯誤: 請提供日期時間"
            usage
        fi
        
        echo "轉換日期時間 \"$DATE_TIME\" 至 Unix 時間戳記 (時區: $TIMEZONE)"
        TZ=$TIMEZONE date -d "$DATE_TIME" +%s
        ;;
        
    ts2date)
        TIMESTAMP=$1
        TIMEZONE=${2:-$(timedatectl show --property=Timezone --value)}
        
        if [ -z "$TIMESTAMP" ]; then
            echo "錯誤: 請提供時間戳記"
            usage
        fi
        
        echo "轉換 Unix 時間戳記 $TIMESTAMP 至日期時間 (時區: $TIMEZONE)"
        TZ=$TIMEZONE date -d @"$TIMESTAMP" "+%Y-%m-%d %H:%M:%S %Z"
        ;;
        
    *)
        echo "錯誤: 未知的操作 \"$ACTION\""
        usage
        ;;
esac
