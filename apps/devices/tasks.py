from __future__ import absolute_import, unicode_literals
from celery import task
import time

from apps.devices.client import GSMClient


@task()
def update_status(id):
    print ("Por Aqui Voy")
    try:
        gsm = GSMClient(id)
        status = gsm.get_status()
        print (status)
    except Exception as e:
        print (e)
