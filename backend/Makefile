flake8 = flake8 --require-plugins darglint,flake8,flake8-rst-docstrings,flake8-pyproject,mccabe,pycodestyle,pyflakes

format:
	isort .
	black .

check: format
	mypy . 
	$(flake8) . 
	pylint app ArcTracker

restart:
	rm db.sqlite3
	python manage.py makemigrations app
	python manage.py migrate

start:
	python manage.py runserver