
import ctypes
import win32com.client
import pandas as pd
cpOhlc = win32com.client.Dispatch("CpSysDib.StockChart")
# https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=288&seq=102&page=2&searchString=&p=&v=&m=


def get_ohlc(code, qty):
    cpOhlc.SetInputValue(0, code)           # 종목 코드
    cpOhlc.SetInputValue(1, ord('2'))       # '1': 기간, '2': 개수 url 참조
    cpOhlc.SetInputValue(4, qty)            # 요청 개수
    cpOhlc.SetInputValue(5, [0,2,3,4,5])    # 0,2,3,4,5: 날짜, 시가, 고가, 저가, 종가
    cpOhlc.SetInputValue(6, ord('D'))       # 일(Day) 단위 검색
    cpOhlc.SetInputValue(9, ord('1'))       # 1: 무수정 주가, 0 : 수정주가
    cpOhlc.BlockRequest()

    count = cpOhlc.GetHeaderValue(3)        # 수신 개수 반환
    columns = ['open', 'high', 'low', 'close']
    index = []
    rows = []
    for i in range(count):
        index.append(cpOhlc.GetDataValue(0, i))
        rows.append([cpOhlc.GetDataValue(1, i), cpOhlc.GetDataValue(2, i),
                     cpOhlc.GetDataValue(3, i), cpOhlc.GetDataValue(4, i)])
    # GetDataValue의 첫번째 인자는 SetInputValue(5,)를 통해 요청한 필드의 index순서
    df = pd.DataFrame(rows, columns=columns, index = index)
    print(df)
    return df


get_ohlc('A305080', 10)     # TIGER 미국채 10년선물 10일 시세(ohlc 조회)
