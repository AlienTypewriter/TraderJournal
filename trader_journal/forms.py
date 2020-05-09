from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from . import models, conv

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class ProfileForm(forms.ModelForm):
    def clean_init_deposit(self):
        data = self.cleaned_data['init_deposit']
        if data < 0:
            raise ValidationError(_('Insufficient amount'))
        return data

    class Meta:
        model = models.Profile
        fields = ('init_deposit',)
        labels = {'init_deposit': _('Enter initial deposit')}
        help_texts = {'init_deposit': _('Enter the amount of fiat initially deposited into the exchange in USD')}

class ActiveForm(forms.ModelForm):
    def clean_amount(self):
        data = self.cleaned_data['amount']
        if data <= 0:
            raise ValidationError(_('Insufficient amount'))
        return data

    def clean_currency(self):
        data = self.cleaned_data['currency']
        if not conv.check_currency(data):
            raise ValidationError(_('This currency does not exist'))
        return data

    class Meta:
        model = models.Active
        fields = ('currency','amount')
        labels = {'currency': _('Enter currency id'),'amount':_('Enter the amount of currency')}
        help_texts = {'currency': _('The currency id must be integreated into CoinAPI')}


class OperationForm(forms.ModelForm):
    def clean_datetime(self):
        data = self.cleaned_data['datetime']
        if data > timezone.now():
            raise ValidationError(_('Operations cannot occur in the future'))
        return data

    def clean_currency_bought(self):
        data = self.cleaned_data['currency_bought']
        if not conv.check_currency(data):
            raise ValidationError(_('This currency does not exist'))
        return data

    def clean_currency_sold(self):
        data = self.cleaned_data['currency_sold']
        if not conv.check_currency(data):
            raise ValidationError(_('This currency does not exist'))
        return data

    def amount_bought(self):
        data = self.cleaned_data['amount_bought']
        if data<=0 :
            raise ValidationError(_('Cannot buy a negative amount of a currency'))
        return data
    
    def clean_comission_percentage(self):
        data = self.cleaned_data['comission_percentage']
        if data<=0 or data>=100:
            raise ValidationError(_('Not a valid percentage'))
        return data

    def clean_buy_rate(self):
        data = self.cleaned_data['buy_rate']
        if data<=0:
            raise ValidationError(_('Buy rate cannot be 0 or below'))
        return data

    class Meta:
        model = models.Operation
        fields = ('datetime','currency_bought','currency_sold','amount_bought','exchange_name','comission_percentage',
        'buy_rate','is_maker','is_open')
        labels = {'currency_bought': _('Enter currency id'),'currency_sold': _('Enter currency id'),
        'amount':_('Enter the amount of currency you received')}
        help_texts = {'currency_bought': _('The currency id must be integreated into CoinAPI'),
        'currency_bought': _('The currency id must be integreated into CoinAPI'),
        'buy_rate':_('How much one unit of currency bought costs compared to currency sold, i. e. 9800 for BTC/USD')}

    