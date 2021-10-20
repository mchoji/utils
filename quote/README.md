# quote

URL encode/decode lines from a file or from stdin

## Use Case

You have a wordlist that should be properly encoded before use it in Burp Intruder, Hydra or similar.

## Help

These are really simple scripts that don't need help messages.


## Example

```
echo Contoso@2021 | ./quote.py
Contoso%402021
```

```
echo Contoso@2021 | ./quote.py | ./unquote.py
Contoso@2021
```

```
./quote.py wordlist
Contoso%402021
Contoso%232021
Contoso%252021
```

```
./quote.py wordlist | ./unquote.py
Contoso@2021
Contoso#2021
Contoso%2021
```

