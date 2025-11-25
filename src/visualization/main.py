"""簡化的視覺化工具

替代原來複雜的視覺化腳本，直接完成繪圖任務。
"""

import argparse
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional

from .plotter import SimpleGPUPlotter
from .font_utils import setup_chinese_font, create_test_plot


class SimpleVisualizer:
    """簡化的視覺化工具"""
    
    def __init__(self, data_dir: str = "./data", output_dir: str = "./plots"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.plotter = SimpleGPUPlotter(output_dir)
        
        if not self.data_dir.exists():
            raise ValueError(f"數據目錄不存在: {self.data_dir}")
    
    def generate_daily_plots(self, date_str: str, nodes: Optional[List[str]] = None) -> List[str]:
        """生成每日圖表
        
        Args:
            date_str: 日期字符串
            nodes: 節點列表，None 表示自動發現
            
        Returns:
            生成的圖表文件路徑列表
        """
        generated_files = []
        
        try:
            # 節點對比圖
            file_path = self.plotter.plot_node_comparison(self.data_dir, date_str, nodes)
            generated_files.append(file_path)
            print(f"✅ 節點對比圖: {file_path}")
        except Exception as e:
            print(f"⚠️  節點對比圖生成失敗: {e}")
        
        try:
            # 使用者使用情況圖
            file_path = self.plotter.plot_user_usage(self.data_dir, date_str, nodes)
            if file_path:
                generated_files.append(file_path)
                print(f"✅ 使用者使用圖: {file_path}")
        except Exception as e:
            print(f"⚠️  使用者使用圖生成失敗: {e}")
        
        # 為每個節點生成時間線圖
        target_nodes = nodes or self._discover_nodes(date_str)
        
        for node in target_nodes:
            try:
                file_path = self.plotter.plot_gpu_timeline(self.data_dir, node, date_str)
                generated_files.append(file_path)
                print(f"✅ {node} 時間線圖: {file_path}")
            except Exception as e:
                print(f"⚠️  {node} 時間線圖失敗: {e}")
        
        return generated_files
    
    def _discover_nodes(self, date_str: str) -> List[str]:
        """發現可用的節點"""
        nodes = []
        for node_dir in self.data_dir.iterdir():
            if node_dir.is_dir() and node_dir.name.startswith('colab-gpu'):
                date_dir = node_dir / date_str
                if date_dir.exists() and any(date_dir.glob('*.csv')):
                    nodes.append(node_dir.name)
        return sorted(nodes)
    
    def test_fonts(self) -> str:
        """測試字體配置"""
        print("🔤 設置字體配置...")
        font = setup_chinese_font()
        print(f"📝 使用字體: {font}")
        
        output_path = self.output_dir / 'font_test.png'
        file_path = create_test_plot(output_path)
        print(f"✅ 字體測試圖: {file_path}")
        
        return file_path


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='簡化的 GPU 視覺化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python -m src.visualization.main daily 2025-09-19    # 生成日常圖表
  python -m src.visualization.main test-fonts          # 測試字體
  python -m src.visualization.main daily --nodes gpu1,gpu2  # 指定節點
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # daily 命令
    daily_parser = subparsers.add_parser('daily', help='生成每日圖表')
    daily_parser.add_argument('date', help='日期 (YYYY-MM-DD)')
    daily_parser.add_argument('--nodes', help='指定節點，逗號分隔')
    daily_parser.add_argument('--data-dir', default='./data', help='數據目錄')
    daily_parser.add_argument('--output-dir', default='./plots', help='輸出目錄')
    
    # test-fonts 命令
    fonts_parser = subparsers.add_parser('test-fonts', help='測試字體配置')
    fonts_parser.add_argument('--output-dir', default='./plots', help='輸出目錄')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'test-fonts':
            visualizer = SimpleVisualizer(output_dir=args.output_dir)
            visualizer.test_fonts()
            
        elif args.command == 'daily':
            # 驗證日期格式
            try:
                datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                print(f"❌ 無效日期格式: {args.date}")
                sys.exit(1)
            
            # 解析節點
            nodes = None
            if args.nodes:
                nodes = [n.strip() for n in args.nodes.split(',')]
            
            # 生成圖表
            visualizer = SimpleVisualizer(args.data_dir, args.output_dir)
            files = visualizer.generate_daily_plots(args.date, nodes)
            
            print(f"\n🎉 完成! 生成了 {len(files)} 個圖表文件")
            
    except Exception as e:
        print(f"💥 錯誤: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()