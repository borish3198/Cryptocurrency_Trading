'''
저자 강환국의 저서 '가상화폐 투자 마법 공식 : 쉽고 안전하게 고수익 내는 검증된 매매 규칙 13' 중 
7번째 투자 전략인 '다자 가상화폐 + 변동성 돌파'를 구현한 프로그램
가상 화폐 거래소 '빗썸'에서 제공하는 pybithumb API를 활용해 구현
거래를 위해선 '빗썸'이 제공하는 API Key를 발급받아야 하며 세부 내용은 해당 사이트 참조 (https://wikidocs.net/21887)
* 매일 자동 거래를 위한 스케줄러
'''

import pybithumb
import datetime
import time
import schedule
import trading_pr as trading

schedule.every().day.at("01:00").do(trading.main)
while True:
    schedule.run_pending()
    time.sleep(1)
