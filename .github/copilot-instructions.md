# GitHub Copilot Instructions for AMD GPU Monitoring & Visualization Project

## Project Overview

This is a comprehensive **AMD GPU monitoring and visualization system** designed for multi-node environments. The project provides automated data collection, statistical analysis, and advanced visualization capabilities for GPU utilization and VRAM usage monitoring across multiple compute nodes.

### Core Functionality
- **Multi-node GPU monitoring** via Netdata API integration
- **Automated data collection** with cron job support  
- **Advanced visualization** with matplotlib, seaborn, and pandas
- **VRAM monitoring** for memory usage analysis
- **Chinese localization** with proper font support
- **Virtual environment automation** for dependency management

## Project Architecture

### Directory Structure
```
data_collection/
├── run_gpu_visualization.sh      # Main visualization script with virtual env support
├── requirements.txt              # Python dependencies
├── data/                         # GPU monitoring data (git ignored)
│   ├── colab-gpu1/              # Node-specific data directories
│   ├── colab-gpu2/              # Contains daily CSV files with timestamps
│   ├── colab-gpu3/              # GPU utilization + VRAM usage data
│   └── colab-gpu4/
├── plots/                       # Generated visualization outputs
├── scripts/                     # Data collection and analysis scripts
│   ├── daily_gpu_log.sh        # Main data collection from Netdata API
│   ├── calculate_gpu_range.sh  # Date range analysis
│   └── calculate_node_gpu_usage.sh # Node usage statistics
├── visualization/               # Python visualization toolkit
│   ├── quick_gpu_trend_plots.py    # Quick plotting functions
│   ├── advanced_gpu_trend_analyzer.py # Advanced analysis
│   ├── vram_monitor.py             # VRAM-specific monitoring
│   ├── font_config.py              # Chinese font configuration
│   └── gpu_trend_visualizer.py     # Core visualization engine
└── examples/                    # Usage examples and tutorials
```

### Technology Stack
- **Shell Scripting**: Bash for automation and data collection
- **Python 3.7+**: Data processing and visualization
- **Netdata API**: Real-time GPU metrics collection (port 19999)
- **Data Processing**: pandas, numpy for data manipulation
- **Visualization**: matplotlib, seaborn for charts and plots
- **Chinese Fonts**: Noto Sans CJK for proper Chinese character display

### Key Components

#### 1. Data Collection System (`scripts/`)
- **`daily_gpu_log.sh`**: Collects GPU utilization and VRAM usage from 4 nodes
- **Network endpoints**: 192.168.10.103-106 (colab-gpu1 to colab-gpu4)
- **Monitored GPUs**: IDs 1, 9, 17, 25, 33, 41, 49, 57 per node
- **Data format**: CSV with timestamps, GPU usage %, VRAM usage %
- **API endpoints**: 
  - `amdgpu.gpu_utilization_unknown_AMD_GPU_card{ID}`
  - `amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card{ID}`

#### 2. Visualization Engine (`visualization/`)
- **Quick plots**: Fast chart generation for common use cases
- **Advanced analysis**: Complex multi-dimensional analysis
- **VRAM monitoring**: Dedicated VRAM usage visualization
- **Heatmaps**: Usage distribution across nodes and time
- **Time series**: Detailed timeline analysis

#### 3. Main Automation Script (`run_gpu_visualization.sh`)
- **Virtual environment management**: Automatic creation and activation
- **Command-line interface**: Multiple modes (quick, nodes, gpu, vram-*)
- **Dependency checking**: Python environment validation
- **Error handling**: Comprehensive error messages and solutions

## Development Guidelines

### Code Style and Patterns

#### Shell Script Conventions
```bash
# Use consistent error handling
set -e

# Color-coded output functions
print_info() { echo -e "\033[1;34m[INFO]\033[0m $1"; }
print_success() { echo -e "\033[1;32m[SUCCESS]\033[0m $1"; }
print_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }

# Validate inputs
if [ -z "$required_param" ]; then
    print_error "Missing required parameter"
    exit 1
fi
```

#### Python Code Patterns
```python
# Always use Chinese font configuration
from font_config import setup_chinese_font
setup_chinese_font()

# Standard plotting setup
fig, ax = plt.subplots(figsize=(15, 8))
ax.set_ylim(0, 100)  # Always 0-100% for usage rates
ax.grid(True, alpha=0.3)

# Consistent data structure
df = pd.read_csv(csv_file)
# Expected columns: '時間戳', '日期時間', 'GPU使用率(%)', 'VRAM使用率(%)'
```

#### File Naming Conventions
- **Data files**: `gpu{ID}_{YYYY-MM-DD}.csv`
- **Plot outputs**: `{type}_{start_date}_to_{end_date}.png`
- **Node-specific**: `{node}_gpu{ID}_{date}.png`
- **VRAM files**: `vram_*` prefix for VRAM-specific outputs

### API Design Patterns

#### Quick Plot Functions
```python
def quick_{plot_type}(start_date, end_date, **kwargs):
    """
    Generate {plot_type} visualization
    
    Args:
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)
        data_dir (str): Data directory path
        plots_dir (str): Output directory path
    
    Returns:
        str: Path to generated plot file
    """
```

#### Class-based Analyzers
```python
class GPUAnalyzer:
    def __init__(self, data_dir=None, plots_dir=None):
        self.data_dir = data_dir or '../data'
        self.plots_dir = plots_dir or '../plots'
        self.nodes = ['colab-gpu1', 'colab-gpu2', 'colab-gpu3', 'colab-gpu4']
        self.gpu_ids = [1, 9, 17, 25, 33, 41, 49, 57]
```

### Data Processing Standards

#### CSV Data Structure
```csv
時間戳,日期時間,GPU使用率(%),VRAM使用率(%)
1716969600,"2025-05-28 00:00:00",1.23,45.67
```

#### Error Handling for Data
```python
try:
    df = pd.read_csv(csv_file)
    if df.empty or 'GPU使用率(%)' not in df.columns:
        print(f"Invalid data format in {csv_file}")
        return None
except Exception as e:
    print(f"Error reading {csv_file}: {e}")
    return None
```

#### Numeric Processing (Shell)
```bash
# Use awk instead of bc for scientific notation handling
average=$(awk "BEGIN {sum=0; count=0} 
    /^[0-9]/ {sum+=\$1; count++} 
    END {if(count>0) print sum/count; else print 0}" <<< "$values")
```

## Feature-Specific Instructions

### GPU Utilization Monitoring
- **Always use percentage scale (0-100%)** for GPU usage charts
- **Include all 8 GPU IDs** per node unless specifically filtered
- **Handle missing data gracefully** with zero values or interpolation
- **Use consistent color schemes** across related charts

### VRAM Monitoring
- **Dual metrics**: Both absolute usage (GB) and percentage (%)
- **Assume 80GB total** VRAM per MI250X GPU for calculations
- **Separate chart functions** with `vram_` prefix
- **Combined data collection** in same CSV files as GPU utilization

### Visualization Best Practices
- **Chinese font support**: Always call `setup_chinese_font()` at module start
- **Consistent styling**: Use seaborn style with custom colors
- **High DPI output**: Save plots with `dpi=300, bbox_inches='tight'`
- **Grid and legends**: Include alpha=0.3 grids and clear legends
- **Title formatting**: Use fontsize=16, fontweight='bold' for titles

### Virtual Environment Management
- **Automatic detection**: Check for `.venv` directory existence
- **Graceful fallback**: Support both venv and system Python
- **Dependency validation**: Verify required packages before execution
- **User guidance**: Provide clear instructions for setup issues

### Network and API Integration
- **Netdata endpoints**: Use port 19999 on each node
- **Timeout handling**: Include proper error handling for network requests
- **Data validation**: Check JSON response structure before processing
- **Retry logic**: Implement basic retry for failed API calls

## Common Use Cases and Examples

### Quick Start Commands
```bash
# Setup virtual environment (first time)
./run_gpu_visualization.sh setup

# Generate all common visualizations
./run_gpu_visualization.sh quick 2025-05-23 2025-05-26

# Node comparison charts
./run_gpu_visualization.sh nodes 2025-05-23 2025-05-26

# VRAM monitoring
./run_gpu_visualization.sh vram-all 2025-05-23 2025-05-26
```

### Python API Usage
```python
from quick_gpu_trend_plots import generate_all_quick_plots
from vram_monitor import VRAMMonitor

# Generate standard charts
generate_all_quick_plots('2025-05-23', '2025-05-26')

# VRAM specific analysis
monitor = VRAMMonitor()
monitor.plot_nodes_vram_comparison('2025-05-23', '2025-05-26')
```

### Data Collection
```bash
# Collect today's data
./scripts/daily_gpu_log.sh

# Collect specific date
./scripts/daily_gpu_log.sh 2025-05-28

# Analyze date range
./scripts/calculate_gpu_range.sh 2025-05-01 2025-05-15
```

## Error Handling and Troubleshooting

### Common Issues
1. **Chinese font display problems**: Run `cd visualization && python3 test_fonts.py`
2. **Virtual environment issues**: Use `./run_gpu_visualization.sh setup`
3. **Network connectivity**: Check Netdata services on nodes (port 19999)
4. **Data format errors**: Validate CSV structure and numeric formats
5. **Permission issues**: Ensure execute permissions on shell scripts

### Debugging Patterns
```python
# Add debug output for data validation
if df.empty:
    print(f"Warning: No data found in {csv_file}")
    return None

# Validate numeric columns
if not pd.api.types.is_numeric_dtype(df['GPU使用率(%)']):
    print(f"Non-numeric data detected in GPU usage column")
```

### Best Practices for New Features
1. **Follow existing naming conventions** for files and functions
2. **Include comprehensive error handling** with user-friendly messages
3. **Add progress indicators** for long-running operations
4. **Test with both virtual environment and system Python**
5. **Update documentation** in README.md for new functionality
6. **Maintain backward compatibility** with existing data formats

## Integration Notes

### Cron Job Integration
```bash
# Example crontab entry for daily data collection
45 23 * * * /bin/bash /path/to/data_collection/scripts/daily_gpu_log.sh
```

### Deployment Considerations
- **Data directory**: Excluded from git (.gitignore)
- **Plot outputs**: Generated in `plots/` directory
- **Dependencies**: Managed via requirements.txt
- **Font packages**: May need system-level installation (Noto Sans CJK)

This project follows a modular design with clear separation between data collection, processing, and visualization components. When contributing new features, maintain this structure and follow the established patterns for consistency and maintainability.
