#!/usr/bin/env python3
"""
Parse saved items (Burp Proxy) from LinkedIn intercepted requests
into CSV format, optionally inferring employees emails.
"""

import pandas as pd
import argparse
import json
import logging
import re
import unicodedata
from base64 import b64decode
from pathlib import Path
from defusedxml.ElementTree import parse

logging.basicConfig(level=logging.INFO)

email_patterns = ['first.last', 'first', 'last', 'flast']

parser = argparse.ArgumentParser(description="Parse Burp's saved items from LinkedIn data")
parser.add_argument(
        "dir",
        help="root directories",
        nargs='+',
        )
parser.add_argument(
        "-d",
        "--domain",
        required=True,
        help="Domain name",
        )
parser.add_argument(
        "-p",
        "--pattern",
        help="Email pattern (default: %(default)s)",
        choices=email_patterns,
        default='first.last',
        )
parser.add_argument(
        "-n",
        "--dry-run",
        dest="dryrun",
        help="Only list the files that should be read",
        action="store_true",
        )
parser.add_argument(
        "-r",
        "--recursive",
        help="Recursively search for files starting from root directory",
        action="store_true",
        )
parser.add_argument(
        "-s",
        "--silent",
        help="Ommit logging messages",
        action="store_true",
        )
parser.add_argument(
        "--columns",
        nargs='+',
        help="Columns to write to output",
        dest="columns",
        metavar="COLUMN"
        )
parser.add_argument(
        "--drop-columns",
        nargs='+',
        help="Drop columns (properties) from result",
        dest="dropc",
        metavar="COLUMN",
        )
parser.add_argument(
        "--sort-by",
        nargs='+',
        help="Sort result by columns",
        dest="sortby",
        metavar="COLUMN",
        )
parser.add_argument(
        "--query",
        type=str,
        help="Apply query to filter final dataset",
        )

args = parser.parse_args()

def search_files(directory, recursive=False):
    dirpath = Path(directory)
    assert dirpath.is_dir()
    file_list = []
    for x in dirpath.iterdir():
        if x.is_file():
            file_list.append(x)
            logging.info("Found file %s", x)
        else:
            logging.info("Found directory %s", x)
            if recursive:
                file_list.extend(search_files(x))
    return file_list


def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)


def infer_email(name: str, surname: str, domain: str, pattern: str) -> str:
    """Infer a person's email based on name, surname and pattern"""
    assert name is not None and surname is not None \
        and domain is not None and pattern is not None \
        and name != "" and surname != "" and domain != "" and pattern != ""

    if pattern not in email_patterns:
        raise ValueError("Unexpected email pattern")
    user = ""
    if pattern == 'first.last':
        user = f'{name}.{surname}'
    elif pattern == 'flast':
        user = f'{name[0]}{surname}'
    elif pattern == 'first':
        user = name
    elif pattern == 'last':
        user = surname

    return (strip_accents(user).strip('.') + "@" + domain).lower()


if (args.silent):
    logging.disable()

logging.info("Searching files starting from %s", args.dir)

file_list = []
for dir in args.dir:
    file_list.extend(search_files(dir, args.recursive))

if args.dryrun:
    logging.info("Running in dry-run mode, so finishing here")
    exit(0)


people = []
for file in file_list:
    try:
        et = parse(file)
    except:
        logging.error("Unable to parse file %s as XML", file)
        continue
    
    root = et.getroot()
    if root.tag != 'items':
        logging.error("Unexpected root element '%s'", root.tag)
        continue

    responses = root.findall(".//response")
    for response in responses:
        if response.attrib['base64']:
            response.text = b64decode(response.text).decode('UTF-8')
        body = re.search(r'{.+}', response.text)
        if body is None:
            logging.debug("JSON object not found on response body")
            continue

        try:
            obj = json.loads(body.group(0))
        except:
            logging.error("Unable to parse response body as JSON")
            continue

        if 'included' not in obj.keys():
            logging.error("Key 'included' not found on JSON object")
            continue

        for entry in obj['included']:
            if '$type' not in entry.keys() or \
                entry['$type'] != 'com.linkedin.voyager.identity.shared.MiniProfile':
                    continue

            # get profile information
            person = {}
            # use regex to avoid garbage like (...) or [..] at the end of name
            # it won't work if name starts with something else
            fullName = re.search(r'^[^\[\]{}()\'"\-|]+',
                    entry['firstName'] + ' ' + entry['lastName'])
            if fullName is None:
                logging.warning("Could not parse full name from '%s'",
                        entry['firstName'] + ' ' + entry['lastName'])
                continue

            fullName = fullName.group(0)
            name_fields = fullName.split()
            if len(name_fields) < 2:
                logging.warning("Full name '%s' is too short", fullName)
                continue

            person['fullName'] = fullName
            person['firstName'] = name_fields[0]
            if name_fields[-1].lower() in ['jr.', 'jr', 'junior'] and \
                name_fields[-2] != name_fields[0]:
                    person['lastName'] = name_fields[-2]
            else:
                person['lastName'] = name_fields[-1]
            person['occupation'] = entry['occupation']
            person['publicIdentifier'] = entry['publicIdentifier']
            person['email'] = infer_email(person['firstName'],
                    person['lastName'], args.domain, args.pattern)
            
            people.append(person)

        logging.info("Current profiles count: %d", len(people))
# end of responses parsing

if len(people) == 0:
    logging.warning("No data was parsed. Verify if files in directory contains Burp items (XML files)")
else:
    result_df = pd.DataFrame(people)
    logging.info("Content parsed. Removing duplicates...")
    result_df.drop_duplicates(inplace=True)
    if args.query:
        logging.info("Applying query to dataset...")
        result_df.query(args.query, inplace=True)
    if args.sortby:
        logging.info("Sorting data...")
        result_df.sort_values(args.sortby, inplace=True)
    if args.dropc:
        logging.info("Dropping columns from result...")
        result_df.drop(columns=args.dropc, inplace=True)
    print(result_df.to_csv(index=False, columns=args.columns))

