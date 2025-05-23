"""
GUI 样式定义

定义应用程序的颜色方案、字体、尺寸等样式配置。
采用现代化的Material Design风格。
"""

# 现代化颜色方案 - Material Design 3.0 风格
COLORS = {
    # 主色调 - 现代蓝色渐变
    'primary': '#1976D2',           # Material Blue 700
    'primary_light': '#42A5F5',     # Material Blue 400
    'primary_dark': '#0D47A1',      # Material Blue 900
    'primary_variant': '#1565C0',   # Material Blue 800
    
    # 辅助色调
    'secondary': '#03DAC6',         # Material Teal A400
    'secondary_light': '#4FE6D7',   # Lighter teal
    'secondary_dark': '#018786',    # Material Teal 700
    
    # 状态颜色 - 更柔和的现代配色
    'success': '#4CAF50',           # Material Green 500
    'success_light': '#81C784',     # Material Green 300
    'warning': '#FF9800',           # Material Orange 500
    'warning_light': '#FFB74D',     # Material Orange 300
    'error': '#F44336',             # Material Red 500
    'error_light': '#E57373',       # Material Red 300
    'info': '#2196F3',              # Material Blue 500
    'info_light': '#64B5F6',        # Material Blue 300
    
    # 背景颜色 - 层次化设计
    'bg_primary': '#FFFFFF',        # 纯白背景
    'bg_secondary': '#F8F9FA',      # 极浅灰 - 卡片背景
    'bg_tertiary': '#E3F2FD',       # 浅蓝背景 - 突出区域
    'bg_surface': '#FAFAFA',        # Surface color
    'bg_dark': '#212121',           # Dark surface
    'bg_darker': '#121212',         # Darker surface
    
    # 文字颜色 - 增强对比度
    'text_primary': '#212121',      # 主要文字 - 深灰
    'text_secondary': '#757575',    # 次要文字 - 中灰
    'text_muted': '#BDBDBD',        # 弱化文字 - 浅灰
    'text_light': '#FFFFFF',        # 白色文字
    'text_on_primary': '#FFFFFF',   # 主色上的文字
    'text_hint': '#9E9E9E',         # 提示文字
    
    # 边框颜色 - 精细化
    'border_light': '#E0E0E0',      # 浅边框
    'border_medium': '#BDBDBD',     # 中等边框
    'border_dark': '#757575',       # 深边框
    'border_accent': '#1976D2',     # 强调边框
    
    # 阴影和高度
    'shadow_light': '#E0E0E0',      # 浅阴影
    'shadow_medium': '#BDBDBD',     # 中等阴影
    'shadow_dark': '#757575',       # 深阴影
    
    # 特殊效果色
    'hover': '#F5F5F5',             # 悬停效果
    'pressed': '#EEEEEE',           # 按压效果
    'selected': '#E3F2FD',          # 选中效果
    'focus': '#BBDEFB',             # 焦点效果
}

# 现代化字体配置
FONTS = {
    'default': ('SF Pro Display', 10) if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 10),
    'heading': ('SF Pro Display', 16, 'bold') if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 16, 'bold'),
    'title': ('SF Pro Display', 20, 'bold') if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 20, 'bold'),
    'subheading': ('SF Pro Display', 12, 'bold') if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 12, 'bold'),
    'body': ('SF Pro Text', 10) if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 10),
    'caption': ('SF Pro Text', 9) if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 9),
    'small': ('SF Pro Text', 8) if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 8),
    'monospace': ('SF Mono', 9) if 'darwin' in __import__('sys').platform.lower() else ('Consolas', 9),
    'button': ('SF Pro Display', 10, 'bold') if 'darwin' in __import__('sys').platform.lower() else ('Segoe UI', 10, 'bold'),
}

# 现代化尺寸配置
SIZES = {
    # 窗口尺寸
    'window_width': 1400,
    'window_height': 900,
    'window_min_width': 1000,
    'window_min_height': 700,
    
    # 间距 - 使用8px网格系统
    'padding_xs': 4,
    'padding_small': 8,
    'padding_medium': 16,
    'padding_large': 24,
    'padding_xl': 32,
    
    # 组件尺寸
    'button_height': 36,
    'button_height_small': 28,
    'button_height_large': 44,
    'entry_height': 32,
    'frame_border': 1,
    
    # 圆角半径
    'border_radius_small': 4,
    'border_radius_medium': 8,
    'border_radius_large': 12,
    'border_radius_xl': 16,
    
    # 阴影
    'shadow_elevation_1': 1,
    'shadow_elevation_2': 2,
    'shadow_elevation_3': 4,
    'shadow_elevation_4': 8,
}

# 现代化图标配置 - 使用更统一的emoji风格
ICONS = {
    # 导航图标
    'dashboard': '📊',
    'proxy': '🌐',
    'config': '⚙️',
    'batch': '🔄',
    'logs': '📋',
    'help': '❓',
    
    # 状态图标 - 使用彩色emoji
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳',
    'pending': '⏸️',
    
    # 操作图标
    'start': '🚀',
    'stop': '⏹️',
    'pause': '⏸️',
    'refresh': '🔄',
    'save': '💾',
    'load': '📁',
    'export': '📤',
    'import': '📥',
    'delete': '🗑️',
    'edit': '✏️',
    'test': '🧪',
    'search': '🔍',
    'settings': '🛠️',
    'add': '➕',
    'remove': '➖',
    'close': '✖️',
    'minimize': '➖',
    'maximize': '🔲',
    
    # 网络图标
    'proxy_active': '🟢',
    'proxy_inactive': '🔴',
    'proxy_warning': '🟡',
    'proxy_disabled': '⚪',
    'network_good': '📶',
    'network_poor': '📳',
    
    # 应用图标
    'email': '📧',
    'cloudflare': '☁️',
    'browser': '🌍',
    'account': '👤',
    'security': '🔐',
    'performance': '⚡',
    'chart': '📈',
    'report': '📊',
    'notification': '🔔',
    'star': '⭐',
    'heart': '❤️',
    'thumb_up': '👍',
}

# 现代化主题配置
THEMES = {
    'light': {
        'bg': COLORS['bg_primary'],
        'fg': COLORS['text_primary'],
        'select_bg': COLORS['primary'],
        'select_fg': COLORS['text_on_primary'],
        'hover_bg': COLORS['hover'],
        'focus_bg': COLORS['focus'],
        'border': COLORS['border_light'],
    },
    'dark': {
        'bg': COLORS['bg_dark'],
        'fg': COLORS['text_light'],
        'select_bg': COLORS['primary_light'],
        'select_fg': COLORS['text_on_primary'],
        'hover_bg': '#424242',
        'focus_bg': '#1565C0',
        'border': COLORS['border_dark'],
    }
}

# 现代化组件样式
STYLES = {
    'main_frame': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['bg_secondary'],
    },
    'card_frame': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'highlightbackground': COLORS['border_light'],
        'highlightthickness': 1,
    },
    'label_frame': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['subheading'],
        'labelanchor': 'nw',
    },
    'button_primary': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['primary'],
        'foreground': COLORS['text_on_primary'],
        'font': FONTS['button'],
        'cursor': 'hand2',
        'pady': 8,
        'padx': 16,
    },
    'button_secondary': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['primary'],
        'font': FONTS['button'],
        'cursor': 'hand2',
        'pady': 6,
        'padx': 14,
        'highlightbackground': COLORS['primary'],
        'highlightthickness': 1,
    },
    'button_success': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['success'],
        'foreground': COLORS['text_on_primary'],
        'font': FONTS['button'],
        'cursor': 'hand2',
        'pady': 8,
        'padx': 16,
    },
    'button_warning': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['warning'],
        'foreground': COLORS['text_on_primary'],
        'font': FONTS['button'],
        'cursor': 'hand2',
        'pady': 8,
        'padx': 16,
    },
    'button_danger': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['error'],
        'foreground': COLORS['text_on_primary'],
        'font': FONTS['button'],
        'cursor': 'hand2',
        'pady': 8,
        'padx': 16,
    },
    'entry': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['body'],
        'insertbackground': COLORS['primary'],
        'highlightbackground': COLORS['border_light'],
        'highlightcolor': COLORS['primary'],
        'highlightthickness': 1,
    },
    'text': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['monospace'],
        'wrap': 'word',
        'insertbackground': COLORS['primary'],
        'selectbackground': COLORS['selected'],
        'selectforeground': COLORS['text_primary'],
        'highlightbackground': COLORS['border_light'],
        'highlightcolor': COLORS['primary'],
        'highlightthickness': 1,
    },
    'listbox': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['body'],
        'selectbackground': COLORS['primary'],
        'selectforeground': COLORS['text_on_primary'],
        'highlightbackground': COLORS['border_light'],
        'highlightcolor': COLORS['primary'],
        'highlightthickness': 1,
    },
    'tab_button_active': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['primary'],
        'foreground': COLORS['text_on_primary'],
        'font': FONTS['button'],
        'cursor': 'hand2',
        'pady': 10,
        'padx': 20,
    },
    'tab_button_inactive': {
        'relief': 'flat',
        'borderwidth': 0,
        'background': COLORS['bg_tertiary'],
        'foreground': COLORS['text_secondary'],
        'font': FONTS['body'],
        'cursor': 'hand2',
        'pady': 10,
        'padx': 20,
    },
    'status_bar': {
        'relief': 'flat',
        'borderwidth': 1,
        'background': COLORS['bg_secondary'],
        'highlightbackground': COLORS['border_light'],
        'highlightthickness': 1,
    }
}

# 动画和过渡效果配置
ANIMATIONS = {
    'hover_duration': 150,      # 悬停动画持续时间(ms)
    'click_duration': 100,      # 点击动画持续时间(ms)
    'fade_duration': 300,       # 淡入淡出持续时间(ms)
    'slide_duration': 250,      # 滑动动画持续时间(ms)
}

# 布局网格系统
GRID = {
    'columns': 12,              # 12列网格系统
    'gutter': 16,               # 列间距
    'margin': 24,               # 页面边距
    'container_max_width': 1200, # 容器最大宽度
} 