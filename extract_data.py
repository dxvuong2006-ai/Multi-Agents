import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import logging
import shutil
from pathlib import Path 
logging.basicConfig(filename=r"D:\PROJECTS\AI\agent_extract_and_analyze_data\pipeline.log",level=logging.INFO,format='%(asctime)s -%(levelname)s-%(message)s',encoding='utf-8')

def extract_market_data(ticker_sumbol,start_date,end_date):
    logging.info(f"Bắt đầu kéo dữ liệu cho {ticker_sumbol} từ {start_date} đến {end_date}")
    try:
        ticker=yf.Ticker(ticker_sumbol)
        df=ticker.history(start=start_date,end=end_date)

        if df.empty:
            logging.warning(f"Không tìm thấy dữ liệu cho mã {ticker_sumbol}")
            return None
        
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        logging.error(f"lỗi khi extract dữ liệu:{e}")
        return None

def transform_data(df):
    if df is None or df.empty:
        return None
    logging.info("Đang xử lí dữ liệu")
    try:
        df.columns=[col.lower().replace(' ','_') for col in df.columns]
        
        #lọc các cột cần thiết
        columns_to_keep=['date','open','high','low','close','volume']
        df=df[columns_to_keep].copy()
        
        #xử lí Timezone:xóa phần thêm múi giờ đi
        df['date']=df['date'].dt.tz_localize(None)

        #thêm cột biến động giá hàng ngày:(P_(t+1)-Pt)/Pt
        df['daily_return']=df['close'].pct_change()

        df.dropna(inplace=True)

        return df
    except Exception as e:
        logging.error(f"có lỗi cần kiểm tra :{e}")
        return None

def load_data(df,file_name):
    if df is None or df.empty:
        logging.warning("không có dữ liệu")
        return None
    try:
        file_name=Path("data") / file_name
        if file_name.exists():
            file_name.unlink()
        os.makedirs('data',exist_ok=True)
        logging.info(f"Đang tiến hành nạp data tại đường dẫn :{file_name}")
        df.to_parquet(file_name,index=False)
        logging.info("đã nạp thành công")
    except Exception as e:
        logging.error(f"có lỗi xảy ra {e}")

def run_pipeline(TICKER):
    START_DATE="2026-07-01"
    END_DATE=datetime.today().strftime('%Y-%m-%d')
    OUTPUT_FILE=f"{TICKER.replace('=', '_')}_historical_{END_DATE}.parquet"
    
    #thực thi tuần tụ luồng ETL
    raw_df=extract_market_data(TICKER,START_DATE,END_DATE)
    clean_df=transform_data(raw_df)
    load_data(clean_df,OUTPUT_FILE)
 

