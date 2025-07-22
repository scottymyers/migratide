# File: migratide/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from tracker import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
 path('admin/', admin.site.urls),
 path('dashboard/', views.dashboard, name='dashboard'),
 path('log/', views.log_migraine, name='log'),
 path('profile/', views.profile, name='profile'),
 #path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=True))
 path('subscribe/', views.subscribe, name='subscribe'),
 path('upgrade/', views.upgrade, name='upgrade'),
 path('export_data/', views.export_data, name='export_data'),
 path('admin_page/', views.admin_page, name='admin_page'),
 path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
 path('register/', views.register, name='register'),
 path('success/', views.success, name='success'),
 path('cancel/', views.cancel, name='cancel'),
 path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
 path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
 path('add_supplement/', views.add_supplement, name='add_supplement'),
 path('add_medication/', views.add_medication, name='add_medication'),
 path('', views.dashboard, name='home'), # Add root URL to point to dashboard or a home view
]

if settings.DEBUG:
 urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
