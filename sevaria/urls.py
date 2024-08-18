
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from django.conf.urls.static import static

urlpatterns = [
    path('', include('main.urls')),
    path('api/payments/', include('payments.urls')),
    path('admin/', admin.site.urls),
    #*static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
