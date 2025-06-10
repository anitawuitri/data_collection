#!/bin/bash

# GPU 使用率趨勢視覺化執行腳本
# 此腳本提供簡易的命令列介面來生成 GPU 使用率趨勢圖

set -e

# 設定腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VISUALIZATION_DIR="$SCRIPT_DIR/visualization"
DATA_DIR="$SCRIPT_DIR/data"
PLOTS_DIR="$SCRIPT_DIR/plots"

# 顏色輸出函數
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

echo "=== AMD GPU 使用率視覺化工具 ==="
echo ""

# 檢查 Python 環境
check_requirements() {
    print_info "檢查 Python 環境和依賴套件..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 python3，請安裝 Python 3"
        exit 1
    fi
    
    # 檢查必要的 Python 套件
    python3 -c "import pandas, matplotlib, numpy, seaborn" 2>/dev/null || {
        print_warning "缺少必要的 Python 套件，正在安裝..."
        pip3 install -r "$SCRIPT_DIR/requirements.txt" || {
            print_error "安裝 Python 套件失敗"
            print_info "請手動執行: pip3 install pandas matplotlib numpy seaborn"
            exit 1
        }
    }
    
    print_success "Python 環境檢查完成"
}

# 檢查數據目錄
check_data() {
    print_info "檢查數據目錄..."
    
    if [ ! -d "$DATA_DIR" ]; then
        print_error "未找到數據目錄: $DATA_DIR"
        exit 1
    fi
    
    # 檢查是否有任何數據檔案
    found_data=false
    for node in colab-gpu1 colab-gpu2 colab-gpu3 colab-gpu4; do
        if [ -d "$DATA_DIR/$node" ]; then
            found_data=true
            break
        fi
    done
    
    if [ "$found_data" = false ]; then
        print_error "未找到任何 GPU 數據檔案"
        print_info "請確保 $DATA_DIR 目錄包含正確的數據結構"
        exit 1
    fi
    
    print_success "數據目錄檢查完成"
}

# 顯示使用說明
show_usage() {
    echo "GPU 使用率與 VRAM 視覺化工具"
    echo "================================"
    echo ""
    echo "使用方法:"
    echo "  $0 [選項] [參數]"
    echo ""
    echo "選項:"
    echo "  quick [開始日期] [結束日期]     - 快速生成所有常用圖表"
    echo "  nodes [開始日期] [結束日期]     - 生成節點對比趨勢圖"
    echo "  node [節點名稱] [開始日期] [結束日期] - 生成單一節點所有 GPU 趨勢圖"
    echo "  gpu [GPU_ID] [開始日期] [結束日期]   - 生成特定 GPU 跨節點對比圖"
    echo "  heatmap [開始日期] [結束日期]   - 生成熱力圖"
    echo "  timeline [節點] [GPU_ID] [日期] - 生成詳細時間序列圖"
    echo ""
    echo "  🔥 VRAM 監控功能:"
    echo "  vram-nodes [開始日期] [結束日期] [GPU_ID] - 生成各節點 VRAM 對比圖"
    echo "  vram-heatmap [開始日期] [結束日期]       - 生成 VRAM 使用率熱力圖"
    echo "  vram-timeline [節點] [GPU_ID] [日期]     - 生成 VRAM 時間序列圖"
    echo "  vram-all [開始日期] [結束日期]           - 生成所有 VRAM 圖表"
    echo ""
    echo "  examples                        - 執行所有範例"
    echo "  auto                            - 自動偵測日期範圍並生成所有圖表"
    echo ""
    echo "日期格式: YYYY-MM-DD (例如: 2025-05-23)"
    echo "節點名稱: colab-gpu1, colab-gpu2, colab-gpu3, colab-gpu4"
    echo "GPU ID: 1, 9, 17, 25, 33, 41, 49, 57"
    echo ""
    echo "範例:"
    echo "  $0 quick 2025-05-23 2025-05-26"
    echo "  $0 nodes 2025-05-23 2025-05-26"
    echo "  $0 node colab-gpu1 2025-05-23 2025-05-26"
    echo "  $0 gpu 1 2025-05-23 2025-05-26"
    echo "  $0 vram-nodes 2025-05-23 2025-05-26 1"
    echo "  $0 vram-heatmap 2025-05-23 2025-05-26"
    echo "  $0 vram-all 2025-05-23 2025-05-26"
    echo "  $0 auto"
    echo ""
}

# 快速生成所有圖表
run_quick() {
    local start_date=$1
    local end_date=$2
    
    print_info "快速生成所有常用 GPU 趨勢圖..."
    
    if [ -z "$start_date" ] || [ -z "$end_date" ]; then
        python3 "$VISUALIZATION_DIR/quick_gpu_trend_plots.py"
    else
        python3 "$VISUALIZATION_DIR/quick_gpu_trend_plots.py" "$start_date" "$end_date"
    fi
    
    print_success "快速圖表生成完成"
}

# 生成節點對比圖
run_nodes() {
    local start_date=$1
    local end_date=$2
    
    if [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少日期參數"
        show_usage
        exit 1
    fi
    
    print_info "生成節點對比趨勢圖..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_nodes_trend
quick_nodes_trend('$start_date', '$end_date')
"
    
    print_success "節點對比圖生成完成"
}

# 生成單一節點所有 GPU 圖
run_node() {
    local node=$1
    local start_date=$2
    local end_date=$3
    
    if [ -z "$node" ] || [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少參數"
        show_usage
        exit 1
    fi
    
    print_info "生成 $node 所有 GPU 趨勢圖..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_single_node_gpus
quick_single_node_gpus('$node', '$start_date', '$end_date')
"
    
    print_success "$node 所有 GPU 趨勢圖生成完成"
}

# 生成特定 GPU 跨節點圖
run_gpu() {
    local gpu_id=$1
    local start_date=$2
    local end_date=$3
    
    if [ -z "$gpu_id" ] || [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少參數"
        show_usage
        exit 1
    fi
    
    print_info "生成 GPU $gpu_id 跨節點對比圖..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_gpu_across_nodes
quick_gpu_across_nodes($gpu_id, '$start_date', '$end_date')
"
    
    print_success "GPU $gpu_id 跨節點對比圖生成完成"
}

# 生成進階分析圖表
run_advanced() {
    local start_date=$1
    local end_date=$2
    local mode=$3
    
    if [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少日期參數"
        show_usage
        exit 1
    fi
    
    print_info "生成進階分析圖表..."
    
    python3 "$VISUALIZATION_DIR/advanced_gpu_trend_analyzer.py" \
        --start-date "$start_date" \
        --end-date "$end_date" \
        --mode "${mode:-all}"
    
    print_success "進階分析圖表生成完成"
}

# 執行範例
run_examples() {
    print_info "執行 GPU 趨勢分析範例..."
    
    cd "$SCRIPT_DIR"
    python3 "visualization/gpu_trend_examples.py"
    
    print_success "範例執行完成"
}

# 自動模式
run_auto() {
    print_info "自動模式：偵測可用數據並生成所有圖表..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import generate_all_quick_plots
generate_all_quick_plots()
"
    
    print_success "自動模式完成"
}

# VRAM 各節點對比
run_vram_nodes() {
    local start_date=$1
    local end_date=$2
    local gpu_id=$3
    
    if [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少日期參數"
        show_usage
        exit 1
    fi
    
    print_info "生成各節點 VRAM 使用量對比圖..."
    
    if [ -n "$gpu_id" ]; then
        python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_vram_nodes_comparison
quick_vram_nodes_comparison('$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR', gpu_id=$gpu_id)
"
    else
        python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_vram_nodes_comparison
quick_vram_nodes_comparison('$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
"
    fi
    
    print_success "VRAM 節點對比圖生成完成"
}

# VRAM 熱力圖
run_vram_heatmap() {
    local start_date=$1
    local end_date=$2
    
    if [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少日期參數"
        show_usage
        exit 1
    fi
    
    print_info "生成 VRAM 使用率熱力圖..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_vram_heatmap
quick_vram_heatmap('$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
"
    
    print_success "VRAM 熱力圖生成完成"
}

# VRAM 時間序列
run_vram_timeline() {
    local node=$1
    local gpu_id=$2
    local date=$3
    
    if [ -z "$node" ] || [ -z "$gpu_id" ] || [ -z "$date" ]; then
        print_error "vram-timeline 模式需要 [節點] [GPU_ID] [日期] 參數"
        show_usage
        exit 1
    fi
    
    print_info "生成 $node GPU $gpu_id 的 VRAM 時間序列圖..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_vram_timeline
quick_vram_timeline('$node', $gpu_id, '$date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
"
    
    print_success "VRAM 時間序列圖生成完成"
}

# 生成所有 VRAM 圖表
run_vram_all() {
    local start_date=$1
    local end_date=$2
    
    if [ -z "$start_date" ] || [ -z "$end_date" ]; then
        print_error "缺少日期參數"
        show_usage
        exit 1
    fi
    
    print_info "生成所有 VRAM 監控圖表..."
    
    python3 -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import generate_all_vram_plots
generate_all_vram_plots('$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
"
    
    print_success "所有 VRAM 圖表生成完成"
}

# 主程式
main() {
    local command=$1
    
    # 檢查環境
    check_requirements
    check_data
    
    # 確保輸出目錄存在
    mkdir -p "$PLOTS_DIR"
    
    case "$command" in
        "quick")
            run_quick "$2" "$3"
            ;;
        "nodes")
            run_nodes "$2" "$3"
            ;;
        "node")
            run_node "$2" "$3" "$4"
            ;;
        "gpu")
            run_gpu "$2" "$3" "$4"
            ;;
        "heatmap")
            run_advanced "$2" "$3" "heatmap"
            ;;
        "timeline")
            if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
                print_error "timeline 模式需要 [節點] [GPU_ID] [日期] 參數"
                show_usage
                exit 1
            fi
            python3 "$VISUALIZATION_DIR/advanced_gpu_trend_analyzer.py" \
                --mode timeline \
                --node "$2" \
                --gpu-id "$3" \
                --date "$4" \
                --start-date "$4" \
                --end-date "$4"
            ;;
        "vram-nodes")
            run_vram_nodes "$2" "$3" "$4"
            ;;
        "vram-heatmap")
            run_vram_heatmap "$2" "$3"
            ;;
        "vram-timeline")
            run_vram_timeline "$2" "$3" "$4"
            ;;
        "vram-all")
            run_vram_all "$2" "$3"
            ;;
        "examples")
            run_examples
            ;;
        "auto")
            run_auto
            ;;
        "help"|"-h"|"--help"|"")
            show_usage
            ;;
        *)
            print_error "未知的命令: $command"
            show_usage
            exit 1
            ;;
    esac
}

# 執行主程式
main "$@"
