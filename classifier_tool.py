from langchain_core.tools import tool
import db  # your db.py module
import os
import json


CLASSIFIER_SOURCE = "classifier"


@tool
def list_classifier_records(source: str = None, type_: str = None, thread_id: str = None, limit: int = 50) -> list:
    """
    List all records with optional filters.
    :param source: Source of records to list (use only: "classifier","json","email","None").
    :param type_: Filter by type (optional).
    :param thread_id: Filter by thread ID (optional).
    :param limit: Max number of records to return.
    :return: List of record dicts.
    """
    entries = db.list_entries(source=source, type_=type_, thread_id=thread_id, limit=limit)
    return entries

@tool
def readfile(filename: str) -> str:
    """
    Read a file from the current directory and return its content with file format as JSON string.
    :param filename: Name of the file to read (with extension).
    :return: JSON string with keys 'content' and 'format' or error message if not found.
    """
    if not os.path.isfile(filename):
        return {"error": f"File '{filename}' not found in current directory."}

    # Get file extension as format
    _, ext = os.path.splitext(filename)
    file_format = ext.lstrip('.').lower() if ext else "unknown"

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "format": file_format}
    except Exception as e:
        return {"error": "can not read file"}
