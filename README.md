# utils
A set of utilities for daily hacking


## Disclaimer

I created this project just to host some scripts that I use in daily (legal) hacking.
Do not expect much technical sophistication on them (you have been told).


## Dependencies

The dependencies are not managed by each script individualy but per project instead.
If you feel lazy and just want to get started, just clone this repo and run

```
poetry install
```

If you are not familiar with `poetry`, refer to their
[usage guide](https://python-poetry.org/docs/basic-usage/).

Alternatively, you could install dependencies with `pip`:

```
pip install -r requirements.txt
```


## Get Started

There is a README inside each directory with description and usage example for each tool.


## Tips

Some tools rely solely on built-in libraries, which make them easier to symlink to `bin`
directory of your choice.

The following are pure Python or shell scripts:
  - [quote](quote)
  - [android-burp-cert](android-burp-cert)
  - [extract-emails](extract-emails)
  - [burp2json](burp2json)


## License

This project is licensed under MIT License. See [LICENSE](LICENSE) for more details.
