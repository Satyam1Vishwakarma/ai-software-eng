from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


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
def write_code(content: str) -> str:
    """Write project code to main.py"""

    with open("main.py", "w") as f:
        f.write(content)

    return "main.py created successfully."


# ==========================================
# AGENT
# ==========================================

coder_agent = create_agent(
    model=llm,
    tools=[write_code],
    system_prompt="""
You are a senior Python engineer.

Your task:
1. Read the implementation plan carefully.
2. Write complete working Python code.
3. ALWAYS use the write_code tool.
4. Generate clean production-ready code.
5. Never ask follow-up questions.
6. You are writing code in a text file, not a .md file.
"""
)


# ==========================================
# NODE
# ==========================================
def coder_node(state):

    response = coder_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
Use this implementation plan to build the project:

{state["plan"]}

Also follow recommendations from the previous review:

{state.get("review", "No recommendations")}
if there is problem which cant be fixed in your sense reqrite the whole code look at it in different way.
"""
            }
        ]
    })

    code_result = response["messages"][-1].content

    print("\n========== CODER ==========\n")
    print(code_result)

    return {
        "code_result": code_result
    }