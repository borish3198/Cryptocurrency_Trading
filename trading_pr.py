import pybithumb
import datetime
import time
import cv2

def main():
    # API key 값 받아오기
    with open("bithumb.txt") as f:
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
        k = 0.5
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

    # 변동률 계산
    def calc_rate(ticker):
        df = pybithumb.get_ohlcv(ticker)
        yesterday = df.iloc[-2]
        yesterday_close = yesterday["close"]
        yesterday_open = yesterday["open"]
        change_rate = (yesterday_close-yesterday_open)/yesterday_open * 100
        return change_rate

    #매일 자정 거래를 위한 시간값
    now = datetime.datetime.now()
    print("프로그램 시작 시간 :", now)

    start = now + datetime.timedelta(seconds=10)
    end = datetime.datetime(now.year, now.month, now.day, 23, 55, 00)

    count=0
    target_price = {}
    ma5 = {}
    buy_flag = {}
    list = {}
    coins = []
#'BTC', 'ETH', 'XRP', 'ADA',  'LTC', 'BCH'(10.29일 부 폐기)
#'MANA', 'SAND', 'BAT', 'ENJ', 'THETA', 'ICX', 'CRO'(11.15일 부 폐기)

    for ticker in bithumb.get_tickers():
        rate = calc_rate(ticker)
        if rate>0:
            list[ticker] = rate
 
    new = dict(sorted(list.items(), key=lambda x:x[1], reverse=True))
    coin = new.keys()
    cnt=0
    for tick in coin:
        cnt+=1
        coins.append(tick)
        if cnt==10:
            break
    print("거래대상 코인 :", coins)

    while True:
        try:
            now = datetime.datetime.now()
            if start < now < start + datetime.timedelta(seconds=2):  #테스트용 거래 시간
                print(now, '거래를 시작합니다.')

                #모두 다 초기화 
                target_price = {} 
                ma5 = {}
                buy_flag = {}
                conut = 0

                # 코인 별 진입가격 계산
                for tick in coins:
                    target_price[tick] = get_target_price(tick)            # 코인 별 진입 가격 계산
                    ma5[tick] = get_yesterday_ma5(tick)                    # 코인 별 이동 평균 계산
                    buy_flag[tick] = 0                                     # buy_flag에 초기값 0
                                                
                print(target_price)
                print(ma5)
                print("코인 매도 완료, 매수 실행")

            # 이동평균 조건 및 진입 가격 먼저 도달하는 상위 20개만 매수(4.13 기준 151개)
            # 5.4 기준 ['BTC', 'ETH', 'XRP', 'ADA', 'LTC', 'BCH'] 해당 코인 6개만 거래
            # 탐색순서에 영향을 많이 받음 / get_tickers() 함수에서 받아오는 순서대로 탐색
            # 보완할 필요 있음, 변동성 돌파 전략 및 이동평균 자격 충족하는 화폐들 리스트 따로 만든 후
            # 그중에 우선순위 판단하여 거래할 수 있도록 보완 필

            if count>=len(coins):
                print("금일 거래를 종료합니다.")
                break

            # 초기 테스트용 (없으면 시작 후 거래 시작까지 오류 발생)
            if len(target_price) == 0:
                continue

            for tick in coins:
                current_price = pybithumb.get_current_price(tick)
                if (current_price>target_price[tick]) and (current_price > ma5[tick]) and (buy_flag[tick] == 0):
                    k=len(coins)-count
                    buy_crypto_currency(tick, k)
                    result = bithumb.get_balance(tick)[0]
                    buy_flag[tick]=1
                    count+=1
                    print(count, "번째 코인 매수 완료\n거래코인 :", tick, "\n거래수량 :", result)
                    print("이동평균 :", ma5[tick], "현재가 :", current_price, "진입가 :", target_price[tick])
                    print("--------------------------------------------------------------------------------")
            
            now = datetime.datetime.now()
            if end < now < end + datetime.timedelta(seconds=2):  #매도 시점 매일 자정에 근접하여 매도
                # 보유 코인 모두 판매
                for tick in coins:
                    balance = bithumb.get_balance(tick)
                    if balance[0]!=0:
                        sell_crypto_currency(tick)
                        print("매도 완료 코인 :", tick)                
                print(now, '거래를 종료합니다.')
                break
                
        except:
            print("에러 발생")

        if cv2.waitKey(1) == ord('q'):
            break
        time.sleep(1)
