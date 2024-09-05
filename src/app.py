import requests
from datetime import datetime
import streamlit as st
import pandas as pd
from binance.um_futures import UMFutures

def get_binance_klines(symbol, interval, limit):
    try:
        um_futures_client = UMFutures()
        data = um_futures_client.klines(symbol, interval, limit=limit)
        return data
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP 错误: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"连接错误: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        st.error(f"请求超时: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        st.error(f"请求错误: {req_err}")
    except Exception as e:
        st.error(f"未知错误: {e}")
    return None


def calculate_percentage_change(current_price, historical_price):
    if historical_price == 0:
        return 0
    change = ((current_price - historical_price) / historical_price) * 100
    return change


def format_price(price_str):
    if '.' in price_str:
        price_str = price_str.rstrip('0').rstrip('.')
    return price_str


def main():
    st.title("币安合约涨幅查询工具")
    symbol = st.text_input("请输入代币符号（如BTC、ETH）", "BTC")

    st.markdown("""
        <style>
        div.stButton > button {
            background-color: pink;
            color: black;
            font-size: 16px;
            height: 3em;
            width: 10%;
            border-radius: 10px;
            border: 2px solid #ff1493;
        }
        </style>
        """, unsafe_allow_html=True)
    if st.button("查询"):
        if symbol:
            symbol = symbol.upper() + "USDT"
            interval = '1m'

            periods = {
                '1分钟': 1,
                '5分钟': 5,
                '10分钟': 10,
                '15分钟': 15,
                '30分钟': 30,
                '1小时': 60,
                '4小时': 240,
                '1天': 1440,
            }

            limit = max(periods.values()) + 1
            klines = get_binance_klines(symbol, interval, limit)

            if not klines or len(klines) < limit:
                st.error(f"从币安获取数据失败。")
                return

            current_price = float(klines[-1][4])
            formatted_price = format_price(klines[-1][4])
            st.markdown(f"**代币名: {symbol}, 价格：{formatted_price} USDT**", unsafe_allow_html=True)

            results = [["间隔", "价格 (USDT)", "时间", "涨幅 (%)"]]

            for label, minutes in periods.items():
                if minutes >= len(klines):
                    st.write(f"错误: 数据不足，无法计算{label}的涨幅。")
                    continue

                historical_kline = klines[-(minutes + 1)]
                historical_price = float(historical_kline[4])
                historical_close_time = datetime.fromtimestamp(historical_kline[6] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                change = calculate_percentage_change(current_price, historical_price)
                results.append([label, format_price(historical_kline[4]), historical_close_time, f"{change:.2f}%"])

            df = pd.DataFrame(results[1:], columns=results[0]).reset_index(drop=True)

            st.markdown("""
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 18px;
                }
                th, td {
                    text-align: center;
                    padding: 10px;
                    border: none;
                }
                th {
                    background-color: #f8f9fa;
                    font-weight: bold;
                    border-bottom: 2px solid #dee2e6;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                tr:nth-child(odd) {
                    background-color: #ffffff;
                }
                </style>
                """, unsafe_allow_html=True)

            table_html = df.to_html(index=False, escape=False)

            st.markdown("<h5 style='font-weight: bold; color: black;'>涨幅数据:</h5>", unsafe_allow_html=True)
            st.markdown(table_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()