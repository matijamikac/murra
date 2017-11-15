from django.conf.urls import url

from . import views


urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^udruga/$', views.about, name='about'),
	url(r'^users/$', views.users, name='users'),
	#url(r'^ponude/$', views.OfferListView.as_view(), name='offers'),
	url(r'^ponude/$', views.list_of_offers, name='offers'),
	url(r'^ponude/pretraga$', views.SearchListView.as_view(), name='search_list_view'),
	url(r'^lista_ponuda/(?P<category_slug>[-\w]+)$', views.list_of_offers_by_category, name='offers_by_category'),
	url(r'^ponude/(?P<pk>[-\w]+)$', views.offerdetail, name='offer-detail'),
	url(r'^ponude/(?P<pk>[-\w]+)/transaction/$', views.offertransaction, name='transaction'),
	url(r'^ponude/transaction/complete/(?P<pk>[-\w]+)$', views.transaction_complete, name='transaction_complete'),
	url(r'^profil/(?P<user_id>[\d]+)$', views.userprofile, name='profile'),
	url(r'^profil/ratings/(?P<user_id>[\d]+)$', views.ratings_list, name='ratings_list'),
	url(r'^userprofile/$', views.user_profile, name='user_profile'),
	url(r'^userprofile/update$', views.user_profile_update, name='user_profile_update'),
	url(r'^userprofile/balance$', views.user_balance, name='user_balance'),
	url(r'^transactions$', views.user_transactions, name='user_transactions'),
	url(r'^obligations$', views.user_obligations, name='user_obligations'),
	url(r'^transactions/(?P<pk>[\d]+)$', views.leave_feedback, name='leave_feedback'),
	url(r'^transactions/(?P<pk>[\d]+)/update$', views.feedback_update, name='feedback_update'),
	#url(r'^userprofile/settings/$', views.user_settings, name='user_settings'),
	
]

urlpatterns += [   
    url(r'^mojeponude/$', views.OffersByUserListView.as_view(), name='user-offers'),
]

urlpatterns += [
	url(r'^ponude/nova-ponuda/$', views.choose_category, name='choose_category'),  
    url(r'^ponude/nova-ponuda/(?P<category_slug>[-\w]+)$', views.offerform, name='offer_create'),
    url(r'^ponude/(?P<pk>[-\w]+)/update/$', views.offerupdate, name='offer_update'),
    url(r'^ponude/(?P<pk>[-\w]+)/delete_offer/$', views.offer_delete, name='offer_delete'),
    #url(r'^ponude/(?P<pk>[-\w]+)/delete/$', views.OfferDelete.as_view(), name='offer_delete1'),
]

urlpatterns += [  
    url(r'^registracija/$', views.register, name='registration'),
    url(r'^registracija/lozinka$', views.change_password, name='change_password'),
]