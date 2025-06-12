from crewai.tools import tool
import yfinance as yf
import pandas as pd
from datetime import datetime

@tool("Stock Analysis Tool")
def stock_analysis_tool(ticker: str) -> dict:
    """
        Analyzes a stock ticker and returns comprehensive financial data including annual/quarterly metrics, growth rates, and current stock price.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def format_number(number):
        if number is None or pd.isna(number):
            return "N/A"
        return f"{number:,.0f}"

    def calculate_growth_rate(current, previous):
        if previous and current != 0:
            return (current - previous) / abs(previous) * 100
        return None

    def format_financial_summary(financials):
        summary = {}
        for date, data in financials.items():
            date_str = date.strftime("%Y-%m-%d")
            summary[date_str] = {
                "총수익": data.get('TotalRevenue'),
                "영업이익": data.get('OperatingIncome'),
                "순이익": data.get('NetIncome'),
                "EBITDA": data.get('EBITDA')
            }
        return summary

    ticker_obj = yf.Ticker(ticker)
    historical_prices = ticker_obj.history(period="1d", interval="1m")
    latest_price = historical_prices['Close'].iloc[-1]
    latest_time = historical_prices.index[-1].strftime("%Y-%m-%d %H:%M:%S")

    annual_financials = ticker_obj.get_financials()
    quarterly_financials = ticker_obj.get_financials(freq="quarterly")
    balance_sheet = ticker_obj.get_balance_sheet()

    revenue = annual_financials.loc["TotalRevenue", annual_financials.columns[0]]
    cost_of_revenue = annual_financials.loc["CostOfRevenue", annual_financials.columns[0]]
    gross_profit = annual_financials.loc["GrossProfit", annual_financials.columns[0]]
    operating_income = annual_financials.loc["OperatingIncome", annual_financials.columns[0]]
    net_income = annual_financials.loc["NetIncome", annual_financials.columns[0]]
    ebitda = annual_financials.loc["EBITDA", annual_financials.columns[0]]

    total_assets = balance_sheet.loc["TotalAssets", balance_sheet.columns[0]]
    total_liabilities = balance_sheet.loc["TotalLiabilitiesNetMinorityInterest", balance_sheet.columns[0]]
    debt_ratio = (total_liabilities / total_assets) * 100 if total_assets != 0 else None

    gross_margin = (gross_profit / revenue) * 100 if revenue != 0 else None
    operating_margin = (operating_income / revenue) * 100 if revenue != 0 else None
    net_margin = (net_income / revenue) * 100 if revenue != 0 else None

    revenue_growth = calculate_growth_rate(
        revenue, annual_financials.loc["TotalRevenue", annual_financials.columns[1]]
    )
    net_income_growth = calculate_growth_rate(
        net_income, annual_financials.loc["NetIncome", annual_financials.columns[1]]
    )

    diluted_eps = annual_financials.loc["DilutedEPS", annual_financials.columns[0]]

    quarterly_revenue = quarterly_financials.loc['TotalRevenue', quarterly_financials.columns[0]]
    quarterly_net_income = quarterly_financials.loc['NetIncome', quarterly_financials.columns[0]]
    quarterly_revenue_growth = calculate_growth_rate(
        quarterly_revenue, quarterly_financials.loc['TotalRevenue', quarterly_financials.columns[1]]
    )
    quarterly_net_income_growth = calculate_growth_rate(
        quarterly_net_income, quarterly_financials.loc['NetIncome', quarterly_financials.columns[1]]
    )

    return {
        "기준 일시": current_time,
        "현재 주가": {
            "현재 주가": latest_price,
            "기준 시간": latest_time
        },
        "연간 데이터": {
            "매출": format_number(revenue),
            "매출원가": format_number(cost_of_revenue),
            "매출총이익": format_number(gross_profit),
            "영업이익": format_number(operating_income),
            "순이익": format_number(net_income),
            "EBITDA": format_number(ebitda),
            "매출총이익률": f"{gross_margin:.2f}%" if gross_margin is not None else "N/A",
            "영업이익률": f"{operating_margin:.2f}%" if operating_margin is not None else "N/A",
            "순이익률": f"{net_margin:.2f}%" if net_margin is not None else "N/A",
            "매출 성장률": f"{revenue_growth:.2f}%" if revenue_growth is not None else "N/A",
            "순이익 성장률": f"{net_income_growth:.2f}%" if net_income_growth is not None else "N/A",
            "희석주당순이익(EPS)": f"{diluted_eps:.2f}" if diluted_eps is not None else "N/A",
            "부채비율": f"{debt_ratio:.2f}%" if debt_ratio is not None else "N/A",
        },
        "분기 데이터": {
            "매출": format_number(quarterly_revenue),
            "순이익": format_number(quarterly_net_income),
            "매출 성장률(QoQ)": f"{quarterly_revenue_growth:.2f}%" if quarterly_revenue_growth is not None else "N/A",
            "순이익 성장률(QoQ)": f"{quarterly_net_income_growth:.2f}%" if quarterly_net_income_growth is not None else "N/A",
        },
        "연간 재무제표 요약": format_financial_summary(annual_financials),
        "분기별 재무제표 요약": format_financial_summary(quarterly_financials),
    }