def parse_first_json_string(json_string):
    """Extract the first JSON object from a string.
    Args:
        json_string (str): String containing a JSON object
    Returns:
        str: Extracted JSON object as a string
    """
    # Find the indicies of the first json_string
    start_index = json_string.find('{')
    end_index = json_string.find('}') + 1

    # Extract the substring between the curly brackets
    extracted_json = json_string[start_index:end_index]

    return extracted_json


def test_parse_first_json_string():
    json_string = 'xxxxx{"name": "John", "age": 30, "city": "New York"}'
    print(parse_first_json_string(json_string))
    

if __name__ == "__main__":
    test_parse_first_json_string()
