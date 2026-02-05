# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个按时间/事件组织的个人项目仓库（almanack = 年鉴），包含数据分析、内容创作和个人反思等多种类型的项目。

## 仓库结构

```
menglong_almanack/
├── projects/              # 所有项目统一存放在此目录
│   ├── YYMMDD_项目名/    # 按日期命名的项目目录
│   └── 描述性项目名/      # 或使用描述性名称
├── subtitle_stitcher.py   # 共享工具：图片字幕拼接工具
├── CLAUDE.md             # Claude Code 工作指南
└── README.md
```

## 项目组织规范

### 目录命名规范
- 所有项目位于 `projects/` 目录下
- 格式：`YYMMDD_项目名称/` 或纯描述性名称
- 示例：`251105_bilibili_study/`、`260127_mediastorm_100h/`、`tedtalk_confidence/`
- 每个项目目录是独立的工作空间

### 文件命名规范
- 输出文件带日期后缀：`filename_YYYYMMDD.csv`
- 生成的报告：`report_v1_YYYYMMDD.md`
- 脚本文件：描述性命名，如 `challenge_analyzer.py`

## 主要项目类型

### 1. 数据分析项目（如 251105_bilibili_study）

**目录结构**：
```
项目目录/
├── venv/                    # Python 虚拟环境
├── outputs/
│   ├── scripts/            # Python 分析脚本
│   ├── raw/                # 原始数据 CSV
│   ├── clean/              # 清洗后的数据 CSV
│   ├── *.md                # 分析报告
│   ├── spec_v1.md          # 项目规范文档
│   └── run.sh              # 一键运行脚本
```

**工作流程**：
```bash
# 设置环境
python3 -m venv venv
source venv/bin/activate
pip install -r outputs/scripts/requirements.txt

# 运行完整流程（如果有 run.sh）
bash outputs/run.sh

# 或手动运行各个脚本
cd outputs/scripts
python script_name.py
```

**数据管理原则**：
- `raw/` 存放原始数据，不修改
- `clean/` 存放处理后的数据
- 所有输出文件带时间戳

### 2. 内容创作项目（如 260127_mediastorm_100h、tedtalk_confidence）

**标准目录结构**：
```
projects/项目目录/
├── source/                # 原始素材（被 gitignore，不提交）
│   └── 素材文件夹/
├── tmp/                   # 临时文件（被 gitignore，不提交）
│   └── *_subtitle_preview/  # 字幕预览文件夹
├── !publish/              # 已发布的最终内容（被 gitignore，不提交）
│   └── *_stitched.png    # 最终拼接图
├── my_word.md            # 个人创作大纲
├── xiaohongshu_post.md   # 社交媒体发布文案
└── from_*.md             # AI 辅助生成的内容（如 from_gpt.md、from_youmind.md）
```

**图像处理工具**（根目录的 subtitle_stitcher.py）：
```bash
# 在项目根目录运行
python subtitle_stitcher.py

# 交互式流程：
# 1. 输入源文件夹路径（如 projects/tedtalk_confidence/source/ted talk）
# 2. 选择字幕类型（中文/英文/中英双语）
# 3. 自动生成 tmp/*_subtitle_preview/ 预览
# 4. 自动生成 !publish/*_stitched.png 最终图
```

## 常用开发命令

### Python 包管理（使用 uv）

**uv 简介**：现代化的 Python 包管理器，速度极快，兼容 pip 生态

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
cd projects/项目名/
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt

# 同步依赖（推荐，更快更准确）
uv pip sync requirements.txt

# 安装单个包
uv pip install package-name

# 在虚拟环境中直接运行脚本（无需手动激活）
uv run python script.py

# 退出虚拟环境
deactivate
```

### 数据分析项目运行
```bash
cd projects/项目名/

# 使用 uv 快速设置环境并运行
uv venv
uv pip install -r outputs/scripts/requirements.txt
uv run python outputs/scripts/script_name.py

# 或者如果有 run.sh，直接运行
bash outputs/run.sh

# 传统方式（激活虚拟环境后）
source .venv/bin/activate
cd outputs/scripts
python script_name.py
```

### 图像处理工具使用
```bash
# 在仓库根目录运行共享工具

# 方式 1：使用 uv run（推荐，自动处理依赖）
uv run --with pillow --with numpy subtitle_stitcher.py

# 方式 2：在虚拟环境中运行
source .venv/bin/activate
python subtitle_stitcher.py

# 输入路径示例：projects/tedtalk_confidence/source/ted talk
```

### Git 工作流和忽略规则
```bash
git status
git add .
git commit -m "描述性提交信息"
```

**重要的 .gitignore 规则**：
- `*tmp*` - 所有包含 tmp 的文件/目录（临时文件）
- `*!publish*` - 所有包含 !publish 的路径（发布文件）
- `*source*` - 所有包含 source 的文件/目录（原始素材）
- `venv/`, `.venv/`, `*.pyc`, `.DS_Store` - Python 虚拟环境和缓存文件
- `*_stitched.png` - 生成的拼接图
- `*_subtitle_preview/` - 字幕预览目录

**注意**：
- 原始素材（source/）、临时文件（tmp/）、发布文件（!publish/）都不会提交到 Git
- uv 默认创建 `.venv/` 目录（已在 .gitignore 中）

## 技术栈

### Python 包管理
- **uv** - 现代化的 Python 包管理器（替代 pip + venv）
  - 极快的安装速度（比 pip 快 10-100 倍）
  - 完全兼容 pip 生态和 requirements.txt
  - 内置虚拟环境管理
  - 使用 `uv run` 可以无需激活环境直接运行

### 数据分析项目
- Python 3.13
- 核心库：pandas, numpy, matplotlib, seaborn, plotly
- 数据获取：requests, beautifulsoup4, lxml
- 数据存储：CSV (openpyxl 用于 Excel)

### 图像处理项目
- Python 3.13
- PIL (Pillow)、numpy
- 支持中英文字幕识别和图片拼接

## 代码架构特点

### 数据分析项目的典型流程
位置：`projects/YYMMDD_项目名/outputs/scripts/`

1. **数据获取脚本**（如 `bilibili_categories.py`）：抓取原始数据到 `raw/`
2. **数据清洗脚本**（如 `creator_scraper.py`）：处理数据到 `clean/`
3. **分析脚本**（如 `sdi_analyzer.py`）：计算指标和评分
4. **报告生成脚本**（如 `report_generator.py`）：生成 Markdown 报告

### 共享工具设计
位置：仓库根目录

**subtitle_stitcher.py** - 图片字幕拼接工具：
- 功能：识别图片中的字幕位置，保留第一张完整画面，其他图片仅保留字幕拼接到底部
- 交互式 CLI 界面
- 支持中文/英文/中英双语字幕识别
- 自动生成预览（`tmp/*_subtitle_preview/`）
- 输出最终拼接图（`!publish/*_stitched.png`）
- 技术：PIL、numpy、图像边缘检测和标准差分析

## 项目主题与内容

该仓库聚焦于：
- B站/影视飓风等内容平台的数据分析
- 内容创作者生态研究
- 社交媒体内容创作（小红书等）
- 个人反思与创业经历记录

## 文件命名与标记约定

### 目录标记
- `source/` - 原始素材目录（不提交）
- `tmp/` - 临时文件目录（不提交）
- `!publish/` - 已发布内容目录（不提交）
- `outputs/` - 数据分析项目的输出目录（提交）
  - `raw/` - 原始数据
  - `clean/` - 清洗后数据
  - `scripts/` - 分析脚本

### 文件标记
- `spec_v*.md` - 项目规范和需求文档
- `*_YYYYMMDD.csv` - 带时间戳的数据文件
- `*_stitched.png` - 生成的拼接图（不提交）
- `*_subtitle_preview/` - 字幕预览目录（不提交）
- `from_*.md` - AI 工具辅助生成的内容草稿（如 `from_gpt.md`、`from_youmind.md`）
- `run.sh` - 项目一键运行脚本

### 项目实例
- `250910_first_found/` - 第一笔融资相关的个人反思
- `251105_bilibili_study/` - B站数据分析项目
- `251115_mediastorm_blind_data_event/` - 影视飓风事件研讨
- `260127_mediastorm_100h/` - 影视飓风100小时直播内容创作
- `tedtalk_confidence/` - TED Talk 相关内容创作
