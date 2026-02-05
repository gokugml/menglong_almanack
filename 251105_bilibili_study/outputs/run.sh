#!/bin/bash
# Bilibili 创作者与粉丝体量测算 - 一键运行脚本

echo "🚀 开始Bilibili分析流程..."

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装Python依赖包..."
pip install -r outputs/scripts/requirements.txt

# 运行分析流程
cd outputs/scripts

echo "1️⃣ 收集分区信息..."
python bilibili_categories.py

echo "2️⃣ 收集创作者数据..."
python creator_scraper.py

echo "3️⃣ 分析脚本依赖指数..."
python sdi_analyzer.py

echo "4️⃣ 生成综合报告..."
python report_generator.py

cd ../..
echo "✅ 分析完成! 查看 outputs/ 目录获取结果"
echo "📋 主报告: outputs/report_v1_$(date +%Y%m%d).md"
