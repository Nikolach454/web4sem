from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/catalog/', permanent=False)),
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls', namespace='catalog')),
]

# В режиме DEBUG отдаём медиафайлы через встроенный сервер Django
# (в продакшене медиафайлы отдаёт веб-сервер — nginx/apache)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
