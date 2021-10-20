# parseJSONFromDir

Given a set of directories, look for files containing lists of objects in JSON format.
Parse all of them and generate a pandas' DataFrame from their content, outputing
the result in CSV format.

## Use Case

You've run Burp Intruder and saved server responses in given directories.
Now you want to parse the results (lists of objects) to have the
information organized (possibly dumps of something).

## Help

```shell
poetry run ./parseJSONFromDir.py -h
usage: parseJSONFromDir.py [-h] [-n] [-r] [-s] [--columns COLUMN [COLUMN ...]] [--drop-columns COLUMN [COLUMN ...]] [--sort-by COLUMN [COLUMN ...]] [--query QUERY]
                           dir [dir ...]

Parse JSON lists from files inside a directory

positional arguments:
  dir                   root directories

optional arguments:
  -h, --help            show this help message and exit
  -n, --dry-run         Only list the files that should be read
  -r, --recursive       Recursively search for files starting from root directory
  -s, --silent          Ommit logging messages
  --columns COLUMN [COLUMN ...]
                        Columns to write to output
  --drop-columns COLUMN [COLUMN ...]
                        Drop columns (properties) from result
  --sort-by COLUMN [COLUMN ...]
                        Sort result by columns
  --query QUERY         Apply query to filter final dataset
```

## Example

```
poetry run ./parseJSONFromDir.py /opt/dirA /opt/dirB --drop-columns X Y Z --sort-by A --columns A B C --query "D==True" -r > output.csv
```
