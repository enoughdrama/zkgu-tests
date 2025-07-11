from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('zkgu_persons.urls')),
    
    # Главная страница перенаправляет на интерфейс
    path('', lambda request: redirect('/api/v1/manage/')),
    
    # Прямой доступ к интерфейсу
    path('manage/', include('zkgu_persons.urls')),
]