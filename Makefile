runserver:
	python manage.py runserver

mig:
	python manage.py makemigrations && python manage.py migrate

admin:
	python manage.py createsuperuser
