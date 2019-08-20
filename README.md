# GSM Api

# Dependencies
Only run in Linuxs
`sudo apt-get install i2c-tools libi2c-dev python-dev python3-dev`

`redis`

# Redis
https://redis.io/download
Conviene usar un docker

# Celery
https://medium.com/@yedjoe/celery-4-periodic-task-in-django-9f6b5a8c21c7
"""
For dev: celery -A proj worker -l info -B
"""

"""
For prod: 
celery -A proj worker -l info
celery -A proj beat -l info
"""