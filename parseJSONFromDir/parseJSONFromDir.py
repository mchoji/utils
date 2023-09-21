#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2021 y0k4i
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

import pandas as pd
import argparse
import json
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description="Parse JSON lists from files inside a directory")
parser.add_argument(
        "dir",
        help="root directories",
        nargs='+',
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


if (args.silent):
    logging.disable()

logging.info("Searching files starting from %s", args.dir)

file_list = []
for dir in args.dir:
    file_list.extend(search_files(dir, args.recursive))

if args.dryrun:
    logging.info("Running in dry-run mode, so finishing here")
    exit(0)


df_list = []
row_count = 0
for file in file_list:
    content = file.read_text()
    body = re.search(r'(\[.*\])', content)
    if body:
        try:
            obj = json.loads(body.group(0))
        except:
            logging.error("Unable to parse content from %s as JSON: %s", file, body.group(0))
        else:
            df_list.append(pd.DataFrame.from_dict(obj))
            #result_df = pd.concat([result_df, pd.DataFrame.from_dict(obj)], ignore_index=True)
            row_count += df_list[-1].shape[0]
            logging.info("Current row count: %d", row_count)

if row_count == 0:
    logging.warning("No data was parsed. Verify if files in directory contains lists of objects")
else:
    result_df = pd.concat(df_list, ignore_index=True)
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
