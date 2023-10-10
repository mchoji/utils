# TLD Extractor

The "TLD Extractor" is a Python script that allows you to extract TLDs from a
file or from stdin.

## Usage

To use the script, simply run it in the terminal, providing the input file as
command-line arguments or pipe from stdin. The script will scan the specified input, extract
TLDs and print them to stdout.

```bash
python extract_tld.py input.txt
```

## Requirements

   - Python 3.x
   - tldextract


## Example

Let's say you have a file named "input.txt" containing the following text:

```
contoso.com
www.contoso.com
ftp.contoso2.com
```

By running the script with this input file, you will get the following output:

```bash
python extract_tld.py input.txt
```
```
contoso.com
contoso.com
contoso2.com
```

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute the code as needed.
