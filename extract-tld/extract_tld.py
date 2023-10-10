#!/usr/bin/env python3
import sys
import tldextract

def extract_tlds(hosts):
    tlds = []
    for host in hosts:
        ext = tldextract.extract(host)
        tld = f"{ext.domain}.{ext.suffix}"
        # remove eventual dot at the end of the TLD
        if tld.endswith("."):
            tld = tld[:-1]
        tlds.append(tld)
    return tlds

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Read from stdin if no file argument is provided
        hosts = sys.stdin.read().splitlines()
    else:
        # Read from the file provided as an argument
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as file:
                hosts = file.read().splitlines()
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

    tlds = extract_tlds(hosts)

    if tlds:
        for tld in tlds:
            print(tld)
    else:
        print("No TLDs found in the provided hosts.")
