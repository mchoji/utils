# uncidr




## Use Case



## How-to







## Example

```
poetry run ./inProfiles.py -d contoso.com burp-base64-dir > profiles.csv
```

Filter out your own profile (which comes together in some results)

```
poetry run ./inProfiles.py -d contoso.com --query "publicIdentifier != 'your-id'" burp-base64-dir  > profiles.csv
```
