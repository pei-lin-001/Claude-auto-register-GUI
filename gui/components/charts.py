import tkinter as tk
from tkinter import ttk
import datetime
from typing import List, Dict, Any, Optional
import json
import os

# 尝试导入matplotlib，如果未安装则提供降级方案
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    from matplotlib.animation import FuncAnimation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("注意: 未安装matplotlib库，图表功能不可用")

class StatisticsData:
    """统计数据管理类"""
    
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), '../resources/statistics.json')
        self.daily_stats = {}
        self.load_data()
    
    def load_data(self):
        """加载统计数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.daily_stats = data.get('daily_stats', {})
        except Exception as e:
            print(f"加载统计数据失败: {e}")
            self.daily_stats = {}
    
    def save_data(self):
        """保存统计数据"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = {
                'daily_stats': self.daily_stats,
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存统计数据失败: {e}")
    
    def add_registration_result(self, success: bool, timestamp: Optional[datetime.datetime] = None):
        """添加注册结果"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        date_str = timestamp.strftime('%Y-%m-%d')
        
        if date_str not in self.daily_stats:
            self.daily_stats[date_str] = {
                'success_count': 0,
                'failed_count': 0,
                'total_count': 0
            }
        
        if success:
            self.daily_stats[date_str]['success_count'] += 1
        else:
            self.daily_stats[date_str]['failed_count'] += 1
        
        self.daily_stats[date_str]['total_count'] += 1
        self.save_data()
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Dict]:
        """获取最近N天的统计数据"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        result = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            result[date_str] = self.daily_stats.get(date_str, {
                'success_count': 0,
                'failed_count': 0,
                'total_count': 0
            })
            current_date += datetime.timedelta(days=1)
        
        return result
    
    def get_total_stats(self) -> Dict[str, int]:
        """获取总统计数据"""
        total_success = 0
        total_failed = 0
        total_count = 0
        
        for stats in self.daily_stats.values():
            total_success += stats.get('success_count', 0)
            total_failed += stats.get('failed_count', 0)
            total_count += stats.get('total_count', 0)
        
        return {
            'total_success': total_success,
            'total_failed': total_failed,
            'total_count': total_count,
            'success_rate': (total_success / total_count * 100) if total_count > 0 else 0
        }

class BaseChart:
    """图表基类"""
    
    def __init__(self, parent, title: str = "", width: int = 400, height: int = 300):
        self.parent = parent
        self.title = title
        self.width = width
        self.height = height
        self.frame = None
        self.canvas = None
        self.figure = None
        self.ax = None
        
    def create_frame(self):
        """创建图表框架"""
        self.frame = ttk.LabelFrame(self.parent, text=self.title, padding=10)
        return self.frame
    
    def update_data(self, data: Dict[str, Any]):
        """更新图表数据"""
        pass
    
    def clear(self):
        """清空图表"""
        if self.ax:
            self.ax.clear()

class DailyRegistrationChart(BaseChart):
    """每日注册统计图表"""
    
    def __init__(self, parent, statistics_data: StatisticsData):
        super().__init__(parent, "每日注册统计", 500, 300)
        self.statistics_data = statistics_data
        self.setup_chart()
    
    def setup_chart(self):
        """设置图表"""
        if not MATPLOTLIB_AVAILABLE:
            self._create_fallback_widget()
            return
        
        self.figure = Figure(figsize=(6, 3), dpi=80)
        self.ax = self.figure.add_subplot(111)
        
        # 设置图表样式
        self.figure.patch.set_facecolor('white')
        self.ax.set_title('每日注册统计', fontsize=12, fontweight='bold')
        self.ax.set_xlabel('日期')
        self.ax.set_ylabel('注册数量')
        self.ax.grid(True, alpha=0.3)
        
        # 创建canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 初始化数据
        self.update_chart()
    
    def _create_fallback_widget(self):
        """创建降级方案控件"""
        fallback_frame = tk.Frame(self.frame, bg='lightgray', height=200)
        fallback_frame.pack(fill="both", expand=True)
        
        fallback_label = tk.Label(
            fallback_frame,
            text="图表功能不可用\n请安装matplotlib库",
            bg='lightgray',
            fg='gray',
            font=('Arial', 12)
        )
        fallback_label.pack(expand=True)
    
    def update_chart(self, days: int = 7):
        """更新图表"""
        if not MATPLOTLIB_AVAILABLE or not self.ax:
            return
        
        try:
            # 获取数据
            daily_stats = self.statistics_data.get_daily_stats(days)
            
            dates = []
            success_counts = []
            failed_counts = []
            
            for date_str, stats in daily_stats.items():
                dates.append(datetime.datetime.strptime(date_str, '%Y-%m-%d'))
                success_counts.append(stats['success_count'])
                failed_counts.append(stats['failed_count'])
            
            # 清空图表
            self.ax.clear()
            
            # 绘制柱状图
            width = 0.35
            x = range(len(dates))
            
            bars1 = self.ax.bar([i - width/2 for i in x], success_counts, 
                              width, label='成功', color='#28A745', alpha=0.8)
            bars2 = self.ax.bar([i + width/2 for i in x], failed_counts, 
                              width, label='失败', color='#DC3545', alpha=0.8)
            
            # 设置标签
            self.ax.set_title('每日注册统计', fontsize=12, fontweight='bold')
            self.ax.set_xlabel('日期')
            self.ax.set_ylabel('注册数量')
            self.ax.set_xticks(x)
            self.ax.set_xticklabels([d.strftime('%m-%d') for d in dates], rotation=45)
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # 在柱子上显示数值
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    self.ax.annotate(f'{int(height)}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 3),
                                   textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8)
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    self.ax.annotate(f'{int(height)}',
                                   xy=(bar.get_x() + bar.get_width() / 2, height),
                                   xytext=(0, 3),
                                   textcoords="offset points",
                                   ha='center', va='bottom', fontsize=8)
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"更新每日注册图表失败: {e}")

class SuccessRateChart(BaseChart):
    """成功率饼图"""
    
    def __init__(self, parent, statistics_data: StatisticsData):
        super().__init__(parent, "注册成功率", 300, 300)
        self.statistics_data = statistics_data
        self.setup_chart()
    
    def setup_chart(self):
        """设置图表"""
        if not MATPLOTLIB_AVAILABLE:
            self._create_fallback_widget()
            return
        
        self.figure = Figure(figsize=(4, 4), dpi=80)
        self.ax = self.figure.add_subplot(111)
        
        # 设置图表样式
        self.figure.patch.set_facecolor('white')
        
        # 创建canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 初始化数据
        self.update_chart()
    
    def _create_fallback_widget(self):
        """创建降级方案控件"""
        fallback_frame = tk.Frame(self.frame, bg='lightgray', height=200)
        fallback_frame.pack(fill="both", expand=True)
        
        # 显示文本统计
        total_stats = self.statistics_data.get_total_stats()
        
        stats_text = f"总注册: {total_stats['total_count']}\n"
        stats_text += f"成功: {total_stats['total_success']}\n"
        stats_text += f"失败: {total_stats['total_failed']}\n"
        stats_text += f"成功率: {total_stats['success_rate']:.1f}%"
        
        stats_label = tk.Label(
            fallback_frame,
            text=stats_text,
            bg='lightgray',
            fg='black',
            font=('Arial', 10),
            justify='left'
        )
        stats_label.pack(expand=True)
    
    def update_chart(self):
        """更新图表"""
        if not MATPLOTLIB_AVAILABLE or not self.ax:
            return
        
        try:
            # 获取总统计数据
            total_stats = self.statistics_data.get_total_stats()
            
            success_count = total_stats['total_success']
            failed_count = total_stats['total_failed']
            
            if success_count == 0 and failed_count == 0:
                # 没有数据时显示占位图
                self.ax.clear()
                self.ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                           transform=self.ax.transAxes, fontsize=14, color='gray')
                self.ax.set_xlim(0, 1)
                self.ax.set_ylim(0, 1)
                self.ax.axis('off')
            else:
                # 清空图表
                self.ax.clear()
                
                # 数据和标签
                sizes = [success_count, failed_count]
                labels = ['成功', '失败']
                colors = ['#28A745', '#DC3545']
                
                # 绘制饼图
                wedges, texts, autotexts = self.ax.pie(
                    sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    startangle=90, textprops={'fontsize': 10}
                )
                
                # 设置标题
                self.ax.set_title(f'注册成功率\n总计: {success_count + failed_count}', 
                                fontsize=12, fontweight='bold')
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"更新成功率图表失败: {e}")

class TrendChart(BaseChart):
    """趋势折线图"""
    
    def __init__(self, parent, statistics_data: StatisticsData):
        super().__init__(parent, "注册趋势", 500, 300)
        self.statistics_data = statistics_data
        self.setup_chart()
    
    def setup_chart(self):
        """设置图表"""
        if not MATPLOTLIB_AVAILABLE:
            self._create_fallback_widget()
            return
        
        self.figure = Figure(figsize=(6, 3), dpi=80)
        self.ax = self.figure.add_subplot(111)
        
        # 设置图表样式
        self.figure.patch.set_facecolor('white')
        
        # 创建canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # 初始化数据
        self.update_chart()
    
    def _create_fallback_widget(self):
        """创建降级方案控件"""
        fallback_frame = tk.Frame(self.frame, bg='lightgray', height=200)
        fallback_frame.pack(fill="both", expand=True)
        
        fallback_label = tk.Label(
            fallback_frame,
            text="趋势图功能不可用\n请安装matplotlib库",
            bg='lightgray',
            fg='gray',
            font=('Arial', 12)
        )
        fallback_label.pack(expand=True)
    
    def update_chart(self, days: int = 14):
        """更新图表"""
        if not MATPLOTLIB_AVAILABLE or not self.ax:
            return
        
        try:
            # 获取数据
            daily_stats = self.statistics_data.get_daily_stats(days)
            
            dates = []
            success_rates = []
            total_counts = []
            
            for date_str, stats in daily_stats.items():
                dates.append(datetime.datetime.strptime(date_str, '%Y-%m-%d'))
                total_count = stats['total_count']
                total_counts.append(total_count)
                
                if total_count > 0:
                    success_rate = stats['success_count'] / total_count * 100
                else:
                    success_rate = 0
                success_rates.append(success_rate)
            
            # 清空图表
            self.ax.clear()
            
            # 创建双y轴
            ax2 = self.ax.twinx()
            
            # 绘制成功率线
            line1 = self.ax.plot(dates, success_rates, 'o-', color='#2E86AB', 
                               linewidth=2, markersize=4, label='成功率 (%)')
            
            # 绘制注册总数线
            line2 = ax2.plot(dates, total_counts, 's-', color='#FFC107', 
                           linewidth=2, markersize=4, label='注册总数')
            
            # 设置标签和标题
            self.ax.set_title('注册趋势分析', fontsize=12, fontweight='bold')
            self.ax.set_xlabel('日期')
            self.ax.set_ylabel('成功率 (%)', color='#2E86AB')
            ax2.set_ylabel('注册总数', color='#FFC107')
            
            # 设置y轴范围
            self.ax.set_ylim(0, 100)
            if max(total_counts) > 0:
                ax2.set_ylim(0, max(total_counts) * 1.1)
            
            # 设置x轴标签
            self.ax.tick_params(axis='x', rotation=45)
            
            # 格式化日期
            if len(dates) > 7:
                self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            # 添加网格
            self.ax.grid(True, alpha=0.3)
            
            # 合并图例
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            self.ax.legend(lines, labels, loc='upper left')
            
            # 调整布局
            self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"更新趋势图表失败: {e}")

class ChartContainer:
    """图表容器类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.statistics_data = StatisticsData()
        self.charts = {}
        self.container_frame = None
        self.setup_container()
    
    def setup_container(self):
        """设置容器"""
        self.container_frame = ttk.Frame(self.parent)
        
        # 创建图表区域
        charts_frame = ttk.Frame(self.container_frame)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 第一行：每日统计和成功率
        row1_frame = ttk.Frame(charts_frame)
        row1_frame.pack(fill="x", pady=(0, 10))
        
        # 每日注册图表
        daily_chart = DailyRegistrationChart(row1_frame, self.statistics_data)
        daily_chart_frame = daily_chart.create_frame()
        daily_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.charts['daily'] = daily_chart
        
        # 成功率图表
        rate_chart = SuccessRateChart(row1_frame, self.statistics_data)
        rate_chart_frame = rate_chart.create_frame()
        rate_chart_frame.pack(side="right", fill="both", padx=(5, 0))
        self.charts['success_rate'] = rate_chart
        
        # 第二行：趋势图
        row2_frame = ttk.Frame(charts_frame)
        row2_frame.pack(fill="both", expand=True)
        
        # 趋势图表
        trend_chart = TrendChart(row2_frame, self.statistics_data)
        trend_chart_frame = trend_chart.create_frame()
        trend_chart_frame.pack(fill="both", expand=True)
        self.charts['trend'] = trend_chart
        
        # 控制按钮
        control_frame = ttk.Frame(self.container_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(control_frame, text="刷新图表", 
                  command=self.refresh_charts).pack(side="left", padx=5)
        ttk.Button(control_frame, text="导出数据", 
                  command=self.export_data).pack(side="left", padx=5)
        ttk.Button(control_frame, text="清空数据", 
                  command=self.clear_data).pack(side="left", padx=5)
    
    def get_container(self):
        """获取容器框架"""
        return self.container_frame
    
    def add_registration_result(self, success: bool):
        """添加注册结果"""
        self.statistics_data.add_registration_result(success)
        self.refresh_charts()
    
    def refresh_charts(self):
        """刷新所有图表"""
        try:
            for chart in self.charts.values():
                chart.update_chart()
            print("图表已刷新")
        except Exception as e:
            print(f"刷新图表失败: {e}")
    
    def export_data(self):
        """导出数据"""
        try:
            from tkinter import filedialog
            
            filepath = filedialog.asksaveasfilename(
                title="导出统计数据",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if filepath:
                export_data = {
                    'daily_stats': self.statistics_data.daily_stats,
                    'total_stats': self.statistics_data.get_total_stats(),
                    'export_time': datetime.datetime.now().isoformat()
                }
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                tk.messagebox.showinfo("导出成功", f"数据已导出到:\n{filepath}")
                
        except Exception as e:
            tk.messagebox.showerror("导出失败", f"导出数据失败:\n{str(e)}")
    
    def clear_data(self):
        """清空数据"""
        if tk.messagebox.askyesno("确认清空", "确定要清空所有统计数据吗？\n此操作无法撤销。"):
            try:
                self.statistics_data.daily_stats = {}
                self.statistics_data.save_data()
                self.refresh_charts()
                tk.messagebox.showinfo("清空成功", "统计数据已清空")
            except Exception as e:
                tk.messagebox.showerror("清空失败", f"清空数据失败:\n{str(e)}")

# 全局统计数据实例
global_statistics = StatisticsData() 