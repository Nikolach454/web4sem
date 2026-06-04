"""
URL-маршруты приложения catalog.

Демонстрация регулярных выражений в URLs (Часть 1 — вопросы):
  - path()     — простые маршруты с конвертерами (<int:pk>)
  - re_path()  — маршруты с регулярными выражениями
    Пример: r'^prostheses/(?P<pk>[0-9]+)/detail/$'
    Здесь (?P<pk>[0-9]+) — именованная группа, захватывает одну или
    более цифр и передаёт их в view как параметр pk.

Структура URL:
  /catalog/prostheses/              — список протезов
  /catalog/prostheses/<pk>/         — детальная страница (через re_path)
  /catalog/prostheses/create/       — создать
  /catalog/prostheses/<pk>/edit/    — редактировать
  /catalog/prostheses/<pk>/delete/  — удалить
  /catalog/requests/                — список заявок
  /catalog/requests/create/         — создать заявку
  /catalog/requests/<pk>/           — детальная страница заявки
  /catalog/stats/                   — статистика (агрегации)
  /catalog/orm-demo/                — демонстрация ORM-операций
  /catalog/blog/<pk>/               — детальная страница статьи
  /catalog/events/<pk>/             — детальная страница мероприятия
  /catalog/documents/<pk>/          — детальная страница документа
"""

from django.urls import path, re_path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home, name='home'),

    # ── Протезы ────────────────────────────────────────────────────────
    path('prostheses/', views.prosthesis_list, name='prosthesis_list'),

    # re_path с регулярным выражением:
    # ^prostheses/(?P<pk>[0-9]+)/$
    #   ^              — начало строки
    #   prostheses/    — литеральный текст
    #   (?P<pk>[0-9]+) — именованная группа: одна или более цифр → pk
    #   /$             — конец строки
    re_path(r'^prostheses/(?P<pk>[0-9]+)/$', views.prosthesis_detail, name='prosthesis_detail'),

    path('prostheses/create/', views.prosthesis_create, name='prosthesis_create'),
    path('prostheses/<int:pk>/edit/', views.prosthesis_edit, name='prosthesis_edit'),
    path('prostheses/<int:pk>/delete/', views.prosthesis_delete, name='prosthesis_delete'),

    # ── Заявки ─────────────────────────────────────────────────────────
    path('requests/', views.request_list, name='request_list'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),

    # ── Аналитика и демо ───────────────────────────────────────────────
    path('stats/', views.stats, name='stats'),
    path('orm-demo/', views.orm_demo, name='orm_demo'),

    # ── Блог ────────────────────────────────────────────────────────────
    path('blog/', views.blogpost_list, name='blogpost_list'),
    path('blog/<int:pk>/', views.blogpost_detail, name='blogpost_detail'),

    # ── Мероприятия ─────────────────────────────────────────────────────
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),

    # ── Документы ───────────────────────────────────────────────────────
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
]
