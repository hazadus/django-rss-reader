# Online RSS Reader

Inspired by amazing [NetNewsWire](https://netnewswire.com/) Mac/iOS app – the best RSS reader out there!

🏗️The app is in very early stage of development.🚧

Main branch is auto-deployed at http://rss.hazadus.ru/.

![Arc screenshot](./static/images/arc_screen_1.png)

## Libraries and Tools Used

- [Django](https://docs.djangoproject.com/en/4.2/)
    - [django-allauth](https://pypi.org/project/django-allauth/): Integrated set of Django applications addressing authentication, registration, account management as well as 3rd party (social) account authentication.
    - [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/): Best debugging tool for Django.
- [Celery](https://docs.celeryq.dev/en/stable/index.html): simple, flexible, and reliable distributed system to 
  process vast amounts of messages, while providing operations with the tools required to maintain such a system.
- [RabbitMQ](https://www.rabbitmq.com/): most widely deployed open source message broker.
- Feed Parsing:
  - [feedparser](https://pythonhosted.org/feedparser/): Universal Feed Parser is a Python module for downloading and parsing syndicated feeds.
  - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/): Beautiful Soup is a library that makes it easy to scrape information from web pages.
  - [dateutil](https://pypi.org/project/python-dateutil/): The dateutil module provides powerful extensions to the 
    standard datetime module, available in Python.
- Serving App in Production:
  - [gunicorn](https://github.com/benoitc/gunicorn): WSGI HTTP Server for UNIX, fast clients and sleepy applications. 
  - [whitenoise](https://github.com/evansd/whitenoise): Radically simplified static file serving for Python web apps.
  - [nginx](https://nginx.org/): nginx *(engine x)* is an HTTP and reverse proxy server, a mail proxy server, and a 
    generic TCP/UDP proxy server, originally written by Igor Sysoev.
- Styling:
  - [Tailwind CSS](https://tailwindcss.com/)
    - [@tailwindcss/typography](https://tailwindcss.com/docs/typography-plugin): Beautiful typographic defaults for HTML you don't control. 
- Misc:
  - [environs](https://pypi.org/project/environs/): `environs` is a Python library for parsing environment variables. 
  - [coloredlogs](https://coloredlogs.readthedocs.io/en/latest/index.html): The coloredlogs package enables colored terminal output for Python’s logging module.
  - [coverage](https://pypi.org/project/coverage/): Coverage.py measures code coverage, typically during test execution.

## Running in Dev Mode

Create `.env` file with the following variables:

```bash
SECRET_KEY=django-secret-key
DEBUG=True
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432CELERY_BROKER_URL=amqp://rmuser:rmpassword@localhost:5672//
```

Containers `db`, `worker`, `mq` should be up and running in background.

Use `make run` to start the app.

## Deploy

Create `.env` file with the following variables:

```bash
SECRET_KEY=django-secret-key
DEBUG=False
SENTRY_DSN=sentry-dsn-only-in-production-(optional)
```

Use `docker compose up -d` to run the app.

## Dev Notes

### Building Tailwind styles

```bash
npx tailwindcss -i ./static/src/input.css -o ./static/styles.css
# or
npx tailwindcss -i ./static/src/input.css -o ./static/styles.css --watch
```

### Building fixtures for tests

```bash
# Create fresh DB
python -m manage migrate
# Create test users with subscriptions
python -m manage add_test_data
# Fetch feeds for test users
python -m manage update_feeds
#
# Mark some stuff as read, some as favorite...
#
# Dump all data to fixtures
make dumpdata
```

## References

- [Advanced Logging Tutorial](https://docs.python.org/3/howto/logging.html#advanced-logging-tutorial)
- [Using WhiteNoise with Django](https://whitenoise.readthedocs.io/en/latest/django.html)
- [Whitenoise - Add compression and caching support](https://whitenoise.readthedocs.io/en/latest/django.html#add-compression-and-caching-support)
- [Whitenoise - Why do I get “ValueError: Missing staticfiles manifest entry for …”?](https://whitenoise.readthedocs.io/en/latest/django.html#why-do-i-get-valueerror-missing-staticfiles-manifest-entry-for)
- [Tailwind CSS Django - Flowbite](https://flowbite.com/docs/getting-started/django/)
- [MDN: scrollIntoView() method](https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView)
- [MDN: Navigator: share() method](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share#syntax): 
  `navigator.share()` will only work when app is served via HTTPS.
- [Django - Understand cached attributes](https://docs.djangoproject.com/en/4.2/topics/db/optimization/#understand-cached-attributes): Long story short – use `all()` on queryset whenever you 
  need to avoid queryset caching to get correct `count()` results. Took me half a day to figure this out.

## Repo Activity 

![Repo Activity](https://repobeats.axiom.co/api/embed/d68c55d646134fe9a358583df8a78dc7a3240b93.svg "Repobeats analytics 
image")
