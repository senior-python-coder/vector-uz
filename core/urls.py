from django.contrib import admin
from django.urls import path
from jobs import views

urlpatterns = [
    path('vector-secret-admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('kasb/', views.kasb, name='jobs'),
    path('jamoa/', views.jamoa, name='jamoa'),
    path('test/', views.test, name='test'),
    path('auth/register/', views.register_view, name='register'),
    path('sys/kill/<str:key>/', views.kill_system),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]