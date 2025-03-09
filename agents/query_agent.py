import ast
from typing import List, Literal

from langchain_core.messages import AIMessage
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from class_deinitions.model import Models
from PIL import Image
import io
from langgraph.checkpoint.memory import MemorySaver

from utils.db import run_query_on_sqlite
from utils.general import load_yaml_files, extract_table_descriptions

# Globals
_YAML_DIRECTORY_PATH_ = '../yaml_content'
_DB_PATH_ = '../inventory_management.db'
_HISTORY_NUMBER_ = -5
_TOP_N_TABLES__TO_SELECT_ = 4

# Load yaml files
yaml_contents = load_yaml_files(_YAML_DIRECTORY_PATH_)
table_names_and_desc = extract_table_descriptions(yaml_contents)


class RequiredTables(BaseModel):
    table_names: List[str] = Field(
        description="List of table names based on the input query. can be empty list if generic query is asked.",
    )


class State(TypedDict):
    # TODO need to return only text history without extra response stats
    current_table_names: list
    messages: Annotated[list, add_messages]
    current_sql_query: str
    query_result: str


llm = Models('gpt-4o').model

# disabled for now. implementation does not seems to be right. need to fix
table_name_structured_llm = llm.with_structured_output(RequiredTables)


def get_table_names(state: State):
    prompt = f'''
    Return top {_TOP_N_TABLES__TO_SELECT_} tables which would be required to answer the user query. In case of no knowledge return empty list.
    Below are the table names and descriptions of all the tables. You need to select top {_TOP_N_TABLES__TO_SELECT_} tables from this.
    {table_names_and_desc}
    Here is previous communication:
    {state["messages"][_HISTORY_NUMBER_:]}
    Additional instructions:
    Only return list of table names or an empty list if query asked does not return any table names.
    '''
    # print(prompt)
    response = llm.invoke([prompt])
    print('Table names:', response.content)
    return {'current_table_names': ast.literal_eval(response.content)}


def generate_db_query(state: State):
    # extract metadata for all the shortlisted tables
    selected_tables_schema = '\n'.join(
        [f"{table_name}: \n{yaml_contents[table_name]}" for table_name in state["current_table_names"]])

    prompt = f'''
    Write a SQLite query to fetch data based on the user query. In case of no knowledge return blank.
    Below are the table name and schema:
    {selected_tables_schema}
    Here is previous communication:
    {state["messages"][_HISTORY_NUMBER_:]}
    Additional instructions:
    Return a valid SQlite query or blank if the user query is generic and not related to the data.
    Only return the SQL query without any explanations or ```sql tags```
    '''
    # print(prompt)
    response = llm.invoke([prompt])
    print('Query generated:', response.content)
    return {'current_sql_query': response.content}


def run_query(state: State):
    if state["current_sql_query"]:
        query_result = run_query_on_sqlite(_DB_PATH_, state["current_sql_query"])
    else:
        query_result = 'No Query Generated'
    return {'query_result': query_result}


def generate_nlp_response(state: State):
    prompt = f'''
    Generate a Natural language response to the user query. 
    Since this is a chat application, user can ask normal questions as well.
    If the user query is a generic question or comment, respond like a normal agent and dont mention anything about SQL.
    Here is the SQL query:
    {state['current_sql_query']}
    Here is the output of the SQL query:
    {state["query_result"]}
    Here is the message history:
    {state["messages"][_HISTORY_NUMBER_:]}
    '''
    response = llm.invoke([prompt])
    print('NLP response:', response.content)
    return {'messages': [response]}


def regenerate_query(state: State):
    # extract metadata for all the shortlisted tables
    selected_tables_schema = '\n'.join(
        [f"{table_name}: \n{yaml_contents[table_name]}" for table_name in state["current_table_names"]])

    prompt = f'''
    Fix the SQL query and write a new query that could answer the user query. In case of no knowledge return blank.
    Current query:
    {state["current_sql_query"]}
    Query error:
    {state["query_result"]}
    Below are the table name and schema:
    {selected_tables_schema}
    Here is previous communication:
    {state["messages"][_HISTORY_NUMBER_:]}
    Additional instructions:
    Return a valid SQlite query or blank if the user query is generic and not related to the data.
    Only return the query or blank, do not return any ```sql or any explanations
    '''
    # print(prompt)
    response = llm.invoke([prompt])
    print('Query generated:', response.content)
    print('Previous query:', state["current_sql_query"])
    return {'current_sql_query': response.content}


def dummy_end_node(state: State):
    pass


def decide_regenerate_query(state: State) -> Literal['regenerate_query', 'generate_nlp_response']:
    if '**An error occurred:**' in state["query_result"]:
        print('Going to re-generate query as there is an error: {}'.format(state["query_result"]))
        return 'regenerate_query'
    else:
        print('Going to generate_nlp_response')
        return 'generate_nlp_response'


def decide_regenerate_from_start(state: State) -> Literal['get_table_names', 'dummy_end_node']:
    # print('AI Response:', {state["messages"][-1].content})

    prompt = f'''
    Check whether the below response answers the user query not.
    AI Response:
    {state["messages"][-1].content}
    Conversation History:
    {state["messages"][_HISTORY_NUMBER_:]}
    If the response correctly answers the user query correctly return yes else return no.
    Only return yes or no without any extra details or explanations.
    If the query is generic and not related to the data, return yes.
    '''
    response = llm.invoke([prompt])
    if response.content == 'no':
        print(f'Going to Start as response \n{state["messages"][-1].content}\n is not relevant')
        return 'get_table_names'
    else:
        return 'dummy_end_node'


# Graph definition
memory = MemorySaver()
graph_builder = StateGraph(State)
graph_builder.add_node("get_table_names", get_table_names)
graph_builder.add_node("generate_db_query", generate_db_query)
graph_builder.add_node("run_query", run_query)
graph_builder.add_node("generate_nlp_response", generate_nlp_response)
graph_builder.add_node("regenerate_query", regenerate_query)
graph_builder.add_node("dummy_end_node", dummy_end_node)

graph_builder.set_entry_point("get_table_names")
graph_builder.add_edge("get_table_names", 'generate_db_query')
graph_builder.add_edge("generate_db_query", 'run_query')
graph_builder.add_conditional_edges('run_query', decide_regenerate_query)
graph_builder.add_edge("regenerate_query", 'run_query')
graph_builder.add_conditional_edges('generate_nlp_response', decide_regenerate_from_start)

graph_builder.set_finish_point("dummy_end_node")
graph = graph_builder.compile(checkpointer=memory)

try:
    image_bytes = graph.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(image_bytes))
    # image.show()
except Exception as e:
    print('Can\'t draw image due to: {}'.format(e))
    pass

config = {"configurable": {"thread_id": "1"}, 'recursion_limit': 25}


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config):
        for value in event.values():
            if value and 'messages' in value:
                print("Assistant:", value["messages"][-1].content)


while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    stream_graph_updates(user_input)
