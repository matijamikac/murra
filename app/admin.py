from django.contrib import admin

from .models import *


class OfferAdmin(admin.ModelAdmin):
	list_display = ('seller', 'title', 'publish_date', 'measure', 'quantity', 'price')


admin.site.register(Offer, OfferAdmin)

admin.site.register(Balance)
admin.site.register(UserProfile)

class TotalBalanceAdmin(admin.ModelAdmin):
	list_display = ('user', 'value')

admin.site.register(TotalBalance, TotalBalanceAdmin)

class TotalLiabilityAdmin(admin.ModelAdmin):
	list_display = ('user', 'value')

admin.site.register(TotalLiability, TotalLiabilityAdmin)

admin.site.register(Transaction)
admin.site.register(PositiveBalance)
admin.site.register(TextRating)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'parent')
	prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)

