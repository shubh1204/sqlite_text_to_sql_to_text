metadata_generator_prompt = '''
Given this data from a table {}, return table description and columns description and schema as a dict format that can be later written to yaml. Only return the dict that can be directly loaded, do not return ```python tag.
'''