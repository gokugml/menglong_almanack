#!/usr/bin/env python3
"""
Bilibili Categories Data Collection Script
获取B站分区信息并创建分区映射表
"""

import pandas as pd
import requests
import json
from datetime import datetime
import time
import os

class BilibiliCategoryCollector:
    def __init__(self):
        self.categories = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_manual_categories(self):
        """
        手动整理的B站分区信息 (基于GitHub社区文档)
        """
        categories_data = [
            # 一级分区
            {"tid": 1, "tname": "动画", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 13, "tname": "番剧", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 167, "tname": "国创", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 3, "tname": "音乐", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 129, "tname": "舞蹈", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 4, "tname": "游戏", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 36, "tname": "知识", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 188, "tname": "科技", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 160, "tname": "生活", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 211, "tname": "美食", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 217, "tname": "动物圈", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 119, "tname": "鬼畜", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 155, "tname": "时尚", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 5, "tname": "娱乐", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 181, "tname": "影视", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 177, "tname": "纪录片", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 23, "tname": "电影", "parent_tid": 0, "parent_name": "根分区"},
            {"tid": 11, "tname": "电视剧", "parent_tid": 0, "parent_name": "根分区"},

            # 二级分区 - 动画
            {"tid": 24, "tname": "MAD·AMV", "parent_tid": 1, "parent_name": "动画"},
            {"tid": 25, "tname": "MMD·3D", "parent_tid": 1, "parent_name": "动画"},
            {"tid": 47, "tname": "短片·手书·配音", "parent_tid": 1, "parent_name": "动画"},
            {"tid": 86, "tname": "特摄", "parent_tid": 1, "parent_name": "动画"},
            {"tid": 27, "tname": "综合", "parent_tid": 1, "parent_name": "动画"},

            # 二级分区 - 音乐
            {"tid": 28, "tname": "原创音乐", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 31, "tname": "翻唱", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 30, "tname": "VOCALOID·UTAU", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 194, "tname": "电音", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 59, "tname": "演奏", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 193, "tname": "MV", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 29, "tname": "音乐现场", "parent_tid": 3, "parent_name": "音乐"},
            {"tid": 130, "tname": "音乐综合", "parent_tid": 3, "parent_name": "音乐"},

            # 二级分区 - 舞蹈
            {"tid": 20, "tname": "宅舞", "parent_tid": 129, "parent_name": "舞蹈"},
            {"tid": 154, "tname": "街舞", "parent_tid": 129, "parent_name": "舞蹈"},
            {"tid": 156, "tname": "明星舞蹈", "parent_tid": 129, "parent_name": "舞蹈"},
            {"tid": 198, "tname": "中国舞", "parent_tid": 129, "parent_name": "舞蹈"},
            {"tid": 199, "tname": "舞蹈综合", "parent_tid": 129, "parent_name": "舞蹈"},
            {"tid": 200, "tname": "舞蹈教学", "parent_tid": 129, "parent_name": "舞蹈"},

            # 二级分区 - 游戏
            {"tid": 17, "tname": "单机游戏", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 171, "tname": "电子竞技", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 172, "tname": "手机游戏", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 65, "tname": "网络游戏", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 173, "tname": "桌游棋牌", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 121, "tname": "GMV", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 136, "tname": "音游", "parent_tid": 4, "parent_name": "游戏"},
            {"tid": 19, "tname": "Mugen", "parent_tid": 4, "parent_name": "游戏"},

            # 二级分区 - 知识
            {"tid": 201, "tname": "科学科普", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 202, "tname": "社科·法律·心理", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 203, "tname": "人文历史", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 204, "tname": "财经商业", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 205, "tname": "校园学习", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 206, "tname": "职业职场", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 207, "tname": "设计·创意", "parent_tid": 36, "parent_name": "知识"},
            {"tid": 208, "tname": "野生技能协会", "parent_tid": 36, "parent_name": "知识"},

            # 二级分区 - 科技
            {"tid": 95, "tname": "数码", "parent_tid": 188, "parent_name": "科技"},
            {"tid": 230, "tname": "软件应用", "parent_tid": 188, "parent_name": "科技"},
            {"tid": 231, "tname": "计算机技术", "parent_tid": 188, "parent_name": "科技"},
            {"tid": 232, "tname": "科工机械", "parent_tid": 188, "parent_name": "科技"},
            {"tid": 233, "tname": "极客DIY", "parent_tid": 188, "parent_name": "科技"},

            # 二级分区 - 生活
            {"tid": 138, "tname": "搞笑", "parent_tid": 160, "parent_name": "生活"},
            {"tid": 21, "tname": "日常", "parent_tid": 160, "parent_name": "生活"},
            {"tid": 161, "tname": "手工", "parent_tid": 160, "parent_name": "生活"},
            {"tid": 162, "tname": "绘画", "parent_tid": 160, "parent_name": "生活"},
            {"tid": 163, "tname": "理容整形", "parent_tid": 160, "parent_name": "生活"},
            {"tid": 174, "tname": "运动", "parent_tid": 160, "parent_name": "生活"},
            {"tid": 175, "tname": "其他", "parent_tid": 160, "parent_name": "生活"},

            # 二级分区 - 美食
            {"tid": 76, "tname": "美食制作", "parent_tid": 211, "parent_name": "美食"},
            {"tid": 212, "tname": "美食侦探", "parent_tid": 211, "parent_name": "美食"},
            {"tid": 213, "tname": "美食测评", "parent_tid": 211, "parent_name": "美食"},
            {"tid": 214, "tname": "田园美食", "parent_tid": 211, "parent_name": "美食"},
            {"tid": 215, "tname": "美食记录", "parent_tid": 211, "parent_name": "美食"},

            # 二级分区 - 动物圈
            {"tid": 218, "tname": "喵星人", "parent_tid": 217, "parent_name": "动物圈"},
            {"tid": 219, "tname": "汪星人", "parent_tid": 217, "parent_name": "动物圈"},
            {"tid": 220, "tname": "大熊猫", "parent_tid": 217, "parent_name": "动物圈"},
            {"tid": 221, "tname": "野生动物", "parent_tid": 217, "parent_name": "动物圈"},
            {"tid": 222, "tname": "爬宠", "parent_tid": 217, "parent_name": "动物圈"},
            {"tid": 75, "tname": "动物综合", "parent_tid": 217, "parent_name": "动物圈"},

            # 二级分区 - 鬼畜
            {"tid": 22, "tname": "鬼畜调教", "parent_tid": 119, "parent_name": "鬼畜"},
            {"tid": 26, "tname": "音MAD", "parent_tid": 119, "parent_name": "鬼畜"},
            {"tid": 126, "tname": "人力VOCALOID", "parent_tid": 119, "parent_name": "鬼畜"},
            {"tid": 216, "tname": "鬼畜剧场", "parent_tid": 119, "parent_name": "鬼畜"},
            {"tid": 127, "tname": "教程演示", "parent_tid": 119, "parent_name": "鬼畜"},

            # 二级分区 - 时尚
            {"tid": 157, "tname": "美妆护肤", "parent_tid": 155, "parent_name": "时尚"},
            {"tid": 158, "tname": "仿妆cos", "parent_tid": 155, "parent_name": "时尚"},
            {"tid": 159, "tname": "穿搭", "parent_tid": 155, "parent_name": "时尚"},
            {"tid": 164, "tname": "时尚潮流", "parent_tid": 155, "parent_name": "时尚"},

            # 二级分区 - 娱乐
            {"tid": 71, "tname": "综艺", "parent_tid": 5, "parent_name": "娱乐"},
            {"tid": 241, "tname": "娱乐杂谈", "parent_tid": 5, "parent_name": "娱乐"},
            {"tid": 242, "tname": "粉丝创作", "parent_tid": 5, "parent_name": "娱乐"},
            {"tid": 137, "tname": "明星综合", "parent_tid": 5, "parent_name": "娱乐"},
        ]

        return pd.DataFrame(categories_data)

    def save_categories(self, df, output_dir):
        """保存分区数据"""
        timestamp = datetime.now().strftime("%Y%m%d")

        # 保存完整分区列表
        categories_file = os.path.join(output_dir, f"categories_{timestamp}.csv")
        df.to_csv(categories_file, index=False, encoding='utf-8-sig')

        # 创建分区层级分析
        primary_categories = df[df['parent_tid'] == 0]
        secondary_categories = df[df['parent_tid'] != 0]

        print(f"✅ 获取到分区信息:")
        print(f"   - 一级分区: {len(primary_categories)} 个")
        print(f"   - 二级分区: {len(secondary_categories)} 个")
        print(f"   - 总计: {len(df)} 个分区")
        print(f"   - 保存到: {categories_file}")

        return categories_file

    def run(self, output_dir):
        """运行分区信息收集"""
        print("🚀 开始收集B站分区信息...")

        # 获取分区数据
        categories_df = self.get_manual_categories()

        # 保存数据
        categories_file = self.save_categories(categories_df, output_dir)

        # 创建统计报告
        self.create_category_report(categories_df, output_dir)

        return categories_file

    def create_category_report(self, df, output_dir):
        """创建分区统计报告"""
        timestamp = datetime.now().strftime("%Y%m%d")
        report_file = os.path.join(output_dir, f"category_report_{timestamp}.md")

        primary_categories = df[df['parent_tid'] == 0].sort_values('tid')

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Bilibili 分区统计报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 一级分区概览\n\n")
            f.write("| TID | 分区名称 | 二级分区数量 |\n")
            f.write("|-----|----------|-------------|\n")

            for _, category in primary_categories.iterrows():
                sub_count = len(df[df['parent_tid'] == category['tid']])
                f.write(f"| {category['tid']} | {category['tname']} | {sub_count} |\n")

            f.write(f"\n**总计**: {len(primary_categories)} 个一级分区，{len(df[df['parent_tid'] != 0])} 个二级分区\n")

        print(f"📊 分区报告已生成: {report_file}")

if __name__ == "__main__":
    collector = BilibiliCategoryCollector()
    output_dir = "../raw"
    os.makedirs(output_dir, exist_ok=True)
    collector.run(output_dir)