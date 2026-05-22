import os
from sre_parse import State

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from typing import Literal
from langgraph.types import interrupt, Command

def approval_node(state: State) -> Command[Literal["proceed", "cancel"]]:
    # Pause execution; payload shows up in result.interrupts (v2) or result["__interrupt__"] (v1)
    is_approved = interrupt({
        "question": "Do you want to proceed?",
        "details": state["action_details"]
    })

    # Route based on the response
    if is_approved:
        return Command(goto="proceed")  # Runs after the resume payload is provided
    else:
        return Command(goto="cancel")

# ==========================================
# LLM
# ==========================================

llm = ChatOllama(
    model="qwen3:4b-instruct",
    temperature=0
)


# ==========================================
# TOOL
# ==========================================

@tool
def write_requirements(content: str) -> str:
    """Write project requirements to /workspace/requirements.md"""
    os.makedirs("./workspace", exist_ok=True)
    with open("./workspace/requirements.md", "w") as f:
        f.write(content)

    return "requirements.md created successfully."


# ==========================================
# AGENT
# ==========================================

#6. Also generate file structure based on the language and framework you choose. Do not recommend unnecessary files. Only generate files that are relevant to the project.

planner_agent = create_agent(
    model=llm,
    tools=[write_requirements],
    system_prompt="""
You are a senior software architect.

Your task:
1. Understand the user's software project idea.
2. Create a concise implementation plan.
3. Save the plan using the write_requirements tool.
4. Never ask unnecessary questions.
5. Be concise in your responses.
6. Also generate file structure based on the language and framework you choose. Do not recommend unnecessary files. Only generate files that are relevant to the project.
"""
)


# ==========================================
# NODE
# ==========================================

def planner_node(state):

    response = planner_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": state["user_request"]
            }
        ]
    })

    plan = response["messages"][-1].content

    print("\n========== PLAN ==========\n")
    print(plan)

    return {
        "plan": plan
    }