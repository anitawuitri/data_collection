# GitHub Copilot Instructions for AMD GPU Monitoring & Visualization Project

## Project Overview

This is a comprehensive **AMD GPU monitoring and visualization system** designed for multi-node environments. The project provides automated data collection, statistical analysis, and advanced visualization capabilities for GPU utilization and VRAM usage monitoring across m### Integration Notes

### Cron Job Integration
```bash
# Example crontab entry for daily data collection (recommended Python version)
45 23 * * * /bin/bash /path/to/data_collection/python/run_daily_gpu_log.sh

# Traditional shell version (backup)
45 23 * * * /bin/bash /path/to/data_collection/scripts/daily_gpu_log.sh
```

### GPU User Tracking System Features
#### API Integration
- **Management endpoint**: `http://192.168.10.100/api/v2/consumption/task`
- **Authentication**: JWT Bearer token authentication  
- **Data retrieval**: User task information including GPU UUID mappings

#### Hardware Mapping System
```python
# GPU Card ID to GPU Index mapping
gpu_card_mapping = {
    1: 0, 9: 1, 17: 2, 25: 3,   # GPU[0-3]
    33: 4, 41: 5, 49: 6, 57: 7  # GPU[4-7] 
}
```

#### Enhanced CSV Format with User Information
```csv
GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者
GPU[0],0.00,0.14,未使用
GPU[3],18.17,82.27,nycubme
全部平均,4.81,20.81,所有使用者
```

#### User Task Information in Summary Reports
- GPU model and memory capacity
- Task type (LAB, WEBAPP, etc.)
- Project UUID and container image
- Task start time and duration
- User name and GPU UUID mapping

### Deployment Considerations
- **Data directory**: Excluded from git (.gitignore)
- **Plot outputs**: Generated in `plots/` directory
- **Dependencies**: Managed via requirements.txt
- **Font packages**: May need system-level installation (Noto Sans CJK)
- **User data privacy**: Handle user information according to privacy policies
- **API token management**: Secure storage and rotation of JWT tokensnodes.

### Core Functionality
- **🔥 GPU User Tracking System** - Real-time tracking of which users are using which GPUs via management API integration
- **Hardware Mapping System** - Automatic mapping between GPU Card IDs and GPU Indexes
- **Multi-node GPU monitoring** via Netdata API integration
- **Automated data collection** with both Python and Shell versions
- **Advanced visualization** with matplotlib, seaborn, and pandas  
- **VRAM monitoring** for memory usage analysis
- **Chinese localization** with proper font support
- **Virtual environment automation** for dependency management
- **Dual collection systems** - Python version (recommended) with enhanced features and Shell version (backup)

## Project Architecture

### Directory Structure
```
data_collection/
├── run_gpu_visualization.sh      # Main visualization script with virtual env support
├── requirements.txt              # Python dependencies
├── data/                         # GPU monitoring data (git ignored)
│   ├── colab-gpu1/              # Node-specific data directories
│   ├── colab-gpu2/              # Contains daily CSV files with timestamps
│   ├── colab-gpu3/              # GPU utilization + VRAM usage data + user info
│   └── colab-gpu4/
├── plots/                       # Generated visualization outputs
├── scripts/                     # Traditional Shell data collection scripts
│   ├── daily_gpu_log.sh        # Original Shell data collection from Netdata API
│   ├── calculate_gpu_range.sh  # Date range analysis
│   └── calculate_node_gpu_usage.sh # Node usage statistics
├── python/                      # 🔥 Python data collection system (RECOMMENDED)
│   ├── daily_gpu_log.py        # Python data collector with user tracking
│   ├── run_daily_gpu_log.sh    # Python execution script
│   ├── README.md               # Python version documentation
│   └── requirements.txt        # Python-specific dependencies
├── visualization/               # Python visualization toolkit
│   ├── quick_gpu_trend_plots.py    # Quick plotting functions
│   ├── advanced_gpu_trend_analyzer.py # Advanced analysis
│   ├── vram_monitor.py             # VRAM-specific monitoring
│   ├── font_config.py              # Chinese font configuration
│   └── gpu_trend_visualizer.py     # Core visualization engine
├── test_cases/                  # Consolidated test files
│   ├── test_gpu_collector.py    # GPU collector tests
│   ├── test_user_info.py        # User tracking tests
│   ├── test_timezone_complete.py # Timezone handling tests
│   └── run_all_tests.py         # Test runner
└── examples/                    # Usage examples and tutorials
```

### Technology Stack
- **Shell Scripting**: Bash for automation and data collection (traditional approach)
- **Python 3.7+**: Data processing, user tracking, and visualization (recommended approach)
- **Management API**: JWT authentication for user task information retrieval
- **Netdata API**: Real-time GPU metrics collection (port 19999)
- **Data Processing**: pandas, numpy for data manipulation, user info integration
- **Visualization**: matplotlib, seaborn for charts and plots
- **Chinese Fonts**: Noto Sans CJK for proper Chinese character display

### Key Components

#### 1. 🔥 Python Data Collection System (`python/`)
**RECOMMENDED**: Enhanced Python version with advanced features
- **`daily_gpu_log.py`**: Modern Python collector with user tracking
- **GPU User Tracking**: Integrates management API to show which users are using which GPUs
- **Hardware Mapping**: Automatic mapping between GPU Card IDs and GPU Indexes
- **Enhanced Reports**: CSV files include user columns, summary reports show detailed user task information
- **Better Error Handling**: Detailed error diagnostics and automatic recovery
- **Data Validation**: Uses pandas for robust data integrity checking
- **Object-Oriented Design**: Easy to maintain and extend architecture
- **API Integration**: 
  - Management endpoint: `http://192.168.10.100/api/v2/consumption/task`
  - JWT Bearer token authentication
  - User task information retrieval

#### 2. Traditional Data Collection System (`scripts/`)
**BACKUP**: Original shell-based approach
- **`daily_gpu_log.sh`**: Collects GPU utilization and VRAM usage from 4 nodes
- **Network endpoints**: 192.168.10.103-106 (colab-gpu1 to colab-gpu4)
- **Monitored GPUs**: IDs 1, 9, 17, 25, 33, 41, 49, 57 per node
- **Data format**: CSV with timestamps, GPU usage %, VRAM usage %
- **API endpoints**: 
  - `amdgpu.gpu_utilization_unknown_AMD_GPU_card{ID}`
  - `amdgpu.gpu_mem_vram_usage_perc_unknown_AMD_GPU_card{ID}`

#### 3. Visualization Engine (`visualization/`)
- **Quick plots**: Fast chart generation for common use cases
- **Advanced analysis**: Complex multi-dimensional analysis
- **VRAM monitoring**: Dedicated VRAM usage visualization
- **Heatmaps**: Usage distribution across nodes and time
- **Time series**: Detailed timeline analysis

#### 4. Test Framework (`test_cases/`)
- **Consolidated Testing**: All test files organized in one location under `test_cases/`
- **Test Categories**:
  - **Basic Functionality**: `test_gpu_collector.py`, `test_chinese_font.py`, `test_gpu_mapping.py`
  - **User Tracking**: `test_user_info.py`, `test_user_column.py`, `test_gpu_task_info.py`
  - **Visualization**: `test_heatmap_users.py`, `test_vram_users.py`
  - **Timezone Handling**: `test_timezone_complete.py`, `test_taiwan_timezone.py`
  - **System Verification**: `chart_verification.py`, `final_verification.py`
- **Test Runner**: `run_all_tests.py` for comprehensive testing
- **Import Structure**: Relative paths (`../python`, `../visualization`) for cross-module testing
- **Test Reporting**: Detailed success/failure reporting with improvement suggestions

#### 5. Main Automation Script (`run_gpu_visualization.sh`)
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

# For user tracking features
df_with_users = pd.read_csv(average_csv)
# Expected columns: 'GPU編號', '平均GPU使用率(%)', '平均VRAM使用率(%)', '使用者'
```

#### Test Case Patterns
```python
# Test import structure (from test_cases/)
import sys
import os
sys.path.append('../python')
sys.path.append('../visualization')

from daily_gpu_log import GPUDataCollector
from vram_monitor import VRAMMonitor

# Standard test validation
def test_feature():
    try:
        # Test implementation
        result = feature_function()
        assert result is not None
        print("✅ Test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
```

#### File Naming Conventions
- **Data files**: `gpu{ID}_{YYYY-MM-DD}.csv`
- **Average files**: `average_{YYYY-MM-DD}.csv` (with user columns)
- **Summary files**: `summary_{YYYY-MM-DD}.txt` (with user task info)
- **Plot outputs**: `{type}_{start_date}_to_{end_date}.png`
- **Node-specific**: `{node}_gpu{ID}_{date}.png`
- **VRAM files**: `vram_*` prefix for VRAM-specific outputs
- **Test files**: `test_{feature}.py` in test_cases/ directory

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
# Individual GPU data files
時間戳,日期時間,GPU使用率(%),VRAM使用率(%)
1716969600,"2025-05-28 00:00:00",1.23,45.67

# Average files with user information (enhanced format)
GPU編號,平均GPU使用率(%),平均VRAM使用率(%),使用者
GPU[0],0.00,0.14,未使用
GPU[1],0.00,0.14,未使用
GPU[3],18.17,82.27,nycubme
全部平均,4.81,20.81,所有使用者
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
# 🔥 Collect today's data (Python version - RECOMMENDED)
./python/run_daily_gpu_log.sh

# Collect specific date (Python version)
./python/run_daily_gpu_log.sh 2025-05-28

# Traditional Shell version (backup)
./scripts/daily_gpu_log.sh
./scripts/daily_gpu_log.sh 2025-05-28

# Analyze date range
./scripts/calculate_gpu_range.sh 2025-05-01 2025-05-15
```

## Error Handling and Troubleshooting

### Common Issues
1. **Chinese font display problems**: Run `cd visualization && python3 test_fonts.py`
2. **Virtual environment issues**: Use `./run_gpu_visualization.sh setup`
3. **Network connectivity**: Check Netdata services on nodes (port 19999) and management API (port 80)
4. **Data format errors**: Validate CSV structure and numeric formats
5. **Permission issues**: Ensure execute permissions on shell scripts
6. **Test import errors**: Use `cd test_cases && python3 run_all_tests.py` for consolidated testing
7. **User tracking failures**: Check JWT token authentication and management API connectivity

### Debugging Patterns
```python
# Add debug output for data validation
if df.empty:
    print(f"Warning: No data found in {csv_file}")
    return None

# Validate numeric columns
if not pd.api.types.is_numeric_dtype(df['GPU使用率(%)']):
    print(f"Non-numeric data detected in GPU usage column")

# Test user tracking functionality
def test_user_tracking():
    try:
        from daily_gpu_log import GPUDataCollector
        collector = GPUDataCollector()
        user_info = collector.get_user_task_info()
        assert user_info is not None
        print("✅ User tracking test passed")
    except Exception as e:
        print(f"❌ User tracking test failed: {e}")
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
# Example crontab entry for daily data collection (recommended Python version)
45 23 * * * /bin/bash /path/to/data_collection/python/run_daily_gpu_log.sh

# Traditional shell version (backup)
45 23 * * * /bin/bash /path/to/data_collection/scripts/daily_gpu_log.sh
```

### Deployment Considerations
- **Data directory**: Excluded from git (.gitignore)
- **Plot outputs**: Generated in `plots/` directory
- **Dependencies**: Managed via requirements.txt
- **Font packages**: May need system-level installation (Noto Sans CJK)

This project follows a modular design with clear separation between data collection, processing, and visualization components. When contributing new features, maintain this structure and follow the established patterns for consistency and maintainability.

### Recent Major Updates (2025-08-06)
The project has undergone significant enhancements in v2.0-v2.1:

#### v2.1 - Heatmap User Integration
- **Enhanced Heatmaps**: Added user information display in GPU utilization heatmaps
- **Multi-date Visualization**: Support for date range heatmap analysis
- **User Labels**: Y-axis labels include node, GPU number, and user information
- **Flexible Display**: `show_users` parameter controls user information visibility

#### v2.0 - User Information Integration
- **Major Bug Fix**: Resolved incorrect GPU ID mapping between API absolute IDs (0-31) and hardware Card IDs (1,9,17,25,33,41,49,57)
- **User Tracking**: Full integration of user information in CSV reports and visualizations
- **Enhanced Charts**: All visualization tools now support user information display
- **Unified Scripts**: Added `run_user_monitor.sh` for streamlined operations

### AI Assistant Guidelines

#### Code Generation Best Practices
- **Use Chinese localization** for all user-facing text and labels
- **Implement user tracking features** when working on data collection or visualization
- **Follow modular design** with clear separation of concerns
- **Include comprehensive error handling** for network requests and data processing
- **Maintain backward compatibility** with existing data formats and APIs

#### Common Development Patterns
```python
# For data collection scripts
class DataCollector:
    def __init__(self):
        self.gpu_card_mapping = {1: 0, 9: 1, 17: 2, 25: 3, 33: 4, 41: 5, 49: 6, 57: 7}
        self.management_api_url = "http://192.168.10.100/api/v2/consumption/task"
    
    def collect_with_user_info(self):
        # Always integrate user tracking when collecting data
        pass

# For visualization scripts  
def plot_with_users(data, show_users=True):
    if show_users:
        # Include user information in labels, titles, legends
        # Use _with_users suffix for filenames
        pass
```

#### Testing Requirements
- **Test user information integration** in all new features
- **Verify Chinese font rendering** for visualization components
- **Validate GPU ID mapping** accuracy when working with hardware interfaces
- **Check API authentication** for management system integration

#### File Organization Guidelines
- **test_cases/**: Place all test files with proper import paths
- **python/**: Enhanced data collection with user tracking
- **visualization/**: Chart generation with user information support
- **scripts/**: Legacy shell scripts maintained for compatibility
