#!/usr/bin/env python3
"""
Bilibili Creator Data Collection Script
从第三方平台获取创作者数据样本
"""

import pandas as pd
import requests
import json
import time
import random
from datetime import datetime, timedelta
import os
from urllib.parse import quote, urljoin
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BilibiliCreatorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # 限制抓取频率
        self.request_delay = 2  # 秒
        self.creators_data = []
        self.videos_data = []

    def get_sample_creators_data(self):
        """
        生成模拟的创作者数据样本
        注：在实际项目中，这里应该从飞瓜数据、火烧云等平台抓取真实数据
        """
        logger.info("🚀 生成模拟创作者数据样本...")

        # 读取分区数据
        categories_df = pd.read_csv('../raw/categories_20251105.csv')
        primary_categories = categories_df[categories_df['parent_tid'] == 0]

        # 为每个主要分区生成样本数据
        sample_creators = []

        # 各分区的模拟创作者特征
        category_profiles = {
            1: {"name_prefix": "动画", "avg_followers": 150000, "content_type": "动画创作"},
            3: {"name_prefix": "音乐", "avg_followers": 180000, "content_type": "音乐制作"},
            4: {"name_prefix": "游戏", "avg_followers": 220000, "content_type": "游戏实况"},
            36: {"name_prefix": "知识", "avg_followers": 120000, "content_type": "知识科普"},
            188: {"name_prefix": "科技", "avg_followers": 95000, "content_type": "科技评测"},
            160: {"name_prefix": "生活", "avg_followers": 85000, "content_type": "生活记录"},
            211: {"name_prefix": "美食", "avg_followers": 110000, "content_type": "美食制作"},
            217: {"name_prefix": "动物", "avg_followers": 130000, "content_type": "萌宠分享"},
            119: {"name_prefix": "鬼畜", "avg_followers": 160000, "content_type": "鬼畜创作"},
            155: {"name_prefix": "时尚", "avg_followers": 90000, "content_type": "时尚穿搭"},
            5: {"name_prefix": "娱乐", "avg_followers": 200000, "content_type": "娱乐解说"},
            181: {"name_prefix": "影视", "avg_followers": 140000, "content_type": "影视解说"},
        }

        creator_id = 100000
        for _, category in primary_categories.iterrows():
            tid = category['tid']
            tname = category['tname']

            if tid not in category_profiles:
                continue

            profile = category_profiles[tid]

            # 为每个分区生成50-150个创作者
            num_creators = random.randint(80, 150)

            for i in range(num_creators):
                creator_id += 1

                # 生成粉丝数（对数正态分布）
                base_followers = profile["avg_followers"]
                followers = max(1000, int(random.lognormvariate(11.0, 1.2)))

                # 生成最近投稿时间
                days_ago = random.randint(1, 365)
                last_video_date = datetime.now() - timedelta(days=days_ago)

                # 生成近12个月投稿数量
                video_count_12m = random.randint(1, 200)

                creator = {
                    'uid': creator_id,
                    'username': f"{profile['name_prefix']}UP_{i+1:03d}",
                    'followers_count': followers,
                    'category_tid': tid,
                    'category_name': tname,
                    'last_video_date': last_video_date.strftime('%Y-%m-%d'),
                    'video_count_12m': video_count_12m,
                    'content_type': profile['content_type'],
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': '模拟数据',
                    'data_quality': 'simulated'
                }

                sample_creators.append(creator)

        logger.info(f"✅ 生成了 {len(sample_creators)} 个创作者样本")
        return pd.DataFrame(sample_creators)

    def get_sample_videos_data(self, creators_df):
        """
        生成模拟的热门视频数据
        """
        logger.info("🚀 生成模拟热门视频数据...")

        sample_videos = []
        video_id = 1000000

        # 为每个分区生成热门视频样本
        categories = creators_df['category_tid'].unique()

        for tid in categories:
            category_creators = creators_df[creators_df['category_tid'] == tid]
            category_name = category_creators.iloc[0]['category_name']

            # 每个分区生成30-50个热门视频
            num_videos = random.randint(30, 50)

            for i in range(num_videos):
                video_id += 1

                # 随机选择该分区的一个创作者
                creator = category_creators.sample(1).iloc[0]

                # 生成视频数据
                play_count = random.randint(10000, 5000000)
                like_count = int(play_count * random.uniform(0.02, 0.15))
                coin_count = int(play_count * random.uniform(0.005, 0.03))
                favorite_count = int(play_count * random.uniform(0.008, 0.025))
                share_count = int(play_count * random.uniform(0.001, 0.008))

                # 计算互动率
                interaction_rate = (like_count + coin_count + favorite_count + share_count) / play_count

                # 生成发布时间
                days_ago = random.randint(1, 365)
                publish_date = datetime.now() - timedelta(days=days_ago)

                video = {
                    'bv_id': f"BV{video_id}",
                    'title': f"{category_name}热门视频_{i+1:02d}",
                    'creator_uid': creator['uid'],
                    'creator_name': creator['username'],
                    'category_tid': tid,
                    'category_name': category_name,
                    'play_count': play_count,
                    'like_count': like_count,
                    'coin_count': coin_count,
                    'favorite_count': favorite_count,
                    'share_count': share_count,
                    'interaction_rate': round(interaction_rate, 4),
                    'publish_date': publish_date.strftime('%Y-%m-%d'),
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'source': '模拟数据',
                    'ranking_position': i + 1
                }

                sample_videos.append(video)

        logger.info(f"✅ 生成了 {len(sample_videos)} 个热门视频样本")
        return pd.DataFrame(sample_videos)

    def calculate_popularity_metrics(self, videos_df, creators_df):
        """
        计算各分区的"爱看程度"指标
        """
        logger.info("🚀 计算分区爱看程度指标...")

        # 按分区汇总视频数据
        category_metrics = []

        for tid in videos_df['category_tid'].unique():
            category_videos = videos_df[videos_df['category_tid'] == tid]
            category_name = category_videos.iloc[0]['category_name']

            # 计算各维度指标
            avg_play_count = category_videos['play_count'].mean()
            avg_interaction_rate = category_videos['interaction_rate'].mean()
            total_videos = len(category_videos)

            # 计算百分位数排名（相对于所有分区）
            play_percentile = videos_df[videos_df['category_tid'] == tid]['play_count'].mean()
            interaction_percentile = videos_df[videos_df['category_tid'] == tid]['interaction_rate'].mean()

            metrics = {
                'category_tid': tid,
                'category_name': category_name,
                'avg_play_count': int(avg_play_count),
                'avg_interaction_rate': round(avg_interaction_rate, 4),
                'total_hot_videos': total_videos,
                'play_score': play_percentile,
                'interaction_score': interaction_percentile,
                'ranking_score': total_videos  # 热门视频数量作为上榜频次
            }

            category_metrics.append(metrics)

        metrics_df = pd.DataFrame(category_metrics)

        # 计算百分位排名
        metrics_df['play_percentile'] = metrics_df['play_score'].rank(pct=True)
        metrics_df['interaction_percentile'] = metrics_df['interaction_score'].rank(pct=True)
        metrics_df['ranking_percentile'] = metrics_df['ranking_score'].rank(pct=True)

        # 计算综合爱看指数 Z = 0.5*播放 + 0.3*互动 + 0.2*上榜
        metrics_df['popularity_index'] = (
            0.5 * metrics_df['play_percentile'] +
            0.3 * metrics_df['interaction_percentile'] +
            0.2 * metrics_df['ranking_percentile']
        )

        # 排序并标记Top5
        metrics_df = metrics_df.sort_values('popularity_index', ascending=False).reset_index(drop=True)
        metrics_df['rank'] = range(1, len(metrics_df) + 1)
        metrics_df['is_top5'] = metrics_df['rank'] <= 5

        logger.info(f"✅ 计算完成，Top5热门分区: {list(metrics_df.head(5)['category_name'])}")

        return metrics_df

    def save_all_data(self, creators_df, videos_df, metrics_df, output_dir):
        """保存所有数据"""
        timestamp = datetime.now().strftime("%Y%m%d")

        # 保存创作者数据
        creators_file = os.path.join(output_dir, f"creators_by_category_{timestamp}.csv")
        creators_df.to_csv(creators_file, index=False, encoding='utf-8-sig')

        # 保存视频数据
        videos_file = os.path.join(output_dir, f"videos_by_category_{timestamp}.csv")
        videos_df.to_csv(videos_file, index=False, encoding='utf-8-sig')

        # 保存指标数据
        metrics_file = os.path.join(output_dir, f"popularity_metrics_{timestamp}.csv")
        metrics_df.to_csv(metrics_file, index=False, encoding='utf-8-sig')

        logger.info(f"💾 数据保存完成:")
        logger.info(f"   - 创作者数据: {creators_file}")
        logger.info(f"   - 视频数据: {videos_file}")
        logger.info(f"   - 指标数据: {metrics_file}")

        return {
            'creators_file': creators_file,
            'videos_file': videos_file,
            'metrics_file': metrics_file
        }

    def run(self, output_dir):
        """运行完整的数据收集流程"""
        logger.info("🚀 开始Bilibili创作者数据收集...")

        # 1. 生成创作者数据
        creators_df = self.get_sample_creators_data()

        # 2. 生成视频数据
        videos_df = self.get_sample_videos_data(creators_df)

        # 3. 计算爱看程度指标
        metrics_df = self.calculate_popularity_metrics(videos_df, creators_df)

        # 4. 保存所有数据
        file_paths = self.save_all_data(creators_df, videos_df, metrics_df, output_dir)

        # 5. 生成数据质量报告
        self.generate_quality_report(creators_df, videos_df, metrics_df, output_dir)

        logger.info("✅ 数据收集流程完成!")

        return file_paths, metrics_df

    def generate_quality_report(self, creators_df, videos_df, metrics_df, output_dir):
        """生成数据质量报告"""
        timestamp = datetime.now().strftime("%Y%m%d")
        report_file = os.path.join(output_dir, f"data_quality_report_{timestamp}.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Bilibili 数据收集质量报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 数据概览\n\n")
            f.write(f"- **创作者总数**: {len(creators_df):,} 人\n")
            f.write(f"- **覆盖分区数**: {creators_df['category_tid'].nunique()} 个\n")
            f.write(f"- **热门视频数**: {len(videos_df):,} 个\n")
            f.write(f"- **数据时间范围**: 近12个月\n\n")

            f.write("## 分区分布\n\n")
            f.write("| 分区 | 创作者数量 | 平均粉丝数 | 热门视频数 |\n")
            f.write("|------|------------|------------|------------|\n")

            for tid in sorted(creators_df['category_tid'].unique()):
                category_creators = creators_df[creators_df['category_tid'] == tid]
                category_videos = videos_df[videos_df['category_tid'] == tid]
                category_name = category_creators.iloc[0]['category_name']

                creator_count = len(category_creators)
                avg_followers = int(category_creators['followers_count'].mean())
                video_count = len(category_videos)

                f.write(f"| {category_name} | {creator_count:,} | {avg_followers:,} | {video_count} |\n")

            f.write("\n## Top5 热门分区\n\n")
            top5 = metrics_df.head(5)
            f.write("| 排名 | 分区 | 爱看指数 | 平均播放量 | 平均互动率 |\n")
            f.write("|------|------|----------|------------|------------|\n")

            for _, row in top5.iterrows():
                f.write(f"| {row['rank']} | {row['category_name']} | {row['popularity_index']:.3f} | {row['avg_play_count']:,} | {row['avg_interaction_rate']:.2%} |\n")

            f.write("\n## 数据质量说明\n\n")
            f.write("⚠️ **重要说明**: 本次收集的数据为模拟数据，用于展示分析框架和方法。\n\n")
            f.write("**实际项目中应包含的真实数据源**:\n")
            f.write("- 飞瓜数据B站版的创作者榜单\n")
            f.write("- 火烧云数据的行业分析\n")
            f.write("- B站官方开放平台的部分统计数据\n")
            f.write("- 第三方监测平台的热门视频榜单\n\n")

            f.write("**数据收集建议**:\n")
            f.write("1. 建立多数据源验证机制\n")
            f.write("2. 设置合理的抓取频率避免反爬\n")
            f.write("3. 保留原始数据的时间戳和来源标识\n")
            f.write("4. 定期更新分区映射和创作者状态\n")

        logger.info(f"📊 数据质量报告已生成: {report_file}")

if __name__ == "__main__":
    scraper = BilibiliCreatorScraper()
    output_dir = "../raw"
    os.makedirs(output_dir, exist_ok=True)

    file_paths, metrics_df = scraper.run(output_dir)

    print("\n🎉 数据收集完成! 可以进行下一步分析。")