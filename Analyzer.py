import pymysql
from datetime import datetime
from datetime import timedelta
import pandas as pd
import re


class MarketDB:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', user='root', passwd='qkqh123', db="investar", charset='utf8')
        self.codes = {}
        self.get_comp_info()

    def __del__(self):
        self.conn.close()

    def get_comp_info(self):
        sql = "select * from company_info"
        krx = pd.read_sql(sql, self.conn)
        for idx in range(len(krx)):
            self.codes[krx.iloc[idx]['code']] = krx.iloc[idx]['company']

    def get_daily_price(self, code, start_date=None, end_date=None):
        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime("%Y-%m-%d")
            print("start_date is initialized to {}".format(start_date))
        else:
            start_lst = re.split('\D+', start_date)
            if (start_lst[0] == ''):
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > 2200:
                print("Value Error: start_year: {} is wrong".format(start_year))
                return
            if start_month < 1 or start_month > 12:
                print("Value Error: start_month {} is wrong".format(start_month))
                return
            if start_day < 1 or start_day > 31:
                print("Value Error: start_day {} is wrong".format(start_day))
                return
            start_date = "{:04d}-{:02d}-{:02d}".format(start_year, start_month, start_day)

        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")
            print("end_date is initialized to {}".format(end_date))
        else:
            end_lst = re.split('\D+', end_date)
            if (end_lst[0] == ''):
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1900 or end_year > 2200:
                print("Value Error: end_year: {} is wrong".format(end_year))
                return
            if end_month < 1 or end_month > 12:
                print("Value Error: end_month {} is wrong".format(end_month))
                return
            if end_day < 1 or end_day > 31:
                print("Value Error: end_day {} is wrong".format(end_day))
                return
            end_date = "{:04d}-{:02d}-{:02d}".format(end_year, end_month, end_day)
        codes_keys = list(self.codes.keys())
        codes_values = list(self.codes.values())
        if code in codes_keys:
            pass
        elif code in codes_values:
            idx = codes_values.index(code)
            code = codes_keys[idx]
        else:
            print("Value Error: Code({}) doesn't exist".format(code))
        # sql을 conn.execute로 실행할 때와, read_sql로 실행할 때 문법이 조금 다르다!!
        # read_sql로 parameter를 읽을 때는 sql문 %s의 s앞에 이름을 명시해줘야 하며, read_sql의 인자로 params를 통해 읽어올 수 있다.
        # 하지만 위 방식은, conn.execute에서는 수행되지 않으므로, 다른 sql문을 각각 작성해줘야될듯?
        sql = "select * from daily_price where code=%(code)s and date >= %(start)s and date <= %(end)s"
        df = pd.read_sql(sql, self.conn, params={'code': code, 'start': start_date, 'end': end_date})
        df.index = df['date']
        return df