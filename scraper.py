import feedparser
import csv
from datetime import datetime
import os

# 定義 RSS Feed 網址 (使用正確的 RSS feed URLs)
rss_urls = [
    "https://finance.yahoo.com/rss/headline?s=WELL",  # Yahoo Finance: WELL
    "https://tw.stock.yahoo.com/rss?q=%E6%88%BF%E5%9C%B0%E7%94%A2"  # TW real estate news
]

def fetch_and_save_rss():
    print("開始抓取 RSS feeds...")
    all_entries = []
    
    for url in rss_urls:
        print(f"正在處理: {url}")
        try:
            feed = feedparser.parse(url)
            
            if feed.bozo:
                print(f"解析錯誤: {feed.bozo_exception}")
                continue
                
            print(f"找到 {len(feed.entries)} 筆文章")
            
            for entry in feed.entries:
                # 存入標題、連結和發布時間
                all_entries.append([
                    entry.title if hasattr(entry, 'title') else 'No Title',
                    entry.link if hasattr(entry, 'link') else 'No Link',
                    entry.published if hasattr(entry, 'published') else 'No Date'
                ])
                print(f"標題: {entry.title if hasattr(entry, 'title') else 'No Title'}")
                
        except Exception as e:
            print(f"處理 {url} 時發生錯誤: {str(e)}")

    # 檢查是否有資料要儲存
    if not all_entries:
        print("沒有找到任何文章")
        return

    # 儲存到 CSV 文件
    csv_filename = "rss_feed_data.csv"
    try:
        with open(csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["標題", "連結", "發布時間"])
            writer.writerows(all_entries)
        print(f"成功儲存至 {os.path.abspath(csv_filename)}")
    except Exception as e:
        print(f"儲存 CSV 時發生錯誤: {str(e)}")

print('開始執行...')
fetch_and_save_rss()
print('執行完成')
