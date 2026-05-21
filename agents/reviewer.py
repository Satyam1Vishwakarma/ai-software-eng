from langchain.tools import tool
from langchain.agents import AgentState, create_agent
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
def read_code() -> str:
    """Read current code from main.py"""

    with open("main.py", "r") as f:
        return f.read()

# ==========================================
# AGENT
# ==========================================

reviewer_agent = create_agent(
    model=llm,
    tools=[read_code],
    system_prompt="""
You are a senior code reviewer.

Your task:
1. ALWAYS use the read_code tool first.
2. Review the generated code carefully.
3. Check for:
   - bugs
   - bad practices
   - missing edge cases
   - poor structure
4. Approve ONLY if code is correct.

Respond EXACTLY in this format:

APPROVED: true/false
REVIEW: your feedback
"""
)

# ==========================================
# NODE
# ==========================================

def reviewer_node(state):

    response = reviewer_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
Review this implementation plan:

{state["plan"]}

and review the generated code
{state["code_result"]}.
"""
            }
        ]
    })

    review_text = response["messages"][-1].content

    approved = False

    if "approved: true" in review_text.lower():
        approved = True

    print("\n========== REVIEW ==========\n")
    print(review_text)

    return {
        "review": review_text,
        "approved": approved
    }