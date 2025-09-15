#!/bin/bash
# AMD GPU 監控系統 - 重構版本快速啟動腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輔助函數
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查 Python 版本
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 Python 3，請先安裝 Python 3.9 或更高版本"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    required_version="3.9"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
        print_error "Python 版本過低，需要 Python $required_version 或更高版本，目前版本: $python_version"
        exit 1
    fi
    
    print_success "Python 版本檢查通過: $python_version"
}

# 檢查並安裝 Poetry
check_poetry() {
    if ! command -v poetry &> /dev/null; then
        print_info "未找到 Poetry，正在安裝..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
        
        if ! command -v poetry &> /dev/null; then
            print_error "Poetry 安裝失敗"
            exit 1
        fi
    fi
    
    print_success "Poetry 已安裝"
}

# 安裝依賴
install_dependencies() {
    print_info "安裝專案依賴..."
    
    # 配置 Poetry
    poetry config virtualenvs.in-project true
    
    # 安裝依賴
    if [ "$1" == "dev" ]; then
        poetry install --extras "full"
        print_success "開發依賴安裝完成"
    else
        poetry install --no-dev --extras "full"
        print_success "生產依賴安裝完成"
    fi
}

# 建立資料目錄
setup_directories() {
    print_info "建立必要目錄..."
    
    mkdir -p data plots logs
    
    # 建立節點子目錄
    for node in colab-gpu1 colab-gpu2 colab-gpu3 colab-gpu4; do
        mkdir -p "data/$node"
    done
    
    print_success "目錄結構建立完成"
}

# 設定環境變數
setup_environment() {
    if [ ! -f .env ]; then
        print_info "設定環境變數..."
        cp .env.example .env
        print_warning "請編輯 .env 文件並填入實際的 API Token"
    fi
}

# 執行測試
run_tests() {
    print_info "執行測試套件..."
    poetry run pytest -v
    print_success "測試執行完成"
}

# 初始化 Git hooks
setup_git_hooks() {
    if [ -d .git ]; then
        print_info "設定 Git hooks..."
        poetry run pre-commit install
        print_success "Git hooks 設定完成"
    fi
}

# 顯示使用說明
show_usage() {
    echo "🔥 AMD GPU 監控系統 - 重構版本"
    echo ""
    echo "用法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  install     安裝依賴和設定環境"
    echo "  install-dev 安裝開發依賴"
    echo "  test        執行測試套件"
    echo "  clean       清理建置文件"
    echo "  docker      使用 Docker 啟動"
    echo "  status      檢查系統狀態"
    echo "  demo        執行示範收集"
    echo "  help        顯示此說明"
    echo ""
    echo "範例:"
    echo "  $0 install      # 安裝生產依賴"
    echo "  $0 install-dev  # 安裝開發依賴"
    echo "  $0 test         # 執行測試"
    echo "  $0 docker       # Docker 啟動"
}

# 清理建置文件
clean() {
    print_info "清理建置文件..."
    
    rm -rf build/
    rm -rf dist/
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "清理完成"
}

# Docker 啟動
start_docker() {
    print_info "使用 Docker 啟動 AMD GPU 監控系統..."
    
    if ! command -v docker &> /dev/null; then
        print_error "未找到 Docker，請先安裝 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "未找到 docker-compose，請先安裝 docker-compose"
        exit 1
    fi
    
    # 建立 .env 文件
    setup_environment
    
    # 啟動服務
    docker-compose up --build -d
    
    print_success "Docker 服務已啟動"
    print_info "使用 'docker-compose logs -f' 查看日誌"
}

# 檢查系統狀態
check_status() {
    print_info "檢查系統狀態..."
    
    if [ -f .venv/bin/activate ]; then
        poetry run python -m src.cli.main status
    else
        print_warning "虛擬環境未建立，請先執行 '$0 install'"
    fi
}

# 執行示範收集
run_demo() {
    print_info "執行示範數據收集..."
    
    if [ -f .venv/bin/activate ]; then
        poetry run python -m src.cli.main collect test
        poetry run python -m src.cli.main query users $(date +%Y-%m-%d)
    else
        print_warning "虛擬環境未建立，請先執行 '$0 install'"
    fi
}

# 主函數
main() {
    case "${1:-help}" in
        install)
            check_python
            check_poetry
            setup_directories
            setup_environment
            install_dependencies
            setup_git_hooks
            print_success "🎉 安裝完成！"
            print_info "現在可以執行: poetry run gpu-monitor --help"
            ;;
        install-dev)
            check_python
            check_poetry
            setup_directories
            setup_environment
            install_dependencies dev
            setup_git_hooks
            print_success "🎉 開發環境安裝完成！"
            ;;
        test)
            run_tests
            ;;
        clean)
            clean
            ;;
        docker)
            start_docker
            ;;
        status)
            check_status
            ;;
        demo)
            run_demo
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "未知選項: $1"
            show_usage
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@"