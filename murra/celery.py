from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'murra.settings')

app = Celery('murra')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


from .app_settings import *
from .models import *


@app.task(bind=True)
def depreciation():
    list_of_positive_balances = PositiveBalance.objects.filter(charge__gt=0)

    for i in list_of_positive_balances:
    	if i.depreciation < 1:
	    	new_balance = Balance()
	    	new_balance.value = i.charge * depreciation_provision
	    	new_balance.user_id = i.user_id
	    	new_balance.type = 5
	    	new_balance.save()
	    	i.transactions.add(new_balance)
	    	i.charge -= new_balance.value

	    	total_balance = TotalBalance.objects.get(user_id=i.user_id)
	    	total_balance.value -= new_balance.value
	    	total_balance.save()

	    	murra = PositiveBalance()
	    	murra.value = new_balance.value
	    	murra.user_id = provision_receiver_id
	    	murra.charge = new_balance.value
	    	murra.positivebalance_type = 4
	    	murra.save()
	    	murra_totalbalance =TotalBalance.objects.get(user_id=provision_receiver_id)
	    	murra_totalbalance.value += murra.value
	    	murra_totalbalance.save()