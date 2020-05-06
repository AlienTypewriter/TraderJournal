from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import date


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    init_deposit = models.DecimalField(max_digits=12,decimal_places=4, null=True)

    def __str__(self):
        user = User.objects.get(profile__id=self.id)
        return str(user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Active(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=16,decimal_places=8)

    def __str__(self):
        return str(self.currency)+': '+self.amount
    
class Operation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    currency = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=16,decimal_places=8)
    current_price = models.DecimalField(max_digits=9,decimal_places=4)
    eventual_price = models.DecimalField(max_digits=9,decimal_places=4,null=True,default=None)
    is_buy = models.BooleanField()
    is_maker = models.BooleanField()
    is_open = models.BooleanField(default=True)
    
    def get_period(self):
        p = Period.objects.get(date_end__gte=self.date).order_by('date_end').first()
        if p.date_start<=self.date:
            return p
        else:
            return None
    
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
    
    def is_current(self):
        if date.today()<=self.date_end and date.today()>=self.date_start:
            return True
        return False

    def __str__(self):
        return 'Started at: '+str(self.date_start)+', ends (or ended) at: '+str(self.date_end)    