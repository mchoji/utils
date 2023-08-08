# burp2json

This script is designed to extract JSON content from base64-encoded responses stored in saved items from Burp Suite. It is particularly useful when dealing with responses stored within CDATA sections or single outputs containing JSON sections.

## Prerequisites

- Python 3.x

## Installation

1. Clone this repository or download the script file (`burp2json.py`).

## Usage

1. Export your saved items from Burp Suite and save them in an XML file.
2. Run the script by executing the following command:

```bash
python burp2json.py input_file.xml --output_file output.json
```


## Script Options

- `input_file`: Path to the XML file containing base64-encoded responses.
- `--output_file`: Specify the path to the output JSON file. If not provided, the JSON content will be printed to the console.

## Example

Suppose you have an XML file named `burp_saved_items.xml` containing saved
items from Burp Suite. To extract and convert the JSON content to an output
JSON file named `output.json`, use the following command:

```bash
python burp2json.py burp_saved_items.xml --output_file output.json
```


## Notes

- Ensure that the XML structure and base64-encoded responses are correctly formatted in the input XML file.
- The script uses manual extraction and decoding techniques to extract JSON content from responses or JSON sections.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
