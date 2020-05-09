from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction

from . import models, forms

@login_required
def index(request):
    """View function for home page of site."""
    user = request.user
    num_ops = 0
    period_desc = 'No current period'
    num_ops = user.operation_set.count()
    periods = user.period_set.all()
    for period in periods:
        if period.is_current():
            period_desc = str(period)
            break
    
    context = {
        'num_ops': num_ops,
        'period_desc': period_desc,
    }

    return render(request, 'index.html', context=context)

@transaction.atomic
def register(request):
    if request.user.is_authenticated():
        messages.error(_("You're already registered!"))
        return redirect('trader_journal:index')
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST, instance=request.user)
        profile_form = forms.ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile has been registered!'))
            return redirect('trader_journal:index')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = forms.UserForm(instance=request.user)
        profile_form = forms.ProfileForm(instance=request.user.profile)
    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('trader_journal:index')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = forms.UserForm(instance=request.user)
    return render(request, 'registration/profile.html', {
        'user_form': user_form
    })

class PeriodCreate(CreateView):
    model = models.Period
    fields = '__all__'

class PeriodUpdate(UpdateView):
    model = models.Period
    fields = '__all__'

class PeriodDelete(DeleteView):
    model = models.Period
    success_url = reverse_lazy('period')