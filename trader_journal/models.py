from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

import datetime
import time
from multiprocessing import Process

from . import conv


def get_current_period(user):
        try:
                current_period=Period.objects.get(user_id=user,date_end__gte=date.today(),date_start__lte=date.today())
                return current_period
        except ObjectDoesNotExist:
                return None

class Active(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=16,decimal_places=8)
    is_initial = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("trader_journal:active_detail", kwargs={"pk": self.pk})

    def get_in_usd(self):
        if self.currency=='USD':
            return self.amount
        query = f'/exchangerate/{self.currency}/USD'
        return conv.get_from_api(query).get('rate')*float(self.amount)

    def __str__(self):
        return str(self.currency)+': '+str(self.amount)
    
class Operation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now,verbose_name='Date and time at which the operation was closed',null=True)
    currency_bought = models.CharField(max_length=20)
    currency_sold = models.CharField(max_length=20)
    exchange_name = models.CharField(max_length=30)
    amount_bought = models.DecimalField(max_digits=16,decimal_places=8)
    amount_sold = models.DecimalField(max_digits=16,decimal_places=8)
    commission_percentage = models.DecimalField(max_digits=5,decimal_places=3)
    eventual_rate = models.DecimalField(max_digits=9,decimal_places=4,default=None,null=True)
    is_maker = models.BooleanField()
    is_open = models.BooleanField()

    def buy_rate(self):
        return self.amount_sold/self.amount_bought

    def get_absolute_url(self):
        return reverse("trader_journal:operation_detail", kwargs={"pk": self.pk})
    
    def get_profit(self):
        if self.eventual_rate is None:
            return 0
        return (self.eventual_rate-self.buy_rate())*self.amount_bought

    def get_profit_perc(self):
        if self.eventual_rate is None:
            return 0
        return (1-self.eventual_rate/self.buy_rate())*100

    def get_eventual_rate(self):
        if self.is_open == True:
            return
        first_pass = True
        prev_rate = 0
        check_time = self.datetime
        while check_time<timezone.now():
            check_time += datetime.timedelta(hours=12)
            rate = self.get_rate(check_time)
            if first_pass:
                prev_rate = rate
                first_pass = False
                continue
            else:
                if prev_rate<self.buy_rate():
                    if rate/prev_rate>=1.02:
                        self.eventual_rate=prev_rate
                        break
                else:
                    if rate/prev_rate<=0.98:
                        self.eventual_rate=prev_rate
                        break
                prev_rate = rate
        self.save()
    
    def get_period(self):
        return Period.objects.filter(date_start__lte=self.datetime,date_end__gte=self.datetime).order_by('date_end').first()

    def get_rate(self, datetime=datetime):
        if datetime is None:
            return None
        query = f'/exchangerate/{self.currency_bought}/{self.currency_sold}'
        query+= f'/?time={datetime.isoformat(timespec="microseconds")[:-6]}0Z'
        return conv.get_from_api(query).get('rate')

    def __str__(self):
        return f'{self.amount_sold} of {self.currency_sold} traded for {self.amount_bought} of {self.currency_bought}'
    
class Period(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date_start = models.DateField(default=timezone.now)
    date_end = models.DateField()
    max_acts = models.PositiveSmallIntegerField()
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    window_choices = [(DAY,'Day'),(WEEK,'Week'),(MONTH,'Month')]
    acts_window = models.CharField(max_length=1,choices=window_choices,default=DAY)
    max_freq = models.PositiveSmallIntegerField()
    max_simultaneous = models.PositiveSmallIntegerField()
    use_shoulder = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("trader_journal:period_detail", kwargs={"pk": self.pk})

    def get_num_ops(self):
        return Operation.objects.filter(user_id=self.user_id,datetime__gte=self.date_start,datetime__lte=self.date_end).count()

    def get_num_ops_open(self):
        return Operation.objects.filter(user_id=self.user_id,datetime__gte=self.date_start,datetime__lte=self.date_end,is_open=True).count()

    def get_total_profit(self):
        profit = 0
        ops = Operation.objects.filter(user_id=self.user_id,datetime__gte=self.date_start,datetime__lte=self.date_end).all()
        for op in ops:
            profit+=op.get_profit()
        return profit

    def limit_exceeded(self):
        ops = Operation.objects.filter(user_id=self.user_id,datetime__gte=self.date_start,datetime__lte=self.date_end).all()
        for op in ops:
            if self.acts_window=='D' and ops.filter(datetime__day=op.datetime.day).count()>self.max_freq:
                return True
            elif self.acts_window=='W' and ops.filter(datetime__week=op.datetime.week).count()>self.max_freq:
                return True
            elif self.acts_window=='M' and ops.filter(datetime__month=op.datetime.month).count()>self.max_freq:
                return True
        if self.get_num_ops_open()>self.max_simultaneous:
            return True
        if self.date_end>=date.today() and self.date_start<=date.today():
            if Active.objects.filter(user_id=self.user_id).count()>self.max_acts:
                return True
        return False

    def __str__(self):
        return f'Started at: {str(self.date_start)}, ends (or ended) at: {str(self.date_end)}'