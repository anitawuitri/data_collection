#!/bin/bash

# GPU 視覺化工具快速執行腳本
# 在 visualization 資料夾內執行

echo "=== GPU 使用率視覺化工具 ==="
echo ""

# 檢查 Python 套件
echo "檢查 Python 套件..."
python3 -c "import pandas, matplotlib, numpy, seaborn" 2>/dev/null || {
    echo "安裝必要的 Python 套件..."
    pip3 install -r requirements.txt
}

# 檢查數據目錄
if [ ! -d "../data" ]; then
    echo "錯誤: 未找到數據目錄 ../data"
    echo "請確保在 visualization 目錄下執行此腳本"
    exit 1
fi

# 創建輸出目錄
mkdir -p ../plots

case "${1:-auto}" in
    "auto")
        echo "自動模式：生成所有常用圖表..."
        python3 quick_gpu_trend_plots.py
        ;;
    "quick")
        echo "快速模式：生成指定日期範圍的圖表..."
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "使用方式: $0 quick [開始日期] [結束日期]"
            echo "範例: $0 quick 2025-05-23 2025-05-26"
            exit 1
        fi
        python3 quick_gpu_trend_plots.py "$2" "$3"
        ;;
    "examples")
        echo "執行範例..."
        python3 gpu_trend_examples.py
        ;;
    "advanced")
        echo "進階分析模式..."
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "使用方式: $0 advanced [開始日期] [結束日期]"
            echo "範例: $0 advanced 2025-05-23 2025-05-26"
            exit 1
        fi
        python3 advanced_gpu_trend_analyzer.py --start-date "$2" --end-date "$3" --mode all
        ;;
    "help"|"-h"|"--help")
        echo "使用方式:"
        echo "  $0 [模式] [參數]"
        echo ""
        echo "模式:"
        echo "  auto            - 自動偵測數據並生成所有圖表（預設）"
        echo "  quick [開始] [結束] - 快速生成指定日期範圍的圖表"
        echo "  examples        - 執行所有範例"
        echo "  advanced [開始] [結束] - 進階分析（所有圖表類型）"
        echo "  help            - 顯示此說明"
        echo ""
        echo "範例:"
        echo "  $0                              # 自動模式"
        echo "  $0 quick 2025-05-23 2025-05-26 # 快速模式"
        echo "  $0 examples                     # 範例模式"
        echo "  $0 advanced 2025-05-23 2025-05-26 # 進階模式"
        ;;
    *)
        echo "未知的模式: $1"
        echo "執行 '$0 help' 查看使用說明"
        exit 1
        ;;
esac

echo ""
echo "完成！圖表已保存在 '../plots/' 目錄中"
