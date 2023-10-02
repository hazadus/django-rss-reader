reset_db:
	rm db.sqlite3
	python -m manage migrate
	python -m manage createsuperuser
run:
	python -m manage runserver