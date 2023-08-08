#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET
import base64
import json
import sys
import re
import binascii

def extract_json_from_http_response(http_response):
    pattern = re.compile(r'^\s*{', re.MULTILINE)
    match = pattern.search(http_response)
    if match:
        json_content = http_response[match.start():]
        return json_content
    return None

def decode_and_convert_to_json(base64_encoded_response):
    try:
        decoded_bytes = base64.b64decode(base64_encoded_response)
        decoded_string = decoded_bytes.decode('utf-8')
        json_content = extract_json_from_http_response(decoded_string)
        print(json_content)
        if json_content:
            return json.loads(json_content)
        else:
            return None
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"Error decoding or parsing response: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Extract JSON content from base64-encoded responses in an XML file.")
    parser.add_argument("input_file", help="Input XML file containing base64-encoded responses")
    parser.add_argument("--output_file", help="Output JSON file (default: print to stdout)")
    args = parser.parse_args()

    try:
        tree = ET.parse(args.input_file)
        root = tree.getroot()

        responses = []
        for response_elem in root.findall('.//response'):
            base64_encoded = response_elem.text
            response_json = decode_and_convert_to_json(base64_encoded)
            if response_json:
                responses.append(response_json)

        if args.output_file:
            with open(args.output_file, 'w') as output_file:
                json.dump(responses, output_file, indent=2)
        else:
            print(json.dumps(responses, indent=2))

    except (FileNotFoundError, ET.ParseError) as e:
        print(f"Error reading or parsing input XML: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
