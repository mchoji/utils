#!/usr/bin/env python3
import sys
import re
import argparse

def extract_emails(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            emails =re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}(?:\.[A-Za-z]{1,})?\b', content)
            return [email.lower() for email in emails]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract unique email addresses from one or more input files.")
    parser.add_argument("files", nargs="+", metavar="FILE", help="Input file(s) to extract email addresses from.")
    args = parser.parse_args()

    unique_emails = set()
    for file_path in args.files:
        emails = extract_emails(file_path)
        unique_emails.update(emails)

    if unique_emails:
        # print("Unique email addresses found:")
        for email in unique_emails:
            print(email)
    else:
        print("No email addresses found in the files.")
