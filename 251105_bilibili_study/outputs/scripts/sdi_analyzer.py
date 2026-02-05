#!/usr/bin/env python3
"""
Script Dependence Index (SDI) Analysis
脚本依赖指数分析系统
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SDIAnalyzer:
    def __init__(self):
        """
        SDI评分维度定义 (1-5分制):
        1. 叙事复杂度 (N): 内容逻辑层次与结构化程度
        2. 信息密度 (I): 单位时间内信息传递量
        3. 口播占比 (V): 语言表达在内容中的重要性
        4. 结构化程度 (S): 分镜/剪辑的规划性要求
        5. 可替代性 (R): 即兴替代的难易程度 (解释性维度)
        """

        # 定义各分区的SDI评分标准
        self.category_sdi_profiles = {
            # 高脚本依赖赛道 (SDI >= 4.0)
            36: {  # 知识
                "category_name": "知识",
                "narrative_complexity": 5,  # 需要清晰的逻辑结构
                "information_density": 5,   # 信息量大，需要精确表达
                "voice_importance": 4,      # 口播解说很重要
                "structure_requirement": 5, # 需要精心规划的分镜
                "replaceability": 5,        # 很难即兴替代
                "reasoning": "知识科普需要严密的逻辑结构、准确的信息传递和清晰的表达，高度依赖脚本规划"
            },
            188: {  # 科技
                "category_name": "科技",
                "narrative_complexity": 4,
                "information_density": 5,
                "voice_importance": 4,
                "structure_requirement": 4,
                "replaceability": 4,
                "reasoning": "科技评测需要专业知识点的准确传达，测试流程的规范化展示"
            },
            181: {  # 影视
                "category_name": "影视",
                "narrative_complexity": 5,
                "information_density": 4,
                "voice_importance": 5,
                "structure_requirement": 4,
                "replaceability": 4,
                "reasoning": "影视解说需要完整的剧情梳理、观点阐述和节奏把控"
            },

            # 中等脚本依赖赛道 (SDI 2.5-4.0)
            3: {   # 音乐
                "category_name": "音乐",
                "narrative_complexity": 2,
                "information_density": 3,
                "voice_importance": 3,
                "structure_requirement": 4,
                "replaceability": 3,
                "reasoning": "音乐创作需要一定的结构规划，但更多依赖创意和技能"
            },
            155: {  # 时尚
                "category_name": "时尚",
                "narrative_complexity": 2,
                "information_density": 3,
                "voice_importance": 3,
                "structure_requirement": 3,
                "replaceability": 2,
                "reasoning": "时尚内容需要搭配思路说明，但可以有较多即兴发挥"
            },
            211: {  # 美食
                "category_name": "美食",
                "narrative_complexity": 3,
                "information_density": 3,
                "voice_importance": 3,
                "structure_requirement": 3,
                "replaceability": 2,
                "reasoning": "美食制作需要步骤说明，但实操性强，可适当即兴调整"
            },
            5: {   # 娱乐
                "category_name": "娱乐",
                "narrative_complexity": 3,
                "information_density": 2,
                "voice_importance": 4,
                "structure_requirement": 2,
                "replaceability": 2,
                "reasoning": "娱乐内容重口播表现力，但内容结构相对简单"
            },
            119: {  # 鬼畜
                "category_name": "鬼畜",
                "narrative_complexity": 4,
                "information_density": 2,
                "voice_importance": 2,
                "structure_requirement": 5,
                "replaceability": 4,
                "reasoning": "鬼畜创作需要精密的剪辑规划和创意设计，但信息传递相对简单"
            },

            # 低脚本依赖赛道 (SDI < 2.5)
            4: {   # 游戏
                "category_name": "游戏",
                "narrative_complexity": 2,
                "information_density": 2,
                "voice_importance": 3,
                "structure_requirement": 2,
                "replaceability": 1,
                "reasoning": "游戏实况更多依赖实时反应和游戏技能，脚本依赖度较低"
            },
            160: {  # 生活
                "category_name": "生活",
                "narrative_complexity": 2,
                "information_density": 2,
                "voice_importance": 2,
                "structure_requirement": 2,
                "replaceability": 1,
                "reasoning": "生活记录类内容更注重真实性和日常性，脚本规划较少"
            },
            217: {  # 动物圈
                "category_name": "动物圈",
                "narrative_complexity": 1,
                "information_density": 2,
                "voice_importance": 2,
                "structure_requirement": 1,
                "replaceability": 1,
                "reasoning": "萌宠内容主要展示动物本身，解说和规划相对简单"
            },
            129: {  # 舞蹈
                "category_name": "舞蹈",
                "narrative_complexity": 1,
                "information_density": 1,
                "voice_importance": 1,
                "structure_requirement": 3,
                "replaceability": 1,
                "reasoning": "舞蹈表演主要依赖技能展示，脚本需求最低"
            }
        }

    def calculate_sdi_scores(self):
        """计算各分区的SDI评分"""
        logger.info("🚀 计算脚本依赖指数(SDI)...")

        sdi_results = []

        for tid, profile in self.category_sdi_profiles.items():
            # 计算SDI分数 (权重相等)
            sdi_score = (
                profile["narrative_complexity"] * 0.25 +
                profile["information_density"] * 0.25 +
                profile["voice_importance"] * 0.25 +
                profile["structure_requirement"] * 0.25
            )

            # 确定依赖程度等级
            if sdi_score >= 4.0:
                dependency_level = "高依赖"
                growth_potential = "高"
            elif sdi_score >= 2.5:
                dependency_level = "中等依赖"
                growth_potential = "中等"
            else:
                dependency_level = "低依赖"
                growth_potential = "低"

            result = {
                "category_tid": tid,
                "category_name": profile["category_name"],
                "narrative_complexity": profile["narrative_complexity"],
                "information_density": profile["information_density"],
                "voice_importance": profile["voice_importance"],
                "structure_requirement": profile["structure_requirement"],
                "replaceability": profile["replaceability"],
                "sdi_score": round(sdi_score, 2),
                "dependency_level": dependency_level,
                "script_growth_potential": growth_potential,
                "reasoning": profile["reasoning"]
            }

            sdi_results.append(result)

        sdi_df = pd.DataFrame(sdi_results)
        sdi_df = sdi_df.sort_values('sdi_score', ascending=False).reset_index(drop=True)

        logger.info(f"✅ SDI计算完成，高脚本依赖赛道: {len(sdi_df[sdi_df['sdi_score'] >= 4.0])} 个")

        return sdi_df

    def analyze_top5_sdi(self, sdi_df, popularity_df):
        """分析Top5热门赛道的脚本依赖情况"""
        logger.info("🚀 分析Top5赛道的脚本依赖度...")

        # 获取Top5热门赛道
        top5_tracks = popularity_df.head(5).copy()

        # 合并SDI数据
        top5_sdi = top5_tracks.merge(
            sdi_df[['category_tid', 'sdi_score', 'dependency_level', 'script_growth_potential', 'reasoning']],
            on='category_tid',
            how='left'
        )

        # 添加脚本提升建议
        def get_script_improvement_advice(row):
            if row['sdi_score'] >= 4.0:
                return {
                    "priority": "高优先级",
                    "advice": "脚本质量直接影响内容效果，建议投入专业编剧或内容策划",
                    "growth_mechanism": "优质脚本→逻辑清晰→用户留存↑→算法推荐↑→粉丝增长"
                }
            elif row['sdi_score'] >= 2.5:
                return {
                    "priority": "中优先级",
                    "advice": "可通过提升脚本结构和信息密度来增强内容竞争力",
                    "growth_mechanism": "脚本优化→内容质量↑→互动率↑→涨粉效率提升"
                }
            else:
                return {
                    "priority": "低优先级",
                    "advice": "脚本提升效果有限，建议重点关注内容创意和表现技巧",
                    "growth_mechanism": "个人魅力和技能>脚本规划，真实性和互动性更重要"
                }

        # 应用建议函数
        advice_data = top5_sdi.apply(get_script_improvement_advice, axis=1)
        top5_sdi['improvement_priority'] = [item['priority'] for item in advice_data]
        top5_sdi['improvement_advice'] = [item['advice'] for item in advice_data]
        top5_sdi['growth_mechanism'] = [item['growth_mechanism'] for item in advice_data]

        return top5_sdi

    def create_case_studies(self, top5_sdi):
        """创建具体案例分析"""
        logger.info("🚀 生成脚本依赖案例分析...")

        case_studies = []

        # 为高SDI分区提供具体案例
        high_sdi_tracks = top5_sdi[top5_sdi['sdi_score'] >= 4.0]

        case_examples = {
            36: {  # 知识
                "success_case": "李永乐老师",
                "case_description": "通过精心设计的教学脚本，将复杂物理概念用通俗语言解释",
                "script_elements": ["清晰的逻辑架构", "层层递进的解释", "恰当的举例说明", "总结归纳"],
                "growth_evidence": "优质脚本内容获得高完播率和转发率，粉丝粘性强"
            },
            188: {  # 科技
                "success_case": "何同学",
                "case_description": "通过精心规划的测试脚本和专业的产品分析框架",
                "script_elements": ["标准化测试流程", "专业术语解释", "对比分析结构", "结论总结"],
                "growth_evidence": "专业的评测脚本建立权威性，吸引品牌合作和用户信任"
            },
            181: {  # 影视
                "success_case": "木鱼水心",
                "case_description": "通过完整的剧情梳理脚本和深度解析",
                "script_elements": ["剧情时间线整理", "角色关系分析", "主题思想挖掘", "个人观点表达"],
                "growth_evidence": "高质量解说脚本提升内容深度，形成独特风格认知"
            }
        }

        for _, row in high_sdi_tracks.iterrows():
            tid = row['category_tid']
            if tid in case_examples:
                case = case_examples[tid].copy()
                case.update({
                    "category_name": row['category_name'],
                    "sdi_score": row['sdi_score'],
                    "popularity_rank": row['rank']
                })
                case_studies.append(case)

        return case_studies

    def generate_comprehensive_analysis(self, output_dir):
        """生成综合分析报告"""
        logger.info("🚀 生成SDI综合分析...")

        # 1. 计算SDI分数
        sdi_df = self.calculate_sdi_scores()

        # 2. 读取热度数据
        popularity_df = pd.read_csv(os.path.join(output_dir, 'popularity_metrics_20251105.csv'))

        # 3. 分析Top5赛道
        top5_sdi = self.analyze_top5_sdi(sdi_df, popularity_df)

        # 4. 生成案例研究
        case_studies = self.create_case_studies(top5_sdi)

        # 5. 保存数据
        timestamp = datetime.now().strftime("%Y%m%d")

        sdi_file = os.path.join(output_dir, '..', 'clean', f'sdi_scores_{timestamp}.csv')
        os.makedirs(os.path.dirname(sdi_file), exist_ok=True)
        sdi_df.to_csv(sdi_file, index=False, encoding='utf-8-sig')

        top5_file = os.path.join(output_dir, '..', 'clean', f'top5_sdi_analysis_{timestamp}.csv')
        top5_sdi.to_csv(top5_file, index=False, encoding='utf-8-sig')

        logger.info(f"💾 SDI分析数据已保存:")
        logger.info(f"   - SDI评分: {sdi_file}")
        logger.info(f"   - Top5分析: {top5_file}")

        return sdi_df, top5_sdi, case_studies

    def create_sdi_report(self, sdi_df, top5_sdi, case_studies, output_dir):
        """生成SDI分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d")
        report_file = os.path.join(output_dir, '..', f'sdi_analysis_report_{timestamp}.md')

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 脚本依赖指数(SDI)分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 核心发现\n\n")
            high_sdi = len(sdi_df[sdi_df['sdi_score'] >= 4.0])
            med_sdi = len(sdi_df[(sdi_df['sdi_score'] >= 2.5) & (sdi_df['sdi_score'] < 4.0)])
            low_sdi = len(sdi_df[sdi_df['sdi_score'] < 2.5])

            f.write(f"- **高脚本依赖赛道** (SDI≥4.0): {high_sdi} 个\n")
            f.write(f"- **中等脚本依赖赛道** (2.5≤SDI<4.0): {med_sdi} 个\n")
            f.write(f"- **低脚本依赖赛道** (SDI<2.5): {low_sdi} 个\n\n")

            f.write("## SDI评分详情\n\n")
            f.write("| 分区 | SDI分数 | 依赖程度 | 叙事复杂度 | 信息密度 | 口播重要性 | 结构化要求 |\n")
            f.write("|------|---------|----------|------------|-----------|------------|------------|\n")

            for _, row in sdi_df.iterrows():
                f.write(f"| {row['category_name']} | {row['sdi_score']} | {row['dependency_level']} | "
                       f"{row['narrative_complexity']} | {row['information_density']} | "
                       f"{row['voice_importance']} | {row['structure_requirement']} |\n")

            f.write("\n## Top5热门赛道的脚本依赖分析\n\n")
            f.write("| 热度排名 | 分区 | SDI分数 | 脚本提升优先级 | 涨粉潜力 |\n")
            f.write("|----------|------|---------|----------------|----------|\n")

            for _, row in top5_sdi.iterrows():
                f.write(f"| {row['rank']} | {row['category_name']} | {row['sdi_score']} | "
                       f"{row['improvement_priority']} | {row['script_growth_potential']} |\n")

            f.write("\n## 脚本提升策略建议\n\n")
            for _, row in top5_sdi.iterrows():
                f.write(f"### {row['category_name']} ({row['dependency_level']})\n")
                f.write(f"**SDI分数**: {row['sdi_score']}/5.0\n\n")
                f.write(f"**提升建议**: {row['improvement_advice']}\n\n")
                f.write(f"**增长机制**: {row['growth_mechanism']}\n\n")
                f.write(f"**分析理由**: {row['reasoning']}\n\n")

            f.write("## 高质量脚本案例分析\n\n")
            for case in case_studies:
                f.write(f"### {case['category_name']}分区 - {case['success_case']}\n\n")
                f.write(f"**案例描述**: {case['case_description']}\n\n")
                f.write("**关键脚本元素**:\n")
                for element in case['script_elements']:
                    f.write(f"- {element}\n")
                f.write(f"\n**增长证据**: {case['growth_evidence']}\n\n")

            f.write("## 结论与建议\n\n")
            f.write("### 核心结论\n")
            f.write("1. **知识、科技、影视**等分区对脚本质量要求最高，脚本优化ROI最大\n")
            f.write("2. **游戏、生活、动物圈**更依赖个人魅力和内容真实性\n")
            f.write("3. **鬼畜**分区虽然SDI适中，但更依赖创意和技术实现\n\n")

            f.write("### 实操建议\n")
            f.write("1. **高SDI赛道创作者**: 投资专业编剧，建立内容规划流程\n")
            f.write("2. **中SDI赛道创作者**: 优化内容结构，提升信息传递效率\n")
            f.write("3. **低SDI赛道创作者**: 重点培养个人特色和用户互动能力\n\n")

            f.write("## 方法论说明\n\n")
            f.write("**SDI计算公式**: SDI = 0.25×叙事复杂度 + 0.25×信息密度 + 0.25×口播重要性 + 0.25×结构化要求\n\n")
            f.write("**评分标准**: 1-5分制，5分表示该维度要求最高\n\n")
            f.write("**依赖程度分级**: \n")
            f.write("- 高依赖 (SDI≥4.0): 脚本质量直接决定内容效果\n")
            f.write("- 中等依赖 (2.5≤SDI<4.0): 脚本优化有明显提升效果\n")
            f.write("- 低依赖 (SDI<2.5): 脚本作用有限，重点在表现力和真实性\n")

        logger.info(f"📊 SDI分析报告已生成: {report_file}")
        return report_file

    def run(self, output_dir):
        """运行完整的SDI分析"""
        logger.info("🚀 开始脚本依赖指数(SDI)分析...")

        # 生成综合分析
        sdi_df, top5_sdi, case_studies = self.generate_comprehensive_analysis(output_dir)

        # 创建分析报告
        report_file = self.create_sdi_report(sdi_df, top5_sdi, case_studies, output_dir)

        logger.info("✅ SDI分析完成!")

        return {
            'sdi_scores': sdi_df,
            'top5_analysis': top5_sdi,
            'case_studies': case_studies,
            'report_file': report_file
        }

if __name__ == "__main__":
    analyzer = SDIAnalyzer()
    output_dir = "../raw"

    results = analyzer.run(output_dir)

    print("\n🎯 SDI分析完成!")
    print(f"📈 高脚本依赖赛道: {len(results['sdi_scores'][results['sdi_scores']['sdi_score'] >= 4.0])} 个")
    print(f"📊 分析报告: {results['report_file']}")