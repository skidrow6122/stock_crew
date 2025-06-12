from crew import StockAnalysisCrew
from datetime import datetime
from dotenv import load_dotenv

# Jupyter 환경 체크 후 조건부 출력포맷 import
try:
    from IPython.display import display, Markdown
    JUPYTER_AVAILABLE = True
except ImportError:
    JUPYTER_AVAILABLE = False

load_dotenv()  # .env 파일에 있는 환경변수 로드

def run():
    ticker = input("Which company would you like to analyze? Enter ticker (e.g. AAPL): ").strip().upper()
    inputs = {
        "company_stock": ticker,
        "current_time": datetime.now().strftime("%B %d, %Y")
    }
    result = StockAnalysisCrew(ticker).crew().kickoff(inputs=inputs)
    print("Analysis Result")
    # Jupyter 환경에서는 Markdown으로 렌더링
    if JUPYTER_AVAILABLE:
        try:
            display(Markdown(result.raw))
        except:
            # result.raw가 없으면 str(result) 사용
            display(Markdown(str(result)))
    else:
        # 일반 터미널에서는 텍스트로 출력
        print(result)


if __name__ == "__main__":
    print("Stock Analysis Crew Multi Agent Started")
    run()