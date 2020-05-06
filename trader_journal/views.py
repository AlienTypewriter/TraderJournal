from django.shortcuts import render
from . import models
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """View function for home page of site."""
    user = request.user
    num_ops = user.operation_set.count()
    period_desc = ''
    current_period = user.period_set.get(is_current=True).first()
    if current_period is not None:
        period_desc = str(current_period)
    else:
        period_desc = 'No current period'
    
    context = {
        'num_ops': num_ops,
        'period_desc': period_desc,
    }

    return render(request, 'index.html', context=context)