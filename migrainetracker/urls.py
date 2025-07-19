from django.contrib import admin
from django.urls import path, include
from tracker import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('log/', views.log_migraine, name='log'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('export/', views.export_data, name='export_data'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('select2/', include('django_select2.urls')),
]