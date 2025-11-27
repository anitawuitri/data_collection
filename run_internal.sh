#!/bin/bash
# GPU Monitor System - User Info Version v2.0
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Fix matplotlib permission issue
export MPLCONFIGDIR="/tmp/matplotlib_cache_$USER"
mkdir -p "$MPLCONFIGDIR"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_env() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found."
        exit 1
    fi
    python3 -c "import pandas, matplotlib, seaborn, requests" 2>/dev/null || {
        log_error "Missing required Python packages (pandas, matplotlib, seaborn, requests)."
        exit 1
    }
}

validate_date() {
    if [[ ! $1 =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        log_error "Invalid date format. Use YYYY-MM-DD."
        exit 1
    fi
}

usage() {
    echo "Usage: $0 <command> [args...]"
    echo "Commands:"
    echo "  collect [date]                  Collect GPU data (default: today)"
    echo "  quick <start> <end>             Generate quick plots"
    echo "  plots <start> <end>             Generate all plots"
    echo "  heatmap <start> <end>           Generate heatmap"
    echo "  vram-users <start> <end>        Generate VRAM user summary"
    echo "  vram-compare <start> <end>      Generate VRAM node comparison"
    echo "  vram-heatmap <start> <end>      Generate VRAM heatmap"
    echo "  users <start> <end>             Generate user activity summary"
    echo "  query-user <user> <date|range>  Query user GPU usage"
    echo "  list-users <date>               List all GPU users"
    echo "  archive [month]                 Archive data (default: previous month)"
    echo "  weekly-plot                     Generate plots for the last 7 days"
}

if [ $# -eq 0 ]; then usage; exit 1; fi
CMD=$1; shift
check_env

case $CMD in
    collect)
        DATE=${1:-$(date +%Y-%m-%d)}
        validate_date "$DATE"
        cd python && python3 daily_gpu_log.py "$DATE"
        ;;
    quick)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 quick_gpu_trend_plots.py "$1" "$2"
        ;;
    plots)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 -c "
from quick_gpu_trend_plots import *
quick_nodes_trend('$1', '$2', show_users=True)
for node in ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']:
    quick_single_node_gpus(node, '$1', '$2', show_users=True)
for i in range(8):
    quick_gpu_across_nodes(i, '$1', '$2', show_users=True)
quick_user_activity_summary('$1', '$2')
"
        ;;
    heatmap)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 -c "from quick_gpu_trend_plots import quick_gpu_heatmap; quick_gpu_heatmap('$1', '$2', show_users=True)"
        ;;
    vram-users)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 -c "from quick_gpu_trend_plots import quick_vram_user_activity_summary; quick_vram_user_activity_summary('$1', '$2')"
        ;;
    vram-compare)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 -c "from quick_gpu_trend_plots import quick_vram_nodes_comparison_with_users; quick_vram_nodes_comparison_with_users('$1', '$2', show_users=True)"
        ;;
    vram-heatmap)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 -c "from quick_gpu_trend_plots import quick_vram_heatmap; quick_vram_heatmap('$1', '$2', show_users=True)"
        ;;
    users)
        validate_date "$1"; validate_date "$2"
        cd visualization && python3 -c "from quick_gpu_trend_plots import quick_user_activity_summary; quick_user_activity_summary('$1', '$2')"
        ;;
    query-user)
        if [ $# -lt 2 ]; then log_error "Usage: query-user <user> <date> [end_date]"; exit 1; fi
        validate_date "$2"
        [ -n "$3" ] && validate_date "$3"
        python3 get_user_gpu_usage.py "$1" "$2" "$3"
        ;;
    list-users)
        validate_date "$1"
        python3 get_user_gpu_usage.py --list-users "$1"
        ;;

    archive)
        python3 scripts/archive_data.py "${@:2}"
        ;;
    weekly-plot)
        END_DATE=$(date +%Y-%m-%d)
        START_DATE=$(date -d "$END_DATE - 7 days" +%Y-%m-%d)
        log_info "Generating weekly plots from $START_DATE to $END_DATE"
        cd visualization && python3 quick_gpu_trend_plots.py "$START_DATE" "$END_DATE"
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        log_error "Unknown command: $CMD"
        usage; exit 1
        ;;
esac

log_success "Command '$CMD' completed successfully."

