import yaml

from class_deinitions.model import Models
from utils.db import fetch_data_as_markdown
from prompts.table_metadata_generator import metadata_generator_prompt
from utils.general import write_to_yaml

llm = Models('gpt-4o-mini').model

_LIST_OF_TABLES_ = ['orders', 'products', 'suppliers', 'warehouses']
# _LIST_OF_TABLES_ = ['inventory']
_DB_PATH_ = '../inventory_management.db'

generated_schema_dict = {}
for table in _LIST_OF_TABLES_:
    markdown_output = fetch_data_as_markdown(_DB_PATH_, table)
    response_content = llm.invoke(
        metadata_generator_prompt.format(table) + '\n' + markdown_output).content
    generated_schema_dict[table] = yaml.safe_load(response_content)


# temporarily writing to disk to prevent recreation everytime

for table, schema in generated_schema_dict.items():
    write_to_yaml(schema, '../yaml_content/'+table+'.yaml')