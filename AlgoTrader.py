#!/usr/bin/env python
# coding: utf-8
import ctypes
import win32com.client
cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpStock = win32com.client.Dispatch("DsCbo1.StockMst")
def check_creon_system():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print('check_creon_system() : admin user -> FAILED')
        return False

    if (cpStatus.IsConnect == 0):
        print('check_creon_system() : connect to server ->FAILED')
        return False

    if cpTradeUtil.TradeInit(0) != 0:
        print('check_creon_system() : init trade -> FAILED')
        return False

    return True

def get_current_price(code):
    cpStock.SetInputValue(0, code)
    cpStock.BlockRequest()

    item = {}
    item['cur_price'] = cpStock.GetHeaderValue(11)  #현재가
    item['ask'] = cpStock.GetHeaderValue(16)        #매수호가
    item['bid'] = cpStock.GetHeaderValue(17)        #매도호가
    print(item)
    return item['cur_price'], item['ask'], item['bid']

check_creon_system()
get_current_price('A305080')

'''
obj = win32com.client.Dispatch("DsCbo1.StockMst")
obj.SetInputValue(0,'A005930')
obj.BlockRequest()
sec={}
sec['현재가'] = obj.GetHeaderValue(11)
sec['전일대비'] = obj.GetHeaderValue(12)
'''
'''
각 숫자별 의미는
https://money2.creontrade.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_Read_Page.aspx?boardseq=288&seq=3&page=3&searchString=&p=&v=&m=
에서 확인
'''
#print(sec)