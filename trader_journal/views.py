from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.views import generic
from django.db.models import Q
from django.http import Http404

from . import models, forms
import logging

logger = logging.getLogger(__name__)

@login_required
def index(request):
    """View function for home page of site."""
    user = request.user
    num_ops = 0
    cur_period = models.get_current_period(user)
    num_ops = user.operation_set.count()
    actives = user.active_set.order_by('-amount')[:5]
    total_worth = 0
    profit_made = 0
    initial_deposit = 0
    for act in actives:
        active_worth = act.get_in_usd()
        total_worth+= float(active_worth)
        if act.is_initial:
            initial_deposit+=float(active_worth)
        else:
            profit_made+=float(active_worth)
    context = {
        'num_ops': num_ops,
        'cur_period': cur_period,
        'actives':actives,
        'total_worth':total_worth,
        'profit_made':profit_made,
        'initial_deposit':initial_deposit,
    }
    return render(request, 'index.html', context=context)

@transaction.atomic
def register(request):
    if request.user.is_authenticated:
        messages.error(request,_("You're already registered!"))
        return redirect('trader_journal:index')
    if request.method == 'POST':
        user_form = forms.RegisterForm(request.POST)
        if user_form.is_valid():
            user = User.objects.create_user(user_form.data['username'], user_form.data['email'], user_form.data['password'])
            user.save()
            messages.success(request, _('Your profile has been registered!'))
            return redirect('trader_journal:index')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = forms.RegisterForm()
    return render(request, 'registration/register.html', {
        'user_form': user_form
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

@login_required
@transaction.atomic
def add_operation(request):
    if request.method == 'POST':
        op_form = forms.OperationForm(request.POST)
        if op_form.is_valid():
            operation = op_form.save(commit=False)
            operation.user_id = request.user
            period = operation.get_period()
            if period is not None:
                all_ops = models.Operation.objects.filter(datetime__gte=period.date_start, datetime__lte=period.date_end)
                if operation.is_open:
                    open_ops = all_ops & models.Operation.objects.filter(is_open=True)
                    if len(open_ops)>=period.max_simultaneous:
                        messages.warning(request, _('Open deal limit for period reached!'))
                        period.limit_exceeded = True
                if period.acts_window=='D':
                    all_ops = all_ops & models.Operation.objects.filter(datetime__day=operation.datetime.day)
                elif period.acts_window == 'W':
                    all_ops = all_ops & models.Operation.objects.filter(datetime__week=operation.datetime.week)
                else:
                    all_ops = all_ops & models.Operation.objects.filter(datetime__month=operation.datetime.month)
                if len(all_ops)>=period.max_freq:
                    messages.warning(request, _('Operation limit for period reached!'))
                    period.limit_exceeded = True
                    period.save()
            operation.save()
            messages.success(request, _('Operation saved!'))
            return redirect('trader_journal:operations')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        op_form = forms.OperationForm()
    return render(request, 'trader_journal/operation_form.html', {
        'form': op_form
    })

class UserDetailView(generic.DetailView):
    def get_object(self, queryset=None):
        obj = super(UserDetailView,self).get_object()
        if not obj.user_id.id==self.request.user.id:
            raise Http404
        else:
            return obj

class UserUpdateView(generic.UpdateView):
    def get_object(self, queryset=None):
        obj = super(UserUpdateView,self).get_object()
        if not obj.user_id.id==self.request.user.id:
            raise Http404
        else:
            return obj

class UserDeleteView(generic.DeleteView):
    def get_object(self, queryset=None):
        obj = super(UserDeleteView,self).get_object()
        if not obj.user_id.id==self.request.user.id:
            raise Http404
        else:
            return obj

class OperationDetailView(UserDetailView):
    model = models.Operation

class OperationListView(generic.ListView):
    model = models.Operation
    
    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise Http404
        else:
            return self.request.user.operation_set.all()

class OperationUpdate(UserUpdateView):
    form_class = forms.OperationForm
    model = models.Operation

class OperationDelete(UserDeleteView):
    model = models.Operation
    success_url = reverse_lazy('trader_journal:operations')

@login_required
@transaction.atomic
def add_active(request):
    if request.method == 'POST':
        act_form = forms.ActiveForm(request.POST)
        if act_form.is_valid():
            active = act_form.save(commit=False)
            active.user_id = request.user
            per = models.get_current_period(request.user)
            if per is not None:
                if per.max_acts<=request.user.active_set.count():
                    messages.warning(request, _('You have exceeded the current limit of actives for the current period.'))
            if request.user.active_set.filter(currency=active.currency).exists():
                messages.error(request, _('You already have this active registered to your account. Please edit it instead of adding duplicates.'))
            else:
                active.save()
                messages.success(request, _('Active saved!'))
                return redirect('trader_journal:actives')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        act_form = forms.ActiveForm()
    return render(request, 'trader_journal/active_form.html', {
        'form': act_form
    })

class ActiveDetailView(UserDetailView):
    model = models.Active

class ActiveListView(generic.ListView):
    model = models.Active

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise Http404
        else:
            return self.request.user.active_set.all()

class ActiveUpdate(UserUpdateView):
    form_class = forms.ActiveForm
    model = models.Active

class ActiveDelete(UserDeleteView):
    model = models.Active
    success_url = reverse_lazy('trader_journal:actives')

def add_period(request):
    if request.method == 'POST':
        per_form = forms.PeriodForm(request.POST)
        if per_form.is_valid():
            period = per_form.save(commit=False)
            period.user_id = request.user
            if request.user.period_set.exclude(Q(date_end__lt=period.date_start)|Q(date_start__gt=period.date_end)).exists():
                messages.error(request, _('Overlapping periods are not allowed.'))
            else:
                period.save()
                messages.success(request, _('Period saved!'))
                return redirect('trader_journal:periods')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        per_form = forms.PeriodForm()
    return render(request, 'trader_journal/period_form.html', {
        'form': per_form
    })

class PeriodDetailView(UserDetailView):
    model = models.Period

class PeriodListView(generic.ListView):
    model = models.Period

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise Http404
        else:
            return self.request.user.period_set.all()

def update_period(request):
    if request.method == 'POST':
        per_form = forms.PeriodForm(request.POST)
        if per_form.is_valid():
            period = per_form.save(commit=False)
            period.user_id = request.user
            if request.user.period_set.exclude(Q(pk=period.pk)|Q(date_end__lt=period.date_start)|Q(date_start__gt=period.date_end)).exists():
                messages.error(request, _('Overlapping periods are not allowed.'))
            else:
                period.save()
                messages.success(request, _('Period updated!'))
                return redirect('trader_journal:periods')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        per_form = forms.PeriodForm()
    return render(request, 'trader_journal/period_form.html', {
        'form': per_form
    })

class PeriodUpdate(UserUpdateView):
    form_class = forms.PeriodForm
    model = models.Period  

class PeriodDelete(UserDeleteView):
    model = models.Period
    success_url = reverse_lazy('trader_journal:periods')