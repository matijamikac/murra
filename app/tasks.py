from celery import Celery
from .app_settings import *

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def depreciation():
    list_of_positive_balances = PositiveBalance.objects.filter(charge__gt=0)

    for i in list_of_positive_balances:
    	if i.depreciation < 1:
	    	new_balance = Balance()
	        new_balance.value = i.charge * depreciation_provision
	        new_balance.user_id = i.user_id
	        new_balance.type = 5
	        #new_balance.offer_id = offer.id
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
