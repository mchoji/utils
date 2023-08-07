# Email Extractor

The "Email Extractor" is a Python script that allows you to extract unique email addresses from one or more input files. It is designed to handle email addresses with different sizes of top-level domains (TLDs) such as ".com", ".co.uk", etc.

## Usage

To use the script, simply run it in the terminal, providing the input file(s) as command-line arguments. The script will scan the specified file(s), extract the email addresses, and display the unique email addresses on the screen, all normalized to lowercase.

```bash
python extract_emails.py file1.txt file2.txt ...
```

## Requirements

   - Python 3.x

## How it Works

The script uses regular expressions to identify email addresses in the input files. It searches for email patterns, allowing for different sizes of TLDs, and then normalizes the email addresses to lowercase before displaying them.


## Example

Let's say you have a file named "contacts.txt" containing the following text:

```csv
John Doe: john.doe@example.com
Jane Smith: jane_smith@gmail.com
Support: support@mycompany.com
Info: info@company.co.uk
```

By running the script with this input file, you will get the following output:

```bash
python extract_emails.py contacts.txt
```
```
info@company.co.uk
jane_smith@gmail.com
john.doe@example.com
support@mycompany.com
```

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute the code as needed.
