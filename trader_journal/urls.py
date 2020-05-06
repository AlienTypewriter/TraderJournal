from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'trader_journal'
urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/',include('django.contrib.auth.urls'))
]