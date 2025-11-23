runserver:
	python3 manage.py runserver

mig:
	python3 manage.py makemigrations && python3 manage.py migrate

admin:
	python3 manage.py createsuperuser

regions:
	python3 manage.py loaddata apps/shared/fixtures/regions.json

districts:
	python3 manage.py loaddata apps/shared/fixtures/districts.json
