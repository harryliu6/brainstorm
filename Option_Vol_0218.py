import signal
import requests
from time import sleep
import math
# from arch import arch_model
import numpy as np
import scipy.stats as si
from itertools import repeat

# IMPORTANT PARAMETERS
delta_limit = input("The delta limit for this sub-heat is:")
delta_limit_1 = int(delta_limit)
# speedbump = 0.5
r = 0
contingency = 0.28


# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass


# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True


# set your API key to authenticate to the RIT client
API_KEY = {'X-API-Key': 'AZXZTB62'}
shutdown = False


# other settings

# this helper method returns the period of the running case
def get_period(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.status_code == 401:
        raise ApiException('Authorization error please check API key ')
    case = resp.json()
    return case['period']


# this helper method returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.status_code == 401:
        raise ApiException('Authorization error please check API key ')
    case = resp.json()
    return case['tick']


# this helper method returns the last close price for the given security, one tick ago
def ticker_close(session, ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = session.get('http://localhost:9999/v1/securities/history', params=payload)
    if resp.status_code == 401:
        raise ApiException('API key error')
    ticker_history = resp.json()
    if ticker_history:
        return ticker_history[0]['close']
    else:
        raise ApiException('Response error. Unexpected JSON response.')


# returns current positions
def get_position(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities', params=payload)
    if resp.status_code == 401:
        raise ApiException('ij')
    securities = resp.json()
    return securities[0]['position']


#####################################################################################################################################

# BS pricing
def Black_Scholes(S, K, T, r, sigma, option):
    # S: spot price
    # K: strike price
    # T: time to maturity
    # r: interest rate
    # sigma: volatility of underlying asset
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option == 'call':
        result = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    if option == 'put':
        result = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return result


#####################################################################################################################################
# Printing the Greeks
# 1. Delta
def delta(S, K, T, r, sigma, option):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option == 'call':
        delta_result = si.norm.cdf(d1, 0.0, 1.0)
    if option == 'put':
        delta_result = -si.norm.cdf(-d1, 0.0, 1.0)
    return delta_result


def total_delta(de, pos):
    total = de * pos * 100

    return total


def minus(a, b):
    resu_m = a - b

    return resu_m


def diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif


def get_news_tick(session):
    resp = session.get('http://localhost:9999/v1/news?limit=30')
    if resp.status_code == 401:
        raise ApiException('Authorization error please check API key')
    news_tick = resp.json()
    return news_tick[0]['tick']


#####################################################################################################################################

ticker_12_call = ['RTM1C45', 'RTM1C46', 'RTM1C47', 'RTM1C48', 'RTM1C49',
                  'RTM1C50', 'RTM1C51', 'RTM1C52', 'RTM1C53', 'RTM1C54']

ticker_12_put = ['RTM1P45', 'RTM1P46', 'RTM1P47', 'RTM1P48', 'RTM1P49',
                 'RTM1P50', 'RTM1P51', 'RTM1P52', 'RTM1P53', 'RTM1P54']

ticker_strike = [45, 46, 47, 48, 49, 50, 51, 52, 53, 54,
                 45, 46, 47, 48, 49, 50, 51, 52, 53, 54]

ticker_22_call = ['RTM2C45', 'RTM2C46', 'RTM2C47', 'RTM2C48', 'RTM2C49',
                  'RTM2C50', 'RTM2C51', 'RTM2C52', 'RTM2C53', 'RTM2C54']

ticker_22_put = ['RTM2P45', 'RTM2P46', 'RTM2P47', 'RTM2P48', 'RTM2P49',
                 'RTM2P50', 'RTM2P51', 'RTM2P52', 'RTM2P53', 'RTM2P54']

ticker_strike_22 = [45, 46, 47, 48, 49, 50, 51, 52, 53, 54]

ticker_all_call = ['RTM1C45', 'RTM1C46', 'RTM1C47', 'RTM1C48', 'RTM1C49',
                   'RTM1C50', 'RTM1C51', 'RTM1C52', 'RTM1C53', 'RTM1C54',
                   'RTM2C45', 'RTM2C46', 'RTM2C47', 'RTM2C48', 'RTM2C49',
                   'RTM2C50', 'RTM2C51', 'RTM2C52', 'RTM2C53', 'RTM2C54']

ticker_all_put = ['RTM1P45', 'RTM1P46', 'RTM1P47', 'RTM1P48', 'RTM1P49',
                  'RTM1P50', 'RTM1P51', 'RTM1P52', 'RTM1P53', 'RTM1P54',
                  'RTM2P45', 'RTM2P46', 'RTM2P47', 'RTM2P48', 'RTM2P49',
                  'RTM2P50', 'RTM2P51', 'RTM2P52', 'RTM2P53', 'RTM2P54']


################################################ PERIOD 1#############################################
def tradebs():
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        ntick = get_news_tick(s)

        if ntick == 0:
            sig = 0.2
        else:
            if ntick % 75 == 0:
                def get_news_75(session):
                    resp = session.get('http://localhost:9999/v1/news?limit=30')
                    if resp.status_code == 401:
                        raise ApiException('Authorization error please check API key')
                    news_late = resp.json()
                    return news_late[0]['body']

                news_late_vol = get_news_75(s)
                sig = int(news_late_vol[-3:-1]) / 100

            if ntick % 75 != 0:
                def get_news_37(session):
                    resp = session.get('http://localhost:9999/v1/news?limit=30')
                    if resp.status_code == 401:
                        raise ApiException('Authorization error please check API key')
                    news_early = resp.json()
                    return news_early[0]['body']

                news_early_vol = get_news_37(s)
                sig = (int(news_early_vol[-32:-30]) + int(news_early_vol[-26:-24])) / 200

        sigma = float(sig)
        sigma = sigma / math.sqrt(252)
        print(sigma)

        price_rtm = ticker_close(s, 'RTM')

        p_20 = [s, s, s, s, s, s, s, s, s, s]
        p_21 = [s, s, s, s, s, s, s, s, s, s, s, s, s, s, s, s, s, s, s, s]

        # Test the map function, see if it will run functions with multiple arguments; they should return in lists
        ticker_last_call = list(map(ticker_close, p_20, ticker_12_call))
        ticker_last_put = list(map(ticker_close, p_20, ticker_12_put))
        ticker_bs_call = list(
            map(Black_Scholes, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_bs_put = list(
            map(Black_Scholes, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))

        ticker_last_call_2 = list(map(ticker_close, p_20, ticker_22_call))
        ticker_last_put_2 = list(map(ticker_close, p_20, ticker_22_put))
        ticker_bs_call_2 = list(
            map(Black_Scholes, repeat(price_rtm), ticker_strike_22, repeat((600 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_bs_put_2 = list(
            map(Black_Scholes, repeat(price_rtm), ticker_strike_22, repeat((600 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))

        ticker_last_all_call = list(map(ticker_close, p_21, ticker_all_call))
        ticker_last_all_put = list(map(ticker_close, p_21, ticker_all_put))

        ######################################################################DELTA DONE#######################################
        ticker_call_600_delta = list(
            map(delta, repeat(price_rtm), ticker_strike, repeat((600 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_put_600_delta = list(
            map(delta, repeat(price_rtm), ticker_strike, repeat((600 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))
        ticker_call_600_1_delta = list(
            map(delta, repeat(price_rtm), ticker_strike_22, repeat((600 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_put_600_1_delta = list(
            map(delta, repeat(price_rtm), ticker_strike_22, repeat((600 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))

        ticker_call_300_delta = list(
            map(delta, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_put_300_delta = list(
            map(delta, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))

        ticker_call_delta_1 = diff(ticker_call_600_delta, ticker_call_600_1_delta)
        ticker_call_delta = ticker_call_300_delta + ticker_call_delta_1
        ticker_put_delta_1 = diff(ticker_put_600_delta, ticker_put_600_1_delta)
        ticker_put_delta = ticker_put_300_delta + ticker_put_delta_1

        ticker_call_position = list(map(get_position, p_21, ticker_all_call))
        ticker_put_position = list(map(get_position, p_21, ticker_all_put))

        RTM_position = get_position(s, 'RTM')
        RTM_delta = 1 * RTM_position

        position_total_delta_call = list(map(total_delta, ticker_call_delta, ticker_call_position))
        position_total_delta_put = list(map(total_delta, ticker_put_delta, ticker_put_position))

        position_delta = sum(position_total_delta_call) + sum(position_total_delta_put) + RTM_delta
        ##################################################################DELTA DONE########################################################

        ticker_spread_bs_call_1 = list(map(minus, ticker_last_call, ticker_bs_call))
        ticker_spread_bs_put_1 = list(map(minus, ticker_last_put, ticker_bs_put))
        ticker_spread_bs_call_2 = list(map(minus, ticker_last_call_2, ticker_bs_call_2))
        ticker_spread_bs_put_2 = list(map(minus, ticker_last_put_2, ticker_bs_put_2))
        ticker_spread_bs_call = ticker_spread_bs_call_1 + ticker_spread_bs_call_2
        ticker_spread_bs_put = ticker_spread_bs_put_1 + ticker_spread_bs_put_2

        print(ticker_spread_bs_call)
        print(ticker_spread_bs_put)

        # trade on mispricing opportunity
        for i in range(0, len(ticker_spread_bs_call)):
            if ticker_spread_bs_call[i] >= contingency:
                sell_payload = {'ticker': ticker_all_call[i], 'type': 'MARKET', 'quantity': 20, 'action': 'SELL',
                                'price': ticker_last_all_call[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            # sell ticker_12_call[i]
            if ticker_spread_bs_call[i] <= (-1) * contingency:
                buy_payload = {'ticker': ticker_all_call[i], 'type': 'MARKET', 'quantity': 20, 'action': 'BUY',
                               'price': ticker_last_all_call[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

                # buy ticker_12_call[i]

        for i in range(0, len(ticker_spread_bs_put)):
            if ticker_spread_bs_put[i] >= contingency:
                sell_payload = {'ticker': ticker_all_put[i], 'type': 'MARKET', 'quantity': 20, 'action': 'SELL',
                                'price': ticker_last_all_put[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)

            # sell ticker_12_put[i]
            if ticker_spread_bs_put[i] <= (-1) * contingency:
                buy_payload = {'ticker': ticker_all_put[i], 'type': 'MARKET', 'quantity': 20, 'action': 'BUY',
                               'price': ticker_last_all_put[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

        # close position
        for i in range(0, len(ticker_call_position)):
            if ticker_call_position[i] > 0 and ticker_spread_bs_call[i] > -0.015:
                sell_payload = {'ticker': ticker_all_call[i], 'type': 'MARKET', 'quantity': 20,
                                'action': 'SELL', 'price': ticker_last_all_call[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            if ticker_call_position[i] < 0 and ticker_spread_bs_call[i] < 0.015:
                buy_payload = {'ticker': ticker_all_call[i], 'type': 'MARKET', 'quantity': 20,
                               'action': 'BUY', 'price': ticker_last_all_call[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)
        for i in range(0, len(ticker_put_position)):
            if ticker_put_position[i] > 0 and ticker_spread_bs_put[i] > -0.015:
                sell_payload = {'ticker': ticker_all_put[i], 'type': 'MARKET', 'quantity': 20,
                                'action': 'SELL', 'price': ticker_last_all_put[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            if ticker_put_position[i] < 0 and ticker_spread_bs_put[i] < 0.015:
                buy_payload = {'ticker': ticker_all_put[i], 'type': 'MARKET', 'quantity': 20,
                               'action': 'BUY', 'price': ticker_last_all_put[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

        ##########DELTA NEUTRAL###############################
        if position_delta > delta_limit_1:
            # quantity_sell = position_delta - delta_limit_1
            price_rtm_sell = ticker_close(s, 'RTM')
            sell_payload = {'ticker': 'RTM', 'type': 'MARKET', 'quantity': 5000, 'action': 'SELL',
                            'price': price_rtm_sell}
            s.post('http://localhost:9999/v1/orders', params=sell_payload)

        if position_delta < (-1) * delta_limit_1:
            # quantity_buy = (-1) * delta_limit_1 - position_delta
            price_rtm_buy = ticker_close(s, "RTM")
            buy_payload = {'ticker': "RTM", 'type': 'MARKET', 'quantity': 5000, 'action': 'BUY',
                           'price': price_rtm_buy}
            s.post('http://localhost:9999/v1/orders', params=buy_payload)
            # buy ticker_12_put[i]

        if position_delta == RTM_position:
            if RTM_position > 0:
                price_rtm_sell = ticker_close(s, 'RTM')
                sell_payload = {'ticker': 'RTM', 'type': 'MARKET', 'quantity': 5000, 'action': 'SELL',
                                'price': price_rtm_sell}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            if RTM_position < 0:
                price_rtm_buy = ticker_close(s, "RTM")
                buy_payload = {'ticker': "RTM", 'type': 'MARKET', 'quantity': 5000, 'action': 'BUY',
                               'price': price_rtm_buy}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

        print(position_delta)


##############################################################PERIOD 2##########################################################

def tradebs_2():
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        ntick = get_news_tick(s)

        if ntick == 0:
            sig = 0.2
        else:
            if ntick % 75 == 0:
                def get_news_75(session):
                    resp = session.get('http://localhost:9999/v1/news?limit=30')
                    if resp.status_code == 401:
                        raise ApiException('Authorization error please check API key')
                    news_late = resp.json()
                    return news_late[0]['body']

                news_late_vol = get_news_75(s)
                sig = int(news_late_vol[-3:-1]) / 100

            if ntick % 75 != 0:
                def get_news_37(session):
                    resp = session.get('http://localhost:9999/v1/news?limit=30')
                    if resp.status_code == 401:
                        raise ApiException('Authorization error please check API key')
                    news_early = resp.json()
                    return news_early[0]['body']

                news_early_vol = get_news_37(s)
                sig = (int(news_early_vol[-32:-30]) + int(news_early_vol[-26:-24])) / 200

        sigma = float(sig)
        sigma = sigma / math.sqrt(252)
        print(sigma)

        price_rtm = ticker_close(s, 'RTM')

        p_10 = [s, s, s, s, s, s, s, s, s, s]

        ticker_last_call_2 = list(map(ticker_close, p_10, ticker_22_call))
        ticker_last_put_2 = list(map(ticker_close, p_10, ticker_22_put))
        ticker_bs_call_2 = list(
            map(Black_Scholes, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_bs_put_2 = list(
            map(Black_Scholes, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))

        ticker_call_delta_2 = list(
            map(delta, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('call')))
        ticker_put_delta_2 = list(
            map(delta, repeat(price_rtm), ticker_strike_22, repeat((300 - tick) / 15), repeat(r), repeat(sigma),
                repeat('put')))

        ticker_call_position_2 = list(map(get_position, p_10, ticker_22_call))
        ticker_put_position_2 = list(map(get_position, p_10, ticker_22_put))

        RTM_position = get_position(s, 'RTM')
        RTM_delta = 1 * RTM_position

        position_total_delta_call_2 = list(map(total_delta, ticker_call_delta_2, ticker_call_position_2))
        position_total_delta_put_2 = list(map(total_delta, ticker_put_delta_2, ticker_put_position_2))

        position_delta_2 = sum(position_total_delta_call_2) + sum(position_total_delta_put_2) + RTM_delta

        ticker_spread_bs_call_2 = list(map(minus, ticker_last_call_2, ticker_bs_call_2))
        ticker_spread_bs_put_2 = list(map(minus, ticker_last_put_2, ticker_bs_put_2))

        print(ticker_spread_bs_call_2)
        print(ticker_spread_bs_put_2)

        # trade on mispricing opportunity
        for i in range(0, len(ticker_spread_bs_call_2)):
            if ticker_spread_bs_call_2[i] >= contingency:
                sell_payload = {'ticker': ticker_22_call[i], 'type': 'MARKET', 'quantity': 20, 'action': 'SELL',
                                'price': ticker_last_call_2[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            # sell ticker_12_call[i]
            if ticker_spread_bs_call_2[i] <= (-1) * contingency:
                buy_payload = {'ticker': ticker_22_call[i], 'type': 'MARKET', 'quantity': 20, 'action': 'BUY',
                               'price': ticker_last_call_2[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

                # buy ticker_12_call[i]

        for i in range(0, len(ticker_spread_bs_put_2)):
            if ticker_spread_bs_put_2[i] >= contingency:
                sell_payload = {'ticker': ticker_22_put[i], 'type': 'MARKET', 'quantity': 20, 'action': 'SELL',
                                'price': ticker_last_put_2[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)

            # sell ticker_12_put[i]
            if ticker_spread_bs_put_2[i] <= (-1) * contingency:
                buy_payload = {'ticker': ticker_22_put[i], 'type': 'MARKET', 'quantity': 20, 'action': 'BUY',
                               'price': ticker_last_put_2[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

        # close position
        for i in range(0, len(ticker_call_position_2)):
            if ticker_call_position_2[i] > 0 and ticker_spread_bs_call_2[i] > -0.015:
                sell_payload = {'ticker': ticker_22_call[i], 'type': 'MARKET', 'quantity': 20,
                                'action': 'SELL', 'price': ticker_last_call_2[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            if ticker_call_position_2[i] < 0 and ticker_spread_bs_call_2[i] < 0.015:
                buy_payload = {'ticker': ticker_22_call[i], 'type': 'MARKET', 'quantity': 20,
                               'action': 'BUY', 'price': ticker_last_call_2[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)
        for i in range(0, len(ticker_put_position_2)):
            if ticker_put_position_2[i] > 0 and ticker_spread_bs_put_2[i] > -0.015:
                sell_payload = {'ticker': ticker_22_put[i], 'type': 'MARKET', 'quantity': 20,
                                'action': 'SELL', 'price': ticker_last_put_2[i]}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            if ticker_put_position_2[i] < 0 and ticker_spread_bs_put_2[i] < 0.015:
                buy_payload = {'ticker': ticker_22_put[i], 'type': 'MARKET', 'quantity': 20,
                               'action': 'BUY', 'price': ticker_last_put_2[i]}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

        # delta neutral

        if position_delta_2 > delta_limit_1:
            # quantity_sell = position_delta - delta_limit_1
            price_rtm_sell = ticker_close(s, 'RTM')
            sell_payload = {'ticker': 'RTM', 'type': 'MARKET', 'quantity': 5000, 'action': 'SELL',
                            'price': price_rtm_sell}
            s.post('http://localhost:9999/v1/orders', params=sell_payload)

        if position_delta_2 < (-1) * delta_limit_1:
            # quantity_buy = (-1) * delta_limit_1 - position_delta
            price_rtm_buy = ticker_close(s, "RTM")
            buy_payload = {'ticker': "RTM", 'type': 'MARKET', 'quantity': 5000, 'action': 'BUY',
                           'price': price_rtm_buy}
            s.post('http://localhost:9999/v1/orders', params=buy_payload)
            # buy ticker_12_put[i]

        if position_delta_2 == RTM_position:
            if RTM_position > 0:
                price_rtm_sell = ticker_close(s, 'RTM')
                sell_payload = {'ticker': 'RTM', 'type': 'MARKET', 'quantity': 5000, 'action': 'SELL',
                                'price': price_rtm_sell}
                s.post('http://localhost:9999/v1/orders', params=sell_payload)
            if RTM_position < 0:
                price_rtm_buy = ticker_close(s, "RTM")
                buy_payload = {'ticker': "RTM", 'type': 'MARKET', 'quantity': 5000, 'action': 'BUY',
                               'price': price_rtm_buy}
                s.post('http://localhost:9999/v1/orders', params=buy_payload)

        print(position_delta_2)


# Either use RTM to hedge or change the contingency smaller so it will close the order sooner

# Calculate the total delta we have with our positions and use RTM to hedge the delta


# use map and list function to do the BS, price, and delta
# get lists and do main

def main():
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        period = get_period(s)
        while tick > 0 and tick < 298 and not shutdown:
            if period == 1:
                tradebs()
            else:
                tradebs_2()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
