import pybithumb
import datetime
import time
import schedule
import trading_pr as trading

schedule.every().day.at("01:00").do(trading.main)
while True:
    schedule.run_pending()
    time.sleep(1)
