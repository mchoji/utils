#!/usr/bin/env python3
import urllib.parse
import fileinput

for line in fileinput.input():
    print(urllib.parse.quote(line.rstrip()))
