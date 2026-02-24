# Day 2: LCEL Execution Model (LangChain Expression Language)

On Day 2, I explored the **LangChain Expression Language (LCEL)**, which is a declarative way to easily chain LangChain components together.

## 🧠 Key Concepts Covered

- **The Pipe Operator (`|`)**: Chaining prompts, models, and parsers.
- **JsonOutputParser**: Forcing LLMs to return structured data using Pydantic schemas.
- **RunnableParallel**: Running multiple chains in parallel to optimize execution time.
- **Environment Management**: Using `python-dotenv` and `uv` to handle secrets and dependencies.

## 📜 Scripts in this Folder

### 1. `simple-LCEL-pipeline.py`

A basic entry point showing the fundamental `Prompt | Model | Parser` flow.

- **Features**: Uses a simple string output parser.
- **Run**: `uv run .\day-02-lcel-execution-model\simple-LCEL-pipeline.py`

### 2. `LCEL-pipeline-json-struture.py`

Demonstrates how to get **structured JSON output** from an LLM.

- **Features**: Uses a Pydantic `Blog` model to define the expected JSON schema.
- **Run**: `uv run .\day-02-lcel-execution-model\LCEL-pipeline-json-struture.py`

### 3. `LCEP-runnable-map.py`

Shows how to execute multiple tasks **simultaneously**.

- **Features**: Uses `RunnableParallel` to generate a summary, keywords, and sentiment analysis for the same text in one go.
- **Run**: `uv run .\day-02-lcel-execution-model\LCEP-runnable-map.py`

## 🛠️ Lessons Learned

- **Import Changes**: In modern LangChain, core components like `PromptTemplate` and `StrOutputParser` live in `langchain_core`.
- **Package Management**: `uv run` is the most efficient way to execute scripts without worrying about manual environment activation issues on Windows.
- **Prompt Partialing**: How to inject format instructions dynamically into prompts using `prompt.partial()`.
