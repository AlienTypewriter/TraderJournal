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

@login_required
def index(request):
    """View function for home page of site."""
    user = request.user
    num_ops = 0
    cur_period = None
    period_exists = False
    num_ops = user.operation_set.count()
    periods = user.period_set.all()
    actives = user.active_set.all()
    for period in periods:
        if period.is_current():
            cur_period = period
            period_exists = True
            break
    context = {
        'num_ops': num_ops,
        'period_exists': period_exists,
        'cur_period': cur_period,
        'actives':actives
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
            return redirect('trader_journal:index')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        op_form = forms.OperationForm()
    return render(request, 'operation_form.html', {
        'form': op_form
    })

class UserDetailView(generic.DetailView):
    def get_object(self, queryset=None):
        obj = super(PeriodUpdate,self).get_object()
        if not obj.user_id==self.request.user:
            raise Http404
        else:
            return obj

class UserListView(generic.ListView):
    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise Http404
        else:
            return models.Active.objects.filter(user_id=self.request.user)

class UserUpdateView(generic.UpdateView):
    def get_object(self, queryset=None):
        obj = super(PeriodUpdate,self).get_object()
        if not obj.user_id==self.request.user:
            raise Http404
        else:
            return obj

class UserDeleteView(generic.UpdateView):
    def get_object(self, queryset=None):
        obj = super(PeriodUpdate,self).get_object()
        if not obj.user_id==self.request.user:
            raise Http404
        else:
            return obj

class OperationDetailView(UserDetailView):
    model = models.Operation

class OperationListView(generic.ListView):
    model = models.Operation

class OperationUpdate(UserUpdateView):
    model = models.Operation
    fields = ['datetime','currency_bought','currency_sold','exchange_name','amount_bought',
    'commission_percentage','buy_rate','is_maker','is_open']

@login_required
class OperationDelete(UserDeleteView):
    model = models.Operation
    success_url = reverse_lazy('operation')

@login_required
@transaction.atomic
def add_active(request):
    if request.method == 'POST':
        act_form = forms.ActiveForm(request.POST)
        if act_form.is_valid():
            active = act_form.save(commit=False)
            active.user_id = request.user
            if active.user_id.active_set.filter(currency=active.currency).exists():
                messages.error(request, _('You already have this active registered to your account. Please edit it instead of adding duplicates.'))
            else:
                active.save()
                messages.success(request, _('Active saved!'))
                return redirect('trader_journal:index')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        act_form = forms.ActiveForm()
    return render(request, 'active_form.html', {
        'form': act_form
    })

class ActiveDetailView(UserDetailView):
    model = models.Active

class ActiveListView(UserListView):
    model = models.Active

class ActiveUpdate(UserUpdateView):
    model = models.Active
    fields = ['currency','amount','is_initial']

class ActiveDelete(UserDeleteView):
    model = models.Active
    success_url = reverse_lazy('active')

@login_required
@transaction.atomic
def add_period(request):
    if request.method == 'POST':
        per_form = forms.PeriodForm(request.POST)
        if per_form.is_valid():
            period = per_form.save(commit=False)
            period.user_id = request.user
            overlap = models.Period.objects.exclude((Q(date_end__gte=period.date_start) | Q(date_start__lte=period.date_end)))
            if overlap.exists():
                messages.error(request, _('Overlapping periods are not allowed!'))
            else:
                period.save()
                messages.success(request, _('Period saved!'))
                return redirect('trader_journal:index')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        per_form = forms.PeriodForm()
    return render(request, 'period_form.html', {
        'form': per_form
    })

class PeriodDetailView(UserDetailView):
    model = models.Period

class PeriodListView(UserListView):
    model = models.Period

class PeriodUpdate(UpdateView):
    model = models.Active
    fields = ['date_start','date_end','max_acts','acts_window','max_freq','max_simultaneous','use_shoulder']    

class PeriodDelete(DeleteView):
    model = models.Period
    success_url = reverse_lazy('period')