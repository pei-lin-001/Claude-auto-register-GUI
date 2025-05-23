# 代理管理器使用说明

## 概述

代理管理器是一个智能的代理使用次数管理系统，可以自动跟踪每个代理的使用次数，当代理使用次数达到设定的最大值（默认3次）时，会自动将该代理注释掉，避免过度使用同一个代理。

## 主要功能

1. **自动跟踪代理使用次数**：记录每个代理的使用次数
2. **自动注释耗尽的代理**：当代理使用次数达到限制时自动注释
3. **智能代理选择**：只从未耗尽的代理中选择
4. **统计信息查看**：提供详细的代理使用统计
5. **手动管理功能**：支持重置使用次数、取消注释等操作

## 文件结构

```
├── utils/
│   └── proxy_manager.py      # 代理管理器核心模块
├── proxypool/                # 代理池目录
│   ├── http_ip_port.txt      # HTTP代理 (IP:端口格式)
│   ├── http_user_pass.txt    # HTTP代理 (用户名:密码@IP:端口格式)
│   ├── socks5.txt            # SOCKS5代理 (IP:端口格式)
│   └── socks5_user_pass.txt  # SOCKS5代理 (用户名:密码@IP:端口格式)
├── proxy_usage.json          # 代理使用次数记录文件
├── proxy_cli.py              # 命令行管理工具
└── test_proxy_manager.py     # 测试脚本
```

## 使用方法

### 1. 在主程序中使用

代理管理器已经集成到 `main.py` 中，会自动管理代理使用次数：

```python
from utils.proxy_manager import ProxyManager

# 创建代理管理器实例
proxy_manager = ProxyManager(max_usage_count=3)

# 获取可用代理
proxy_details = proxy_manager.get_available_proxy()

# 记录代理使用
if proxy_details:
    proxy_manager.record_proxy_usage(
        proxy_details["proxy_string"], 
        proxy_details["file_path"]
    )
```

### 2. 使用命令行工具

#### 查看代理统计信息
```bash
python proxy_cli.py stats
```

#### 查看详细使用次数
```bash
python proxy_cli.py usage
```

#### 列出所有代理文件内容
```bash
python proxy_cli.py list
```

#### 重置所有代理使用次数
```bash
python proxy_cli.py reset
```

#### 重置特定代理使用次数
```bash
python proxy_cli.py reset --proxy "192.168.1.100:8080"
```

#### 取消注释特定代理
```bash
python proxy_cli.py uncomment "192.168.1.100:8080"
```

#### 运行测试
```bash
python proxy_cli.py test
```

#### 设置不同的最大使用次数
```bash
python proxy_cli.py --max-usage 5 stats
```

### 3. 运行测试脚本

```bash
python test_proxy_manager.py
```

测试脚本会：
1. 创建测试代理文件
2. 模拟多次使用代理
3. 演示自动注释功能
4. 显示统计信息

## 代理文件格式

### HTTP代理 (IP:端口)
```
192.168.1.100:8080
192.168.1.101:8080
# 192.168.1.102:8080  # 已注释的代理
```

### HTTP代理 (用户名:密码@IP:端口)
```
user1:pass1@192.168.1.100:8080
user2:pass2@192.168.1.101:8080
```

### SOCKS5代理
```
192.168.1.200:1080
192.168.1.201:1080
```

## 工作原理

1. **代理选择**：从代理池中随机选择一个未达到使用次数限制的代理
2. **使用记录**：每次使用代理后，在 `proxy_usage.json` 中记录使用次数
3. **自动注释**：当代理使用次数达到最大值时，在代理文件中添加 `#` 注释符
4. **过滤机制**：读取代理文件时自动过滤掉已注释的代理

## 配置选项

### 最大使用次数
默认为3次，可以在创建 `ProxyManager` 实例时修改：

```python
proxy_manager = ProxyManager(max_usage_count=5)  # 设置为5次
```

### 代理文件路径
默认在 `proxypool/` 目录下，可以通过修改 `ProxyManager` 类的 `proxy_files_map` 属性来自定义。

## 日志记录

代理管理器会记录以下信息：
- 代理选择过程
- 使用次数更新
- 自动注释操作
- 错误信息

日志会输出到控制台和日志文件中。

## 注意事项

1. **备份代理文件**：在使用前建议备份原始代理文件
2. **文件权限**：确保程序有读写代理文件的权限
3. **并发使用**：如果多个程序实例同时运行，可能会出现竞争条件
4. **代理格式**：确保代理文件中的格式正确，每行一个代理

## 故障排除

### 常见问题

1. **代理文件为空**
   - 检查代理文件是否存在且包含有效代理
   - 使用 `proxy_cli.py list` 查看文件内容

2. **所有代理都被注释**
   - 使用 `proxy_cli.py reset` 重置使用次数
   - 使用 `proxy_cli.py uncomment` 取消注释特定代理

3. **使用次数记录丢失**
   - 检查 `proxy_usage.json` 文件是否存在
   - 确保程序有写入权限

### 恢复操作

如果需要恢复所有代理：

```bash
# 重置所有使用次数
python proxy_cli.py reset

# 手动编辑代理文件，移除所有 # 注释符
# 或者从备份文件恢复
```

## 扩展功能

可以根据需要扩展以下功能：
- 代理质量评估
- 自动代理获取
- 代理池动态更新
- 更复杂的使用策略
- Web界面管理

## 示例输出

### 统计信息示例
```
=== 代理统计信息 ===
总代理数量: 5
活跃代理数量: 3
已耗尽代理数量: 2

=== 详细统计 ===
http_ip_port:
  总计: 3 个
  活跃: 1 个
  已注释: 2 个
socks5:
  总计: 2 个
  活跃: 2 个
  已注释: 0 个
```

### 使用次数详情示例
```
=== 代理使用次数详情 ===
192.168.1.100:8080: 3/3 次 (已耗尽)
192.168.1.101:8080: 3/3 次 (已耗尽)
192.168.1.200:1080: 1/3 次 (可用)
192.168.1.201:1080: 0/3 次 (可用)
``` 