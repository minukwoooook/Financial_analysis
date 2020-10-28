
import win32com.client


cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpBalance = win32com.client.Dispatch('CpTrade.CpTd6033')
cpCodeMgr = win32com.client.Dispatch('CpUtil.CpStockCode')
cpCash = win32com.client.Dispatch("CpTrade.CpTdNew5331A")


def get_stock_balance(code):
    '''
    주식 잔고 조회
    '''
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]
    accFlag = cpTradeUtil.GoodsList(acc, 1) # -1: 전체, 1: 주식, 2:선물/옵션
    cpBalance.SetInputValue(0, acc)
    cpBalance.SetInputValue(1, accFlag[0])
    cpBalance.SetInputValue(2, 50)
    cpBalance.BlockRequest()
    print("Account Number:" + acc)
    if code == 'ALL':
        print('계좌명:' + str(cpBalance.GetHeaderValue(0)))
        print('결제 잔고 수량:' + str(cpBalance.GetHeaderValue(1)))
        print('평가 금액:' + str(cpBalance.GetHeaderValue(3)))
        print('평가 손익:' + str(cpBalance.GetHeaderValue(4)))
        print('종목 수:' + str(cpBalance.GetHeaderValue(7)))

    stocks=[]
    for i in range(cpBalance.GetHeaderValue(7)):
        stock_code = cpBalance.GetDataValue(12, i)  #종목코드
        stock_name = cpBalance.GetDataValue(0, i)   #종목명
        stock_qty = cpBalance.GetDataValue(15, i)   #수량
        if code == 'ALL':
            print(str(i+1)+' '+stock_cde + '(' + stock_name+')'+':'+ str(stock_qty))
            stocks.append({'code':stock_code, 'name':stock_name, 'qty': stock_qty})
        if stock_code == code:
            return stock_name, stock_qty
    if code == 'ALL':
        return stocks
    else:
        stock_name = cpCodeMgr.CodeToName(code)
        return stock_name, 0


def cut_current_cash():
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]
    accFlag = cpTradeUtil.GoodsList(acc,1)
    cpCash.SetInputValue(0, acc)
    cpCash.SetInputValue(1, accFlag[0])
    cpCash.BlockRequest()
    val = cpCash.GetHeaderValue(9)
    print("증거금 100% 주문가능 금액:"+str(val))
    return val


get_stock_balance('ALL')
cut_current_cash()