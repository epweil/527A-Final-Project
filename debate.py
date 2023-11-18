##Ethan Weilheimer 
##CSE 527A LLM Agent Paper 
##Code adapted from Cobus Greyling (https://cobusgreyling.medium.com/two-llm-based-autonomous-agents-debate-each-other-e13e0a54429b)
from typing import List, Dict, Callable
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from typing import Optional, Type
from langchain.tools import BaseTool

from pydantic import BaseModel, BaseSettings, Field

class DialogueAgent:
        def __init__(self,name: str,system_message: SystemMessage,model: ChatOpenAI,) -> None:
                self.name = name
                self.system_message = system_message
                self.model = model
                self.prefix = f"{self.name}: "
                

        def reset(self):
                self.message_history = ["Here is the conversation so far."]

        def send(self) -> str:
                message = self.model(
                [
                        self.system_message,
                        HumanMessage(content="\n".join(self.message_history + [self.prefix])),
                ]
                )
                return message.content

        def receive(self, name: str, message: str) -> None:
                self.message_history.append(f"{name}: {message}")



class ModeratorDialogueAgent():
        def __init__(self,name: str,system_message: SystemMessage,model: ChatOpenAI,situation) -> None:
                self.name = name
                self.system_message = system_message
                self.model = model
                self.prefix = f"{self.name}: "
                self.situation = situation
                

        def reset(self):
                self.message_history = ["Situation: " + self.situation]

        def start(self) -> str:
                message = self.model(
                
                        self.system_message
                
                )
                return message.content

        def end(self) -> str:
                message = self.model(
                [
                SystemMessage(content="Given the following message history, you the moderator will give your final decison on what to do. \n Just state what your final idea is, do not state any reasoning"),
                HumanMessage(content="\n".join(self.message_history) + "\n Moderator:"),
                ]
                )
                return message.content
        
        def receive(self, name: str, message: str) -> None:
                self.message_history.append(f"{name}: {message}")


class DialogueSimulator:
    
    def __init__(self,moderator:ModeratorDialogueAgent, agents: List[DialogueAgent],selection_function: Callable[[int, List[DialogueAgent]], int],) -> None:
        self.agents = agents
        self.moderator = moderator
        self._step = 0
        self.select_next_speaker = selection_function

    def voidStep(self):
        self._step +=1
    def reset(self):
        for agent in self.agents:
            agent.reset()
        self.moderator.reset()
    def inject(self, name: str, message: str):
        for agent in self.agents:
            agent.receive(name, message)
        self._step += 1

    def step(self) -> tuple[str, str]:
            
        speaker_idx = self.select_next_speaker(self._step, self.agents)
        speaker = self.agents[speaker_idx]
        message = speaker.send()


        for receiver in self.agents:
            receiver.receive(speaker.name, message)
        self.moderator.receive(speaker.name, message)
        self._step += 1

        return speaker.name, message
    
    def start(self) -> tuple[str, str]:
        speaker = self.moderator
        message = speaker.start()


        for receiver in self.agents:
            receiver.receive(speaker.name, message)
        self.moderator.receive(speaker.name, message)

        return speaker.name, message

    def end(self) -> tuple[str, str]:
        speaker = self.moderator
        message = speaker.end()

        self.moderator.receive(speaker.name, message)
        return speaker.name, message
    






def generate_system_message(name, description):
            return f"""
    
                Your name is {name}.

                Your description is as follows: {description}

                Your goal is to persuade your conversation partner of your point of view.

                DO look up information with your tool to refute your partner's claims.
                DO NOT fabricate fake citations.
                DO NOT cite any source that you did not look up.
                Do not add anything else.
                Stop speaking the moment you finish speaking from your perspective.
                """

def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
        idx = (step) % len(agents)
        return idx



    

def run(situation):
    negativeFirst = False
    max_iters = 2
    temperature = 0.1
    names = {
        "AI affirm": ["gpt-3.5-turbo"],
        "AI negative": ["gpt-3.5-turbo"],
    }
    descriptions= {
        "AI affirm": "Your job is to fight that the opinion you are given is correct",
        "AI negative": "Your job is to fight that the opinion you are given is wrong",
    }


    conversation_description = f"""Here is the situation at hand: {situation}
        The participants are: {', '.join(names.keys())}"""    
    firstAgent = "AI positive"
    if(negativeFirst):
        firstAgent = "AI negative"

    

    topic_specifier_prompt = [
        HumanMessage(
            content=f"""
            You are trying to decide what the best move in the following situation is {situation}
            Come up with your decision and then speak with the participants: AI affirm, AI negative to get their opinions on your choice.
            You will hear from {firstAgent} first"""
        ),
    ]



    agent_system_messages = {
        name: generate_system_message(name, descriptions[name])
        for name in names
    }

    
    agents = [
        DialogueAgent(
            name="AI affirm",
            system_message=SystemMessage(content=agent_system_messages["AI affirm"]),
            model=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature)
        ),
        DialogueAgent(
            name="AI negative",
            system_message=SystemMessage(content=agent_system_messages["AI negative"]),
            model=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature)
        )
    ]


    moderatorAgent = ModeratorDialogueAgent("Moderator",topic_specifier_prompt,ChatOpenAI(model_name="gpt-3.5-turbo", temperature=temperature),situation)
    n = 0
    history = []
    simulator = DialogueSimulator(moderatorAgent,agents=agents, selection_function=select_next_speaker)
    simulator.reset()
    name, message = simulator.start()
    history.append((f"{name} : {message}"))
    if(negativeFirst):
        simulator.voidStep()

    while n < max_iters:
        name, message = simulator.step()
        n += 1
        history.append((f"{name} : {message}"))

    name, message = simulator.end()
    history.append((f"{name} : {message}"))
    return "\n".join(history)
    

