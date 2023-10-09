# Online RSS Reader

🏗️The app is in very early stage of development.🚧

Main branch is auto-deployed at http://rss.hazadus.ru/feeds/.

## Libraries Used

- [Django](https://docs.djangoproject.com/en/4.2/)
- [feedparser](https://pythonhosted.org/feedparser/): Universal Feed Parser is a Python module for downloading and parsing syndicated feeds.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/): Beautiful Soup is a library that makes it easy to scrape information from web pages.
- [environs](https://pypi.org/project/environs/): `environs` is a Python library for parsing environment variables. 
- [coloredlogs](https://coloredlogs.readthedocs.io/en/latest/index.html): The coloredlogs package enables colored terminal output for Python’s logging module.
- [dateutil](https://pypi.org/project/python-dateutil/): The dateutil module provides powerful extensions to the 
  standard datetime module, available in Python.
- [gunicorn](https://github.com/benoitc/gunicorn): WSGI HTTP Server for UNIX, fast clients and sleepy applications. 
- [whitenoise](https://github.com/evansd/whitenoise): Radically simplified static file serving for Python web apps.
- [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/): Best debugging tool for Django.
- [Tailwind CSS](https://tailwindcss.com/)
  - [@tailwindcss/typography](https://tailwindcss.com/docs/typography-plugin): Beautiful typographic defaults for HTML you don't control. 

## Building Tailwind styles

```bash
npx tailwindcss -i ./static/src/input.css -o ./static/styles.css
# or
npx tailwindcss -i ./static/src/input.css -o ./static/styles.css --watch
```

## References

- [Advanced Logging Tutorial](https://docs.python.org/3/howto/logging.html#advanced-logging-tutorial)
- [Using WhiteNoise with Django](https://whitenoise.readthedocs.io/en/latest/django.html)
- [Tailwind CSS Django - Flowbite](https://flowbite.com/docs/getting-started/django/)
- [MDN: scrollIntoView() method](https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView)
- [MDN: Navigator: share() method](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share#syntax)
- [Django - Understand cached attributes](https://docs.djangoproject.com/en/4.2/topics/db/optimization/#understand-cached-attributes): Long story short – use `all()` on queryset whenever you 
  need to avoid queryset caching to get correct `count()` results. Took me half a day to figure this out.