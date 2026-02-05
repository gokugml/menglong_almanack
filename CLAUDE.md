# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个按时间/事件组织的个人项目仓库（almanack = 年鉴），包含数据分析、内容创作和个人反思等多种类型的项目。

## 项目组织规范

### 目录命名规范
- 格式：`YYMMDD_项目名称/`
- 示例：`251105_bilibili_study/`、`260127_mediastorm_100h/`
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

### 2. 内容创作项目（如 260127_mediastorm_100h）

**目录结构**：
```
项目目录/
├── media/                  # 媒体素材和处理工具
│   ├── *.py               # 图像/视频处理脚本
│   ├── venv/              # Python 虚拟环境
│   └── 素材文件夹/
├── !published/            # 已发布的最终内容
├── my_word.md            # 个人创作大纲
├── xiaohongshu_post.md   # 社交媒体发布文案
└── from_*.md             # AI 辅助生成的内容
```

**图像处理工具**（如 subtitle_stitcher.py）：
```bash
cd media
source venv/bin/activate
python subtitle_stitcher.py
# 交互式选择源文件夹和字幕类型
```

## 常用开发命令

### Python 虚拟环境管理
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

### 数据分析项目运行
```bash
# 如果有 run.sh，直接运行
bash outputs/run.sh

# 手动运行单个脚本
cd outputs/scripts
python script_name.py
```

### Git 工作流
```bash
# 项目已忽略：venv/、*.pyc、.DS_Store、*_stitched.png 等
git status
git add .
git commit -m "描述性提交信息"
```

## 技术栈

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
1. **数据获取脚本**（如 `bilibili_categories.py`）：抓取原始数据到 `raw/`
2. **数据清洗脚本**（如 `creator_scraper.py`）：处理数据到 `clean/`
3. **分析脚本**（如 `sdi_analyzer.py`）：计算指标和评分
4. **报告生成脚本**（如 `report_generator.py`）：生成 Markdown 报告

### 图像处理工具的设计模式
- 交互式 CLI 界面
- 自动检测和处理逻辑
- 生成预览和最终拼接图

## 项目主题与内容

该仓库聚焦于：
- B站/影视飓风等内容平台的数据分析
- 内容创作者生态研究
- 社交媒体内容创作（小红书等）
- 个人反思与创业经历记录

## 特殊标记与约定

- `!published/`：表示已发布的最终内容
- `spec_v*.md`：项目规范和需求文档
- `*_stitched.png`：图像处理工具生成的拼接图（已忽略）
- `from_*.md`：AI 工具辅助生成的内容草稿
