flake8 = flake8 --require-plugins darglint,flake8,flake8-rst-docstrings,flake8-pyproject,mccabe,pycodestyle,pyflakes
TEST_TARGET ?= 
format:
	isort .
	black .

format_check:
	isort . --check
	black . --check

test:
	python manage.py test $(TEST_TARGET)

check: format_check
	mypy . 
	$(flake8) . 
	export DJANGO_SETTINGS_MODULE=ArcTracker.settings ; pylint app

restart:
	rm -f db.sqlite3
	rm -f app/migrations/*.py
	python manage.py makemigrations app
	python manage.py migrate

initial_data:
	python3 manage.py loaddata app/initial_data/initial_data.json

start:
	python manage.py runserver

full_restart: restart initial_data start