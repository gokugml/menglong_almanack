#!/usr/bin/env python3
"""
Comprehensive Analysis Report Generator
生成Bilibili创作者与粉丝体量测算综合报告
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BilibiliReportGenerator:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.report_date = datetime.now().strftime('%Y-%m-%d')
        self.timestamp = datetime.now().strftime('%Y%m%d')

    def load_all_data(self):
        """加载所有分析数据"""
        logger.info("📊 加载分析数据...")

        # 加载分区信息
        categories_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'categories_{self.timestamp}.csv'))

        # 加载创作者数据
        creators_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'creators_by_category_{self.timestamp}.csv'))

        # 加载视频数据
        videos_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'videos_by_category_{self.timestamp}.csv'))

        # 加载热度指标
        popularity_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'popularity_metrics_{self.timestamp}.csv'))

        # 加载SDI分析
        sdi_df = pd.read_csv(os.path.join(self.data_dir, 'clean', f'sdi_scores_{self.timestamp}.csv'))
        top5_sdi_df = pd.read_csv(os.path.join(self.data_dir, 'clean', f'top5_sdi_analysis_{self.timestamp}.csv'))

        logger.info("✅ 数据加载完成")

        return {
            'categories': categories_df,
            'creators': creators_df,
            'videos': videos_df,
            'popularity': popularity_df,
            'sdi': sdi_df,
            'top5_sdi': top5_sdi_df
        }

    def calculate_category_rollups(self, creators_df, popularity_df):
        """计算分区汇总指标"""
        logger.info("🔢 计算分区汇总指标...")

        rollups = []

        for tid in creators_df['category_tid'].unique():
            category_creators = creators_df[creators_df['category_tid'] == tid]
            category_name = category_creators.iloc[0]['category_name']

            # 基础指标
            creator_count = len(category_creators)
            total_followers_a = category_creators['followers_count'].sum()  # 口径A：直接累加
            total_followers_b_conservative = int(total_followers_a * 0.7)   # 口径B保守：70%去重
            total_followers_b_aggressive = int(total_followers_a * 0.85)    # 口径B激进：85%去重

            # 分布指标
            avg_followers = int(category_creators['followers_count'].mean())
            median_followers = int(category_creators['followers_count'].median())

            # Top10创作者占比
            top10_followers = category_creators.nlargest(10, 'followers_count')['followers_count'].sum()
            top10_ratio = top10_followers / total_followers_a if total_followers_a > 0 else 0

            # 长尾指标 (P80/P90)
            p80_threshold = category_creators['followers_count'].quantile(0.8)
            p90_threshold = category_creators['followers_count'].quantile(0.9)
            p80_creators = len(category_creators[category_creators['followers_count'] >= p80_threshold])
            p90_creators = len(category_creators[category_creators['followers_count'] >= p90_threshold])

            # 活跃度指标
            avg_videos_12m = category_creators['video_count_12m'].mean()

            # 获取热度排名
            popularity_info = popularity_df[popularity_df['category_tid'] == tid]
            popularity_rank = popularity_info.iloc[0]['rank'] if len(popularity_info) > 0 else 999
            popularity_index = popularity_info.iloc[0]['popularity_index'] if len(popularity_info) > 0 else 0

            rollup = {
                'category_tid': tid,
                'category_name': category_name,
                'creator_count': creator_count,
                'total_followers_a': total_followers_a,
                'total_followers_b_conservative': total_followers_b_conservative,
                'total_followers_b_aggressive': total_followers_b_aggressive,
                'avg_followers': avg_followers,
                'median_followers': median_followers,
                'top10_ratio': round(top10_ratio, 3),
                'p80_creators': p80_creators,
                'p90_creators': p90_creators,
                'avg_videos_12m': round(avg_videos_12m, 1),
                'popularity_rank': popularity_rank,
                'popularity_index': round(popularity_index, 3)
            }

            rollups.append(rollup)

        rollups_df = pd.DataFrame(rollups)

        # 计算占比
        total_creators = rollups_df['creator_count'].sum()
        total_followers_a = rollups_df['total_followers_a'].sum()

        rollups_df['creator_count_pct'] = rollups_df['creator_count'] / total_creators
        rollups_df['followers_a_pct'] = rollups_df['total_followers_a'] / total_followers_a

        # 按创作者数量排序
        rollups_df = rollups_df.sort_values('creator_count', ascending=False).reset_index(drop=True)

        return rollups_df

    def generate_executive_summary(self, data_dict, rollups_df):
        """生成执行摘要"""
        logger.info("📝 生成执行摘要...")

        total_creators = data_dict['creators']['uid'].nunique()
        total_categories = data_dict['categories']['tid'].nunique()
        top5_categories = data_dict['top5_sdi'].head(5)['category_name'].tolist()

        # 核心发现
        findings = [
            f"共统计 {total_categories} 个分区的 {total_creators:,} 名活跃创作者",
            f"Top5热门分区为：{', '.join(top5_categories)}",
            f"高脚本依赖赛道（SDI≥4.0）有 {len(data_dict['sdi'][data_dict['sdi']['sdi_score'] >= 4.0])} 个，脚本优化ROI最高"
        ]

        # 关键建议
        recommendations = [
            "知识、科技类赛道应重点投资内容脚本规划和专业编剧",
            "游戏、生活类赛道应专注个人特色打造和用户互动",
            "建立分区差异化的内容策略，避免一刀切的运营方式"
        ]

        return findings, recommendations

    def create_comprehensive_report(self, data_dict, rollups_df):
        """生成综合报告"""
        logger.info("📖 生成综合分析报告...")

        report_file = os.path.join(self.data_dir, f'report_v1_{self.timestamp}.md')

        findings, recommendations = self.generate_executive_summary(data_dict, rollups_df)

        with open(report_file, 'w', encoding='utf-8') as f:
            # 报告头部
            f.write("# Bilibili 各分区粉丝与创作者体量测算报告 v1\n\n")
            f.write(f"**项目**: Bilibili 各分区粉丝与创作者体量测算 + \"脚本依赖度\"洞察\n")
            f.write(f"**分析时间窗**: 2024-11-01 至 2025-10-31 (滚动近12个月)\n")
            f.write(f"**报告生成日期**: {self.report_date}\n")
            f.write(f"**数据收集日期**: 2025-11-05\n\n")

            # 执行摘要
            f.write("## 📋 执行摘要\n\n")
            f.write("### 核心发现\n")
            for i, finding in enumerate(findings, 1):
                f.write(f"{i}. {finding}\n")
            f.write("\n### 关键建议\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
            f.write("\n")

            # 方法与口径
            f.write("## 🔍 方法与口径\n\n")
            f.write("### 数据来源\n")
            f.write("- **分区信息**: Bilibili开放平台分区体系\n")
            f.write("- **创作者数据**: 模拟数据集（实际项目中从飞瓜数据、火烧云等平台获取）\n")
            f.write("- **热度指标**: 基于播放量、互动率、上榜频次的综合评分\n\n")

            f.write("### 核心定义\n")
            f.write("- **活跃创作者**: 近12个月内发布≥1个视频的UP主\n")
            f.write("- **粉丝总数口径A**: 各分区创作者粉丝数直接累加（存在重复计数）\n")
            f.write("- **粉丝总数口径B**: 基于重叠系数的去重估计（保守70%/激进85%去重）\n")
            f.write("- **爱看程度指数**: Z = 0.5×播放量百分位 + 0.3×互动率百分位 + 0.2×上榜频次百分位\n")
            f.write("- **脚本依赖指数(SDI)**: 基于叙事复杂度、信息密度、口播重要性、结构化要求的综合评分\n\n")

            # 表A：分区层级汇总
            f.write("## 📊 表A：分区层级汇总\n\n")
            f.write("| 分区 | 创作者数 | 占比 | 粉丝总数A | 占比 | 粉丝总数B(保守) | 粉丝总数B(激进) | 平均粉丝 | Top10占比 |\n")
            f.write("|------|----------|------|-----------|------|-----------------|-----------------|----------|----------|\n")

            for _, row in rollups_df.head(15).iterrows():  # 显示前15个分区
                f.write(f"| {row['category_name']} | {row['creator_count']:,} | {row['creator_count_pct']:.1%} | "
                       f"{row['total_followers_a']:,} | {row['followers_a_pct']:.1%} | "
                       f"{row['total_followers_b_conservative']:,} | {row['total_followers_b_aggressive']:,} | "
                       f"{row['avg_followers']:,} | {row['top10_ratio']:.1%} |\n")

            # 汇总统计
            total_creators_all = rollups_df['creator_count'].sum()
            total_followers_a_all = rollups_df['total_followers_a'].sum()
            total_followers_b_cons = rollups_df['total_followers_b_conservative'].sum()
            total_followers_b_aggr = rollups_df['total_followers_b_aggressive'].sum()

            f.write(f"\n**汇总统计**:\n")
            f.write(f"- 总创作者数: {total_creators_all:,} 人\n")
            f.write(f"- 粉丝总数A（累加口径）: {total_followers_a_all:,} 人\n")
            f.write(f"- 粉丝总数B（去重估计）: {total_followers_b_cons:,} - {total_followers_b_aggr:,} 人\n")
            f.write(f"- 去重率估计: 15%-30%\n\n")

            # 表B：Top5赛道爱看程度分析
            f.write("## 🔥 表B：Top5赛道爱看程度分析\n\n")
            top5_popularity = data_dict['popularity'].head(5)

            f.write("| 排名 | 分区 | 爱看指数 | 平均播放量 | 平均互动率 | 热门视频数 | 创作者数 |\n")
            f.write("|------|------|----------|------------|------------|------------|----------|\n")

            for _, row in top5_popularity.iterrows():
                creators_in_cat = len(data_dict['creators'][data_dict['creators']['category_tid'] == row['category_tid']])
                f.write(f"| {row['rank']} | {row['category_name']} | {row['popularity_index']:.3f} | "
                       f"{row['avg_play_count']:,} | {row['avg_interaction_rate']:.2%} | "
                       f"{row['total_hot_videos']} | {creators_in_cat:,} |\n")

            f.write(f"\n**指数说明**: 爱看程度指数综合考虑播放量表现、用户互动积极性和内容上榜频次\n\n")

            # 表C：Top5赛道SDI评分与脚本依赖分析
            f.write("## 🎯 表C：Top5赛道脚本依赖指数(SDI)分析\n\n")

            f.write("### SDI评分详情\n")
            f.write("| 热度排名 | 分区 | SDI分数 | 依赖程度 | 脚本优先级 | 涨粉潜力 |\n")
            f.write("|----------|------|---------|----------|------------|----------|\n")

            for _, row in data_dict['top5_sdi'].iterrows():
                f.write(f"| {row['rank']} | {row['category_name']} | {row['sdi_score']:.2f} | "
                       f"{row['dependency_level']} | {row['improvement_priority']} | {row['script_growth_potential']} |\n")

            f.write("\n### 脚本提升→粉丝增长路径分析\n\n")

            # 高SDI赛道分析
            high_sdi_tracks = data_dict['top5_sdi'][data_dict['top5_sdi']['sdi_score'] >= 4.0]
            if len(high_sdi_tracks) > 0:
                f.write("#### 🎖️ 高脚本依赖赛道 (SDI≥4.0)\n")
                f.write("**特征**: 内容质量高度依赖脚本规划，优质脚本直接影响用户留存和传播\n\n")

                for _, row in high_sdi_tracks.iterrows():
                    f.write(f"**{row['category_name']}分区** (SDI: {row['sdi_score']:.2f})\n")
                    f.write(f"- *增长机制*: {row['growth_mechanism']}\n")
                    f.write(f"- *实操建议*: {row['improvement_advice']}\n\n")

            # 中等SDI赛道分析
            med_sdi_tracks = data_dict['top5_sdi'][(data_dict['top5_sdi']['sdi_score'] >= 2.5) & (data_dict['top5_sdi']['sdi_score'] < 4.0)]
            if len(med_sdi_tracks) > 0:
                f.write("#### 📈 中等脚本依赖赛道 (2.5≤SDI<4.0)\n")
                f.write("**特征**: 脚本优化有明显效果，但不是唯一成功要素\n\n")

                for _, row in med_sdi_tracks.iterrows():
                    f.write(f"**{row['category_name']}分区** (SDI: {row['sdi_score']:.2f})\n")
                    f.write(f"- *增长机制*: {row['growth_mechanism']}\n")
                    f.write(f"- *实操建议*: {row['improvement_advice']}\n\n")

            # 低SDI赛道分析
            low_sdi_tracks = data_dict['top5_sdi'][data_dict['top5_sdi']['sdi_score'] < 2.5]
            if len(low_sdi_tracks) > 0:
                f.write("#### 🎪 低脚本依赖赛道 (SDI<2.5)\n")
                f.write("**特征**: 个人魅力和内容真实性比脚本规划更重要\n\n")

                for _, row in low_sdi_tracks.iterrows():
                    f.write(f"**{row['category_name']}分区** (SDI: {row['sdi_score']:.2f})\n")
                    f.write(f"- *增长机制*: {row['growth_mechanism']}\n")
                    f.write(f"- *实操建议*: {row['improvement_advice']}\n\n")

            # 成功案例
            f.write("### 📚 高质量脚本成功案例\n\n")
            f.write("#### 知识分区 - 李永乐老师\n")
            f.write("- **脚本特色**: 逻辑清晰的教学架构，复杂概念的通俗化表达\n")
            f.write("- **关键要素**: 层层递进的解释逻辑、恰当的举例说明、完整的总结归纳\n")
            f.write("- **增长证据**: 高质量教学脚本带来极高的完播率和转发率，建立强粉丝粘性\n\n")

            f.write("#### 科技分区 - 何同学\n")
            f.write("- **脚本特色**: 标准化测试流程，专业而易懂的产品分析框架\n")
            f.write("- **关键要素**: 结构化测试方法、专业术语科普、客观对比分析\n")
            f.write("- **增长证据**: 专业评测脚本建立行业权威性，吸引品牌合作和用户信任\n\n")

            # 数据局限性
            f.write("## ⚠️ 数据局限性与风险\n\n")
            f.write("### 已知局限\n")
            f.write("1. **样本偏倚**: 第三方平台榜单可能无法完全代表全平台情况\n")
            f.write("2. **时效性**: 粉丝数等指标为抓取时点数据，存在时间差\n")
            f.write("3. **重复计数**: 口径A存在粉丝重复计数，口径B基于估计系数\n")
            f.write("4. **模拟数据**: 本次分析使用模拟数据展示框架，实际项目需真实数据\n\n")

            f.write("### 风险缓解\n")
            f.write("1. **多源验证**: 建议使用多个数据源进行交叉验证\n")
            f.write("2. **敏感性分析**: 对关键参数进行敏感性测试（详见挑战分析）\n")
            f.write("3. **定期更新**: 建立数据更新机制，跟踪趋势变化\n")
            f.write("4. **真实数据**: 实际应用中需获取飞瓜、火烧云等平台的真实数据\n\n")

            # 后续工作
            f.write("## 🔮 后续工作建议\n\n")
            f.write("### 数据深化\n")
            f.write("1. 获取真实的第三方平台数据（飞瓜数据、火烧云等）\n")
            f.write("2. 建立月度/季度的数据更新机制\n")
            f.write("3. 补充创作者内容质量评分数据\n")
            f.write("4. 增加用户画像和观看行为数据\n\n")

            f.write("### 分析拓展\n")
            f.write("1. 建立创作者分级体系（头部/腰部/长尾）\n")
            f.write("2. 分析不同分区的季节性和趋势性特征\n")
            f.write("3. 研究跨分区创作者的表现差异\n")
            f.write("4. 开发预测模型评估创作者增长潜力\n\n")

            f.write("### 应用落地\n")
            f.write("1. 为不同SDI等级的创作者提供定制化成长建议\n")
            f.write("2. 建立内容脚本质量评估工具\n")
            f.write("3. 开发分区选择和内容策略推荐系统\n")
            f.write("4. 设计创作者培训课程和脚本模板\n\n")

            # 技术实现
            f.write("## 🛠️ 技术实现说明\n\n")
            f.write("### 数据处理流程\n")
            f.write("1. **数据收集**: 分区清单 → 创作者数据 → 视频热度数据\n")
            f.write("2. **数据清洗**: 去重、异常值处理、缺失值填充\n")
            f.write("3. **指标计算**: 爱看程度指数、SDI评分、分区汇总统计\n")
            f.write("4. **分析生成**: 综合分析、案例研究、建议输出\n\n")

            f.write("### 可复现性\n")
            f.write("- **运行环境**: Python 3.8+, pandas, requests, numpy\n")
            f.write("- **一键运行**: `bash run.sh` 可完整复现分析流程\n")
            f.write("- **数据标识**: 所有输出数据包含时间戳和来源标识\n")
            f.write("- **版本控制**: 代码和配置文件均在版本控制系统中\n\n")

            # 结语
            f.write("---\n\n")
            f.write("**报告生成**: 🤖 Claude Code自动生成\n\n")
            f.write("**联系方式**: 如需获取原始数据或详细分析，请联系项目团队\n\n")

        logger.info(f"📋 综合报告已生成: {report_file}")
        return report_file

    def create_run_script(self):
        """创建一键运行脚本"""
        run_script = os.path.join(self.data_dir, 'run.sh')

        with open(run_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Bilibili 创作者与粉丝体量测算 - 一键运行脚本\n\n")
            f.write("echo \"🚀 开始Bilibili分析流程...\"\n\n")

            f.write("# 创建虚拟环境\n")
            f.write("if [ ! -d \"venv\" ]; then\n")
            f.write("    echo \"📦 创建Python虚拟环境...\"\n")
            f.write("    python3 -m venv venv\n")
            f.write("fi\n\n")

            f.write("# 激活虚拟环境\n")
            f.write("source venv/bin/activate\n\n")

            f.write("# 安装依赖\n")
            f.write("echo \"📥 安装Python依赖包...\"\n")
            f.write("pip install -r outputs/scripts/requirements.txt\n\n")

            f.write("# 运行分析流程\n")
            f.write("cd outputs/scripts\n\n")
            f.write("echo \"1️⃣ 收集分区信息...\"\n")
            f.write("python bilibili_categories.py\n\n")
            f.write("echo \"2️⃣ 收集创作者数据...\"\n")
            f.write("python creator_scraper.py\n\n")
            f.write("echo \"3️⃣ 分析脚本依赖指数...\"\n")
            f.write("python sdi_analyzer.py\n\n")
            f.write("echo \"4️⃣ 生成综合报告...\"\n")
            f.write("python report_generator.py\n\n")

            f.write("cd ../..\n")
            f.write("echo \"✅ 分析完成! 查看 outputs/ 目录获取结果\"\n")
            f.write("echo \"📋 主报告: outputs/report_v1_$(date +%Y%m%d).md\"\n")

        # 添加执行权限
        os.chmod(run_script, 0o755)
        logger.info(f"🔧 一键运行脚本已创建: {run_script}")

        return run_script

    def run(self):
        """运行报告生成"""
        logger.info("📊 开始生成综合分析报告...")

        # 加载所有数据
        data_dict = self.load_all_data()

        # 计算分区汇总
        rollups_df = self.calculate_category_rollups(data_dict['creators'], data_dict['popularity'])

        # 保存汇总数据
        rollups_file = os.path.join(self.data_dir, 'clean', f'category_rollups_{self.timestamp}.csv')
        rollups_df.to_csv(rollups_file, index=False, encoding='utf-8-sig')
        logger.info(f"💾 分区汇总数据已保存: {rollups_file}")

        # 生成综合报告
        report_file = self.create_comprehensive_report(data_dict, rollups_df)

        # 创建一键运行脚本
        run_script = self.create_run_script()

        logger.info("✅ 报告生成完成!")

        return {
            'report_file': report_file,
            'rollups_file': rollups_file,
            'run_script': run_script
        }

if __name__ == "__main__":
    generator = BilibiliReportGenerator("../")
    results = generator.run()

    print("\n🎉 综合分析报告生成完成!")
    print(f"📋 主报告: {results['report_file']}")
    print(f"📊 汇总数据: {results['rollups_file']}")
    print(f"🔧 运行脚本: {results['run_script']}")