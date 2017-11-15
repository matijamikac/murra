from .models import *
from django import forms
from django.forms import widgets
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from functools import partial



def userid(request):
    data = request.user.id
    return data

class UserForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput, label="Lozinka")
    password2 = forms.CharField(label="Lozinka (ponovo)", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        labels = { 'username': 'Korisničko ime', 'email': 'Email adresa'}
        help_texts = { 'username': 'Upišite željeno korisničko ime.', }
        widgets = {'username': forms.TextInput(attrs={'size': 40}),
                    'email': forms.TextInput(attrs={'size': 40})} 

    def clean_password2(self):
        
        data = self.cleaned_data['password2']
          
        if data != self.cleaned_data['password']:        
            raise ValidationError('Unešena lozinka se ne podudara s prethodno upisanom')
        return data 
        

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'automatic_max')
        widgets = {'address': forms.Textarea(attrs={'rows': '3', 'cols': '40'}),
                 }
        localized_fields = '__all__'

class ProfileFormUpdate(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'automatic_max', 'birth_date', 'OIB', 'first_name', 'last_name', 'registration_date')
        localized_fields = '__all__'   

class UserFormUpdate(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)


class OfferForm(forms.ModelForm):
    
    class Meta:
        model = Offer
        exclude = ('seller', 'id', 'publish_date', 'active', 'category', )
        widgets = {'used_quantity': forms.NumberInput(attrs={'hidden': True}), 
        'address_type' : forms.RadioSelect(attrs={'class': 'list-unstyled',}), 
        'address': forms.Textarea(attrs={'rows': '3', 'cols': '40'})}
        localized_fields = '__all__'

    def clean(self):
        cleaned_data = super(OfferForm, self).clean()
        start = cleaned_data.get("start_quantity")
        used = cleaned_data.get("used_quantity")

        if start and used:
            # Only do something if both fields are valid so far.
            if start < used:
                raise ValidationError('Količinu ponude nije moguće postavite niže od već predane količine po ovoj ponudi')

class DefineQuantity(forms.Form):
    quantity = forms.IntegerField(label='Količina', min_value=1, initial=1, localize=True)
    
    def __init__(self, *args, **kwargs):
        super(DefineQuantity, self).__init__(*args, **kwargs)
        self.fields['quantity'].error_messages = {'required' : 'Upišite količinu koju želite preuzeti'}


class SearchUsers(forms.Form):
    name = forms.CharField(label='Ime', localize=True, required=False)
    surname = forms.CharField(label='Prezime', localize=True, required=False)
    town = forms.CharField(label='Mjesto', localize=True, required=False)


class DateRange(forms.Form):
    start_date = forms.DateTimeField(label='Početni datum', localize=True, input_formats=['%d-%m-%Y'], widget=forms.DateTimeInput(attrs={'class': 'datepicker'}))
    end_date = forms.DateTimeField(label='Završni datum', localize=True, widget=forms.DateTimeInput(attrs={'class': 'datepicker'}))


class TextRatingForm(forms.ModelForm):
    
    class Meta:
        model = TextRating
        exclude = ('user', 'transaction', 'date')
        widgets = {'value': forms.RadioSelect}
        localized_fields = '__all__'


"""
class SettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
       super(SettingsForm, self).__init__(*args, **kwargs)
       self.fields['max_liab'].widget.attrs['readonly'] = True
       self.fields['max_liab'].widget.attrs['class'] = "form-control"
       #self.fields['automatic_max'].widget.attrs['class'] = "form-control"
       #self.fields['auto_maximum'].widget.attrs['class'] = "form-control"
       self.fields['maximum_sale'].widget.attrs['class'] = "form-control"
    
    class Meta:
        model = UserProfile
        fields = ('automatic_increment','max_liab', 'auto_maximum', 'automatic_max', 'maximum_sale')
        labels = { 'automatic_increment':'Automatsko povećavanje obveze',
                    'max_liab':'Vaš maksimalni kreditni limit',
                    'automatic_max': '',
                    'maximum_sale':'Prihvatljivi maksimalni promet' }
        help_texts = { 'auto_maximum': ('Unesite vašu željenu maksimalnu obvezu a koja nije veća od vašeg maksimalnog kreditnog limita'), 
                        'automatic_increment':'Uključite opciju ukoliko želite ponuditi Udruzi vrijednost višu od vašeg kreditnog limita, čime se ostvaruje mogućnost da raspoloživ saldo za razmjene automatski raste za iznos neiskorištenog raspoloživog kreditnog limita u slučaju gdje on padne ispod naznačene željene razine',
                        'max_liab':'Trenutni maksimalni dozvoljeni kreditni limit temeljen na vašoj aktivnosti u Udruzi',
                        'maximum_sale':'Vaš maksimalni iznos ponuda koje ste spremni razmijeniti u razdoblju od 30 dana. Po prelasku ove granice sve vaše ponude će automatski biti izbrisane iz sustava'
                        }
        widgets = {'auto_maximum': forms.RadioSelect()}
        
    def clean_automatic_max(self):
        
        data = self.cleaned_data['automatic_max']
          
        if data > self.cleaned_data['max_liab']:        
            raise ValidationError('Unešeni limit je veći od vašeg dozvoljenog')
        return data    
"""

