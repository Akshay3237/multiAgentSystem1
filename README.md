# 🧠 ParseAgent – A Multi-Agent JSON/Email/Classifier AI Assistant

This project is a powerful multi-agent conversational system built using **LangGraph** and **LangChain**, allowing you to interact with structured data using natural language. It supports **JSON, Email**, and **Custom Classifier** records, and integrates tools for reading,  storing, and listing records via natural prompts.

---

## ✨ Features

- 🔍 Natural language interface for managing structured data.
- 📦 **JSON Agent**: Add, get, update, delete, list, and search JSON records.
- 📬 **Email Agent**: Manage email-like records easily.
- 🧾 **Classifier Agent**: Run file classification and record insights.
- 📂 Tool-based reading from `.json` files using `readfile`.
- 🔁 Intelligent agent routing using **LangGraph**.
- 💾 In-memory checkpointing via `MemorySaver`.
- 🤖 Built-in multi-turn support via conversation state.

---

## 🗂️ Project Structure

```
parseAgent/
│
├── main.py                 # Main entry point,Base LangGraph setup
├── json_agent.py           # JSON-specific logic and LLM tools
├── json_tool.py            # Tool functions for JSON handling
├── email_agent.py          # Email agent logic
├── email_tool.py           # Tool functions for email operations
├── classifier_agent.py     # File classifier logic
├── classifier_tool.py      # Classifier tool (e.g., readfile)
├── my.json                 # Sample input file
├── first.txt               # Sample input file
└── ...
```

---

## 🚀 Getting Started

### 1. Install dependencies

Make sure you have a virtual environment set up. Then install:

```bash
    pip install -r requirements.txt
```

> Note: You also need to configure your Gemini keys if you're using LLMs.

---

### 2. Run the Assistant

```bash
python main.py
```

Then interact with the assistant, for example:

```text
User: read my.json
Assistant: OK. I’ve read the file. What type should I assign to this record?
User: json
Assistant: Successfully stored the record.
```

---

## 🛠 Tools Overview

Each agent uses tools defined in their respective files. Tools are functions that handle:

- Reading files
- Storing records
- Listing/searching/updating/deleting

Example tools:
- `add_json_record`
- `readfile`
- `list_email_records`

These tools are passed into the LLM chains so that the model can decide when and how to call them.

---

## 🔧 How It Works

- The `StateGraph` defines conversation flow.
- `input_json()` collects user input as `HumanMessage`.
- Each node (agent) processes the message using the correct LLM and toolset.
- System messages provide instruction like “Store this data” or “Route to correct agent”.
- Final responses are generated and printed back to the user.

---

## 🧪 Example Prompts

```text
read ak.json
list all email records
store this JSON data
get classifier record with id 5
```

---

## 🧠 Future Improvements

- Persistent DB integration (SQLite)
- Better error handling and validation

---

## 🧑‍💻 Author

**Akshay** – [GitHub](https://github.com/Akshay3237)

---

## 📜 License

This project is open-source and available under the MIT License.
