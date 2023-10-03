reset_db:
	rm db.sqlite3
	python -m manage migrate
	python -m manage createsuperuser
update_feeds:
	python -m manage add_feeds
	python -m manage update_feeds
run:
	python -m manage runserver