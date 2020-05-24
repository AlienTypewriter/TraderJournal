from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from django.urls import reverse

import datetime
import time
from multiprocessing import Process

from . import conv

class Active(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=16,decimal_places=8)
    is_initial = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("active_detail", kwargs={"pk": self.pk})

    def get_in_usd(self):
        if self.currency=='USD':
            return self.amount
        query = f'/exchangerate/{self.currency}/USD'
        return conv.get_from_api(query).get('rate')*self.amount

    def __str__(self):
        return str(self.currency)+': '+str(self.amount)
    
class Operation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now,verbose_name='Date and time at which the operation was closed',null=True)
    currency_bought = models.CharField(max_length=20)
    currency_sold = models.CharField(max_length=20)
    exchange_name = models.CharField(max_length=30)
    amount_bought = models.DecimalField(max_digits=16,decimal_places=8)
    commission_percentage = models.DecimalField(max_digits=5,decimal_places=3)
    buy_rate = models.DecimalField(max_digits=9,decimal_places=4)
    eventual_rate = models.DecimalField(max_digits=9,decimal_places=4,default=0)
    is_maker = models.BooleanField()
    is_open = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse("operation_detail", kwargs={"pk": self.pk})
    
    def get_profit(self):
        profit_in_cur = (self.eventual_rate-self.buy_rate)*self.amount_bought
        query = f'/exchangerate/{self.currency}/USD'
        return conv.get_from_api(query).get('rate')*profit_in_cur

    def get_profit_perc(self):
        return (1-self.eventual_rate/self.buy_rate)*100

    def amount_sold(self):
        return self.get_rate()*self.amount_bought/(1-self.commission_percentage/100)

    def __wait_12_hours(self):
        time.sleep(43200)
        self.get_eventual_rate()

    def get_eventual_rate(self):
        if self.is_open == True:
            raise ValueError('The transaction is still open')
        first_pass = True
        prev_rate = 0
        check_time = self.datetime
        while True:
            check_time += datetime.timedelta(hours=12)
            if check_time<datetime.now():
                rate = self.get_rate(check_time)
                if first_pass:
                    prev_rate = rate
                    first_pass = False
                    continue
                else:
                    if prev_rate<self.buy_rate:
                        if rate>prev_rate:
                            self.eventual_rate=prev_rate
                            break
                    else:
                        if rate<prev_rate:
                            self.eventual_rate=prev_rate
                            break
                prev_rate = rate
            else:
                p = Process(target=self.__wait_12_hours)
                p.start()
        self.save()
    
    def get_period(self):
        p = Period.objects.filter(date_end__gte=self.date).order_by('date_end').first()
        if p.date_start<=self.date:
            return p
        else:
            return None

    def get_rate(self, datetime=self.datetime):
        query = f'/exchangerate/{self.currency_bought}/{self.currency_sold}'
        query+= f'/?time={datetime.isoformat(timespec="microseconds")[:-6]}0Z'
        return conv.get_from_api(query).get('rate')

    def __str__(self):
        return f'{self.amount_sold()} of {self.currency_sold} traded for {self.currency_bought}'
    
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
    limit_exceeded = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("period_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f'Started at: {str(self.date_start)}, ends (or ended) at: {str(self.date_end)}' 