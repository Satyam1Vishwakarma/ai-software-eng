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
def write_code(path: str, content: str) -> str:
    """Write project code to a file"""

    import os
    import traceback

    try:

        folder = os.path.dirname(path)

        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

        return f"{path} created successfully."

    except Exception as e:

        traceback.print_exc()

        return f"ERROR WRITING FILE: {str(e)}"

@tool
def bash_command(command: str) -> str:
    """Execute a bash command and return the output"""

    import subprocess

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        return f"Error: {result.stderr}"

    return result.stdout


# ==========================================
# AGENT
# ==========================================

coder_agent = create_agent(
    model=llm,
    tools=[write_code, bash_command],
    system_prompt="""
You are a senior software engineer responsible for implementing software projects.

Your responsibilities:

1. Read the implementation plan carefully.
2. Create ALL folders and files mentioned in the plan.
3. Use the write_code tool to write EVERY file.
4. Use correct file paths when creating nested folders and files.
5. Generate COMPLETE production-ready code.
6. Never write placeholder code.
7. Never write explanations instead of code.
8. Never wrap code in markdown.
9. If a file already exists, overwrite it with improved code.
10. Use the bash_command tool to:
   - verify file creation
   - inspect folders
   - check project structure
   - debug issues if needed

Workflow you MUST follow:

Step 1:
Analyze the implementation plan and identify:
- folders
- files
- dependencies
- architecture

Step 2:
Create the required folder structure.

Step 3:
Write ALL required files using write_code.

Step 4:
Use bash_command to verify:
- files exist
- folders exist
- structure is correct

Step 5:
Fix missing files or structural problems if found.

Step 6:
If review feedback exists:
- improve the implementation
- fix bugs
- refactor bad code
- rewrite broken architecture if necessary

Important rules:

- You are writing REAL source files.
- Do NOT generate markdown documentation unless requested.
- Do NOT output code directly in chat.
- ALWAYS use tools.
- Ensure imports between files are correct.
- Ensure the project can run successfully.
- Be autonomous and proactive.
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
Implementation Plan:

{state["plan"]}

Previous Review Feedback:

{state.get("review", "No previous review feedback.")}

Your task:
- build the complete project
- create all required folders
- create all required files
- implement all functionality
- verify the structure using bash commands
- fix issues automatically if found
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