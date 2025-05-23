# Claude 自动注册工具

## 项目介绍

Claude自动注册工具是一个功能强大的自动化注册系统，支持GUI界面和命令行操作。工具采用现代化设计，集成了无痕模式浏览器、健壮自动化系统、智能代理管理等核心功能。

### 🚀 核心特性

- **🎨 现代化GUI界面**：Material Design 3.0设计，响应式布局
- **🛡️ 无痕模式启动**：保护隐私，提高注册成功率
- **🤖 健壮自动化系统**：多策略元素查找，智能重试机制
- **🌐 智能代理管理**：自动测试、轮换、状态监控
- **📧 临时邮箱创建**：利用Cloudflare API创建临时邮箱
- **📊 实时监控**：注册进度、成功率、系统状态实时显示
- **🔄 批量注册**：支持并发注册，可暂停/恢复操作

## 系统要求

- **Python**: 3.8+ (推荐 3.11)
- **浏览器**: Chrome 最新版本
- **网络**: 稳定的网络连接
- **代理**: 高质量代理IP（重要）

## 🛠️ 安装步骤

### 1. 克隆项目
```bash
git clone https://github.com/your-username/Claude-auto-register-GUI.git
cd Claude-auto-register-GUI
```

### 2. 环境配置
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\Activate.ps1

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate
```

### 3. 安装依赖

#### 方法一：一键安装（推荐）
```bash
python install_dependencies.py
```

#### 方法二：手动安装
```bash
pip install -r requirements.txt
```

### 4. 启动程序

#### GUI界面启动
```bash
python gui_app.py
```

#### 命令行启动
```bash
python main.py
```

## ⚙️ 配置说明

### 1. 邮箱配置
编辑配置文件或在GUI中设置：
```python
# IMAP邮箱设置
imap_server = "imap.qq.com"
mail_address = "your@qq.com"
mail_password = "your-app-password"  # 邮箱授权码
```

### 2. Cloudflare配置
```python
# Cloudflare API设置
zone_identifier = "your-zone-id"
api_key = "your-api-key"
auth_email = "your-cloudflare-email"
rules_domain = "your-domain.com"
```

### 3. 代理配置
将代理添加到 `proxypool/` 目录下的文件中：
- `http_ip_port.txt`: HTTP代理
- `socks5_ip_port.txt`: SOCKS5代理

格式：`ip:port` 每行一个

## 🎯 使用指南

### GUI界面使用

#### 主要功能区域
- **📊 仪表板**: 快速启动、系统状态、统计信息
- **🌐 代理管理**: 添加、测试、管理代理服务器  
- **⚙️ 配置设置**: 邮箱、Cloudflare、浏览器配置
- **🔄 批量注册**: 设置参数、启动批量任务
- **📋 日志查看**: 详细日志、实时更新

#### 首次使用流程
1. 启动GUI: `python gui_app.py`
2. 配置邮箱设置（配置设置页面）
3. 添加代理（代理管理页面）
4. 测试连接和代理
5. 开始注册（仪表板或批量注册页面）

### 命令行使用
```bash
# 单次注册
python main.py

# 带参数启动
python main.py --position 100,200
```

## 🤖 技术特性

### 无痕模式启动
- 默认启用无痕模式，保护隐私
- 每次启动全新浏览器会话
- GUI可配置启用/禁用

### 健壮自动化系统
- **多策略元素查找**: 20+种年龄验证选择器
- **智能点击方法**: 直接点击、JS点击、ActionChains、滚动点击
- **自适应重试**: 失败时自动尝试其他方法
- **页面状态检测**: 确保页面稳定后操作

```python
# 健壮元素查找示例
age_verification_selectors = [
    "//*[@id='age-verification']",
    "//input[@type='checkbox']",
    "//label[contains(text(), '18')]",
    "//form//input[not(@type='email')]"
    # ... 更多选择器
]
```

### 智能代理管理
- 自动测试代理有效性
- 使用次数限制和轮换
- 代理池状态实时监控
- 支持HTTP和SOCKS5代理

## 📊 核心依赖

### 必需依赖
```
selenium>=4.32.0              # Web自动化
undetected-chromedriver>=3.5.5 # 反检测浏览器
requests>=2.32.3              # HTTP请求
beautifulsoup4>=4.12.0        # HTML解析
```

### GUI增强
```
ttkbootstrap>=1.10.1          # 现代化主题
pystray>=0.19.4               # 系统托盘
pillow>=10.0.0                # 图像处理
psutil>=5.9.0                 # 系统监控
```

### 数据处理
```
pandas>=2.0.0                 # 数据分析
openpyxl>=3.1.0              # Excel支持
```

## 📁 项目结构

```
Claude-auto-register-GUI/
├── gui_app.py               # GUI启动入口
├── main.py                  # 命令行入口
├── gui/                     # GUI界面模块
│   ├── main_window.py       # 主窗口
│   ├── components/          # UI组件
│   ├── services/            # 服务层
│   └── resources/           # 样式资源
├── chrome_bot/              # 浏览器自动化
│   ├── insbot.py           # 浏览器控制
│   └── robust_automation.py # 健壮自动化
├── mail/                    # 邮件处理
├── cloudflare/              # Cloudflare API
├── utils/                   # 工具函数
├── proxypool/              # 代理池
├── logs/                   # 日志文件
└── driver/                 # 浏览器驱动
```

## 🔧 高级功能

### 批量注册
```python
# 启动批量注册
service = RegistrationService()
service.start_batch_registration(
    account_count=10,
    concurrent=3,
    interval=5
)
```

### 自定义配置
```python
# 浏览器配置
chrome = bot.createWebView(
    proxy_details=proxy_info,
    incognito=True  # 启用无痕模式
)

# 健壮自动化
automation = create_robust_automation(chrome, logger)
element = automation.find_element_robust(selectors)
```

### 代理管理
```bash
# 代理管理CLI
python proxy_cli.py add proxy_file.txt
python proxy_cli.py test
python proxy_cli.py stats
```

## 📋 输出文件

注册成功后会生成：
- `cookies.json`: Cookie信息
- `sessionKey.txt`: 普通版SessionKey  
- `sessionKey-phone.txt`: 手机版SessionKey
- `logs/`: 详细运行日志

## 🐛 常见问题

### 代理相关
- 确保代理IP质量高且稳定
- 一个IP建议最多注册3-5个账号
- 定期更换代理池

### 邮箱配置
- 使用邮箱授权码，不是登录密码
- 确保IMAP服务已开启
- 检查防火墙设置

### 浏览器问题  
- 确保Chrome版本最新
- ChromeDriver会自动下载
- 如有问题，尝试手动更新Chrome

### 年龄验证超时
- 系统已支持20+种年龄验证选择器
- 如仍超时，可能是网络或页面变化
- 查看日志获取详细错误信息

## 🎨 界面自定义

### 主题修改
编辑 `gui/resources/styles.py`:
```python
COLORS = {
    'primary': '#1976D2',      # 主色调
    'success': '#4CAF50',      # 成功色
    'warning': '#FF9800',      # 警告色
    'error': '#F44336'         # 错误色
}
```

### 响应式设计
- 支持窗口大小自动调整
- 小屏模式优化
- 卡片化布局

## 📈 开发计划

- [x] 现代化GUI界面
- [x] 无痕模式启动
- [x] 健壮自动化系统
- [x] 智能代理管理
- [ ] 深色主题支持
- [ ] 动画效果增强
- [ ] 多语言支持
- [ ] 验证码识别

## ⚠️ 注意事项

- 本工具仅供学习和研究使用
- 请遵守Claude AI的服务条款
- 不要过度频繁注册，避免IP被封
- 代理质量直接影响成功率

## 📄 许可证

[MIT许可证](LICENSE)

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**技术特点总结**:
- ✅ 20+种年龄验证元素选择器，适应页面变化
- ✅ 4种点击策略，确保操作成功
- ✅ 无痕模式默认启用，保护隐私
- ✅ Material Design 3.0现代化界面
- ✅ 实时监控和统计分析
- ✅ 完整的错误处理和日志记录