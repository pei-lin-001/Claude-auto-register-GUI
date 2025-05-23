"""
GUI 样式定义

定义应用程序的颜色方案、字体、尺寸等样式配置。
"""

# 颜色方案
COLORS = {
    # 主色调
    'primary': '#2E86AB',
    'primary_light': '#3A96BB',
    'primary_dark': '#246B8A',
    
    # 状态颜色
    'success': '#28A745',
    'warning': '#FFC107',
    'error': '#DC3545',
    'info': '#17A2B8',
    
    # 背景颜色
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F8F9FA',
    'bg_tertiary': '#E9ECEF',
    'bg_dark': '#343A40',
    
    # 文字颜色
    'text_primary': '#212529',
    'text_secondary': '#6C757D',
    'text_muted': '#ADB5BD',
    'text_light': '#FFFFFF',
    
    # 边框颜色
    'border_light': '#DEE2E6',
    'border_medium': '#CED4DA',
    'border_dark': '#6C757D',
}

# 字体配置
FONTS = {
    'default': ('Microsoft YaHei', 9),
    'heading': ('Microsoft YaHei', 12, 'bold'),
    'subheading': ('Microsoft YaHei', 10, 'bold'),
    'small': ('Microsoft YaHei', 8),
    'monospace': ('Consolas', 9),
}

# 尺寸配置
SIZES = {
    # 窗口尺寸
    'window_width': 1200,
    'window_height': 800,
    'window_min_width': 800,
    'window_min_height': 600,
    
    # 间距
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 20,
    
    # 组件尺寸
    'button_height': 32,
    'entry_height': 28,
    'frame_border': 1,
}

# 图标配置
ICONS = {
    'dashboard': '📊',
    'proxy': '🌐',
    'config': '⚙️',
    'batch': '🔄',
    'logs': '📋',
    'help': '❓',
    
    # 状态图标
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '🔄',
    
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
    
    # 网络图标
    'proxy_active': '🟢',
    'proxy_inactive': '🔴',
    'proxy_warning': '🟡',
    'proxy_disabled': '⚪',
    
    # 邮件图标
    'email': '📧',
    'cloudflare': '☁️',
}

# 主题配置
THEMES = {
    'light': {
        'bg': COLORS['bg_primary'],
        'fg': COLORS['text_primary'],
        'select_bg': COLORS['primary'],
        'select_fg': COLORS['text_light'],
    },
    'dark': {
        'bg': COLORS['bg_dark'],
        'fg': COLORS['text_light'],
        'select_bg': COLORS['primary_light'],
        'select_fg': COLORS['text_light'],
    }
}

# 组件样式
STYLES = {
    'frame': {
        'relief': 'solid',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
    },
    'label_frame': {
        'relief': 'groove',
        'borderwidth': 2,
        'background': COLORS['bg_secondary'],
        'font': FONTS['subheading'],
    },
    'button': {
        'relief': 'raised',
        'borderwidth': 1,
        'background': COLORS['primary'],
        'foreground': COLORS['text_light'],
        'font': FONTS['default'],
        'height': 2,
    },
    'entry': {
        'relief': 'sunken',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['default'],
    },
    'text': {
        'relief': 'sunken',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['monospace'],
        'wrap': 'word',
    },
    'listbox': {
        'relief': 'sunken',
        'borderwidth': 1,
        'background': COLORS['bg_primary'],
        'foreground': COLORS['text_primary'],
        'font': FONTS['default'],
        'selectbackground': COLORS['primary'],
        'selectforeground': COLORS['text_light'],
    }
} 