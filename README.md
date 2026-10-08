[English](./README.en.md) | 中文

# TF2 Demo Analyzer
你硬盘里是不是也攒了一堆 TF2 Demo 录像？文件名一串时间戳，看着眼熟，却完全想不起来那局到底谁超神、谁被按在地上摩擦。
> 把一堆躺在硬盘里吃灰的 `.dem` 录像，变成一张看得懂的比赛战报。

一个 TF2（Team Fortress 2）录像分析工具。选择 `.dem` 文件，把里面的比赛数据解析出来，在网页上查看战报。

## ✨ 功能

- 🔍 解析 Demo 录像：基于 [demostf/parser](https://github.com/demostf/parser) 的 Rust 解析器，提取玩家、击杀、职业、武器、回合、聊天等数据
- 💾 数据存进本地 SQLite，之后可以反复查询
- 🧾 用文件 SHA-256 去重，同一份录像不会重复入库
- 🖥️ 桌面界面（Tkinter）选择文件并解析，解析在后台线程进行，界面不会卡
- 📊 网页仪表盘（Flask + Chart.js）展示红蓝双方数据、玩家图表、回合等
- 🗂️ 管理页支持搜索、排序、多选删除历史记录；删除只针对数据库，不影响磁盘上的录像文件
- 🌐 支持中文 / English / 한국어 / 日本語
- 📦 用 PyInstaller 打包成免安装的 exe，目标电脑不需要装 Python 等任何环境

## 🚀 使用

### 直接下载发布版

1. 从 [Releases](https://github.com/TiAmo-ssx/TF2-Demo-Analyzer/releases) 下载 `TF2-Demo-Analyzer-v1.0.0.zip` 并解压。
2. 双击 `TF2-Demo-Analyzer.exe`。
3. 点「添加文件」或「添加文件夹」选择 `.dem` 文件，然后点「开始解析」。
4. 解析完成后会自动打开网页战报，也可以在界面上点「打开分析页面」或「管理比赛」。

### 从源码运行 / 构建

```bash
git clone https://github.com/TiAmo-ssx/TF2-Demo-Analyzer.git
cd TF2-Demo-Analyzer
pip install -r requirements.txt
```

注意：仓库里没有 `parse_demo.exe`（Rust 解析器的二进制文件）。构建前需要先从 Releases 下载它，或者自己编译 Rust 解析器，放到 `resources/parser/parse_demo.exe`。

打包：

```bash
build.bat
```

或者：

```bash
python -m PyInstaller --clean --noconfirm TF2-Demo-Analyzer.spec
```

打包结果在 `dist/TF2-Demo-Analyzer/`。

## 📁 目录结构

```
TF2-Demo-Analyzer/
├── app.py                   # 程序入口
├── config/config.py         # 路径和配置
├── core/                    # 核心逻辑
│   ├── parser.py            #   Rust 解析器封装
│   ├── analyzer.py          #   数据分析
│   ├── database.py          #   SQLite 数据库
│   ├── hash_manager.py      #   SHA-256 去重
│   └── task_manager.py      #   批量任务编排
├── gui/main_window.py       # Tkinter 主界面
├── web/                     # Flask 网页
│   ├── server.py            #   服务器、空闲端口查找
│   ├── routes.py            #   路由
│   ├── templates/           #   模板
│   └── static/              #   CSS / JS / Chart.js
├── utils/i18n.py            # 多语言
├── requirements.txt
├── build.bat                # 打包脚本
└── TF2-Demo-Analyzer.spec   # PyInstaller 配置
```

## 💾 数据存放位置

- 开发环境：项目内的 `workspace/`
- 发布版（exe）：`%LOCALAPPDATA%\TF2-Demo-Analyzer`
- 原dem位置：steamapps\common\Team Fortress 2\tf\demos

数据库放在用户目录而不是 exe 旁边，是为了避免把程序装到 `Program Files` 这类目录时因为权限问题写不了数据。

## ❓ 常见问题

- 删除历史记录会不会删掉录像文件？不会，删除只影响数据库。
- 网页会被别人访问吗？不会，服务器只监听 `127.0.0.1`。
- 端口被占用会怎样？会自动往后找空闲端口。
- 语言设置会保存吗？会。网页用 Cookie，桌面界面用 `settings.json`。

## 🙏 致谢

Demo 解析能力来自 [demostf/parser](https://github.com/demostf/parser)，感谢该项目提供的专门用于TF2 Demo的 Rust 解析库，为本项目增加了更丰富的数据。

## 📄 License
用户可以自由使用、复制、修改、分发和商业使用该软件，但在分发软件或其主要部分时，必须保留原版权声明和许可证文本。\
软件按“现状”提供，作者不对因使用软件产生的问题或损失承担责任。
[MIT](./LICENSE)

## 碎碎念
这个版本可能是最终版了，作者也没什么精力改进升级了😬\
如果有什么问题可以到b站上找到我哦😯\
附上链接🤲https://space.bilibili.com/505994875/
