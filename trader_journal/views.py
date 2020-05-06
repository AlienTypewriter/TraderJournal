from django.shortcuts import render
from . import models
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """View function for home page of site."""
    user = request.user
    num_ops = 0
    period_desc = 'No current period'
    if user.is_authenticated:
        num_ops = user.operation_set.count()
        periods = user.period_set.all()
        for period in periods:
            if period.is_current():
                period_desc = str(period)
    
    context = {
        'num_ops': num_ops,
        'period_desc': period_desc,
    }

    return render(request, 'index.html', context=context)