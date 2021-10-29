# webDiscovery

Generate wordlists from most searched/accessed subdomains and URIs


## Use Case

You want modern and up-to-date wordlist for subdomain and URI brute-forcing.


## Help

```shell
poetry run ./webDiscovery.py -h
usage: webDiscovery.py [-h] [-s] [-c] [--days YYYY-MM-DD [YYYY-MM-DD ...]] {sub,uri}

Fetch data from Internet and generate subdomain or URI wordlists

positional arguments:
  {sub,uri}             Type of wordlist to generate

optional arguments:
  -h, --help            show this help message and exit
  -s, --silent          Ommit logging messages
  -c, --count           Show output with count for each entry
  --days YYYY-MM-DD [YYYY-MM-DD ...]
                        Fetch data from these days (only valid for 'sub')
```

## Example

Generate a subdomain wordlist based on most recent data:

```
poetry run ./webDiscovery/webDiscovery.py sub > subs.txt
```

Generate a subdomain wordlist based on specific data, with count:

```
poetry run ./webDiscovery/webDiscovery.py sub --days 2021-10-28 2021-07-28 2021-04-28 2021-01-28 2020-10-28 -c >| subs-withcount.txt
```

### Note

The data in [output](output) directory were generated using the days mentioned in the previous command.
