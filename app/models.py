from django.db import models
from django.urls import reverse #Used to generate URLs by reversing the URL patterns

import uuid
from datetime import datetime, date
from django.utils import timezone
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User
from .app_settings import *
from stdimage import StdImageField



class UserProfile(models.Model):
    user = models.OneToOneField(User)
    OIB = models.CharField('OIB', max_length=11, unique=True, validators=[RegexValidator(regex='^\d{11}$', message='Unesite ispravni OIB')])
    first_name = models.CharField('Ime', max_length=20)
    last_name = models.CharField('Prezime', max_length=25)
    address = models.CharField('Adresa', max_length=30)
    town = models.CharField('Mjesto', max_length=15)
    phone = models.CharField('Telefon', max_length=15, validators=[RegexValidator(r'^[0-9\s()_+-]+$', 'Upišite ispravan broj telefona')])
    #auto_maximum = models.CharField('Automatska obveza', blank=False, default = 'a', max_length=1, choices=(('a', 'automatski maksimum'), ('b', 'korisnički unos')),)
    #max_liab = models.PositiveIntegerField(default=max_liability)
    automatic_max = models.DecimalField(max_digits=15, decimal_places=2, default=max_liability, )
    birth_date = models.DateField('Datum rođenja', null=True, blank=True)
    profile_photo = StdImageField('Fotka', 
                    upload_to = 'images/profile_photos', 
                    help_text="Opcionalna profilna fotografija", 
                    default = 'images/profile_photos/no_photo.png', 
                    variations={
                                'small': (100, 100, True),
                                'thumbnail': (200, 200, True),})

    summary = models.TextField('Kratki opis', max_length=1000, help_text="Opcionalno recite nešto o sebi i proizvodima i uslugama koje nudite", blank=True, null=True)
    registration_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('profile', args=[self.pk])

class Category(models.Model):

    name = models.CharField('kategorija', max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True)

   
    @property
    def level(self):
        if self.parent is None:
            level = 1
        else:
            level = self.parent.level + 1
        return level
        
    
    def __str__(self):    
        return self.name

    def get_absolute_url(self):
        return reverse('offers_by_category', args=[self.slug])

    class Meta:
        ordering = ('name',)
        verbose_name = 'kategorija'
        verbose_name_plural = 'kategorije'


class Offer(models.Model):
    
    title = models.CharField('Naziv ponude', max_length=70)
    category = models.ForeignKey(Category, verbose_name='Kategorija')
    seller = models.ForeignKey(User)
    summary = models.TextField('Opis ponude', max_length=1000, help_text="Unesite kratki opis vaše ponude")
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular offer")
    used_quantity = models.PositiveIntegerField(default=0)
    start_quantity = models.PositiveIntegerField('Količina',)
    publish_date = models.DateField('Objavljeno', default=timezone.now)
    active = models.BooleanField(default=True)
    

    def quantity(self):
        return self.start_quantity - self.used_quantity
    quantity = property(quantity)

    def _get_total(self):
    	return self.quantity * self.price
    value = property(_get_total)
    
    def __str__(self):    
        return self.title
    
    def get_absolute_url(self):
        return reverse('offer-detail', args=[self.pk])

    measure_type = (
        ('kom', 'komad'),
        ('kg', 'kilogram'),
        ('h', 'sat'),
       )

    measure = models.CharField('Jedinična mjera', max_length=3, choices=measure_type,  
        default='kom')
    price = models.DecimalField('Cijena po jedinici', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    addresses = (
        (1, 'Kućna adresa'),
        (2, 'Druga adresa'),)
    address_type = models.IntegerField('Adresa preuzimanja', choices=addresses, default=1, help_text="Gdje se može preuzeti vaša roba/usluga?")
    address = models.TextField('Adresa', max_length=500, blank=True, null=True)
    offer_pic = StdImageField('Fotografija', 
                upload_to = 'images/offer_pics', 
                help_text="Opcionalna fotografija uz vašu ponudu", 
                default = 'images/offer_pics/no-img.jpg', 
                variations={
                            #'large': (600, 400),
                            'thumbnail': (120, 120, True),
    })
    

    class Meta:
        ordering = ["publish_date"]


class Transaction(models.Model):
    offer = models.ForeignKey(Offer)
    buyer = models.ForeignKey(User)
    quantity = models.PositiveIntegerField('Količina')
    date = models.DateTimeField('Provedeno', default=timezone.now)
    #id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    rated = models.BooleanField(default = False)

    @property
    def value(self):
        return self.quantity * self.offer.price

    def get_absolute_url(self):
        
        return reverse('transaction_complete', args=[self.pk])

    def __str__(self):    
        return self.offer.title


class Balance(models.Model):
    value = models.DecimalField('Vrijednost', max_digits=15, decimal_places=2)
    user = models.ForeignKey(User)
    balance_type = models.IntegerField(default=1) #1 = provizija, 2=ažuriranje ponude, 3=brisanje ponude, 4=transakcija
    trans = models.ForeignKey(Transaction, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    offer = models.ForeignKey(Offer, null=True, blank=True)

    class Meta:
        ordering = ['date']

class TotalLiability(models.Model):
    value = models.DecimalField(max_digits=15, decimal_places=2)
    user = models.OneToOneField(User)

    def __str__(self):    
        return self.user.username

class TotalBalance(models.Model):
    value = models.DecimalField(max_digits=15, decimal_places=2)
    user = models.OneToOneField(User)

    def __str__(self):    
        return self.user.username

class PositiveBalance(models.Model):
    value = models.DecimalField('Vrijednost', max_digits=15, decimal_places=2)
    user = models.ForeignKey(User)
    publish_date = models.DateTimeField(default=timezone.now)
    transactions = models.ManyToManyField(Balance)
    charge = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    positivebalance_type = models.IntegerField(default=1) #1=nova ponuda, 2=automatski po transakciji, 3=MURRA
    offer = models.ForeignKey(Offer, null=True, blank=True)
    transaction = models.ForeignKey(Transaction, null=True, blank=True)

    @property
    def used(self):
        return self.value - self.charge

    @property
    def depreciation(self):
        days = timezone.now() - self.publish_date
        return depreciation_days - days.days

    class Meta:
        ordering = ['publish_date']

class TextRating(models.Model):
    user = models.ForeignKey(User)
    transaction = models.OneToOneField(Transaction)
    text_rating = models.TextField('Komentar', max_length=1000, null=True, blank=True, help_text="Unesite vaše dojmove vezano uz korisnika odnosno robu/uslugu")
    date = models.DateTimeField(default=timezone.now)
    RATINGS = (
        (1, 'Loše'),
        (2, 'Moglo bi i bolje'),
        (3, 'Zadovoljavajuće'),
        (4, 'Vrlo dobro'),
        (5, 'Odlično'),
    )
    value = models.IntegerField(choices=RATINGS, help_text='Ocijenite korisnika i preuzetu robu/uslugu od 1-5',)
    