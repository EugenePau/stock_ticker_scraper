import pandas as pd
import requests
import re
import time
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime

# 設定字體
zhfont = fm.FontProperties(fname=r'C:\Windows\Fonts\kaiu.ttf')  # 使用原始字串
plt.rcParams['font.family'] = zhfont.get_name()

# 定義下載資料的函數
def fetch_data(date, stock_no):
    url = f'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={stock_no}'
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # 如果請求失敗，則引發異常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching data for {date}: {e}. Retry {i + 1}/{max_retries}')
            time.sleep(3)
    raise Exception(f'Failed to fetch data for {date} after {max_retries} retries')

# 定義下載和合併資料的函數
def download_stock_data(start_year, start_month, end_year, end_month, stock_no='2330'):
    data_frames = []
    for year in range(start_year, end_year + 1):
        start_m = start_month if year == start_year else 1
        end_m = end_month if year == end_year else 12
        for month in range(start_m, end_m + 1):
            date_str = f'{year}{month:02d}01'
            try:
                json_data = fetch_data(date_str, stock_no)
                columns = ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']
                df = pd.DataFrame(json_data['data'], columns=columns)
                data_frames.append(df)
            except Exception as e:
                print(f'Error fetching data for {date_str}: {e}')
            # 跳過未來的月份
            current_date = datetime.now()
            if year == current_date.year and month >= current_date.month:
                break
    all_data = pd.concat(data_frames, ignore_index=True)
    return all_data

# 日期轉換和資料清洗
def clean_data(all_data):
    all_data['日期'] = all_data['日期'].apply(lambda x: re.sub(r'(\d+)(/\d+/\d+)', lambda y: str(int(y.group(1)) + 1911) + y.group(2), x))
    all_data[['成交股數', '成交金額', '成交筆數']] = all_data[['成交股數', '成交金額', '成交筆數']].replace(',', '', regex=True)

    # 移除無法轉換為數字的異常值
    def to_float(x):
        try:
            return float(x)
        except ValueError:
            return float('nan')

    all_data.iloc[:, 1:] = all_data.iloc[:, 1:].applymap(to_float)

    # 轉換成交股數和成交金額的單位
    all_data[['成交股數', '成交金額']] = all_data[['成交股數', '成交金額']] / 1000
    all_data = all_data.rename(columns={'成交股數': '成交張數'})

    # 移除包含 NaN 的行
    all_data = all_data.dropna()

    # 轉換日期為日期格式
    all_data['日期'] = pd.to_datetime(all_data['日期'])

    # 重命名列以符合 mplfinance 的要求
    all_data = all_data.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交張數': 'Volume'
    })

    # 確保所有列都轉換為浮點數類型
    all_data['Open'] = all_data['Open'].astype(float)
    all_data['High'] = all_data['High'].astype(float)
    all_data['Low'] = all_data['Low'].astype(float)
    all_data['Close'] = all_data['Close'].astype(float)
    all_data['Volume'] = all_data['Volume'].astype(float)

    # 設置日期為索引
    all_data.set_index('日期', inplace=True)

    return all_data

# 主程序
start_year = 2024
start_month = 4
end_year = 2024
end_month = 6

all_data = download_stock_data(start_year, start_month, end_year, end_month)
cleaned_data = clean_data(all_data)
print(cleaned_data)

cleaned_data.to_csv("all_data.txt", sep="\t", encoding="utf-8-sig", index=True)

print("✅ 成功將 all_data 寫入 all_data.txt")

# 繪製 K 線圖
def plot_data(all_data, title):
    fig, ax = plt.subplots()

    # mplfinance.plot 函數不接受 fontproperties 這個參數。
    # 相反，我們可以在設置標題和標籤時手動指定字體屬性。
    mpf.plot(all_data, type='candle', style='charles', ax=ax, warn_too_much_data=len(all_data) + 1)
    ax.set_title(title, fontproperties=zhfont)
    ax.set_ylabel('價格', fontproperties=zhfont)
    plt.show()
    
# 這邊改一下圖表上的名稱為 台積電
plot_data(cleaned_data, f'台積電 {start_year}/{start_month} - {end_year}/{end_month} 每日股票交易價格和收盤情況')
