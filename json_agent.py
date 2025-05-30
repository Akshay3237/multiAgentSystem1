import os
import getpass
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from json_tool import  add_json_record,get_json_record,update_json_record,delete_json_record,list_json_records,search_json_records


tools = [add_json_record,get_json_record,update_json_record,delete_json_record,list_json_records,search_json_records]

# Load environment variables from .env file
load_dotenv()

# Check for GOOGLE_API_KEY, prompt if missing
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")


# Initialize Gemini chat model from Google
model = init_chat_model(
    model="gemini-2.0-flash",
    model_provider="google_genai"
)

json_llm_with_tools =model.bind_tools(tools)

