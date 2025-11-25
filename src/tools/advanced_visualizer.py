"""高級視覺化工具

替代複雜的 run_gpu_visualization.sh，提供所有視覺化功能。
去掉 shell 腳本的複雜性，直接用 Python 實現。
"""

import argparse
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
import glob
import os

from ..visualization.plotter import SimpleGPUPlotter
from ..visualization.font_utils import setup_chinese_font


class AdvancedVisualizer:
    """高級視覺化工具
    
    整合原來 run_gpu_visualization.sh 的所有功能。
    """
    
    def __init__(self, data_dir: str = "./data", output_dir: str = "./plots"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.plotter = SimpleGPUPlotter(output_dir)
        
        # 確保目錄存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 節點配置
        self.nodes = ["colab-gpu1", "colab-gpu2", "colab-gpu3", "colab-gpu4"]
        
        if not self.data_dir.exists():
            print(f"⚠️  數據目錄不存在: {self.data_dir}")
    
    def auto_detect_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """自動檢測可用的日期範圍"""
        available_dates = set()
        
        for node in self.nodes:
            node_dir = self.data_dir / node
            if node_dir.exists():
                for date_dir in node_dir.iterdir():
                    if date_dir.is_dir() and date_dir.name.count('-') == 2:
                        try:
                            # 驗證日期格式
                            datetime.strptime(date_dir.name, '%Y-%m-%d')
                            available_dates.add(date_dir.name)
                        except ValueError:
                            continue
        
        if not available_dates:
            return None, None
        
        # 返回最新的7天範圍
        sorted_dates = sorted(available_dates, reverse=True)
        end_date = sorted_dates[0]
        start_date = sorted_dates[min(6, len(sorted_dates)-1)]
        
        return start_date, end_date
    
    def quick_plots(self, start_date: str, end_date: str, nodes: List[str] = None) -> List[str]:
        """快速生成常用圖表"""
        if not nodes:
            nodes = self.discover_nodes_with_data(start_date, end_date)
        
        generated_files = []
        
        print(f"📊 生成 {start_date} 到 {end_date} 的快速圖表...")
        
        try:
            # 節點對比圖 - 每天一張
            current = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            while current <= end:
                date_str = current.isoformat()
                try:
                    file_path = self.plotter.plot_node_comparison(self.data_dir, date_str, nodes)
                    generated_files.append(file_path)
                    print(f"  ✅ {date_str} 節點對比圖")
                except Exception as e:
                    print(f"  ⚠️  {date_str} 節點對比圖失敗: {e}")
                
                current += timedelta(days=1)
            
            # 每個節點的每日時間線圖
            for node in nodes:
                # 為每個節點生成範圍內每一天的時間線圖
                current = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                node_files = 0
                while current <= end_date_obj:
                    date_str = current.isoformat()
                    try:
                        file_path = self.plotter.plot_gpu_timeline(
                            self.data_dir, node, date_str
                        )
                        generated_files.append(file_path)
                        node_files += 1
                    except Exception:
                        # 靜默忽略缺失的單日數據
                        pass
                    current += timedelta(days=1)
                
                if node_files > 0:
                    print(f"  ✅ {node} 時間線圖 ({node_files}天)")
                else:
                    print(f"  ⚠️  {node} 無可用數據")
        
        except Exception as e:
            print(f"❌ 快速圖表生成失敗: {e}")
        
        return generated_files
    
    def nodes_comparison(self, start_date: str, end_date: str) -> List[str]:
        """生成節點對比圖"""
        generated_files = []
        current = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        print(f"📊 生成節點對比圖: {start_date} 到 {end_date}")
        
        while current <= end:
            date_str = current.isoformat()
            try:
                file_path = self.plotter.plot_node_comparison(self.data_dir, date_str)
                generated_files.append(file_path)
                print(f"  ✅ {date_str}")
            except Exception as e:
                print(f"  ⚠️  {date_str} 失敗: {e}")
            
            current += timedelta(days=1)
        
        return generated_files
    
    def single_node_analysis(self, node: str, start_date: str, end_date: str) -> List[str]:
        """分析單個節點"""
        generated_files = []
        
        print(f"📊 生成 {node} 分析圖: {start_date} 到 {end_date}")
        
        # 每天的詳細時間線
        current = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        while current <= end:
            date_str = current.isoformat()
            try:
                file_path = self.plotter.plot_gpu_timeline(self.data_dir, node, date_str)
                generated_files.append(file_path)
                print(f"  ✅ {node} {date_str}")
            except Exception as e:
                # 靜默處理單日缺失數據
                pass
            
            current += timedelta(days=1)
        
        return generated_files
    
    def discover_nodes_with_data(self, start_date: str, end_date: str) -> List[str]:
        """發現在指定日期範圍內有數據的節點"""
        nodes_with_data = []
        
        current = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        for node in self.nodes:
            has_data = False
            check_date = current
            
            while check_date <= end and not has_data:
                date_str = check_date.isoformat()
                date_dir = self.data_dir / node / date_str
                
                if date_dir.exists() and any(date_dir.glob('*.csv')):
                    has_data = True
                
                check_date += timedelta(days=1)
            
            if has_data:
                nodes_with_data.append(node)
        
        return nodes_with_data
    
    def auto_mode(self) -> List[str]:
        """自動模式 - 檢測數據並生成圖表"""
        print("🔍 自動檢測可用數據...")
        
        start_date, end_date = self.auto_detect_date_range()
        
        if not start_date or not end_date:
            print("❌ 未找到可用的數據")
            return []
        
        print(f"📅 檢測到數據範圍: {start_date} 到 {end_date}")
        
        available_nodes = self.discover_nodes_with_data(start_date, end_date)
        print(f"🖥️  可用節點: {', '.join(available_nodes)}")
        
        return self.quick_plots(start_date, end_date, available_nodes)
    
    def test_environment(self) -> bool:
        """測試環境是否準備就緒"""
        print("🔧 檢查環境...")
        
        try:
            # 測試字體配置
            font = setup_chinese_font()
            print(f"✅ 字體配置: {font}")
            
            # 檢查數據目錄
            if self.data_dir.exists():
                print(f"✅ 數據目錄: {self.data_dir}")
                
                # 統計數據文件
                total_files = 0
                for node in self.nodes:
                    node_dir = self.data_dir / node
                    if node_dir.exists():
                        csv_files = list(node_dir.glob('*/*.csv'))
                        total_files += len(csv_files)
                
                print(f"📊 發現 {total_files} 個數據文件")
            else:
                print(f"⚠️  數據目錄不存在: {self.data_dir}")
            
            # 檢查輸出目錄
            print(f"✅ 輸出目錄: {self.output_dir}")
            
            print("✅ 環境檢查完成")
            return True
            
        except Exception as e:
            print(f"❌ 環境檢查失敗: {e}")
            return False


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='高級 GPU 視覺化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  # 快速生成圖表
  python -m src.tools.advanced_visualizer quick 2025-09-15 2025-09-19
  
  # 節點對比
  python -m src.tools.advanced_visualizer nodes 2025-09-15 2025-09-19
  
  # 單節點分析
  python -m src.tools.advanced_visualizer node colab-gpu1 2025-09-15 2025-09-19
  
  # 自動模式
  python -m src.tools.advanced_visualizer auto
  
  # 環境測試
  python -m src.tools.advanced_visualizer test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # quick 命令
    quick_parser = subparsers.add_parser('quick', help='快速生成常用圖表')
    quick_parser.add_argument('start_date', help='開始日期 (YYYY-MM-DD)')
    quick_parser.add_argument('end_date', help='結束日期 (YYYY-MM-DD)')
    quick_parser.add_argument('--nodes', help='指定節點，逗號分隔')
    
    # nodes 命令
    nodes_parser = subparsers.add_parser('nodes', help='生成節點對比圖')
    nodes_parser.add_argument('start_date', help='開始日期 (YYYY-MM-DD)')
    nodes_parser.add_argument('end_date', help='結束日期 (YYYY-MM-DD)')
    
    # node 命令
    node_parser = subparsers.add_parser('node', help='單節點分析')
    node_parser.add_argument('node_name', help='節點名稱')
    node_parser.add_argument('start_date', help='開始日期 (YYYY-MM-DD)')
    node_parser.add_argument('end_date', help='結束日期 (YYYY-MM-DD)')
    
    # auto 命令
    auto_parser = subparsers.add_parser('auto', help='自動模式')
    
    # test 命令
    test_parser = subparsers.add_parser('test', help='測試環境')
    
    # 通用參數
    for sub_parser in [quick_parser, nodes_parser, node_parser, auto_parser]:
        sub_parser.add_argument('--data-dir', default='./data', help='數據目錄')
        sub_parser.add_argument('--output-dir', default='./plots', help='輸出目錄')
    
    test_parser.add_argument('--data-dir', default='./data', help='數據目錄')
    test_parser.add_argument('--output-dir', default='./plots', help='輸出目錄')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        visualizer = AdvancedVisualizer(
            data_dir=args.data_dir,
            output_dir=args.output_dir
        )
        
        if args.command == 'test':
            success = visualizer.test_environment()
            sys.exit(0 if success else 1)
        
        elif args.command == 'auto':
            files = visualizer.auto_mode()
            print(f"\n🎉 自動模式完成! 生成 {len(files)} 個圖表文件")
        
        elif args.command == 'quick':
            # 驗證日期格式
            try:
                datetime.strptime(args.start_date, '%Y-%m-%d')
                datetime.strptime(args.end_date, '%Y-%m-%d')
            except ValueError:
                print("❌ 無效的日期格式，請使用 YYYY-MM-DD")
                sys.exit(1)
            
            nodes = None
            if args.nodes:
                nodes = [n.strip() for n in args.nodes.split(',')]
            
            files = visualizer.quick_plots(args.start_date, args.end_date, nodes)
            print(f"\n🎉 快速圖表完成! 生成 {len(files)} 個文件")
        
        elif args.command == 'nodes':
            try:
                datetime.strptime(args.start_date, '%Y-%m-%d')
                datetime.strptime(args.end_date, '%Y-%m-%d')
            except ValueError:
                print("❌ 無效的日期格式，請使用 YYYY-MM-DD")
                sys.exit(1)
            
            files = visualizer.nodes_comparison(args.start_date, args.end_date)
            print(f"\n🎉 節點對比完成! 生成 {len(files)} 個文件")
        
        elif args.command == 'node':
            try:
                datetime.strptime(args.start_date, '%Y-%m-%d')
                datetime.strptime(args.end_date, '%Y-%m-%d')
            except ValueError:
                print("❌ 無效的日期格式，請使用 YYYY-MM-DD")
                sys.exit(1)
            
            files = visualizer.single_node_analysis(
                args.node_name, args.start_date, args.end_date
            )
            print(f"\n🎉 {args.node_name} 分析完成! 生成 {len(files)} 個文件")
        
        # 顯示生成的文件
        if hasattr(visualizer, 'output_dir'):
            print(f"\n📁 圖表保存位置: {visualizer.output_dir}")
            recent_files = list(visualizer.output_dir.glob('*.png'))
            if recent_files:
                recent_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                print("📊 最新生成的圖表:")
                for i, file_path in enumerate(recent_files[:5]):  # 顯示最新5個
                    print(f"   {i+1}. {file_path.name}")
        
    except Exception as e:
        print(f"💥 錯誤: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()