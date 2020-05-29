from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from . import models, conv

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class ActiveForm(forms.ModelForm):
    def clean_currency(self):
        data = self.cleaned_data['currency']
        if not conv.check_currency(data):
            raise ValidationError(_('This currency does not exist'))
        return data

    class Meta:
        model = models.Active
        fields = ('currency','amount','is_initial')
        labels = {'currency': _('Enter currency id'),'amount':_('Enter the amount of currency')}
        help_texts = {'currency': _('The currency id must be integreated into CoinAPI'),
        'amount':_('You can enter negative amounts of actives to signify a net loss.')}


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

    def amount_sold(self):
        data = self.cleaned_data['amount_sold']
        if data<=0 :
            raise ValidationError(_('Cannot sell a negative amount of a currency'))
        return data
    
    def clean_comission_percentage(self):
        data = self.cleaned_data['commission_percentage']
        if data<=0 or data>=100:
            raise ValidationError(_('Not a valid percentage'))
        return data

    class Meta:
        model = models.Operation
        fields = ('datetime','currency_bought','currency_sold','amount_bought','amount_sold','exchange_name','commission_percentage','is_maker','is_open')
        labels = {'currency_bought': _('Enter bought currency id'),'currency_sold': _('Enter spent currency id'),
        'amount_bought':_('Enter the amount of currency you received'),
        'amount_sold':_('Enter the amount of currency you spent')}
        help_texts = {'currency_bought': _('The currency id must be integreated into CoinAPI'),
        'currency_sold': _('The currency id must be integreated into CoinAPI')}

class PeriodForm(forms.ModelForm):
    def clean_date_end(self):
        data = self.cleaned_data['date_end']
        if data<self.cleaned_data['date_start']:
            raise ValidationError(_('The period cannot end before starting'))
        return data

    def clean_max_acts(self):
        data = self.cleaned_data['max_acts']
        if data<=0:
            raise ValidationError(_('Not a valid amount of actives'))
        return data

    def clean_max_freq(self):
        data = self.cleaned_data['max_freq']
        if data<=0:
            raise ValidationError(_('Not a valid amount of total operations'))
        return data

    def clean_max_simultaneous(self):
        data = self.cleaned_data['max_simultaneous']
        if data<=0:
            raise ValidationError(_('Not a valid amount of open operations'))
        return data

    class Meta:
        model = models.Period
        fields = ('date_start','date_end','max_acts','acts_window','max_freq','max_simultaneous','use_shoulder')
        labels = {'max_acts': _('Max actives'),
        'acts_window': _('Reset period'),
        'max_freq':_('Max in period'),
        'max_simultaneous':_('Max simultaneously open'),
        'use_shoulder':_('Use of shoulder')}
        help_texts = {'max_acts': _('How many actives will you own during the period'),
        'acts_window': _('How frequently does the total operation limit reset'),
        'max_freq':_('Limit on total operations in the period'),
        'max_simultaneous':_('Limit on open operations in the period'),
        'use_shoulder':_('Whether the use of shoulder is allowed')}

    