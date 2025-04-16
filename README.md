# Claude 自动注册工具

## 项目介绍

本工具用于自动化 Claude AI 账号的注册过程，通过使用代理IP和临时邮箱实现批量注册。工具的主要功能包括：

- 利用 Cloudflare 创建临时邮箱
- 自动填写注册表单
- 接收并处理验证邮件
- 自动完成注册流程
- 保存 Cookie 和 SessionKey 信息

## 系统要求

- Python 3.8 或更高版本
- Chrome 浏览器
- 稳定的网络连接
- 高质量代理IP（重要）

## 安装步骤

1. 克隆本项目到本地

```bash
git clone https://github.com/your-username/Claude-auto-register.git
cd Claude-auto-register
```

2. 创建并激活虚拟环境

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 代理IP配置

将代理IP列表添加到 `Proxy.txt` 文件中，每行一个IP地址，格式如下：

```
ip:port
```

**注意**：IP质量要求极高，一个高质量IP仅可注册3-5个账号

### 2. 配置邮箱和Cloudflare

编辑 `utils/config.py` 文件或创建一个新的 `.env` 文件，设置以下参数：

```python
# 邮箱设置
mail_address = "youremail@example.com"  # 接收验证码的邮箱
mail_password = "your-mail-password"  # 邮箱IMAP密码（不是登录密码）
imap_server = "imap.example.com"  # IMAP服务器地址

# Cloudflare设置
rules_domain = "your-domain.com"  # 自定义域名后缀
zone_identifier = "your-zone-id"  # Cloudflare区域ID
api_key = "your-api-key"  # Cloudflare API密钥
auth_email = "your-cloudflare-email"  # Cloudflare账户邮箱
```

### 3. 浏览器驱动（非必要）

确保已安装与Chrome浏览器版本兼容的ChromeDriver，并添加到系统PATH或项目的driver目录中。

## 使用方法

1. 确保所有配置正确设置

2. 运行主程序

```bash
python main.py
```

3. 程序将自动:
   - 创建临时邮箱
   - 打开Chrome浏览器访问Claude注册页面
   - 填写注册表单
   - 接收验证邮件并完成注册
   - 保存Cookie和SessionKey信息

## 运行参数

主程序支持以下命令行参数：

```bash
python main.py --position 100,200  # 设置浏览器窗口位置
```

## 输出文件

成功注册后，程序会生成以下文件：

- `cookies.json`: 包含所有Cookie信息
- `sessionKey.txt`: 普通版本的SessionKey
- `sessionKey-phone.txt`: 手机版本的SessionKey（如果检测到）
- `logs/yyyy-mm-dd_HH-MM-SS.log`: 运行日志

## 常见问题解决

1. **代理IP问题**
   - 确保代理IP质量高且稳定
   - 一个IP使用次数有限，建议定期更换

2. **邮箱验证失败**
   - 检查邮箱配置是否正确
   - 确保IMAP服务已开启
   - 检查邮箱密码是否为应用专用密码

3. **浏览器自动化问题**
   - 确保ChromeDriver版本与Chrome浏览器版本兼容
   - 尝试更新Chrome和ChromeDriver到最新版本

4. **Cloudflare配置错误**
   - 验证Cloudflare API密钥和区域ID是否正确
   - 确保域名配置正确并已激活

## 注意事项

- 本工具仅供学习和研究使用
- 请遵守Claude AI的服务条款
- 不要过度频繁地注册账号，以避免IP被封

## 高级用法

### 定制浏览器配置

修改 `chrome_bot/insbot.py` 中的 `create_web_view` 函数来自定义浏览器设置。

### 自定义注册流程

修改 `main.py` 中的 `startMain` 函数来自定义注册流程中的步骤和逻辑。

### 批量注册

可以创建一个简单的脚本来多次调用主程序，实现批量注册：

```python
import subprocess
import time

for i in range(5):  # 注册5个账号
    subprocess.run(["python", "main.py"])
    time.sleep(60)  # 等待1分钟再次运行
```

## 项目结构

```
Claude-auto-register/
├── main.py              # 主程序
├── Proxy.txt            # 代理IP列表
├── .env                 # 环境变量配置
├── README.md            # 使用文档
├── utils/               # 工具函数
│   ├── config.py        # 配置管理
│   └── cookie_utils.py  # Cookie工具
├── mail/                # 邮件处理模块
├── cloudflare/          # Cloudflare API模块
├── chrome_bot/          # 浏览器自动化模块
├── driver/              # 浏览器驱动
├── logs/                # 日志目录
└── examples/            # 示例和测试
```

## 开发计划

- [ ] 添加更多邮箱服务提供商支持
- [ ] 优化代理IP管理
- [ ] 添加图形用户界面
- [ ] 增加验证码识别功能
- [ ] 支持更多注册选项

## 贡献

欢迎提交问题和代码改进。请确保遵循项目的代码风格和贡献指南。

## 许可证

[MIT许可证](LICENSE)