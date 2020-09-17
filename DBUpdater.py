import pymysql
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import time

class DBUpdater:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', passwd='qkqh123', db='investar', charset='utf8')
        # charset을 utf8로 해야 한글 회사명에서 오류를 방지할 수 있음.
        # 이렇게 했는데도 안됨-->mysql> ALTER TABLE table_name convert to charset utf8; 이렇게 설정해줘버렸음
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE IF NOT EXISTS company_info (
                code VARCHAR(20),
                company VARCHAR(40),
                last_update DATE,
                PRIMARY KEY(code)
            )
            """
            curs.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS daily_price(
            code VARCHAR(20),
            date DATE,
            open BIGINT(20),
            high BIGINT(20),
            low BIGINT(20),
            close BIGINT(20),
            diff BIGINT(20),
            volume BIGINT(20),
            PRIMARY KEY(code,date)
            )
            """
            curs.execute(sql)
        self.conn.commit()
        self.codes = dict()
        self.update_comp_info()

    def __del__(self):
        self.conn.close()

    def read_krx_code(self):
        # 책이랑 다른 방식으로 구현(내가 직접 해본 방식으로...)
        url = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
        dat = {
            'method': 'download',
            'pageIndex': 1,
            'currentPageSize': 5000,
            'orderMode': 3,
            'orderStat': 'D',
            'searchType': 13,
            'fiscalYearEnd': 'all',
            'location': 'all'
        }
        #ret = requests.post(url, data=dat)
        ret = requests.get(url, params=dat)
        krx = pd.read_html(ret.text)[0]
        krx = krx[['종목코드', '회사명']]
        krx = krx.rename(columns={'종목코드': 'code', '회사명': 'company'})
        krx['code'] = krx['code'].map('{:06d}'.format)
        return krx

    def update_comp_info(self):
        """종목 코드를 company_info table에 업데이트 후 딕셔너리 저장"""
        sql = "SELECT * FROM company_info"
        df = pd.read_sql(sql, self.conn)
        for idx in range(len(df)):
            self.codes[df.iloc[idx]['code']] = df.iloc[idx]['company']

        with self.conn.cursor() as curs:
            sql = "select max(last_update) from company_info"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime("%Y-%m-%d")
            if rs[0] == None or rs[0].strftime("%Y-%m-%d") < today:
                krx = self.read_krx_code()

                for idx in range(len(krx)):
                    code = krx.iloc[idx]['code']
                    company = krx.iloc[idx]['company']
                    sql1 = "insert into company_info(code,company,last_update) values(%s, %s, %s)"
                    sql2 = "update company_info set company = %s, last_update =%s where code = %s"
                    sql3 = "select * from company_info where code=%s"
                    rs2 = curs.execute(sql3, code)
                    if rs2 == 0:
                        curs.execute(sql1, (code, company, today))
                    else:
                        curs.execute(sql2, (company, today, code))
                    self.codes[code] = company
                    tmnow = datetime.now().strftime("%Y-%m-%d %H:%M")
                    print(
                        "[{}]{:04d} UPDATE INTO company_info VALUES ({},{},{})".format(tmnow, idx, code, company,
                                                                                       today))
                self.conn.commit()

    def read_naver(self, code, company, pages_to_fetch):
        """네이버에서 주식 시세를 읽어서 DF로 변환"""
        try:
            url = 'https://finance.naver.com/item/sise_day.nhn?code={}'.format(code)
            head = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
            }
            with requests.get(url,headers=head) as doc:
                if doc is None:
                    return None
                html = bs(doc.text, 'html.parser')
                pgrr = html.find("td", {'class': 'pgRR'})
                if pgrr is None:
                    return None
                lastpage = int(pgrr.find("a")['href'].split('=')[-1])
            df = pd.DataFrame()
            pages = min(lastpage, pages_to_fetch)
            for page in range(1, pages + 1):
                pg_url = '{}&page={}'.format(url, page)
                df = df.append(pd.read_html(pg_url)[0])
                tmnow = datetime.now().strftime("%Y-%m-%d %H:%M")
                print(
                '[{}]{}({}) : {:04d}/{:04d} pages are downloading....'.format(tmnow, company, code, page, pages), end
                ='\r')
                if page % 100 == 0:
                    time.sleep(3)
            df = df.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff'
                , '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
            df['date'] = df['date'].replace('.', '-')
            df = df.dropna()
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[
                ['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
            df = df[['date', 'open', 'high', 'low', 'close', 'diff', 'volume']]
        except Exception as e:
            print('Exception occured:', str(e))
            return None
        return df

    def replace_into_db(self, df, num, code, company):
        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql1 = "select * from daily_price where code = %s and date=%s"
                sql2 = "insert into daily_price(code,date,open,high,low,close,diff,volume) values(%s, %s, %s,%s,%s,%s,%s,%s)"
                sql3 = "update daily_price set open = %s, high =%s, low=%s, close=%s, diff=%s, volume=%s where code = %s and date=%s"
                rs = curs.execute(sql1, (code, r.date))
                if rs == 0:
                    curs.execute(sql2, (code, r.date, r.open, r.high, r.low, r.close, r.diff, r.volume))
                else:
                    curs.execute(sql3, (r.open, r.high, r.low, r.close, r.diff, r.volume, code, r.date))
            self.conn.commit()
            print('[{}] #{:04d} {} ({}) : {} rows > REPLACE INTO daily_' \
                  'price [OK]'.format(datetime.now().strftime("%Y-%m-%d %H:%M"), num + 1, company, code, len(df)))

    def update_daily_price(self, pages_to_fetch):
        for idx, code in enumerate(self.codes):
            df = self.read_naver(code, self.codes[code], pages_to_fetch)
            if df is None:
                continue
            self.replace_into_db(df, idx, code, self.codes[code])


if __name__ == '__main__':
    dbu = DBUpdater()
    dbu.update_comp_info()
    dbu.update_daily_price(1)