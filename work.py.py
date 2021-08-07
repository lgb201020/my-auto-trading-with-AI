import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet
import requests

access = "pwYRR31WBdL3n1aSuauBuIvbIGqYrcxrExMCawgA"
secret = "6KUJW2wtXXymYlL9iIPbTvF4HWhy0xi0bUieV2Ko"
myToken = "xoxb-2032756729879-2047786896035-z0jMNZ1ZtjVsUh1gHWsrLfZu"


#slack으로 메시지 보내기
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]



# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            
            target_price = get_target_price("KRW-BTC", 0.43)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            
            if target_price < current_price and ma15 < current_price :
                
                krw = get_balance("KRW")
                
                if krw > 5000:
                    
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)

                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)

                    post_message(myToken,"#autotrading","BTC buy : " +str(krw*0.9995)+"₩" )
                    
                 

            if int(now.minute) == 0 and int(now.second)==0:
                
                post_message(myToken,"#autotrading","코딩이 잘 작동중입니다.")
                
                print("2 okay")   
                
                if target_price > current_price:
                    
                    post_message(myToken,"#autotrading","현재 BTC 가격이 매수 목표가 보다 낮습니다.")
                    
                    print("3 okay")   
                

        else:
            
            btc = get_balance("BTC")
            
            if btc > 0.00008:

                current_price = get_current_price("KRW-BTC")
                
                upbit.sell_market_order("KRW-BTC", btc*0.9995)

                sell_result = upbit.sell_market_order("KRW-BTC", btc*0.9995)

                post_message(myToken,"#autotrading", "BTC sell : " +str(btc*0.9995*current_price)+"₩")


               
        
        time.sleep(1)
    
    except Exception as e:
        print(e)

        print("error1")

        post_message(myToken,"#autotrading","오류발생! 1초 쉽니다.")

        time.sleep(1)