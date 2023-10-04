# Online RSS Reader

## Libraries Used

- [Django](https://docs.djangoproject.com/en/4.2/)
- [feedparser](https://pythonhosted.org/feedparser/): Universal Feed Parser is a Python module for downloading and parsing syndicated feeds.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/): Beautiful Soup is a library that makes it easy to scrape information from web pages.
- [environs](https://pypi.org/project/environs/): `environs` is a Python library for parsing environment variables. 
- [coloredlogs](https://coloredlogs.readthedocs.io/en/latest/index.html): The coloredlogs package enables colored terminal output for Python’s logging module.
- [dateutil](https://pypi.org/project/python-dateutil/): The dateutil module provides powerful extensions to the 
  standard datetime module, available in Python.
- [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/): Best debugging tool for Django.

## Building Tailwind styles

```bash
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css
# or
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch
```

## References

- [Advanced Logging Tutorial](https://docs.python.org/3/howto/logging.html#advanced-logging-tutorial)
- [Tailwind CSS Django - Flowbite](https://flowbite.com/docs/getting-started/django/)