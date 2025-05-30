from langchain_core.tools import tool
import db  # your db.py module

JSON_SOURCE = "json"

@tool
def add_json_record(type_: str, data:str, thread_id: str = None) -> str:
    """
    Add a new JSON record to the database.
    :param type_: The JSON record type or intent.
    :param data: Extracted values string like disctionary formate.
    :param thread_id: Optional conversation or thread ID.
    :return: Confirmation string with new entry ID.
    """
    # print(data)
    entry_id = db.add_entry(source=JSON_SOURCE, type_=type_, data=data, thread_id=thread_id)
    return f"Added JSON record with ID: {entry_id}"
    # return f"Added JSON record with ID: {1}"

@tool
def get_json_record(entry_id: int) -> dict:
    """
    Retrieve a JSON record by its ID.
    :param entry_id: Record ID to fetch.
    :return: The JSON record as a dict or empty dict if not found.
    """
    record = db.get_entry_by_id(entry_id)
    return record or {}

@tool
def update_json_record(entry_id: int, data: str = None, thread_id: str = None) -> str:
    """
    Update an existing JSON record.
    :param entry_id: ID of the record to update.
    :param data: New extracted values dict to update.
    :param thread_id: Optional new thread ID.
    :return: Success/failure message.
    """
    success = db.update_entry(entry_id, data=data, thread_id=thread_id)
    return f"Updated record {entry_id}" if success else f"Record {entry_id} not found"

@tool
def delete_json_record(entry_id: int) -> str:
    """
    Delete a JSON record by its ID.
    :param entry_id: Record ID to delete.
    :return: Success/failure message.
    """
    success = db.delete_entry(entry_id)
    return f"Deleted record {entry_id}" if success else f"Record {entry_id} not found"

@tool
def list_json_records(source: str = JSON_SOURCE, type_: str = None, thread_id: str = None, limit: int = 50) -> list:
    """
    List JSON records with optional filters.
    :param source: Source of records to list (default: "json").
    :param type_: Filter by type (optional).
    :param thread_id: Filter by thread ID (optional).
    :param limit: Max number of records to return.
    :return: List of record dicts.
    """
    entries = db.list_entries(source=source, type_=type_, thread_id=thread_id, limit=limit)
    return entries

@tool
def search_json_records(query: str, source: str = JSON_SOURCE, limit: int = 20) -> list:
    """
    Search JSON records for a query string inside extracted values.
    :param query: String to search inside extracted data fields.
    :param source: Source filter (default "json").
    :param limit: Max records to return.
    :return: List of matching records.
    """
    entries = db.list_entries(source=source, limit=1000)  # fetch more, filter locally
    results = []
    query_lower = query.lower()
    for entry in entries:
        # Search all extracted values converted to string
        text_fields = " ".join(str(v).lower() for v in entry.get("data", {}).values())
        if query_lower in text_fields:
            results.append(entry)
            if len(results) >= limit:
                break
    return results
