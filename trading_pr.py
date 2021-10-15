'''
저자 강환국의 저서 '가상화폐 투자 마법 공식 : 쉽고 안전하게 고수익 내는 검증된 매매 규칙 13' 중 
7번째 투자 전략인 '다자 가상화폐 + 변동성 돌파'를 구현한 프로그램
가상 화폐 거래소 '빗썸'에서 제공하는 pybithumb API를 활용해 구현
거래를 위해선 '빗썸'이 제공하는 API Key를 발급받아야 하며 세부 내용은 해당 사이트 참조 (https://wikidocs.net/21887)
'''


import pybithumb
import datetime
import time

def main():
    # API key 값 받아오기
    with open("key값이 있는 txt파일") as f:
        lines = f.readlines()
        key = lines[0].strip()
        secret = lines[1].strip()
        bithumb = pybithumb.Bithumb(key, secret)
        

    # 이동평균 계산 함수
    def get_yesterday_ma5(ticker):
        df = pybithumb.get_ohlcv(ticker)
        close = df['close']
        ma5 = close.rolling(5).mean()
        return ma5[-2]

    # 매수 지점 계산
    def get_target_price(ticker):
        df = pybithumb.get_ohlcv(ticker)
        yesterday = df.iloc[-2]

        k = 0.5                                    # 매수 포인트를 가늠하는 중요한 지표로, 높을수록 더욱 확실할때에 진입한다.
        today_open = yesterday["close"]
        yesterday_high = yesterday["high"]
        yesterday_low = yesterday["low"]
        target = round(today_open + (yesterday_high - yesterday_low) * k)
        return target

    # 매수 함수
    def buy_crypto_currency(ticker, k):
        krw = bithumb.get_balance(ticker)[2]/k
        orderbook = pybithumb.get_orderbook(ticker)
        sell_price = orderbook['asks'][0]['price']
        unit = krw/float(sell_price)
        bithumb.buy_market_order(ticker, unit)


    #매도 함수
    def sell_crypto_currency(ticker):
        unit = bithumb.get_balance(ticker)[0]
        bithumb.sell_market_order(ticker, unit)



    #매일 자정 거래를 위한 시간값
    now = datetime.datetime.now()
    print("프로그램 시작 시간 :", now)

    test = now + datetime.timedelta(seconds=10)
    # print(test)

    count=0
    target_price = {}
    ma5 = {}
    buy_flag = {}
    coins = ["거래 희망하는 코인의 코드 값을 리스트 형태로 입력"]       #예시) coins = ['BTC', 'ETH', 'XRP', 'ADA',  'LTC', 'BCH']

    while True:
        try:
            now = datetime.datetime.now()
            if test < now < test + datetime.timedelta(seconds=2): 
                print(now, '거래를 시작합니다.')

                #모두 다 초기화 
                target_price = {} 
                ma5 = {}
                buy_flag = {}
                conut = 0

                # 보유 코인 모두 판매
                for tick in coins:
                    target_price[tick] = get_target_price(tick)            # 코인 별 진입 가격 계산
                    
                    ma5[tick] = get_yesterday_ma5(tick)                    # 코인 별 이동 평균 계산
                    buy_flag[tick] = 0                                     # buy_flag에 초기값 0
                                    
                    balance = bithumb.get_balance(tick)

                    if balance[0]!=0:
                        sell_crypto_currency(tick)
                        print("매도 완료 코인 :", tick)
            
                print(target_price)
                print(ma5)
                print("코인 매도 완료, 매수 실행")

            if count>=6:                              # 거래 대상에 속한 코인의 개수에 따라 조건값 수정 필요
                print("금일 거래를 종료합니다.")
                break

            # 초기 테스트용 (없으면 시작 후 거래 시작까지 오류 발생)
            if len(target_price) == 0:
                continue

            for tick in coins:
                current_price = pybithumb.get_current_price(tick)
                if (current_price>target_price[tick]) and (current_price > ma5[tick]) and (buy_flag[tick] == 0):
                    k=6-count
                    # print("지표2")
                    buy_crypto_currency(tick, k)
                    result = bithumb.get_balance(tick)[0]
                    buy_flag[tick]=1
                    # print("지표3")
                    count+=1
                    print(count, "번째 코인 매수 완료\n거래코인 :", tick, "\n거래수량 :", result)
                    print("이동평균 :", ma5[tick], "현재가 :", current_price, "진입가 :", target_price[tick])
                    print("--------------------------------------------------------------------------------")
                        
        except:
            print("에러 발생")
        
        time.sleep(1)
