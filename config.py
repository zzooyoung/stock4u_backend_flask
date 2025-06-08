# config.py
TICKERS = ["AMZN", "NVDA", "AAPL"]
TICKERS_NAME = ["아마존", "엔비디아", "애플"]

###
# 0 7 * * * /bin/bash -c 'cd /your/script/folder && /usr/bin/python3 30days_data_loader.py && /usr/bin/python3 get_prediction.py >> cron.log 2>&1'