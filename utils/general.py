import os
import yaml


def write_to_yaml(yaml_content, file_path=None):
    """
    Convert YAML content to a string or write to a file if a file path is provided.

    Args:
        yaml_content (dict): The YAML content to process (as a Python dictionary).
        file_path (str, optional): The path of the file to save the YAML content. Defaults to None.

    Returns:
        str: YAML string if file_path is not provided.
    """
    try:
        # Convert content to YAML string
        yaml_string = yaml.dump(yaml_content, allow_unicode=True, default_flow_style=False)

        if file_path:
            # Write YAML string to file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(yaml_string)
            print(f"YAML content successfully written to {file_path}")
        else:
            # Return YAML string
            return yaml_string

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def load_yaml_files(directory):
    """
    Load all YAML files in the given directory as key-value pairs.

    Args:
        directory (str): The path to the directory containing YAML files.

    Returns:
        dict: A dictionary where keys are file names (without extensions) and values are file contents as dictionaries.
    """
    yaml_data = {}

    try:
        for file_name in os.listdir(directory):
            if file_name.endswith(('.yaml', '.yml')):  # Check for YAML files
                file_path = os.path.join(directory, file_name)

                # Extract file name without the extension
                key = os.path.splitext(file_name)[0]

                # Read and load YAML content
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = yaml.safe_load(file)
                    yaml_data[key] = content

        return yaml_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def extract_table_descriptions(yaml_content):
    """
    Extract table names and their descriptions from the loaded YAML content.

    Args:
        yaml_content (dict): Loaded YAML content as a Python dictionary.

    Returns:
        dict: A dictionary with table names as keys and their descriptions as values.
    """
    table_descriptions = {}

    for table_name, table_details in yaml_content.items():
        # Extract table descriptions if available
        description = table_details.get("table_description", "No description available")
        table_descriptions[table_name] = description

    return table_descriptions


# Sample data in the given format
data = """
AI Assistant: shubham is biggest spender
User: What is total order count.
"""


# Function to extract and structure data
def extract_data(input_data: list):
    # Split the input into lines
    lines = input_data.strip().split("\n")

    # Dictionary to store extracted information
    extracted_data = {"AI Assistant": None, "User": None}

    for line in lines:
        # Split the line into key and value based on ":"
        if ": " in line:
            key, value = line.split(": ", 1)
            if key in extracted_data:
                extracted_data[key] = value

    return extracted_data
