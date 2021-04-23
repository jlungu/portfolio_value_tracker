import csv
import collections
from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pandas_market_calendars as mcal
import copy

def peformance():
    d = {}
    dt = None
    holdings = []
    with open("my_port.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[2] not in holdings:
                holdings.append(row[2])
            #dt = datetime.strptime(row[0], "%m/%d/%Y").date()
            dt = pd.Timestamp(row[0])
            # dt = dt.replace(hour=20, minute=0, second=0, microsecond=0)
            if dt in d:
                d[dt].append(row)
            else:
                d[dt] = [row]
        d = sorted(d.items(), key=lambda item: item[0])
        d = dict(d)
        print(d)
        # print(holdings)
        daily_holdings = {}
        # print(d)
        histories = {}
        range_date = []
        print(holdings)
        for ticker in holdings:
            r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol='+ticker+'&resolution=D&from=1564012740&'
                                             'to=1595635140&token=brain17rh5rbgnjpuck0')
            #r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + ticker + '&resolution=D&from=1595735940&'
            #                                     'to=1618113540&token=brain17rh5rbgnjpuck0')
            r = r.json()
            if r["s"] == 'no_data':
                continue
            histories[ticker] = r["c"]
        for t in r["t"]:
            #range_date.append(datetime.fromtimestamp(t).date())
            range_date.append(pd.Timestamp(t, unit='s'))
        # spy
        spy = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=SPY&resolution=D&from=1564012740&'
                                            'to=1595635140&token=brain17rh5rbgnjpuck0')
        #spy = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=SPY&resolution=D&from=1595735940&'
        #                                     'to=1618113540&token=brain17rh5rbgnjpuck0')
        spy = spy.json()
        print(spy)
        # for a in histories.keys():
        #     print(a, histories[a])
        # datelist = pd.date_range(pd.Timestamp('07/23/2019'), pd.Timestamp('04/01/2020')).tolist()
        # aggregate 'portfolio shares' each day, from the range given. iterating for each day, seeing what shares we have
        port_holdings = {}
        spy_holdings = spy["c"]
        spy_value = []
        port_value = []
        holdings.sort()
        for ticker in holdings:
            port_holdings[ticker] = 0
        counter = 0
        spy_sum = 0
        for i in range_date:  # for every day. see if a trade occured.
            print(i)
            if i in d.keys():
                temp = d[i]
                for j in temp:  # grab the shares
                    if j[1] == 'Buy' or j[1] == 'Reinvest' or j[1] == 'Reinvest Shares':
                        port_holdings[j[2]] += float(j[3])
                        spy_sum += (float(j[3]) * histories[j[2]][counter]) / spy_holdings[counter]
                    elif j[1] == 'Sell':
                        port_holdings[j[2]] -= float(j[3])
                        spy_sum -= (float(j[3]) * histories[j[2]][counter]) / spy_holdings[counter]
            sum = 0
            for p in port_holdings.keys():
                if port_holdings[p] != 0:
                    sum += port_holdings[p] * histories[p][counter]
            port_value.append(sum)
            print(i)
            print(port_holdings)
            spy_value.append(spy_sum * spy_holdings[counter])
            counter += 1
        range_date2 = range_date
        time.sleep(60)
        for ticker in holdings:
            r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + ticker + '&resolution=D&from=1595735940&'
                                                 'to=1618113540&token=brain17rh5rbgnjpuck0')
            r = r.json()
            if r["s"] == 'no_data':
                continue
            histories[ticker] = r["c"]
        range_date = []

        for t in r["t"]:
            #range_date.append(datetime.fromtimestamp(t).date())
            range_date.append(pd.Timestamp(t, unit='s'))
        # spy
        spy = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=SPY&resolution=D&from=1595735940&'
                                             'to=1618113540&token=brain17rh5rbgnjpuck0')
        spy = spy.json()
        # for a in histories.keys():
        #     print(a, histories[a])
        # datelist = pd.date_range(pd.Timestamp('07/23/2019'), pd.Timestamp('04/01/2020')).tolist()
        # aggregate 'portfolio shares' each day, from the range given. iterating for each day, seeing what shares we have
        #port_holdings = {}
        spy_holdings = spy["c"]
        # holdings.sort()
        # for ticker in holdings:
        #     port_holdings[ticker] = 0
        counter = 0
        #spy_sum = 0
        for i in range_date:  # for every day. see if a trade occured.
            print(i)
            if i in d.keys():
                temp = d[i]
                for j in temp:  # grab the shares
                    if j[1] == 'Buy' or j[1] == 'Reinvest' or j[1] == 'Reinvest Shares':
                        port_holdings[j[2]] += float(j[3])
                        spy_sum += (float(j[3]) * histories[j[2]][counter]) / spy_holdings[counter]
                    elif j[1] == 'Sell':
                        port_holdings[j[2]] -= float(j[3])
                        spy_sum -= (float(j[3]) * histories[j[2]][counter]) / spy_holdings[counter]
            sum = 0
            for p in port_holdings.keys():
                if len(histories[p]) < len(range_date):
                    continue
                if port_holdings[p] != 0:
                    sum += port_holdings[p] * histories[p][counter]
            port_value.append(sum)
            print(i)
            print(port_holdings)
            spy_value.append(spy_sum * spy_holdings[counter])
            counter += 1
        range_date = range_date2 + range_date
        values = pd.DataFrame({'Date': range_date, 'Value': port_value, 'SPY': spy_value})
        values.to_csv("ordered_trades3.csv", index=False)


def calculate_shares():
    d = {}
    holdings = []
    port_holdings = {}
    port_value = []
    with open("my_port.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[2] not in holdings:
                holdings.append(row[2])
            dt = pd.Timestamp(row[0])
            if dt in d:
                d[dt].append(row)
            else:
                d[dt] = [row]
        d = sorted(d.items(), key=lambda item: item[0])
        d = dict(d)
    holdings.sort()
    for ticker in holdings:
        port_holdings[ticker] = 0
    date_range = pd.date_range(start='07/24/2019', end='4/15/2021')
    counter = 0
    daily_holdings = {}
    for date in date_range:
        daily_holdings[date.date().strftime("%m/%d/%Y")] = []
    for i in date_range:  # for every day. see if a trade occurred.
        if i in d.keys():
            temp = d[i]
            for j in temp:  # grab the shares
                if j[1] == 'Buy' or j[1] == 'Reinvest' or j[1] == 'Reinvest Shares':
                    port_holdings[j[2]] += float(j[3])
                elif j[1] == 'Sell':
                    port_holdings[j[2]] -= float(j[3])
        sum = 0
        for p in port_holdings.keys():
            if port_holdings[p] != 0:
                sum += port_holdings[p]
        port_value.append(sum)
        counter += 1
        daily_holdings[i.date().strftime("%m/%d/%Y")] = port_holdings
    values = pd.DataFrame(daily_holdings)
    values.to_csv("my_stocks2.csv", index=False)


def price_histories():
    holdings = []
    inception_date = pd.to_datetime("today")
    today = inception_date
    nyse = mcal.get_calendar('NYSE')
    market_dates = []
    dates = []
    with open("evans_port.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[2] not in holdings and (row[1] == 'Buy' or row[1] == 'Sell' or row[1] == 'Reinvest' or row[1] == 'Dividend'):
                if row[2] != 'QACDS' and row[2] != 'QCDSM':
                    holdings.append(row[2])
            if pd.to_datetime(row[0]) < inception_date:
                inception_date = pd.to_datetime(row[0])
    holdings.sort()
    # go ahead and get the price history.
    # done in increments of 1 yr, bc finance APIs are expensive.
    histories = {}
    print(holdings)
    for ticker in holdings:
        histories[ticker] = []
    while inception_date + pd.DateOffset(months=12) < today:
        period_length = len(mcal.date_range(nyse.schedule(start_date=inception_date, end_date=inception_date + pd.DateOffset(months=12)), frequency='1D'))
        market_dates += mcal.date_range(nyse.schedule(start_date=inception_date, end_date=inception_date + pd.DateOffset(months=12)), frequency='1D')
        end_date = inception_date + pd.DateOffset(months=12)
        i = 0
        for ticker in holdings:  # get close prices for each ticker!
            print(ticker)
            if i == 60:
                i = 0
                time.sleep(60)
            r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + ticker + '&resolution=D&from=' +
                             str(int(pd.Timestamp(inception_date).timestamp()))+'&to=' +
                             str(int(pd.Timestamp(end_date).timestamp()))+'&token=brain17rh5rbgnjpuck0')
            r = r.json()
            print(r)
            if r["s"] == 'no_data':
                print("hey")
                histories[ticker] += [0] * len(market_dates)
            elif len(r["c"]) < period_length:
                histories[ticker] += ([0] * (period_length - len(r["c"]))) + r["c"]
            else:
                histories[ticker] += r["c"]  # append!
            i += 1
        inception_date = end_date
        time.sleep(60)  # 30 API calls a minute :(
    period_length = len(mcal.date_range(nyse.schedule(start_date=inception_date, end_date=today), frequency='1D'))
    market_dates += mcal.date_range(nyse.schedule(start_date=inception_date, end_date=today), frequency='1D')
    i = 0
    for ticker in holdings:  # get close prices for each ticker!
        if i == 60:
            i = 0
            time.sleep(60)
        r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + ticker + '&resolution=D&from=' +
                         str(int(pd.Timestamp(inception_date).timestamp())) + '&to=' +
                         str(int(pd.Timestamp(today).timestamp())) + '&token=brain17rh5rbgnjpuck0')
        r = r.json()
        print(r)
        if r["s"] == 'no_data':
            histories[ticker] += [0] * len(market_dates)
        elif len(r["c"]) < period_length:
            histories[ticker] += ([0] * (period_length - len(r["c"]))) + r["c"]
        else:
            histories[ticker] += r["c"]  # append!
        i += 1
    for h in histories.keys():
        print(len(histories[h]), h, histories[h])
    for date in market_dates:
        dates.append(date.normalize().strftime("%m/%d/%Y"))
    dates_dict = {}
    for i in range(0, len(dates)):
        dates_dict[i] = dates[i]
    df = pd.DataFrame.from_dict(histories)
    df = df.rename(index=dates_dict)
    df.to_csv("ev_price_history.csv")


def index_histories():
    holdings = ['SPY', 'DIA']
    inception_date = pd.to_datetime("10/22/2019")
    today = pd.to_datetime("today")
    nyse = mcal.get_calendar('NYSE')
    market_dates = []
    dates = []
    # go ahead and get the price history.
    # done in increments of 1 yr, bc finance APIs are expensive.
    histories = {}
    for ticker in holdings:
        histories[ticker] = []
    while inception_date + pd.DateOffset(months=12) < today:
        period_length = len(mcal.date_range(
            nyse.schedule(start_date=inception_date, end_date=inception_date + pd.DateOffset(months=12)),
            frequency='1D'))
        market_dates += mcal.date_range(
            nyse.schedule(start_date=inception_date, end_date=inception_date + pd.DateOffset(months=12)),
            frequency='1D')
        end_date = inception_date + pd.DateOffset(months=12)
        for ticker in holdings:  # get close prices for each ticker!
            r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + ticker + '&resolution=D&from=' +
                             str(int(pd.Timestamp(inception_date).timestamp())) + '&to=' +
                             str(int(pd.Timestamp(end_date).timestamp())) + '&token=brain17rh5rbgnjpuck0')
            r = r.json()
            if r["s"] == 'no_data':
                histories[ticker] += [0] * len(market_dates)
            elif len(r["c"]) < period_length:
                histories[ticker] += ([0] * (period_length - len(r["c"]))) + r["c"]
            else:
                histories[ticker] += r["c"]  # append!
        inception_date = end_date
        # time.sleep(60)  # 30 API calls a minute :(
    period_length = len(mcal.date_range(nyse.schedule(start_date=inception_date, end_date=today), frequency='1D'))
    market_dates += mcal.date_range(nyse.schedule(start_date=inception_date, end_date=today), frequency='1D')
    for ticker in holdings:  # get close prices for each ticker!
        r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=' + ticker + '&resolution=D&from=' +
                         str(int(pd.Timestamp(inception_date).timestamp())) + '&to=' +
                         str(int(pd.Timestamp(today).timestamp())) + '&token=brain17rh5rbgnjpuck0')
        r = r.json()
        if r["s"] == 'no_data':
            histories[ticker] += [0] * len(market_dates)
        elif len(r["c"]) < period_length:
            histories[ticker] += ([0] * (period_length - len(r["c"]))) + r["c"]
        else:
            histories[ticker] += r["c"]  # append!
    for date in market_dates:
        dates.append(date.normalize().strftime("%m/%d/%Y"))
    for i in histories.keys():
        print(len(i))
    print(len(dates), len(histories['SPY']))
    dates_dict = {}
    for i in range(0, len(dates)):
        dates_dict[i] = dates[i]
    df = pd.DataFrame.from_dict(histories)
    df = df.rename(index=dates_dict)
    df.to_csv("ev_index_history.csv")


def portfolio_value():
    # pull dataframe from the csv file we made.
    df = pd.read_csv("price_history.csv", index_col=0)
    holdings = []
    d = {}
    with open("my_port.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[2] not in holdings:
                holdings.append(row[2])
            dt = pd.Timestamp(row[0])
            if dt in d:
                d[dt].append(row)
            else:
                d[dt] = [row]
    day_values = []
    shares = {}
    pct_values = []
    pct_sum = []
    for ticker in holdings:
        shares[ticker] = 0
    i = 0
    last = None
    last_sum = 0.0
    for day in df.index.tolist():
        if pd.to_datetime(day) in d.keys(): # incorporate trades for that day.
            for trade in d[pd.to_datetime(day)]:
                if trade[1] == 'Buy' or trade[1] == 'Reinvest' or trade[1] == 'Reinvest Shares':
                    shares[trade[2]] += float(trade[3])
                elif trade[1] == 'Sell':
                    shares[trade[2]] -= float(trade[3])
        sum = 0
        yes_sum = 0
        for p in shares.keys():
            sum += shares[p] * df[p][day]
        if last:
            for p in shares.keys():
                yes_sum += shares[p] * df[p][last]
            temp = ((sum-yes_sum)/yes_sum) * 100
            print(temp)
            pct_values.append(temp)
            pct_sum.append(last_sum+temp)
            last_sum += temp
        else:
            pct_values.append(0.0)
            pct_sum.append(0.0)
        day_values.append(sum)
        last = day
        #last_sum += ((sum-yes_sum)/yes_sum) * 100
    values = pd.DataFrame({'Date': df.index.tolist(), 'Value': day_values, '%': pct_values, '% sum': pct_sum})  # off to a csv
    values.to_csv("portfolio_value.csv", index=False)
    #print(len(pct_values), len(df.index.tolist()))
    # plt.plot(df.index.tolist(), )
    # plt.show()


def portfolio_value_compare():
    # pull dataframe from the csv file we made.
    df = pd.read_csv("price_history.csv", index_col=0)
    index_df = pd.read_csv("index_history.csv", index_col=0)
    holdings = []
    d = {}
    with open("my_port.CSV") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[2] not in holdings and (row[1] == 'Buy' or row[1] == 'Sell' or row[1] == 'Reinvest' or row[1] == 'Dividend'):
                if row[2] != 'QACDS' and row[2] != 'QCDSM':
                    holdings.append(row[2])
            dt = pd.Timestamp(row[0])
            if dt in d:
                d[dt].append(row)
            else:
                d[dt] = [row]
    day_values = []
    index_day_values = []
    shares = {}
    indicies = {}
    pct_values = []
    pct_sum = []
    pct_index_values = []
    pct_index_sum = []
    for ticker in holdings:
        shares[ticker] = 0
    for ticker in ['SPY', 'DJI']:
        indicies[ticker] = 0
    last = None
    last_sum = 0.0
    index = 'SPY'  # i want to compare to SPY, but can compare to DJI as well.
    last_index_sum = 0.0
    index_shares = 0
    for day in df.index.tolist():
        if pd.to_datetime(day) in d.keys():  # incorporate trades for that day.
            print(day)
            for trade in d[pd.to_datetime(day)]:
                if (trade[1] == 'Buy' or trade[1] == 'Reinvest' or trade[1] == 'Reinvest Shares') and trade[2] != 'QACDS' and trade[2] != 'QCDSM':
                    shares[trade[2]] += float(trade[3])
                    index_shares += (float(trade[3]) * df[trade[2]][day]) / index_df[index][day]
                elif trade[1] == 'Sell':
                    shares[trade[2]] -= float(trade[3])
                    index_shares -= (float(trade[3]) * df[trade[2]][day]) / index_df[index][day]
        sum = 0
        yes_sum = 0
        i_sum = 0
        i_yes_sum = 0
        for p in shares.keys():
            sum += shares[p] * df[p][day]
        i_sum = index_shares * index_df[index][day]
        if last:
            for p in shares.keys():
                yes_sum += shares[p] * df[p][last]
            i_yes_sum = index_shares * index_df[index][last]
            temp = (sum-yes_sum) # change from yesterday
            temp2 = (i_sum-i_yes_sum) # change from yesterday index
            pct_values.append(temp)  # percent daily
            pct_sum.append(last_sum+temp) # percent sum vals.
            pct_index_values.append(temp2) # percent daily
            pct_index_sum.append(last_index_sum + temp2)
            last_sum += temp
            last_index_sum += temp2
            print("Date", day, "yesterday's value:", yes_sum, "todays value:", sum)
        else:
            pct_values.append(0.0)
            pct_sum.append(0.0)
            pct_index_sum.append(0.0)
            pct_index_values.append(0.0)
        day_values.append(sum)
        index_day_values.append(i_sum)
        last = day
        #last_sum += ((sum-yes_sum)/yes_sum) * 100
    values = pd.DataFrame({'Date': df.index.tolist(), 'Value': day_values, 'Day Gain/Loss': pct_values, 'Gain/Loss': pct_sum,
                           'SPY Value': index_day_values, 'SPY Day Gain/Loss': pct_index_values, 'SPY Gain/Loss': pct_index_sum})  # off to a csv
    values.to_csv("portfolio_value.csv", index=False)
    #print(len(pct_values), len(df.index.tolist()))
    # plt.plot(df.index.tolist(), )
    # plt.show()


def portfolio_info(): # cost basis, ticker, name, etc
    holdings = []
    d = {}
    df = pd.read_csv("price_history.csv", index_col=0)
    with open("my_port.CSV") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[2] not in holdings and (row[1] == 'Buy' or row[1] == 'Sell' or row[1] == 'Reinvest' or row[1] == 'Dividend'):
                if row[2] != 'QACDS' and row[2] != 'QCDSM':
                    holdings.append(row[2])
            dt = pd.Timestamp(row[0])
            if dt in d:
                d[dt].append(row)
            else:
                d[dt] = [row]
    shares = {}
    cost_basis = {}
    costs = {}
    for ticker in holdings:
        shares[ticker] = 0
        cost_basis[ticker] = 0
        costs[ticker] = 0
    for day in df.index.tolist():
        if pd.to_datetime(day) in d.keys():  # incorporate trades for that day.
            for trade in d[pd.to_datetime(day)]:
                if (trade[1] == 'Buy' or trade[1] == 'Reinvest' or trade[1] == 'Reinvest Shares') and trade[2] != 'QACDS' and trade[2] != 'QCDSM':
                    shares[trade[2]] += float(trade[3])
                    costs[trade[2]] += float(trade[3]) * df[trade[2]][day]
                    if trade[1] == 'Buy':
                        if cost_basis[trade[2]] != 0:
                            cost_basis[trade[2]] = (cost_basis[trade[2]] + float(trade[3])) / 2
                            print(cost_basis)
                        else:
                            cost_basis[trade[2]] = float(trade[3])
                elif trade[1] == 'Sell':
                    shares[trade[2]] -= float(trade[3])
                    costs[trade[2]] -= float(trade[3]) * df[trade[2]][day]
                elif trade[1] == 'Exchange' and trade[2] != "":
                    shares[trade[2]] = float(trade[3])
                    if trade[2] == 'SKLZ': # SPACS!
                        cost_basis[trade[2]] = cost_basis['FEAC']
                        costs[trade[2]] = costs['FEAC']
                        del shares['FEAC']
                        del cost_basis['FEAC']
                        del costs['FEAC']
                    elif trade[2] == 'BFLY':
                        cost_basis[trade[2]] = cost_basis['LGVW']
                        costs[trade[2]] = costs['LGVW']
                        del shares['LGVW']
                        del cost_basis['LGVW']
                        del costs['LGVW']
                    elif trade[2] == 'GOEV':
                        cost_basis[trade[2]] = cost_basis['HCAC']
                        costs[trade[2]] = costs['HCAC']
                        del shares['HCAC']
                        del cost_basis['HCAC']
                        del costs['HCAC']
    # filter through the holdings we client no longer has
    old_shares = copy.deepcopy(shares)
    old_cost_basis = copy.deepcopy(cost_basis)
    old_costs = copy.deepcopy(costs)
    shares = dict()
    cost_basis = dict()
    costs = dict()
    for s in old_shares.keys():
        old_shares[s] = round(old_shares[s], 2)
        if float(abs(old_shares[s])) != 0.0:
            shares[s] = old_shares[s]
            cost_basis[s] = old_cost_basis[s]
            costs[s] = old_costs[s]
    i = 0  # abide by 60 requests/min
    names = []
    logos = []
    industries = []
    for ticker in shares.keys():  # grab some info on each of the tickers.
        if i == 60:
            i = 0
            time.sleep(60)
        r = requests.get('https://finnhub.io/api/v1/stock/profile2?symbol=' + ticker + '&token=brain17rh5rbgnjpuck0')
        r = r.json()
        if r == {}:
            names.append("ETF")
            logos.append("ETF")
            industries.append("ETF")
        else:
            names.append(r["name"])
            logos.append(r["logo"])
            industries.append(r["finnhubIndustry"])
        i += 1
    values = pd.DataFrame({'Ticker': shares.keys(), 'Shares': shares.values(), 'Avg Cost Basis': cost_basis.values(), 'Name': names, 'Logo': logos,
                           'Industry': industries})  # off to a csv
    values.to_csv("port_metrics.csv", index=False)
