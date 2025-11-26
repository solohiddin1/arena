runserver:
	python3 manage.py runserver

runserver2:
	python3 manage.py runserver 8001

mig:
	python3 manage.py makemigrations && python3 manage.py migrate

admin:
	python3 manage.py createsuperuser

regions:
	python3 manage.py loaddata apps/shared/fixtures/regions.json

districts:
	python3 manage.py loaddata apps/shared/fixtures/districts.json
