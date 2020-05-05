from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Trader(User):
    init_deposit = models.DecimalField(max_digits=12,decimal_places=4)

class Active(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=16,decimal_places=8)
    
class Operation(models.Model):
    user_id = models.ForeignKey(Trader, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now())
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=16,decimal_places=8)
    current_price = models.DecimalField(max_digits=9,decimal_places=4)
    eventual_price = models.DecimalField(max_digits=9,decimal_places=4,null=True,default=None)
    is_buy = models.BooleanField()
    is_maker = models.BooleanField()
    is_open = models.BooleanField(default=True)
    
    def get_period(self):
        p = Period.objects.get(date_end__gte=self.date).first()
        return p
    
class Period(models.Model):
    user_id = models.ForeignKey(Trader, on_delete=models.CASCADE)
    date_start = models.DateField(default=timezone.now())
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
    
    def is_current(self):
        if timezone.now()<self.date_end:
            return True
        return False
    