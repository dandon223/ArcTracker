flake8 = flake8 --require-plugins darglint,flake8,flake8-rst-docstrings,flake8-pyproject,mccabe,pycodestyle,pyflakes

format:
	isort .
	black .

check: format
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