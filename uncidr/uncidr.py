#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2023 y0k4i
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
This script will print all the IP addresses in a given CIDR range.
"""


import ipaddress
import sys


def get_all_ips_in_cidr(cidr):
    try:
        network = ipaddress.IPv4Network(cidr, strict=False)
        for ip in network.hosts():
            print(ip)
    except ipaddress.AddressValueError as e:
        print(f"Error: {e}")
    except ipaddress.NetmaskValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cidr_input = sys.argv[1]
        get_all_ips_in_cidr(cidr_input)
    else:
        # Read CIDR notations from stdin line by line
        for line in sys.stdin:
            cidr_input = line.strip()
            get_all_ips_in_cidr(cidr_input)
