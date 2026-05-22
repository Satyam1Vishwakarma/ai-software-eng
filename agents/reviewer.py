import os

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


# ==========================================
# CONFIG
# ==========================================

WORKSPACE_DIR = "workspace"


# ==========================================
# LLM
# ==========================================

llm = ChatOllama(
    model="qwen3:4b-instruct",
    temperature=0
)


# ==========================================
# TOOLS
# ==========================================

@tool
def list_files(path: str = "") -> str:
    """List all files and folders inside workspace"""

    try:

        path = path.strip().replace("\\", "/")

        if ".." in path:
            return "ERROR: Invalid path"

        full_path = os.path.join(WORKSPACE_DIR, path)

        if not os.path.exists(full_path):
            return f"ERROR: Path does not exist -> {full_path}"

        output = []

        for root, dirs, files in os.walk(full_path):

            for d in dirs:

                rel_dir = os.path.relpath(
                    os.path.join(root, d),
                    WORKSPACE_DIR
                )

                output.append(f"DIR: {rel_dir}")

            for f in files:

                rel_file = os.path.relpath(
                    os.path.join(root, f),
                    WORKSPACE_DIR
                )

                output.append(f"FILE: {rel_file}")

        if not output:
            return "Workspace is empty."

        return "\n".join(output)

    except Exception as e:

        return f"ERROR: {str(e)}"


@tool
def read_file(path: str) -> str:
    """Read a file inside workspace"""

    try:

        path = path.strip().replace("\\", "/")

        if path.startswith("workspace/"):
            path = path[len("workspace/"):]

        if ".." in path:
            return "ERROR: Invalid path"

        full_path = os.path.join(WORKSPACE_DIR, path)

        if not os.path.exists(full_path):
            return f"ERROR: File does not exist -> {full_path}"

        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:

        return f"ERROR: {str(e)}"


@tool
def check_python_syntax(path: str) -> str:
    """Check Python syntax of a file inside workspace"""

    import py_compile

    try:

        path = path.strip().replace("\\", "/")

        if path.startswith("workspace/"):
            path = path[len("workspace/"):]

        if ".." in path:
            return "ERROR: Invalid path"

        full_path = os.path.join(WORKSPACE_DIR, path)

        if not os.path.exists(full_path):
            return f"ERROR: File does not exist -> {full_path}"

        py_compile.compile(full_path, doraise=True)

        return f"Syntax OK: {path}"

    except Exception as e:

        return f"Syntax Error in {path}: {str(e)}"


# ==========================================
# AGENT
# ==========================================

reviewer_agent = create_agent(
    model=llm,
    tools=[
        list_files,
        read_file,
        check_python_syntax
    ],
    system_prompt="""
You are a senior software reviewer.

Your responsibilities:

1. All tools are automatically scoped to the workspace folder.
2. ALWAYS inspect the project structure first using list_files.
3. Read important files using read_file.
4. Check Python files using check_python_syntax.
5. Verify:
   - missing files
   - broken imports
   - syntax issues
   - architectural problems
   - missing functionality
   - runtime risks

6. Focus on IMPORTANT issues only.
7. Avoid unnecessary nitpicking.
8. Be practical and iterative.

Approve if:
- the project is functional
- structure is reasonable
- no critical errors exist

IMPORTANT:
- Use tools to inspect the real filesystem.
- Do NOT assume files exist.
- Do NOT hallucinate project structure.
- Verify everything using tools.

Respond EXACTLY in this format:

APPROVED: true/false
REVIEW: detailed feedback
"""
)


# ==========================================
# NODE
# ==========================================

def reviewer_node(state):

    print("\n========== REVIEWER START ==========\n")

    print("CURRENT WORKSPACE CONTENTS:\n")

    if not os.path.exists(WORKSPACE_DIR):
        print("Workspace folder does not exist.")
    else:

        for root, dirs, files in os.walk(WORKSPACE_DIR):

            print(f"ROOT: {root}")
            print(f"DIRS: {dirs}")
            print(f"FILES: {files}")
            print()

    response = reviewer_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""
Review the generated software project.

Implementation Plan:

{state["plan"]}

Previous Review Feedback:

{state.get("review", "No previous review feedback.")}

Your task:
- inspect the workspace
- review the project structure
- inspect source files
- identify critical problems
- validate Python syntax
- determine whether the implementation is acceptable
"""
            }
        ]
    })

    print("\n========== FULL REVIEWER RESPONSE ==========\n")
    print(response)

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