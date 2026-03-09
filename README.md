# TcpSessionBench - TCP连接数限制测试工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

一款用于测试家庭宽带运营商 TCP 连接数限制的 GUI 工具，帮助用户了解网络环境下的并发连接能力。

![Screenshot](https://user-images.githubusercontent.com/placeholder.png)

## 📋 功能特性

- **多会话并发测试** - 支持自定义并发会话数，模拟高并发场景
- **实时统计监控** - 实时显示成功/失败连接数、测试用时
- **智能自动停止** - 达到探测上限或失败次数自动停止并报告结果
- **毫秒级间隔控制** - 精确控制连接发起间隔（毫秒级）
- **完整的日志记录** - 详细记录每次连接的结果和状态
- **跨平台支持** - 基于 Python tkinter，支持 Windows/Linux/macOS
- **单文件可执行** - 可打包为独立 exe，无需 Python 环境即可运行

## 🚀 快速开始

### 方式一：直接运行 Python 脚本

#### 环境要求
- Python 3.8 或更高版本

#### 安装依赖
```bash
# 克隆仓库
git clone https://github.com/coflery/TcpSessionBench.git
cd TcpSessionBench

# 运行脚本（无需额外依赖，使用标准库）
python TcpSessionBench.py
```

### 方式二：使用打包好的可执行文件

从 [Releases](https://github.com/coflery/TcpSessionBench/releases) 页面下载对应平台的可执行文件，双击即可运行。

## 📖 使用说明

### 界面说明

```
┌─────────────────────────────────────────────────────────────┐
│ TCP连接数限制测试工具 V2.0                                   │
├─────────────────────────────────────────────────────────────┤
│ 测试配置                                                    │
│  服务器地址: [223.6.6.6    ]  端口: [53   ]                 │
│  并发会话数: [100         ]个  连接间隔: [100    ]毫秒       │
│  探测上限:  [10000       ]    0=无限制                      │
│  失败停止:  [100         ]    0=不限制                      │
│  连接超时:  [5           ]秒                                │
├─────────────────────────────────────────────────────────────┤
│ [▶ 开始测试]  [⏹ 停止测试]  [🗑 清空日志]                   │
├─────────────────────────────────────────────────────────────┤
│ 实时统计                                                    │
│  状态: 运行中...    成功: 150 (绿色)  失败: 0 (红色)  用时: 15.23s │
├─────────────────────────────────────────────────────────────┤
│ 测试日志                                                    │
│  [10:23:45] [INFO] 开始TCP连接数测试...                     │
│  [10:23:45] [INFO] 参数: 会话数=100, 间隔=100ms...          │
│  [10:23:46] [DEBUG] [1] TCP连接 成功 (用时: 0.05s)          │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

### 参数详解

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **服务器地址** | 223.6.6.6 | 目标测试服务器 IP 或域名 |
| **端口** | 53 | 目标服务端口（DNS常用端口） |
| **并发会话数** | 100 | 同时发起连接的会话数量 |
| **连接间隔** | 100 ms | 每个会话发起连接的间隔时间 |
| **探测上限** | 10000 | 最大连接尝试次数，0=无限制 |
| **失败停止次数** | 100 | 累计失败多少次自动停止，0=不限制 |
| **连接超时** | 5 s | 单次连接超时时间 |

### 测试建议

1. **初次测试**：建议使用默认参数，观察基础连接能力
2. **压力测试**：逐步增加会话数和减少间隔，测试极限
3. **稳定性测试**：设置较大的探测上限，长时间运行观察
4. **阈值判断**：当失败率超过 10% 时，说明可能触发了连接数限制

## 🔧 高级用法

### 自定义测试目标

- **DNS 服务器测试**: `223.6.6.6:53` (阿里DNS) 或 `8.8.8.8:53` (Google DNS)
- **HTTP 服务器测试**: `www.baidu.com:80` 或自定义服务器
- **TCP 服务测试**: 任意支持 TCP 的服务器地址

### 判断连接数限制

当测试过程中出现以下现象时，说明可能触发了运营商或路由器的连接数限制：

- 失败次数突然增加
- 成功率明显下降（低于 90%）
- 出现大量 "连接超时" 或 "拒绝连接" 错误
- 同时正常上网受到影响（网页打不开等）

## 📦 打包发布

### Windows 打包为 EXE

```bash
# 安装 PyInstaller
pip install pyinstaller

# 单文件模式（推荐给用户使用）
pyinstaller --onefile --windowed --name TcpSessionBench TcpSessionBench.py

# 目录模式（启动更快，文件多）
pyinstaller --windowed --name TcpSessionBench TcpSessionBench.py

# 输出目录: dist/
```

### Linux 打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --name TcpSessionBench TcpSessionBench.py
```

### macOS 打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为 app
pyinstaller --windowed --onefile --name TcpSessionBench TcpSessionBench.py
```

## 🛠️ 技术实现

### 核心逻辑

- **多会话并发**: Python `threading` 模块实现高并发连接
- **连接保持**: 成功连接后保持不关闭，模拟真实场景
- **线程安全**: 使用 `threading.Lock` 保护共享数据
- **GUI 框架**: 基于 `tkinter` 的标准跨平台界面

### 项目结构

```
TcpSessionBench/
├── TcpSessionBench.py    # 主程序文件
├── README.md            # 项目说明文档
├── LICENSE              # 开源协议
├── build.bat            # Windows 打包脚本
└── screenshots/         # 截图目录
    └── screenshot.png
```

## ⚠️ 注意事项

1. **网络影响**: 测试会占用网络资源，建议在网络空闲时进行
2. **系统限制**: 操作系统和路由器也有连接数限制，测试结果可能受此限制
3. **合法使用**: 请仅用于测试自己的网络环境，不要对他人服务器进行压力测试
4. **防火墙**: 部分安全软件可能会拦截大量 TCP 连接，必要时添加白名单

## 📝 更新日志

### v2.0 (2024-03-10)
- ✨ 优化默认测试目标为阿里 DNS (223.6.6.6:53)
- ✨ 添加自动停止功能（达到上限自动停止并报告）
- ✨ 连接间隔改为毫秒级，更精确控制
- ✨ 完善日志输出和统计信息
- 🔧 修复连接销毁逻辑

### v1.0 (2024-03-09)
- 🎉 初始版本发布
- ✨ 支持多会话 TCP 连接测试
- ✨ 支持自定义参数配置
- ✨ 实时统计和日志记录

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建新的分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

## 🙏 致谢

- 感谢 Python 社区提供的优秀标准库
- 感谢 PyInstaller 提供的打包工具

---

> ⚡ **提示**: 如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！
