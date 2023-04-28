#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2021 M. Choji
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
from typing import List

logging.basicConfig(level=logging.INFO)

email_patterns = ['first.last', 'first', 'last', 'flast']
profile_types = {
        "voyager_miniprofile": "com.linkedin.voyager.identity.shared.MiniProfile",
        "voyager_profile": "com.linkedin.voyager.dash.identity.profile.Profile",
        "voyager_entityresult": "com.linkedin.voyager.dash.search.EntityResultViewModel"
        }


class ParseError(Exception):
    """Base class for profile parsing exceptions"""
    pass


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
        help=f"Comma-separated email patterns (default: %(default)s) (options: {','.join(email_patterns)})",
        type=str,
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
        help="Columns to write to output (default: %(default)s)",
        dest="columns",
        metavar="COLUMN",
        default="email,fullName,firstName,lastName,publicIdentifier,occupation,headline".split(",")
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


def infer_email(name: str, otherNames: List[str], domain: str, pattern: str) -> str:
    """Infer a person's email based on name, surname/middlenames and pattern"""
    assert name is not None \
        and domain is not None and pattern is not None \
        and name != "" and domain != "" and pattern != ""

    # if pattern != 'first':
    #     assert otherNames is not None \
    #         and len(otherNames) > 0
    patterns = pattern.split(',')

    if all(list(map(lambda x: x not in email_patterns, patterns))):
        raise ValueError("Unexpected email pattern")
    user = []
    for pattern in patterns:
        if pattern not in email_patterns:
            continue
        if pattern == 'first.last':
            user.extend([f'{name}.{surname}' for surname in otherNames])
        elif pattern == 'flast':
            user.extend([f'{name[0]}{surname}' for surname in otherNames])
        elif pattern == 'first':
            user.append(name)
        elif pattern == 'last':
            user.extend(otherNames)

    # remove invalid chars from begining and end
    user = list(map(lambda x: x.strip('.,;'), user))
    # remove duplicates
    user = list(set(user))

    emails = map(lambda x: strip_accents(x).strip('.').lower() + "@" + domain, user)
    return ("|".join(list(emails)))



def parse_profile(entry: dict, ptype: str, supported_types: dict) -> dict:
    """Parse LinkedIn profile as found in JSON responses into
    a dictionary containing only properties of interest"""
    if entry is None:
        raise ValueError(f"entry should not be None")
    if ptype not in supported_types.values():
        raise ValueError(f"Type {ptype} not supported")

    # com.linkedin.voyager.dash.search.EntityResultViewModel
    if ptype == supported_types['voyager_entityresult']:
        if not (fullName := entry["title"]["text"]):
            raise ValueError(f"Full name not found for {ptype}")
        fullName = fullName.lower()
    else:
        # use regex to avoid garbage like (...) or [..] at the end of name
        # it won't work if name starts with something else
        fullName = re.search(r'^[^\[\]{}()\'"\-|]+',
                        entry.get('firstName', '') + ' ' + entry.get('lastName', ''))
        if fullName is None:
            logging.warning("Could not parse full name from '%s'",
                    entry['firstName'] + ' ' + entry['lastName'])
            raise ParseError("Unable to parse full name")

        fullName = fullName.group(0).lower()

    # ignore anonymous linkedin member
    if fullName == "linkedin member":
        raise ParseError("Anonymous Linkedin Member")
    # remove undesirable characters
    fullName = fullName.translate({ord(c): None for c in "._!,;"})
    name_fields = fullName.split()
    # remove blank fields
    name_fields = [n for n in name_fields if n != '' and n != ' ']
    if len(name_fields) < 1:
        logging.warning("Full name '%s' is too short", fullName)
        raise ParseError("Full name too short")

    # replace jr by junior
    if name_fields[-1] in ['jr.', 'jr']:
        name_fields[-1] = 'junior'

    person['fullName'] = fullName.title()
    person['firstName'] = name_fields[0].title()
    person['lastName'] = name_fields[-1].title() if len(name_fields) > 1 else ''

    otherNames = name_fields[1:]
    # remove some elements
    for x in ['de', 'da', 'do', 'das', 'dos']:
        if x in otherNames:
            otherNames.remove(x)
    # also, remove single letter names
    otherNames = list(filter(lambda x: len(x) > 1, otherNames))

    person['publicIdentifier'] = entry.get('publicIdentifier', '')

    if ptype == supported_types['voyager_miniprofile']:
        person['occupation'] = entry.get('occupation').replace("\n", ". ") if entry['occupation'] else ''
    elif ptype == supported_types['voyager_profile']:
        person['headline'] = entry.get('headline', '').replace("\n", ". ") if 'headline' in entry and entry['headline'] is not None else ''
    elif ptype == supported_types['voyager_entityresult']:
        if (summary := entry.get('summary')) and (occupation := summary.get('text')):
            person['occupation'] = occupation.replace("\n", ". ")
        elif (summary := entry.get('primarySubtitle')) and (occupation := summary.get('text')):
            person['occupation'] = occupation.replace("\n", ". ")
        # Example: "Current: system analyst at Company"
        if person.get('occupation') and person['occupation'].startswith("Current: "):
            person['occupation'] = person['occupation'].split(' ', 1)[1].replace("\n", ". ")


    try:
        person['email'] = infer_email(name_fields[0],
                            otherNames, args.domain, args.pattern)
    except AssertionError:
        logging.warning("Could not infer email from '%s'", ' '.join(name_fields))
        person['email'] = ''


    return person



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
            if '$type' not in entry.keys():
                continue
            if entry['$type'] not in profile_types.values():
                continue

            # get profile information
            person = {}
            try:
                person = parse_profile(entry, entry['$type'], profile_types)
            except ValueError:
                logging.error("Unsupported type %s", entry['$type'])
                continue
            except ParseError as e:
                logging.error(e)
                continue
            else:
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
