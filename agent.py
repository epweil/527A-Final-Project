from langchain.agents import AgentType, Tool, initialize_agent 
from langchain.llms import OpenAI
from langchain.tools import StructuredTool
from debate import run
from pydantic import BaseModel, BaseSettings, Field



tools = [
                StructuredTool.from_function(
                func= run,
                name="Debate",
                description="useful for when you need to decide on an action in a situation. The input to this tool should be a word for word description of the situation'"
                )
                ]               
    


llm = OpenAI(temperature=0.1, model_name="gpt-3.5-turbo")
react = initialize_agent(tools, llm, verbose=True)
situation = "You are in a room with three doors. One leads to saftey the other two have fire behind them. What do you do first."
print(react(situation))