import json
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage,SystemMessage

from langgraph.checkpoint.memory import MemorySaver

# --- Import your agents with tools and tools list ---


from json_tool import (
    add_json_record, get_json_record, update_json_record,
    delete_json_record, list_json_records, search_json_records
)
from email_tool import (
    add_email_record, get_email_record, update_email_record,
    delete_email_record, list_email_records, search_email_records
)
from classifier_tool import (
     list_classifier_records,
    readfile
)
from email_agent import email_llm_with_tools
from json_agent import json_llm_with_tools
from classifier_agent import classifier_llm_with_tools


# --- 1. Define tools list ---
tools = [
    list_classifier_records, 
    readfile,
    add_email_record, get_email_record, update_email_record,
    delete_email_record, list_email_records, search_email_records,
    add_json_record, get_json_record, update_json_record,
    delete_json_record, list_json_records, search_json_records,
]

# --- 2. Define State ---
class State(TypedDict):
    messages: Annotated[list, add_messages]

# --- 3. Memory ---
memory = MemorySaver()
from langchain_core.messages import SystemMessage, HumanMessage

# --- 4. Agent functions ---
def classifier_chatbot(state: State) -> dict:
    result = classifier_llm_with_tools.invoke(state["messages"])
    return {"messages": [result]}

def email_chatbot(state: State) -> dict:
    state["messages"].append(
        HumanMessage(content="Please add email the previously read  data using the appropriate tool.")
    )

    result = email_llm_with_tools.invoke(state["messages"])
    # print("here1")
    return {"messages": state["messages"] + [result]}

def json_chatbot(state: State) -> dict:
    
    state["messages"].append(
        HumanMessage(content="Please store the previously read JSON data using the appropriate tool.")
    )

    result = json_llm_with_tools.invoke(state["messages"])
    # print("here1")
    return {"messages": state["messages"] + [result]}

# --- 5. Tool caller node ---
class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        outputs = []
        for tool_call in getattr(message, "tool_calls", []):
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_result = self.tools_by_name[tool_name].invoke(tool_args)
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_name,
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

tool_node = BasicToolNode(tools)
read_tool=BasicToolNode([readfile])
list_record_tool=BasicToolNode([list_classifier_records])
def router(state: State) -> str:
    last_msg = state["messages"][-1]
    # print(last_msg)
    if isinstance(last_msg, AIMessage):
        tool_calls = last_msg.additional_kwargs
        if tool_calls:
            
            if 'readfile'==tool_calls['function_call'].get('name'):
                return "read_tool"
            elif 'list_classifier_records'==tool_calls['function_call'].get('name'):
                print(tool_calls['function_call'])
                return "list_record"
            else:
                return END
        else:
            return END
    return END
from langchain_core.messages import SystemMessage

def from_readtool(state: State) -> str:
    last_msg = state["messages"][-1]

    if last_msg.content:
        try:
            parsed_data = json.loads(last_msg.content)

            if parsed_data.get('error'):
                return 'classifier'

            file_format = parsed_data.get("format")
            if file_format == 'json':
                # 💡 Tell json_agent to store it
                
                
                return 'json'

            elif file_format == 'txt':
               
                return 'email'

            else:
                return END
        except json.JSONDecodeError:
            print("eror from here")
            return END
    else:
        return END


def from_email_root(state: State) -> str:
    last_msg = state["messages"][-1]
   
    if last_msg.additional_kwargs:
        print(last_msg.additional_kwargs)
        return 'call_tools' 
    else:
        return 'input_email'
    return END
    

def from_json_root(state: State) -> str:
    last_msg = state["messages"][-1]
   
    if last_msg.additional_kwargs:
        print(last_msg.additional_kwargs)
        return 'call_tools' 
    else:
        return 'input_json'
    return END
from langchain_core.messages import HumanMessage

def input_json(state: State) -> dict:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        # Optionally exit or return something to end the graph
        return {"messages": state["messages"]}  # or some suitable return

    # Append the user input wrapped as HumanMessage to existing messages
    updated_messages = state["messages"] + [HumanMessage(content=user_input)]
    return {"messages": updated_messages}


def input_email(state: State) -> dict:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        # Optionally exit or return something to end the graph
        return {"messages": state["messages"]}  # or some suitable return

    # Append the user input wrapped as HumanMessage to existing messages
    updated_messages = state["messages"] + [HumanMessage(content=user_input)]
    return {"messages": updated_messages}




# --- 7. Build graph ---
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("classifier", classifier_chatbot)
graph_builder.add_node("email", email_chatbot)
graph_builder.add_node("json", json_chatbot)
graph_builder.add_node("call_tools", tool_node)
graph_builder.add_node("read_tool",read_tool)
graph_builder.add_node("input_json",input_json)
graph_builder.add_node("input_email",input_email)
graph_builder.add_node("list_record",list_record_tool)
# Add routing after classifier
graph_builder.add_conditional_edges("classifier", router)
graph_builder.add_conditional_edges("read_tool", from_readtool)
graph_builder.add_edge("input_json", "json")
graph_builder.add_edge("input_email", "email")


graph_builder.add_edge("call_tools", END)
graph_builder.add_edge("list_record", "classifier")
# After email, json, classifier go to call_tools to process tools if any
graph_builder.add_conditional_edges("email", from_email_root)
graph_builder.add_conditional_edges("json", from_json_root)


# graph_builder.add_edge("classifier", "call_tools")

# From call_tools, if tool calls happened, go back to classifier, else end
# def tool_node_router(state: State) -> str:
#     last_msgs = state["messages"][-1:]
#     if last_msgs and isinstance(last_msgs[0], ToolMessage):
#         # If the last message is a ToolMessage, go back to classifier to continue
#         return "classifier"
#     return END

# graph_builder.add_edges("call_tools", END)

# Entry point is classifier
graph_builder.set_entry_point("classifier")

# Compile the graph with memory
graph = graph_builder.compile(checkpointer=memory)
def stream_graph_updates(user_input: str):
    messages_list = [HumanMessage(content=user_input)]

    events = graph.stream(
        {"messages": messages_list},
        {"configurable": {"thread_id": "2"}},
    )
    
    for event in events:
        # print(event)
        for value in event.values():
            messages = value.get("messages", [])
            if messages:
                assistant_message = messages[-1]
                if isinstance(assistant_message, AIMessage):
                    print("Assistant:", assistant_message.content)
                    messages_list.append(assistant_message)
                elif isinstance(assistant_message, ToolMessage):
                    # Optional: handle tool message differently
                    print("Tool response:", assistant_message.name)
                    messages_list.append(assistant_message)
                elif isinstance(assistant_message, HumanMessage):
                    messages_list.append(assistant_message)
            else:
                print("No messages returned from graph step")

# --- 9. Main interaction loop ---
if __name__ == "__main__":
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            stream_graph_updates(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print("Error:", e)
            break
