runserver:
	python manage.py runserver

mig:
	python manage.py makemigrations && python manage.py migrate

admin:
	python manage.py createsuperuser

regions:
	python3 manage.py loaddata apps/shared/fixtures/regions.json

districts:
	python3 manage.py loaddata apps/shared/fixtures/districts.json
