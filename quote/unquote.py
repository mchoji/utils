#!/usr/bin/env python3
import urllib.parse
import fileinput

for line in fileinput.input():
    print(urllib.parse.unquote(line.rstrip()))
