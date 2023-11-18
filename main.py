from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import StructuredTool
import os
import requests
from utils import get_next_task


api_key = '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'
os.environ['OPENAI_API_KEY'] = api_key


llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)



def take_environment_action(action: str) -> float:
    """Take an action within the household environment."""
    url = 'http://localhost:8000/take_action'
    data = {
        "action": action
    }

    response = requests.post(url, json=data)
    json_response = response.json()
    observation = json_response.get("observation")
    return observation


tool = StructuredTool.from_function(take_environment_action)


agent_executor = initialize_agent(
    [tool],
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)


task_prompt = get_next_task()

print(agent_executor.run(task_prompt))



# # from langchain import hub
# # prompt = hub.pull("hwchase17/react-multi-input-json")


# # from langchain.tools.render import render_text_description_and_args
# # prompt = prompt.partial(
# #     tools=render_text_description_and_args(tools),
# #     tool_names=", ".join([t.name for t in tools]),
# # )
# llm = ChatOpenAI(model='gpt-4-1106-preview', temperature=0)

# print(llm.invoke('Do you know about LangChain? It is a python framework for building applications with Large Language Models. If you do, I need you to help me with something. I am trying to build a "structured-chat-zero-shot" agent, i.e., a ReAct agent that is able to use tools with multiple arguments. Right now, I would like to create such an agent, as well as a custom tool called "take_environment_action" that takes 1 argument called "action". Basically, the agent will be prompted with a problem such as "find the apple" and it will call "take_environment_action" with parameter such as "go to kitchen 1" to take actions in a virtual environment. The implementation of "take_environment_action" should simply call an API located on at localhost:8000/take_action. This is a POST endpoint, and the body needs to be a JSON with one keyword "action" with the value of the string passed into "take_environment_action". \n\n What I would like for you to do is to output the contents of a python file that implements everything I said before. Please do not output anything other than python code.'))

# exit()


# # llm_with_stop = llm.bind(stop=["Observation"])


# from langchain.agents.format_scratchpad import format_log_to_str
# from langchain.agents.output_parsers import JSONAgentOutputParser
# agent = (
#     {
#         "input": lambda x: x["input"],
#         "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
#     }
#     | prompt
#     | llm_with_stop
#     | JSONAgentOutputParser()
# )


# from langchain.agents import AgentExecutor
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# response = await agent_executor.ainvoke(
#     {"input": "Browse to blog.langchain.dev and summarize the text, please."}
# )
# print(response["output"])





# import os

# api_key = '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'

# # os.environ['LANGCHAIN_TRACING_V2'] = 'false'
# # os.environ['LANGCHAIN_API_KEY'] = api_key
# os.environ['OPENAI_API_KEY'] = api_key
# from langchain.chat_models import ChatOpenAI

# llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

# # print(os.environ['LANGCHAIN_TRACING_V2'])
# # print(os.environ['LANGCHAIN_API_KEY'])
# # print(os.environ['OPENAI_API_KEY'])

# # answer = llm.invoke('how many letters are in the word educa?')

# # print(answer)
# # print(type(answer))

# from langchain.agents import tool

# @tool
# def get_word_length(word: str) -> int:
#     """Returns the length of a word."""
#     return len(word)

# tools = [get_word_length]

# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are very powerful assistant, but bad at calculating lengths of words.",
#         ),
#         ("user", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ]
# )

# from langchain.tools.render import format_tool_to_openai_function

# llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])



# from langchain.agents.format_scratchpad import format_to_openai_function_messages
# from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

# agent = (
#     {
#         "input": lambda x: x["input"],
#         "agent_scratchpad": lambda x: format_to_openai_function_messages(
#             x["intermediate_steps"]
#         ),
#     }
#     | prompt
#     | llm_with_tools
#     | OpenAIFunctionsAgentOutputParser()
# )

# # response = agent.invoke({"input": "how many letters in the word educa?", "intermediate_steps": []})








# # from langchain.schema.agent import AgentFinish

# # user_input = "how many letters in the word educa?"
# # intermediate_steps = []
# # while True:
# #     output = agent.invoke(
# #         {
# #             "input": user_input,
# #             "intermediate_steps": intermediate_steps,
# #         }
# #     )
# #     if isinstance(output, AgentFinish):
# #         final_result = output.return_values["output"]
# #         break
# #     else:
# #         print(f"TOOL NAME: {output.tool}")
# #         print(f"TOOL INPUT: {output.tool_input}")
# #         tool = {"get_word_length": get_word_length}[output.tool]
# #         observation = tool.run(output.tool_input)
# #         intermediate_steps.append((output, observation))
# # print(final_result)


# from langchain.agents import AgentExecutor

# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# # res = agent_executor.invoke({"input": "how many letters in the word educa?"})

# # print("***************")
# # print(res)

# from langchain.prompts import MessagesPlaceholder

# MEMORY_KEY = "chat_history"
# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are very powerful assistant, but bad at calculating lengths of words.",
#         ),
#         MessagesPlaceholder(variable_name=MEMORY_KEY),
#         ("user", "{input}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ]
# )

# from langchain.schema.messages import AIMessage, HumanMessage

# chat_history = []

# agent = (
#     {
#         "input": lambda x: x["input"],
#         "agent_scratchpad": lambda x: format_to_openai_function_messages(
#             x["intermediate_steps"]
#         ),
#         "chat_history": lambda x: x["chat_history"],
#     }
#     | prompt
#     | llm_with_tools
#     | OpenAIFunctionsAgentOutputParser()
# )
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# input1 = "how many letters in the word educa?"
# result = agent_executor.invoke({"input": input1, "chat_history": chat_history})
# chat_history.extend(
#     [
#         HumanMessage(content=input1),
#         AIMessage(content=result["output"]),
#     ]
# )
# agent_executor.invoke({"input": "is that a real word?", "chat_history": chat_history})