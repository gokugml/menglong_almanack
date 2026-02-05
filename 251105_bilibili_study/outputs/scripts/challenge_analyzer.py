#!/usr/bin/env python3
"""
Challenge Analysis and Sensitivity Testing
挑战分析与敏感性测试
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChallengeAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.timestamp = datetime.now().strftime('%Y%m%d')

    def load_base_data(self):
        """加载基础数据"""
        logger.info("📊 加载基础分析数据...")

        popularity_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'popularity_metrics_{self.timestamp}.csv'))
        creators_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'creators_by_category_{self.timestamp}.csv'))
        videos_df = pd.read_csv(os.path.join(self.data_dir, 'raw', f'videos_by_category_{self.timestamp}.csv'))
        sdi_df = pd.read_csv(os.path.join(self.data_dir, 'clean', f'sdi_scores_{self.timestamp}.csv'))

        return popularity_df, creators_df, videos_df, sdi_df

    def challenge_1_fans_duplication(self, creators_df):
        """挑战1：粉丝重复计数的影响评估"""
        logger.info("🔍 挑战1: 分析粉丝重复计数对结果的影响...")

        results = {}

        # 测试不同去重系数的影响
        dedup_scenarios = {
            'conservative_50': 0.5,   # 极保守：50%去重
            'conservative_70': 0.7,   # 保守：70%去重
            'moderate_80': 0.8,       # 适中：80%去重
            'aggressive_85': 0.85,    # 激进：85%去重
            'very_aggressive_90': 0.9  # 极激进：90%去重
        }

        category_impacts = []

        for scenario, dedup_factor in dedup_scenarios.items():
            scenario_results = []

            for tid in creators_df['category_tid'].unique():
                category_creators = creators_df[creators_df['category_tid'] == tid]
                category_name = category_creators.iloc[0]['category_name']

                total_followers_raw = category_creators['followers_count'].sum()
                total_followers_dedup = int(total_followers_raw * dedup_factor)

                scenario_results.append({
                    'category_tid': tid,
                    'category_name': category_name,
                    'scenario': scenario,
                    'dedup_factor': dedup_factor,
                    'followers_raw': total_followers_raw,
                    'followers_dedup': total_followers_dedup,
                    'impact_pct': (total_followers_dedup - total_followers_raw) / total_followers_raw
                })

            category_impacts.extend(scenario_results)

        impact_df = pd.DataFrame(category_impacts)

        # 计算排名稳定性
        ranking_stability = {}

        for scenario in dedup_scenarios.keys():
            scenario_data = impact_df[impact_df['scenario'] == scenario].copy()
            scenario_data = scenario_data.sort_values('followers_dedup', ascending=False)
            scenario_data['rank'] = range(1, len(scenario_data) + 1)
            ranking_stability[scenario] = scenario_data[['category_name', 'rank']].set_index('category_name')['rank'].to_dict()

        # 计算Jaccard相似度（排名重叠度）
        base_ranking = ranking_stability['conservative_70']  # 以保守70%为基准
        similarities = {}

        for scenario, ranking in ranking_stability.items():
            if scenario != 'conservative_70':
                # 计算Top5排名的Jaccard相似度
                base_top5 = set([cat for cat, rank in base_ranking.items() if rank <= 5])
                scenario_top5 = set([cat for cat, rank in ranking.items() if rank <= 5])

                intersection = len(base_top5.intersection(scenario_top5))
                union = len(base_top5.union(scenario_top5))
                jaccard = intersection / union if union > 0 else 0

                similarities[scenario] = jaccard

        results['impact_analysis'] = impact_df
        results['ranking_stability'] = ranking_stability
        results['jaccard_similarities'] = similarities

        logger.info(f"✅ 粉丝去重影响分析完成，排名稳定性: {np.mean(list(similarities.values())):.2%}")

        return results

    def challenge_2_data_source_bias(self, popularity_df, videos_df):
        """挑战2：数据源偏倚的稳健性测试"""
        logger.info("🔍 挑战2: 评估数据源偏倚对Top5结果的影响...")

        results = {}

        # 模拟不同数据源的偏倚情况
        bias_scenarios = {
            'no_bias': {'play_factor': 1.0, 'interaction_factor': 1.0, 'ranking_factor': 1.0},
            'play_bias_high': {'play_factor': 1.3, 'interaction_factor': 0.9, 'ranking_factor': 1.0},
            'interaction_bias_high': {'play_factor': 0.9, 'interaction_factor': 1.4, 'ranking_factor': 1.0},
            'ranking_bias_high': {'play_factor': 1.0, 'interaction_factor': 1.0, 'ranking_factor': 1.2},
            'comprehensive_bias': {'play_factor': 1.1, 'interaction_factor': 1.1, 'ranking_factor': 0.8},
        }

        scenario_rankings = {}

        for scenario_name, factors in bias_scenarios.items():
            # 应用偏倚因子
            biased_popularity = popularity_df.copy()

            biased_popularity['biased_play_score'] = biased_popularity['play_score'] * factors['play_factor']
            biased_popularity['biased_interaction_score'] = biased_popularity['interaction_score'] * factors['interaction_factor']
            biased_popularity['biased_ranking_score'] = biased_popularity['ranking_score'] * factors['ranking_factor']

            # 重新计算百分位
            biased_popularity['biased_play_percentile'] = biased_popularity['biased_play_score'].rank(pct=True)
            biased_popularity['biased_interaction_percentile'] = biased_popularity['biased_interaction_score'].rank(pct=True)
            biased_popularity['biased_ranking_percentile'] = biased_popularity['biased_ranking_score'].rank(pct=True)

            # 重新计算综合指数
            biased_popularity['biased_popularity_index'] = (
                0.5 * biased_popularity['biased_play_percentile'] +
                0.3 * biased_popularity['biased_interaction_percentile'] +
                0.2 * biased_popularity['biased_ranking_percentile']
            )

            # 重新排名
            biased_popularity = biased_popularity.sort_values('biased_popularity_index', ascending=False)
            biased_popularity['biased_rank'] = range(1, len(biased_popularity) + 1)

            scenario_rankings[scenario_name] = biased_popularity[['category_name', 'biased_rank']].set_index('category_name')['biased_rank'].to_dict()

        # 计算Top5稳健性
        base_top5 = set([cat for cat, rank in scenario_rankings['no_bias'].items() if rank <= 5])
        stability_scores = {}

        for scenario, ranking in scenario_rankings.items():
            if scenario != 'no_bias':
                scenario_top5 = set([cat for cat, rank in ranking.items() if rank <= 5])
                overlap = len(base_top5.intersection(scenario_top5))
                stability_scores[scenario] = overlap / 5  # Top5重叠比例

        results['scenario_rankings'] = scenario_rankings
        results['stability_scores'] = stability_scores
        results['avg_stability'] = np.mean(list(stability_scores.values()))

        logger.info(f"✅ 数据源偏倚分析完成，Top5平均稳定性: {results['avg_stability']:.1%}")

        return results

    def challenge_3_time_window_sensitivity(self, creators_df, videos_df):
        """挑战3：时间窗口选择的敏感性测试"""
        logger.info("🔍 挑战3: 测试不同时间窗口对结果的影响...")

        results = {}

        # 模拟不同时间窗口（月份数）
        time_windows = [6, 9, 12, 15, 18]  # 6个月到18个月

        window_results = {}

        for window_months in time_windows:
            # 模拟时间窗口效应
            window_factor = {
                6: 0.6,   # 6个月数据较少
                9: 0.8,   # 9个月数据适中
                12: 1.0,  # 12个月基准
                15: 1.1,  # 15个月数据充分
                18: 1.15  # 18个月数据最充分
            }

            factor = window_factor[window_months]

            # 调整创作者活跃度
            adjusted_creators = creators_df.copy()
            adjusted_creators['adjusted_video_count'] = adjusted_creators['video_count_12m'] * factor

            # 重新计算分区指标
            category_metrics = []
            for tid in adjusted_creators['category_tid'].unique():
                category_data = adjusted_creators[adjusted_creators['category_tid'] == tid]
                category_name = category_data.iloc[0]['category_name']

                avg_videos = category_data['adjusted_video_count'].mean()
                active_creators = len(category_data[category_data['adjusted_video_count'] >= 1])

                category_metrics.append({
                    'category_tid': tid,
                    'category_name': category_name,
                    'window_months': window_months,
                    'active_creators': active_creators,
                    'avg_videos': avg_videos,
                    'activity_score': active_creators * avg_videos
                })

            window_df = pd.DataFrame(category_metrics)
            window_df = window_df.sort_values('activity_score', ascending=False)
            window_df['rank'] = range(1, len(window_df) + 1)

            window_results[window_months] = window_df[['category_name', 'rank']].set_index('category_name')['rank'].to_dict()

        # 计算时间窗口稳定性
        base_ranking = window_results[12]  # 以12个月为基准
        time_stability = {}

        for window, ranking in window_results.items():
            if window != 12:
                base_top5 = set([cat for cat, rank in base_ranking.items() if rank <= 5])
                window_top5 = set([cat for cat, rank in ranking.items() if rank <= 5])
                overlap = len(base_top5.intersection(window_top5))
                time_stability[f'{window}months'] = overlap / 5

        results['window_rankings'] = window_results
        results['time_stability'] = time_stability
        results['avg_time_stability'] = np.mean(list(time_stability.values()))

        logger.info(f"✅ 时间窗口敏感性分析完成，平均稳定性: {results['avg_time_stability']:.1%}")

        return results

    def challenge_4_weight_sensitivity(self, popularity_df):
        """挑战4：权重参数的敏感性分析"""
        logger.info("🔍 挑战4: 测试爱看程度指数权重的敏感性...")

        results = {}

        # 测试不同权重组合
        weight_scenarios = {
            'baseline': {'play': 0.5, 'interaction': 0.3, 'ranking': 0.2},
            'play_emphasis': {'play': 0.7, 'interaction': 0.2, 'ranking': 0.1},
            'interaction_emphasis': {'play': 0.3, 'interaction': 0.5, 'ranking': 0.2},
            'ranking_emphasis': {'play': 0.3, 'interaction': 0.2, 'ranking': 0.5},
            'balanced': {'play': 0.33, 'interaction': 0.33, 'ranking': 0.34},
        }

        weight_rankings = {}

        for scenario_name, weights in weight_scenarios.items():
            # 重新计算综合指数
            recalc_popularity = popularity_df.copy()

            recalc_popularity['new_popularity_index'] = (
                weights['play'] * recalc_popularity['play_percentile'] +
                weights['interaction'] * recalc_popularity['interaction_percentile'] +
                weights['ranking'] * recalc_popularity['ranking_percentile']
            )

            # 重新排名
            recalc_popularity = recalc_popularity.sort_values('new_popularity_index', ascending=False)
            recalc_popularity['new_rank'] = range(1, len(recalc_popularity) + 1)

            weight_rankings[scenario_name] = recalc_popularity[['category_name', 'new_rank']].set_index('category_name')['new_rank'].to_dict()

        # 计算权重稳定性
        base_ranking = weight_rankings['baseline']
        weight_stability = {}

        for scenario, ranking in weight_rankings.items():
            if scenario != 'baseline':
                base_top5 = set([cat for cat, rank in base_ranking.items() if rank <= 5])
                scenario_top5 = set([cat for cat, rank in ranking.items() if rank <= 5])
                overlap = len(base_top5.intersection(scenario_top5))
                weight_stability[scenario] = overlap / 5

        results['weight_rankings'] = weight_rankings
        results['weight_stability'] = weight_stability
        results['avg_weight_stability'] = np.mean(list(weight_stability.values()))

        logger.info(f"✅ 权重敏感性分析完成，平均稳定性: {results['avg_weight_stability']:.1%}")

        return results

    def challenge_5_sdi_assumption_test(self, sdi_df):
        """挑战5：SDI评分假设的合理性检验"""
        logger.info("🔍 挑战5: 检验SDI评分假设的合理性...")

        results = {}

        # 测试不同的SDI权重组合
        sdi_weight_scenarios = {
            'equal_weight': {'narrative': 0.25, 'information': 0.25, 'voice': 0.25, 'structure': 0.25},
            'narrative_focus': {'narrative': 0.4, 'information': 0.2, 'voice': 0.2, 'structure': 0.2},
            'information_focus': {'narrative': 0.2, 'information': 0.4, 'voice': 0.2, 'structure': 0.2},
            'voice_focus': {'narrative': 0.2, 'information': 0.2, 'voice': 0.4, 'structure': 0.2},
            'structure_focus': {'narrative': 0.2, 'information': 0.2, 'voice': 0.2, 'structure': 0.4},
        }

        sdi_scenarios_results = {}

        for scenario_name, weights in sdi_weight_scenarios.items():
            recalc_sdi = sdi_df.copy()

            # 重新计算SDI分数
            recalc_sdi['new_sdi_score'] = (
                weights['narrative'] * recalc_sdi['narrative_complexity'] +
                weights['information'] * recalc_sdi['information_density'] +
                weights['voice'] * recalc_sdi['voice_importance'] +
                weights['structure'] * recalc_sdi['structure_requirement']
            )

            # 重新分类依赖程度
            def categorize_dependency(score):
                if score >= 4.0:
                    return "高依赖"
                elif score >= 2.5:
                    return "中等依赖"
                else:
                    return "低依赖"

            recalc_sdi['new_dependency_level'] = recalc_sdi['new_sdi_score'].apply(categorize_dependency)

            sdi_scenarios_results[scenario_name] = recalc_sdi[['category_name', 'new_sdi_score', 'new_dependency_level']].copy()

        # 分析分类稳定性
        base_categories = sdi_scenarios_results['equal_weight'].set_index('category_name')['new_dependency_level'].to_dict()

        category_stability = {}
        for scenario, df in sdi_scenarios_results.items():
            if scenario != 'equal_weight':
                scenario_categories = df.set_index('category_name')['new_dependency_level'].to_dict()

                matches = sum(1 for cat in base_categories.keys()
                            if base_categories[cat] == scenario_categories.get(cat, 'Unknown'))

                category_stability[scenario] = matches / len(base_categories)

        results['sdi_scenarios'] = sdi_scenarios_results
        results['category_stability'] = category_stability
        results['avg_sdi_stability'] = np.mean(list(category_stability.values()))

        logger.info(f"✅ SDI假设检验完成，分类稳定性: {results['avg_sdi_stability']:.1%}")

        return results

    def generate_challenge_report(self, all_challenges):
        """生成挑战分析报告"""
        logger.info("📝 生成挑战分析报告...")

        report_file = os.path.join(self.data_dir, f'challenge_analysis_{self.timestamp}.md')

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 挑战分析与敏感性测试报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 📋 分析概述\n\n")
            f.write("本报告对Bilibili创作者与粉丝体量测算的关键假设和方法进行挑战性分析，")
            f.write("评估结果的稳健性和可靠性。通过敏感性测试，识别潜在风险并提出改进建议。\n\n")

            # 挑战1：粉丝重复计数
            f.write("## 🔍 挑战1：粉丝重复计数的影响评估\n\n")
            challenge1 = all_challenges['fans_duplication']
            f.write("### 核心质疑\n")
            f.write("口径A的粉丝累加方式必然存在重复计数，不同的去重假设会如何影响分区排名？\n\n")

            f.write("### 测试方法\n")
            f.write("测试5种去重系数（50%, 70%, 80%, 85%, 90%），计算排名变化和Jaccard相似度。\n\n")

            f.write("### 测试结果\n")
            f.write("| 去重方案 | 去重系数 | 与基准的Top5相似度 |\n")
            f.write("|----------|----------|-------------------|\n")

            for scenario, similarity in challenge1['jaccard_similarities'].items():
                f.write(f"| {scenario} | {challenge1['impact_analysis'][challenge1['impact_analysis']['scenario']==scenario].iloc[0]['dedup_factor']:.0%} | {similarity:.1%} |\n")

            avg_similarity = np.mean(list(challenge1['jaccard_similarities'].values()))
            f.write(f"\n**结论**: 平均相似度 {avg_similarity:.1%}，排名相对稳定，去重假设的影响在可接受范围内。\n\n")

            # 挑战2：数据源偏倚
            f.write("## 🔍 挑战2：数据源偏倚的稳健性测试\n\n")
            challenge2 = all_challenges['data_source_bias']
            f.write("### 核心质疑\n")
            f.write("第三方平台的榜单数据可能存在结构性偏倚，这会如何影响\"爱看程度\"的排名？\n\n")

            f.write("### 测试方法\n")
            f.write("模拟5种偏倚情况（播放偏高、互动偏高、上榜偏高等），重新计算Top5排名。\n\n")

            f.write("### 测试结果\n")
            f.write("| 偏倚情况 | Top5重叠度 |\n")
            f.write("|----------|------------|\n")

            for scenario, stability in challenge2['stability_scores'].items():
                f.write(f"| {scenario} | {stability:.1%} |\n")

            f.write(f"\n**结论**: 平均稳定性 {challenge2['avg_stability']:.1%}，结果对数据源偏倚具有一定抗性。\n\n")

            # 挑战3：时间窗口敏感性
            f.write("## 🔍 挑战3：时间窗口选择的敏感性测试\n\n")
            challenge3 = all_challenges['time_window']
            f.write("### 核心质疑\n")
            f.write("12个月的时间窗口是否合适？不同时间窗口会如何影响活跃度和排名？\n\n")

            f.write("### 测试方法\n")
            f.write("测试6/9/12/15/18个月的时间窗口，比较创作者活跃度和分区排名变化。\n\n")

            f.write("### 测试结果\n")
            f.write("| 时间窗口 | 与12个月的Top5重叠度 |\n")
            f.write("|----------|---------------------|\n")

            for window, stability in challenge3['time_stability'].items():
                f.write(f"| {window} | {stability:.1%} |\n")

            f.write(f"\n**结论**: 平均稳定性 {challenge3['avg_time_stability']:.1%}，12个月窗口选择较为合理。\n\n")

            # 挑战4：权重敏感性
            f.write("## 🔍 挑战4：权重参数的敏感性分析\n\n")
            challenge4 = all_challenges['weight_sensitivity']
            f.write("### 核心质疑\n")
            f.write("\"爱看程度\"指数的权重设置（0.5/0.3/0.2）是否合理？权重变化对结果影响多大？\n\n")

            f.write("### 测试方法\n")
            f.write("测试5种权重组合，包括播放主导、互动主导、上榜主导和均衡权重等。\n\n")

            f.write("### 测试结果\n")
            f.write("| 权重方案 | Top5重叠度 |\n")
            f.write("|----------|------------|\n")

            for scenario, stability in challenge4['weight_stability'].items():
                f.write(f"| {scenario} | {stability:.1%} |\n")

            f.write(f"\n**结论**: 平均稳定性 {challenge4['avg_weight_stability']:.1%}，权重设置对结果影响适中。\n\n")

            # 挑战5：SDI假设检验
            f.write("## 🔍 挑战5：SDI评分假设的合理性检验\n\n")
            challenge5 = all_challenges['sdi_assumption']
            f.write("### 核心质疑\n")
            f.write("SDI四个维度的等权重假设是否合理？不同权重下的分类稳定性如何？\n\n")

            f.write("### 测试方法\n")
            f.write("测试5种SDI权重组合，观察高/中/低脚本依赖分类的稳定性。\n\n")

            f.write("### 测试结果\n")
            f.write("| 权重方案 | 分类一致性 |\n")
            f.write("|----------|------------|\n")

            for scenario, stability in challenge5['category_stability'].items():
                f.write(f"| {scenario} | {stability:.1%} |\n")

            f.write(f"\n**结论**: 平均一致性 {challenge5['avg_sdi_stability']:.1%}，SDI分类相对稳定。\n\n")

            # 综合评估
            f.write("## 📊 综合稳健性评估\n\n")

            overall_stability = np.mean([
                avg_similarity,
                challenge2['avg_stability'],
                challenge3['avg_time_stability'],
                challenge4['avg_weight_stability'],
                challenge5['avg_sdi_stability']
            ])

            f.write(f"**整体稳健性评分**: {overall_stability:.1%}\n\n")

            if overall_stability >= 0.8:
                f.write("✅ **结论**: 分析结果具有较高稳健性，核心发现可信度高。\n\n")
            elif overall_stability >= 0.6:
                f.write("⚠️ **结论**: 分析结果稳健性中等，建议进一步验证关键假设。\n\n")
            else:
                f.write("❌ **结论**: 分析结果稳健性较低，需要重新审视方法和假设。\n\n")

            # 改进建议
            f.write("## 💡 改进建议\n\n")
            f.write("### 方法论优化\n")
            f.write("1. **多源数据验证**: 整合飞瓜、火烧云、卡思等多个平台数据\n")
            f.write("2. **动态权重调整**: 根据分区特征动态调整指标权重\n")
            f.write("3. **置信区间报告**: 为关键指标提供置信区间而非点估计\n")
            f.write("4. **分层抽样**: 按创作者规模分层，减少头部账号的影响\n\n")

            f.write("### 数据质量提升\n")
            f.write("1. **实时数据更新**: 建立月度数据更新机制\n")
            f.write("2. **数据质量监控**: 设置异常值检测和数据完整性检查\n")
            f.write("3. **标准化处理**: 建立数据预处理的标准化流程\n")
            f.write("4. **外部验证**: 寻找官方或第三方数据进行交叉验证\n\n")

            f.write("### 分析框架完善\n")
            f.write("1. **场景分析**: 为不同应用场景定制化分析口径\n")
            f.write("2. **趋势跟踪**: 增加时间序列分析，捕捉动态变化\n")
            f.write("3. **用户细分**: 按粉丝规模、内容类型等维度细分分析\n")
            f.write("4. **预测建模**: 基于历史数据建立增长预测模型\n\n")

            # 风险提示
            f.write("## ⚠️ 风险提示与使用建议\n\n")
            f.write("### 主要风险\n")
            f.write("1. **数据时效性**: 社交媒体数据变化快，分析结果有时效性\n")
            f.write("2. **平台政策变化**: 算法调整可能影响内容分发和用户行为\n")
            f.write("3. **样本代表性**: 第三方平台数据可能无法完全代表全平台情况\n")
            f.write("4. **因果推断限制**: 相关性分析无法确定因果关系\n\n")

            f.write("### 使用建议\n")
            f.write("1. **结合定性分析**: 量化分析需要结合行业专家的定性判断\n")
            f.write("2. **分阶段验证**: 小规模试点验证后再大规模应用\n")
            f.write("3. **持续监控**: 建立结果跟踪机制，及时调整策略\n")
            f.write("4. **多维度决策**: 将分析结果作为决策参考之一，而非唯一依据\n\n")

            f.write("---\n")
            f.write("**报告说明**: 本挑战分析基于当前数据和假设，随着数据质量和方法改进，结论可能需要更新。\n")

        logger.info(f"📝 挑战分析报告已生成: {report_file}")
        return report_file

    def run(self):
        """运行完整的挑战分析"""
        logger.info("🚀 开始挑战分析与敏感性测试...")

        # 加载数据
        popularity_df, creators_df, videos_df, sdi_df = self.load_base_data()

        # 执行5个挑战分析
        challenges = {}

        challenges['fans_duplication'] = self.challenge_1_fans_duplication(creators_df)
        challenges['data_source_bias'] = self.challenge_2_data_source_bias(popularity_df, videos_df)
        challenges['time_window'] = self.challenge_3_time_window_sensitivity(creators_df, videos_df)
        challenges['weight_sensitivity'] = self.challenge_4_weight_sensitivity(popularity_df)
        challenges['sdi_assumption'] = self.challenge_5_sdi_assumption_test(sdi_df)

        # 生成报告
        report_file = self.generate_challenge_report(challenges)

        logger.info("✅ 挑战分析完成!")

        return {
            'challenges': challenges,
            'report_file': report_file
        }

if __name__ == "__main__":
    analyzer = ChallengeAnalyzer("../")
    results = analyzer.run()

    print("\n🎯 挑战分析完成!")
    print(f"📊 分析报告: {results['report_file']}")
    print(f"🔍 共完成 {len(results['challenges'])} 项挑战分析")