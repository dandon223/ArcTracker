flake8 = flake8 --require-plugins darglint,flake8,flake8-rst-docstrings,flake8-pyproject,mccabe,pycodestyle,pyflakes

format:
	isort .
	black .

check: format
	export DJANGO_SETTINGS_MODULE=ArcTracker.settings
	mypy . 
	$(flake8) . 
	pylint app

restart:
	rm -f db.sqlite3
	rm -f app/migrations/*.py
	python manage.py makemigrations app
	python manage.py migrate

start:
	python manage.py runserver