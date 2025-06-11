#!/bin/bash

# GPU 使用率趨勢視覺化執行腳本
# 此腳本提供簡易的命令列介面來生成 GPU 使用率趨勢圖

set -e

# 設定腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VISUALIZATION_DIR="$SCRIPT_DIR/visualization"
DATA_DIR="$SCRIPT_DIR/data"
PLOTS_DIR="$SCRIPT_DIR/plots"
VENV_DIR="$SCRIPT_DIR/.venv"

# 檢查並激活虛擬環境
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

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
    
    if ! command -v $PYTHON_CMD &> /dev/null; then
        print_error "未找到 $PYTHON_CMD，請安裝 Python 3"
        exit 1
    fi
    
    # 檢查必要的 Python 套件
    $PYTHON_CMD -c "import pandas, matplotlib, numpy, seaborn" 2>/dev/null || {
        print_warning "缺少必要的 Python 套件，正在安裝..."
        
        # 如果使用虛擬環境，直接安裝；否則提示用戶
        if [ -d "$VENV_DIR" ] && [ -n "$VIRTUAL_ENV" ]; then
            $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt" || {
                print_error "安裝 Python 套件失敗"
                exit 1
            }
        else
            print_error "需要安裝 Python 套件，請執行以下命令之一："
            print_info "1. 使用虛擬環境: source .venv/bin/activate && pip3 install -r requirements.txt"
            print_info "2. 系統安裝: pip3 install --user pandas matplotlib numpy seaborn"
            print_info "3. 如果需要系統級安裝: pip3 install --break-system-packages pandas matplotlib numpy seaborn"
            exit 1
        fi
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
    echo "  setup                           - 創建 Python 虛擬環境並安裝依賴套件"
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
    echo "  $0 setup                         - 初始化 Python 虛擬環境"
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
        $PYTHON_CMD -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import generate_all_quick_plots
generate_all_quick_plots(data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
"
    else
        $PYTHON_CMD -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import generate_all_quick_plots
generate_all_quick_plots('$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
"
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
    
    $PYTHON_CMD -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_nodes_trend
quick_nodes_trend('$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
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
    
    $PYTHON_CMD -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_single_node_gpus
quick_single_node_gpus('$node', '$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
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
    
    $PYTHON_CMD -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import quick_gpu_across_nodes
quick_gpu_across_nodes($gpu_id, '$start_date', '$end_date', data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
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
    
    $PYTHON_CMD -c "
import sys
sys.path.append('$VISUALIZATION_DIR')
from quick_gpu_trend_plots import generate_all_quick_plots
generate_all_quick_plots(data_dir='$DATA_DIR', plots_dir='$PLOTS_DIR')
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

# 創建虛擬環境函數
create_venv() {
    print_info "正在創建 Python 虛擬環境..."
    
    # 檢查是否已存在虛擬環境
    if [ -d "$VENV_DIR" ]; then
        print_warning "虛擬環境已存在於: $VENV_DIR"
        return 0
    fi
    
    # 檢查 Python 版本
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 python3，請先安裝 Python 3.7+"
        exit 1
    fi
    
    # 檢查 Python 版本是否符合要求 (3.7+)
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    version_check=$(python3 -c "import sys; print(1 if sys.version_info >= (3, 7) else 0)")
    if [ "$version_check" = "0" ]; then
        print_error "Python 版本過舊 ($python_version)，需要 Python 3.7 或更新版本"
        exit 1
    fi
    
    print_info "使用 Python 版本: $python_version"
    
    # 創建虛擬環境
    print_info "創建虛擬環境到: $VENV_DIR"
    python3 -m venv "$VENV_DIR" || {
        print_error "創建虛擬環境失敗"
        print_info "請確保已安裝 python3-venv 套件:"
        print_info "Ubuntu/Debian: sudo apt install python3-venv"
        print_info "CentOS/RHEL: sudo yum install python3-venv"
        exit 1
    }
    
    # 激活虛擬環境
    source "$VENV_DIR/bin/activate"
    
    # 升級 pip
    print_info "升級 pip..."
    pip install --upgrade pip
    
    # 安裝依賴套件
    print_info "安裝 Python 依賴套件..."
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip install -r "$SCRIPT_DIR/requirements.txt" || {
            print_error "安裝依賴套件失敗"
            exit 1
        }
    else
        print_warning "未找到 requirements.txt，安裝基本套件..."
        pip install pandas matplotlib numpy seaborn || {
            print_error "安裝基本套件失敗"
            exit 1
        }
    fi
    
    # 如果有 visualization/requirements.txt，也安裝它
    if [ -f "$VISUALIZATION_DIR/requirements.txt" ]; then
        print_info "安裝視覺化模組的依賴套件..."
        pip install -r "$VISUALIZATION_DIR/requirements.txt" || {
            print_warning "安裝視覺化模組依賴套件失敗，但繼續執行..."
        }
    fi
    
    print_success "虛擬環境創建完成!"
    print_info "虛擬環境位置: $VENV_DIR"
    print_info "若要手動激活虛擬環境，請執行: source $VENV_DIR/bin/activate"
}

# 主程式
main() {
    local command=$1
    
    # 如果是 setup 命令，直接執行而不檢查依賴
    if [ "$command" = "setup" ]; then
        create_venv
        print_success "虛擬環境設置完成！現在可以使用其他選項來生成圖表。"
        exit 0
    fi
    
    # 如果不是 setup 命令，檢查是否建議建立虛擬環境
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "未找到虛擬環境，建議先執行 setup 來創建虛擬環境："
        print_info "$0 setup"
        echo ""
    fi
    
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
