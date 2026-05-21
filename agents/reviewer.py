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
def list_files(path: str = ".") -> str:
    """List all files and folders in the project"""

    import os

    output = []

    for root, dirs, files in os.walk(path):

        for d in dirs:
            output.append(f"DIR: {os.path.join(root, d)}")

        for f in files:
            output.append(f"FILE: {os.path.join(root, f)}")

    return "\n".join(output)


@tool
def read_file(path: str) -> str:
    """Read any project file"""

    try:

        with open(path, "r") as f:
            return f.read()

    except Exception as e:
        return f"ERROR: {str(e)}"


# ==========================================
# AGENT
# ==========================================

reviewer_agent = create_agent(
    model=llm,
    tools=[
        list_files,
        read_file,
    ],
    system_prompt="""
You are a senior software reviewer.

Your responsibilities:

1. ALWAYS inspect the project structure first using list_files.
2. Review important source files using read_file.
3. Identify:
   - broken imports
   - missing critical files
   - runtime risks
   - architectural issues
   - missing functionality

4. Focus on IMPORTANT issues only.
5. Avoid nitpicking minor production optimizations.
6. Be practical and iterative.

Approve if:
- the project is functional
- structure is reasonable
- no critical errors exist

Respond EXACTLY in this format:

APPROVED: true/false
REVIEW: detailed feedback
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