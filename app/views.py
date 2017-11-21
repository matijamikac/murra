from django.shortcuts import render, redirect, get_object_or_404, render_to_response

from .models import *
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.urls import reverse_lazy
import uuid
from django.views.generic import View, FormView
from .forms import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from .app_settings import *
import operator
from functools import reduce
from django.db.models import Q
from django.template import RequestContext
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify

def index(request):
    
    data = Offer.objects.all()

    def market_size(data):
    	total = 0
    	for i in data:
    		total += i.value
    	return total

    num_users=User.objects.all().count()
    num_offers=Offer.objects.filter(active=True).count()
    market_size= market_size(data)
    
    
    return render(
        request,
        'index.html',
        context={'num_users':num_users,'num_offers':num_offers,'market_size':market_size},
    )
def about(request):
    return render(
        request,
        'about.html')

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        total_balance = TotalBalance()
        total_liability = TotalLiability()
        if user_form.is_valid() and profile_form.is_valid():
            userreg = user_form.save(commit=False)
            reg_number = len(User.objects.all())+1

            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            userreg.set_password(password)
            userreg.id = reg_number

            profile = profile_form.save(commit=False)
            profile.user_id = reg_number
            total_balance.user_id = reg_number
            total_balance.value = 0
            total_liability.user_id = reg_number
            total_liability.value = 0

            userreg.save()
            profile.save()
            total_balance.save()
            total_liability.save()

            messages.add_message(request, messages.INFO, 'Registracija uspješna.')
            return HttpResponseRedirect(reverse('login'))
        else:
            messages.error(request, ('Molimo ispravite greške.'))
    else:
        user_form = UserForm(None)
        profile_form = ProfileForm(None)

    return render(request, 
        'app/registration_form.html', 
        context={'user_form': user_form, 'profile_form': profile_form})  

def user_profile_update(request):
    user = get_object_or_404(User, id=request.user.id)
    user_profile = get_object_or_404(UserProfile, user_id=request.user.id)

    if request.method == 'POST':
        user_form = UserFormUpdate(request.POST, instance=user)
        profile_form = ProfileFormUpdate(request.POST, request.FILES, instance=user_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.add_message(request, messages.INFO, 'Uspješna izmjena podataka.')
            return HttpResponseRedirect(reverse('user_profile'))
        else:
            messages.error(request, ('Molimo ispravite greške.'))

    else:
        user_form = UserFormUpdate(instance=user)
        profile_form = ProfileFormUpdate(instance=user_profile)


    return render(request, 
        'app/user_profile_update.html', 
        context={'profile_form': profile_form, 'user_form':user_form})  

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Lozinka je uspješno promijenjena!')
            return redirect('user_profile')
        else:
            messages.error(request, 'Ispravite greške.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })

def userprofile(request, user_id):

    user_profile = UserProfile.objects.get(user_id=user_id)
    user_offers = Offer.objects.filter(seller_id=user_id).filter(active=True).order_by('publish_date')
    ratinginstances = TextRating.objects.filter(user_id=user_id)
    num_instances = len(ratinginstances)

    def rating(x):
        
        total = 0
        if len(x) > 0:
            for i in x:
                total += i.value
            average = total / len(x)
        else:
            average = 0
        return average
    rating = rating(ratinginstances)
    

    return render(
        request,
        'app/profile.html',
        context={'user_profile': user_profile, 'user_offers': user_offers,
                'rating': rating, 'ratinginstances': ratinginstances, 'num_instances': num_instances
        },
    )

@login_required
def user_profile(request):

   
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    user_offers = Offer.objects.filter(seller=request.user).filter(active=True).order_by('publish_date')
    ratinginstances = TextRating.objects.filter(user_id=request.user.id)
    num_instances = len(ratinginstances)

    def rating(x):
        
        total = 0
        if len(x) > 0:
            for i in x:
                total += i.value
            average = total / len(x)
        else:
            average = 0
        return average
    rating = rating(ratinginstances)
    
    def offertotal(x):
        offertotal=0
        for i in x:
            offertotal+=i.value
        return offertotal
    total_offer = offertotal(user_offers)

    return render(
        request,
        'app/user_profile.html',
        context={'user_profile':user_profile,
         'total_offer':total_offer, 'user_offers': user_offers,
                'rating': rating, 'ratinginstances': ratinginstances, 'num_instances': num_instances},
    )

"""
@login_required
def user_settings(request):
    item = get_object_or_404(UserProfile, user_id=request.user.id)
    if request.method == 'POST':
        
        form = SettingsForm(request.POST, instance=item)
        
        if form.is_valid():
            item.automatic_increment = form.cleaned_data['automatic_increment']
            if item.auto_maximum == 'a':
                item.automatic_max = item.max_liab
            else:
                item.automatic_max = form.cleaned_data['automatic_max']
            item.maximum_sale = form.cleaned_data['maximum_sale']
            item.save()

            return HttpResponseRedirect(reverse('user_profile'))

        else:
            messages.error(request, ('Molimo ispravite greške.')) 

    else:
        form = SettingsForm(instance=item)
        
    return render(request, 
        'app/user_settings.html', 
        context={'form': form,
        'item': item})    
"""

def user_balance(request):

    date_form = DateRange()
    data = PositiveBalance.objects.filter(user_id=request.user.id).order_by('-publish_date')
        
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    if start is not None and end is not None:
        def date_format_change(x):
            string = x[6:]+ x[2:6]+ x[:2]
            return string
        start_date = date_format_change(start)
        end_date = date_format_change(end) + ' 23:59'
        data = data.filter(publish_date__range=[start_date, end_date])
        date_form = DateRange(request.GET)
    
    paginator = Paginator(data, 15) 

    page = request.GET.get('page')
    try:
        balances = paginator.page(page)
    except PageNotAnInteger:
        balances = paginator.page(1)
    except EmptyPage:
        balances = paginator.page(paginator.num_pages)

    return render(
        request,
        'app/user_balance.html',
        context={'page_obj':balances, 'date_form': date_form } 
    )

"""
class OfferListView(generic.ListView):
    model = Offer
    paginate_by = 15

    def get_queryset(self):
        return Offer.objects.filter(quantity__gt=0).order_by('publish_date')
"""

def list_of_offers(request):
    offer_list = Offer.objects.filter(active=True).order_by('publish_date')
    main_categories = Category.objects.filter(parent_id__isnull=True)
    subcategories = Category.objects.filter(parent_id__isnull=False)


    def final_category(main_categories, subcategories):
        dic_of_final_categories={}
        for i in main_categories:
            list_of_subcategories=[]
            for sub in subcategories:
                if sub.parent_id == i.id:
                    list_of_subcategories.append(sub)
            dic_of_final_categories[i] = list_of_subcategories
        return dic_of_final_categories
    final_categories = final_category(main_categories, subcategories)

    paginator = Paginator(offer_list, 15) 

    page = request.GET.get('page')
    try:
        offers = paginator.page(page)
    except PageNotAnInteger:
        offers = paginator.page(1)
    except EmptyPage:
        offers = paginator.page(paginator.num_pages)

    return render(
        request,
        'app/offer_list_by_category.html',
        context={'page_obj':offers, 'final_categories':final_categories } 
    )

def list_of_offers_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    def category1(x):
        if x.parent_id is not None:
            category1 = Category.objects.get(id=x.parent_id)
        else:
            category1= None
        return category1
    category1=category1(category)
    
    def category2(x):
        if x is not None:
            if x.parent_id is not None:
                category2=Category.objects.get(id=x.parent_id)
            else:
                category2= None
        else:
            category2 = None
        return category2
    category2 = category2(category1)

    #main_categories = Category.objects.filter(parent_id__isnull=True)
    subcategories = Category.objects.filter(parent_id__isnull=False)

    
    def second_category(subcategories):
        list_of_categories=[]
        for sub in subcategories:
            if sub.parent_id == category.id:
                list_of_categories.append(sub)
        return list_of_categories
    second_categories = second_category(subcategories)

    def final_category(subcategories, second_categories):
        dic_of_final_categories={}
        for i in second_categories:
            list_of_final_categories=[]
            for sub in subcategories:
                if sub.parent_id == i.id:
                    list_of_final_categories.append(sub)
            dic_of_final_categories[i] = list_of_final_categories
        return dic_of_final_categories
    final_categories = final_category(subcategories, second_categories)

    
    def categories_list(x):
        categories_to_list =[]
        categories_to_list.append(x.id)
        for sub in subcategories:
            if sub.parent_id == x.id:
                categories_to_list.append(sub.id)
                for i in subcategories:
                    if i.parent_id == sub.id:
                        categories_to_list.append(i.id)
        return categories_to_list
    categories_to_list=categories_list(category)

    offer_list = Offer.objects.filter(category_id__in=categories_to_list).filter(active=True).order_by('publish_date')

    paginator = Paginator(offer_list, 15) 

    page = request.GET.get('page')
    try:
        offers = paginator.page(page)
    except PageNotAnInteger:
        offers = paginator.page(1)
    except EmptyPage:
        offers = paginator.page(paginator.num_pages)

    return render(
        request,
        'app/offer_list_by_category.html',
        context={'page_obj':offers,
         'category':category, 
         'category1':category1,
         'category2': category2,
         'final_categories': final_categories } 
    )

class OffersByUserListView(LoginRequiredMixin, generic.ListView):
    model = Offer
    template_name ='app/user_offers.html'
    paginate_by = 15

   
    def get_queryset(self):
        return Offer.objects.filter(seller=self.request.user).filter(active=True).order_by('publish_date')


@login_required
def choose_category(request):
    categories = Category.objects.filter(parent_id__isnull=True)
    subcategories = Category.objects.filter(parent_id__isnull=False)

    if request.method == 'POST':
        slug = request.POST['slug']
        user_input = request.POST['user_input']
        category = get_object_or_404(Category, slug=slug)
        new_category = Category()
        new_category.parent_id = category.id
        new_category.name = user_input
        new_category.slug = slugify(user_input)
        new_category.save()

    return render(
        request,
        'app/choose_category1.html',
        context={'categories':categories, 'subcategories':subcategories } 
    )


@login_required
def offerform(request, category_slug):
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    total_balance = TotalBalance.objects.get(user=request.user)
    total_liability = TotalLiability.objects.get(user=request.user)
    available = user_profile.automatic_max - total_liability.value
    category = get_object_or_404(Category, slug=category_slug)

    if request.method == 'POST':
        offer_form = OfferForm(request.POST, request.FILES)
        positive_balance = PositiveBalance()
        

        if offer_form.is_valid():
            
            offer = offer_form.save(commit=False)
        
            offer.seller = request.user
            offer.category = category
            positive_balance.user_id = request.user.id
        
            if (total_liability.value + offer.value)<=user_profile.automatic_max:
                total_balance.value += offer.value
                total_liability.value += offer.value
                positive_balance.value = offer.value
                positive_balance.charge = offer.value
            else:
                difference = user_profile.automatic_max - total_liability.value

                total_balance.value += difference
                positive_balance.value = difference
                positive_balance.charge = difference
                total_liability.value += difference
        
            offer.save()
            total_liability.save()

            if positive_balance.value > 0:
                positive_balance.offer_id = offer.id
                if provision > 0:
                    new_balance = Balance()
                    new_balance.value = positive_balance.value * provision
                    new_balance.user_id = request.user.id
                    new_balance.offer_id = offer.id
                    new_balance.save()
                    positive_balance.save()
                    positive_balance.transactions.add(new_balance)
                    positive_balance.charge -= new_balance.value
                    total_balance.value -= new_balance.value

                    murra = PositiveBalance()
                    murra.value = new_balance.value
                    murra.user_id = provision_receiver_id
                    murra.charge = new_balance.value
                    murra.positivebalance_type = 3
                    murra.save()
                    murra_totalbalance =TotalBalance.objects.get(user_id=provision_receiver_id)
                    murra_totalbalance.value += murra.value
                    murra_totalbalance.save()
                positive_balance.save()
            else:
                pass
            total_balance.save()
            return redirect(offer)
        else:
            messages.error(request, ('Molimo ispravite greške.'))
        
    else:
        offer_form = OfferForm(None)
        

    return render(request, 
        'app/offer_form.html', 
        context={'offer_form': offer_form, 'category':category})    


@login_required
def offerupdate(request, pk):
    item = get_object_or_404(Offer, pk=pk)

    if request.method == 'POST':
        x = Offer.objects.filter(seller=request.user).filter(active=True)
        def offertotal(x):
            offertotal=0
            for i in x:
                offertotal+=i.value
            return offertotal
        total_offer = offertotal(x)
        old_value = item.value
        new_total = total_offer - old_value

        total_balance = TotalBalance.objects.get(user=request.user)
        total_liability = TotalLiability.objects.get(user=request.user)
        userprofile = UserProfile.objects.get(user=request.user)
        net_liability = total_liability.value - total_balance.value


        form = OfferForm(request.POST, request.FILES, instance=item)

        if form.is_valid():

            offer = form.save(commit = False)
            new_value = (form.cleaned_data['start_quantity'] - item.used_quantity) * form.cleaned_data['price']
            old_liability = total_liability.value
            new_offer_total = new_total + new_value

            if net_liability <= new_offer_total:
                offer.save()

                if new_offer_total < old_liability:
                    difference = old_liability - new_offer_total
                    total_liability.value = old_liability - difference
                    total_balance.value -= difference
                elif new_offer_total > old_liability:
                    remainder = new_offer_total - old_liability
                    if old_liability < userprofile.automatic_max:
                        old_max_diff = userprofile.automatic_max - old_liability
                        if remainder >= old_max_diff:
                            total_liability.value += old_max_diff
                            total_liability.value += old_max_diff
                        else:
                            total_liability.value += remainder
                            total_balance.value += remainder
                else:
                    pass    
                

                if total_liability.value > old_liability:
                    positive_balance = PositiveBalance()
                    positive_balance.value = total_liability.value - old_liability
                    positive_balance.charge = total_liability.value - old_liability
                    positive_balance.user_id = request.user.id
                    positive_balance.offer_id = offer.id
                    if provision > 0:
                        new_balance = Balance()
                        new_balance.value = positive_balance.value * provision
                        new_balance.user_id = request.user.id
                        new_balance.offer_id = offer.id
                        new_balance.save()
                        positive_balance.charge -= new_balance.value
                        positive_balance.save()
                        positive_balance.transactions.add(new_balance)
                        positive_balance.charge -= new_balance.value
                        total_balance.value -= new_balance.value

                        murra = PositiveBalance()
                        murra.value = new_balance.value
                        murra.user_id = provision_receiver_id
                        murra.charge = new_balance.value
                        murra.positivebalance_type = 3
                        murra.save()
                        murra_totalbalance =TotalBalance.objects.get(user_id=provision_receiver_id)
                        murra_totalbalance.value += murra.value
                        murra_totalbalance.save()
                    positive_balance.save()
                    
                elif total_liability.value < old_liability:
                    total = old_liability - total_liability.value
                    list_pos_balance = PositiveBalance.objects.filter(user_id=request.user.id).filter(charge__gt=0)
                    for i in list_pos_balance:
                        balance_buyer = Balance()
                        balance_buyer.balance_type = 2 #2 je oznaka za balance koji dolazi od ažuriranja ponude
                        balance_buyer.offer_id = offer.id
                        balance_buyer.user_id = request.user.id
                        charged = i.charge
                        if total >= charged:
                            balance_buyer.value = charged
                            balance_buyer.save()
                            i.charge = 0
                            i.transactions.add(balance_buyer)
                            i.save()
                            total -= charged
                        else:
                            if total != 0:
                                balance_buyer.value = total
                                balance_buyer.save()
                                i.charge -= total
                                i.transactions.add(balance_buyer)
                                i.save()
                            else:
                                pass
                            break
                else:
                    pass

                total_liability.save()
                total_balance.save()

                    
                return redirect(offer)
            else:
                messages.error(request, ('Nije moguće promijeniti ponudu. S navedenim promjenama nije moguće zadovoljiti saldo obveza. Molimo promijenite parametre ili unesite novu ponudu prije promjene ove.'))

            return redirect(offer)
        else:
            messages.error(request, ('Molimo ispravite greške.'))

    else:
        form = OfferForm(instance=item)

    return render(request, 
        'app/offer_update.html', 
        context={'form': form})    


 

def offer_delete(request, pk):
       
    offer = Offer.objects.get(pk=pk)

    if request.method == 'POST':

        x = Offer.objects.filter(seller=request.user).filter(active=True)
        def offertotal(x):
            offertotal=0
            for i in x:
                offertotal+=i.value
            return offertotal
        total_offer = offertotal(x)
        old_value = offer.value
        new_total = total_offer - old_value

        total_balance = TotalBalance.objects.get(user=request.user)
        old_balance = total_balance.value
        total_liability = TotalLiability.objects.get(user=request.user)
        old_liability = total_liability.value
        userprofile = UserProfile.objects.get(user=request.user)
        net_liability = total_liability.value - old_balance

        if net_liability <= new_total:

            if new_total < old_liability:
                difference = old_liability - new_total
                total_liability.value = old_liability - difference
                total_balance.value -= difference
            else:
                pass

            if total_balance.value < old_balance:

                total = old_balance - total_balance.value
                list_pos_balance = PositiveBalance.objects.filter(user_id=request.user.id).filter(charge__gt=0)
                for i in list_pos_balance:
                    balance_buyer = Balance()
                    balance_buyer.balance_type = 3
                    balance_buyer.offer_id = offer.id
                    balance_buyer.user_id = request.user.id
                    charged = i.charge
                    if total >= charged:
                        balance_buyer.value = charged
                        balance_buyer.save()
                        i.charge = 0
                        i.transactions.add(balance_buyer)
                        i.save()
                        total -= charged
                    else:
                        if total != 0:
                            balance_buyer.value = total
                            balance_buyer.save()
                            i.charge -= total
                            i.transactions.add(balance_buyer)
                            i.save()
                        else:
                            pass
                        break

                total_liability.save()
                total_balance.save()
                offer.active = False
                offer.save()

                messages.add_message(request, messages.INFO, 'Ponuda obrisana.')
                return HttpResponseRedirect(reverse('user-offers'))

            else:
                total_liability.save()
                total_balance.save()
                offer.active = False
                offer.save()
                messages.add_message(request, messages.INFO, 'Ponuda obrisana.')
                return HttpResponseRedirect(reverse('user-offers'))

        else:
            messages.error(request, ('Nije moguće izbrisati ponudu. S navedenim promjenama nije moguće zadovoljiti saldo obveza. Molimo unesite novu ponudu prije brisanja ove ili izmijenite ovu.'))


    return render(request, 
        'app/offer_confirm_delete.html',
        context={'offer': offer}) 




def offerdetail(request, pk):

    offer = Offer.objects.get(pk=pk)
    
    return render(
        request,
        'app/offer_detail.html',
        context={'offer':offer},
    )

@login_required
def offertransaction(request, pk):

    data = Offer.objects.get(pk=pk)
    title = data.title
    summary = data.summary
    seller = data.seller
    value = data.value
    price = data.price
    quantity = data.quantity
    measure = data.measure
    pk = data.pk

    if request.method == 'POST':
        quantityform = DefineQuantity(request.POST)
        sellerprofile = UserProfile.objects.get(user=seller)
        offer = get_object_or_404(Offer, pk=pk)
        total_balance = TotalBalance.objects.get(user_id=request.user.id)
        total_liability = TotalLiability.objects.get(user=seller)
        positive_balance = PositiveBalance.objects.filter(user_id=request.user.id).filter(charge__gt=0)
        trans = Transaction()
        if quantityform.is_valid():
            if quantityform.cleaned_data['quantity'] <= quantity:
                transaction = quantityform.cleaned_data['quantity'] * price
                if total_balance.value >= transaction:
                    total_balance.value -= transaction
                    total_balance.save()

                    trans.offer_id = data.pk
                    trans.buyer_id = request.user.id
                    trans.quantity = quantityform.cleaned_data['quantity']
                    offer.used_quantity += quantityform.cleaned_data['quantity']
                    offer.save()
                    trans.save()
                    
                    total = transaction
                    for i in positive_balance:
                        balance_buyer = Balance()
                        balance_buyer.balance_type = 4
                        balance_buyer.trans_id = trans.id
                        balance_buyer.user_id = request.user.id
                        charged = i.charge
                        if total >= charged:
                            balance_buyer.value = charged
                            balance_buyer.save()
                            i.charge = 0
                            i.transactions.add(balance_buyer)
                            i.save()
                            total -= charged
                        else:
                            if total != 0:
                                balance_buyer.value = total
                                balance_buyer.save()
                                i.charge -= total
                                i.transactions.add(balance_buyer)
                                i.save()
                            else:
                                pass
                            break

                    automax = transaction*liability_growth
                    sellerprofile.automatic_max += automax
                    
                    sellerprofile.save()

                    sell_pos_balance = PositiveBalance()
                    sell_pos_balance.positivebalance_type = 2
                    sell_pos_balance.transaction_id = trans.id
                    sell_total_balance = TotalBalance.objects.get(user=seller)
                    sell_pos_balance.user_id = data.seller_id
                    sell_pos_balance.value = 0
                    sell_pos_balance.charge = 0
                    if transaction >=total_liability.value:
                        remainder = transaction - total_liability.value
                        total_liability.value = 0
                        sell_pos_balance.value = remainder
                        sell_pos_balance.charge = remainder
                        sell_total_balance.value += remainder
                    else:
                        total_liability.value -= transaction

                    
                    x = Offer.objects.filter(seller=seller).filter(active=True)
                    def offertotal(x):
                        offertotal=0
                        for i in x:
                            offertotal+=i.value
                        return offertotal
                    total_offer = offertotal(x)
                    available_liab = sellerprofile.automatic_max - total_liability.value
                    offer_difference = total_offer - total_liability.value

                    if offer_difference >= available_liab:
                        total_liability.value += available_liab
                        sell_pos_balance.value += available_liab
                        sell_pos_balance.charge += available_liab
                        sell_total_balance.value += available_liab
                    else:
                        total_liability.value += offer_difference
                        sell_pos_balance.value += offer_difference
                        sell_pos_balance.charge += offer_difference
                        sell_total_balance.value += offer_difference

                    total_liability.save()                 
                    if sell_pos_balance.value != 0:
                        if provision > 0:
                            new_balance = Balance()
                            new_balance.value = sell_pos_balance.value * provision
                            new_balance.user_id = data.seller_id
                            new_balance.save()
                            sell_pos_balance.charge -= new_balance.value
                            sell_pos_balance.save()
                            sell_pos_balance.transactions.add(new_balance)
                            sell_pos_balance.charge -= new_balance.value
                            sell_total_balance.value -= new_balance.value

                            murra = PositiveBalance()
                            murra.value = new_balance.value
                            murra.user_id = provision_receiver_id
                            murra.charge = new_balance.value
                            murra.positivebalance_type = 3
                            murra.save()
                            murra_totalbalance =TotalBalance.objects.get(user_id=provision_receiver_id)
                            murra_totalbalance.value += murra.value
                            murra_totalbalance.save()
                        sell_pos_balance.save()
                    sell_total_balance.save()       
                    return redirect(trans)
                else:
                    messages.error(request, ('Nedovoljan saldo.'))
            else:
                messages.error(request, ('Zatražena količina nije dostupna'))
        else:
            messages.error(request, ('Molimo ispravite greške.'))

    else:
        quantityform = DefineQuantity()

    return render(
        request,
        'app/transaction.html',
        context={'pk':pk, 'title':title,'seller':seller,'price':price, 'value':value, 'summary':summary, 
        'quantity':quantity, 'measure':measure, 'quantityform':quantityform},
    )

@login_required
def transaction_complete(request, pk):

    data = Transaction.objects.get(pk=pk)
    offer_id = data.offer_id
    data2 = Offer.objects.get(id=offer_id)

    seller_id = data2.seller_id
    seller = data2.seller
    title = data2.title
    quantity = data.quantity
    measure = data2.measure
    price = data2.price
    value = quantity * price

    messages.add_message(request, messages.INFO, 'Transakcija uspješna.')

    return render(
        request,
        'app/transaction_complete.html',
        context={'title':title, 'seller':seller, 'seller_id':seller_id,'price':price, 'value':value,  
        'quantity':quantity, 'measure':measure},
    )



class SearchListView(generic.ListView):
    
    model = Offer
    paginate_by = 15
    template_name = 'app/offer_list_by_category.html'

    def get_queryset(self):
        result = super(SearchListView, self).get_queryset().filter(active=True)

        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(operator.and_,
                       (Q(title__icontains=q) for q in query_list)) |
                reduce(operator.and_,
                       (Q(summary__icontains=q) for q in query_list))
            )

        return result

@login_required
def user_transactions(request):

    date_form = DateRange()
    transactions_list = Transaction.objects.filter(buyer_id=request.user.id).order_by('-date')
            
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    if start is not None and end is not None:
        def date_format_change(x):
            string = x[6:]+ x[2:6]+ x[:2]
            return string
        start_date = date_format_change(start)
        end_date = date_format_change(end) + " 23:59"
        transactions_list = transactions_list.filter(date__range=[start_date, end_date])
        date_form = DateRange(request.GET)

    paginator = Paginator(transactions_list, 15) 

    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(request,
        'app/user_transactions.html',
        context={'page_obj': transactions, 'date_form':date_form})

@login_required
def user_obligations(request):

    date_form = DateRange()
    seller_offers = Offer.objects.filter(seller_id=request.user.id)
    list_of_offer_ids = []
    for i in seller_offers:
        list_of_offer_ids.append(i.id)

    transactions_list = Transaction.objects.filter(offer_id__in=list_of_offer_ids).order_by('-date')
            
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    if start is not None and end is not None:
        def date_format_change(x):
            string = x[6:]+ x[2:6]+ x[:2]
            return string
        start_date = date_format_change(start)
        end_date = date_format_change(end) + " 23:59"
        transactions_list = transactions_list.filter(date__range=[start_date, end_date])
        date_form = DateRange(request.GET)

    paginator = Paginator(transactions_list, 15) 

    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(request,
        'app/user_obligations.html',
        context={'page_obj': transactions, 'date_form':date_form})

@login_required
def leave_feedback(request, pk):

    transaction = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        rating_form = TextRatingForm(request.POST)
        if rating_form.is_valid():
            ratinginstance = rating_form.save(commit=False)
            ratinginstance.user = transaction.offer.seller
            ratinginstance.transaction_id = transaction.id
            transaction.rated=True
            
            ratinginstance.save()
            transaction.save()

            messages.add_message(request, messages.INFO, 'Ocjena korisnika, odnosno robe/usluge uspješna.')
            return HttpResponseRedirect(reverse('user_transactions'))
        else:
            messages.error(request, ('Molimo ispravite greške.'))
    else:
        rating_form = TextRatingForm(None)


    return render(request, 
        'app/rating_form.html', 
        context={'rating_form': rating_form,
                'transaction': transaction})

@login_required
def feedback_update(request, pk):

    ratinginstance = get_object_or_404(TextRating, transaction_id=pk)
    transaction = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        rating_form = TextRatingForm(request.POST, instance=ratinginstance)
        if rating_form.is_valid():
            updated_rating = rating_form.save(commit=False)
            
            updated_rating.save()

            messages.add_message(request, messages.INFO, 'Ocjena uspješno izmijenjena.')
            return HttpResponseRedirect(reverse('user_transactions'))
        else:
            messages.error(request, ('Molimo ispravite greške.'))
    else:
        rating_form = TextRatingForm(instance=ratinginstance)


    return render(request, 
        'app/rating_form.html', 
        context={'rating_form': rating_form,
                'transaction': transaction,
                'ratinginstance': ratinginstance})


def ratings_list(request, user_id):
    list_of_ratings = TextRating.objects.filter(user_id=user_id).order_by('-date')
    userinstance= get_object_or_404(User, id=user_id)

    return render(request, 
    'app/ratings_list.html', 
    context={'list_of_ratings': list_of_ratings, 'userinstance':userinstance})

def users(request):

    users_list = UserProfile.objects.all().order_by('?')
    name = request.GET.get('name')
    surname = request.GET.get('surname')
    town = request.GET.get('town')

    if surname:
        users_list = users_list.filter(last_name=surname)
    if name:
        users_list = users_list.filter(first_name=name)
    if town:
        users_list = users_list.filter(town=town)
    form = SearchUsers(request.GET)
    
    paginator = Paginator(users_list, 20) 

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request,
        'app/user_search.html',
        context={'page_obj': page_obj, 'form': form})
