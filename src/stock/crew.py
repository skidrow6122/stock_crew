from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from tools.stock_analysis_tool import stock_analysis_tool
from crewai_tools import SerperDevTool
from datetime import datetime
import yaml
from string import Template

def load_and_format_yaml(path: str, context: dict):
    with open(path, 'r', encoding='utf-8') as file:
        raw_yaml = file.read()
    return yaml.safe_load(Template(raw_yaml).substitute(context))

llm = ChatOpenAI(model="gpt-4o-mini")
invest_llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
search_tool = SerperDevTool()

@CrewBase
class StockAnalysisCrew:
    ## 초기화
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.current_time = datetime.now().strftime("%B %d, %Y")
        self.agents_config = load_and_format_yaml("config/agents.yaml", {
            "current_time": self.current_time
        })
        self.tasks_config = load_and_format_yaml("config/tasks.yaml", {
            "company_stock": self.ticker,
            "current_time": self.current_time
        })

## agent injection
    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_analyst"],
            tools=[stock_analysis_tool],
            llm=llm,
            max_iter=3,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["market_analyst"],
            tools=[search_tool],
            llm=llm,
            max_iter=3,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def risk_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_analyst"],
            tools=[stock_analysis_tool],
            llm=llm,
            max_iter=3,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def investment_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["investment_advisor"],
            llm=invest_llm,
            allow_delegation=False,
            verbose=True
        )

## taask injection
    @task
    def financial_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["financial_analysis"],
            agent=self.financial_analyst()
        )

    @task
    def market_analysis(self) -> Task:
        return Task(
            config=self.tasks_config["market_analysis"],
            agent=self.market_analyst()
        )

    @task
    def risk_assessment(self) -> Task:
        return Task(
            config=self.tasks_config["risk_assessment"],
            agent=self.risk_analyst()
        )

    @task
    def investment_recommendation(self) -> Task:
        return Task(
            config=self.tasks_config["investment_recommendation"],
            agent=self.investment_advisor()
        )

## crew final injection
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )