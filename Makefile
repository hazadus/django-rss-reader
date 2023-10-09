reset_db:
	rm db.sqlite3
	python -m manage migrate
	python -m manage createsuperuser
update_feeds:
	python -m manage add_feeds
	python -m manage update_feeds
dumpdata:
	python manage.py dumpdata --indent=2 --output=./feeds/tests/fixtures/feeds.json feeds.Feed
	python manage.py dumpdata --indent=2 --output=./feeds/tests/fixtures/entries.json feeds.Entry
	python manage.py dumpdata --indent=2 --output=./feeds/tests/fixtures/tags.json feeds.Tag
	python manage.py dumpdata --indent=2 --output=./users/tests/fixtures/users.json users.CustomUser
format:
	python -m isort --profile black .
lint:
	python -m isort --check-only --profile black .
	flake8 .
test:
	python -m manage test --timing --shuffle
run:
	python -m manage runserver