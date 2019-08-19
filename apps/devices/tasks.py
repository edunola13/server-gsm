from __future__ import absolute_import, unicode_literals
from celery import task


@task()
def update_status(id):
    print (id)
    print ("Aca va")
