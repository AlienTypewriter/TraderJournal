from django.urls import include, path
from . import views

app_name = 'trader_journal'
urlpatterns = [
    path('',views.index,name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
]