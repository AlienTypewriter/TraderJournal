from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'trader_journal'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/',views.register, name='register'),
    path('profile/',views.profile, name='profile'),
    path('operations/',views.OperationListView.as_view(),name='operations'),
    path('operation/<int:pk>/', views.OperationDetailView.as_view(), name='operation_detail'),
    path('operation/create/', views.add_operation, name='operation_create'),
    path('operation/<int:pk>/update/', views.OperationUpdate.as_view(), name='operation_update'),
    path('operation/<int:pk>/delete/', views.OperationDelete.as_view(), name='operation_delete'),
    path('actives/',views.ActiveListView.as_view(),name='actives'),
    path('active/<int:pk>/', views.ActiveDetailView.as_view(), name='active_detail'),
    path('active/create/', views.add_active, name='active_create'),
    path('active/<int:pk>/update/', views.ActiveUpdate.as_view(), name='active_update'),
    path('active/<int:pk>/delete/', views.ActiveDelete.as_view(), name='active_delete'),
    path('periods/',views.PeriodListView.as_view(),name='periods'),
    path('period/<int:pk>/', views.PeriodDetailView.as_view(), name='period_detail'),
    path('period/create/', views.add_period, name='period_create'),
    path('period/<int:pk>/update/', views.PeriodUpdate.as_view(), name='period_update'),
    path('period/<int:pk>/delete/', views.PeriodDelete.as_view(), name='period_delete'),
    path('accounts/',include('django.contrib.auth.urls'))
]