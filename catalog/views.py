"""
views.py — демонстрация всех требуемых возможностей Django ORM и CBV/FBV.

Карта демонстраций:
  Часть 1: timezone, ordering, choices, related_name, filter, __, exclude,
           order_by, кастомный менеджер, get_absolute_url/reverse,
           aggregation/annotation
  Часть 2: CRUD, select_related, prefetch_related
  Часть 3: redirect, Http404 (ImageField и FileField — в models.py)
  Часть 4: __icontains/__contains, values/values_list, count/exists,
           update/delete
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.db.models import Avg, Count, Max, Min, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    Prosthesis, ProsthesisType, Request, RequestStatus,
    User, BlogPost, Event, Document,
)
from .forms import ProsthesisForm, RequestForm


# ══════════════════════════════════════════════
# ПРОТЕЗЫ — LIST
# Демонстрирует:
#   filter(), exclude(), order_by()
#   __ (метод поля: created_at__gte)
#   __ (обращение к связанной таблице: prosthesis_type__name__icontains)
#   __icontains, __contains
#   select_related()
#   кастомный менеджер (active)
#   count(), exists()
#   values_list()
# ══════════════════════════════════════════════

def prosthesis_list(request):
    # Кастомный менеджер: только активные протезы
    qs = Prosthesis.active.all()

    # select_related: загружает связанный ProsthesisType одним JOIN-запросом
    # (без него каждое обращение к prosthesis.prosthesis_type — отдельный запрос)
    qs = qs.select_related('prosthesis_type')

    # __icontains — поиск без учёта регистра (Часть 4)
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) |                          # поиск по имени
            Q(prosthesis_type__name__icontains=search)           # __ к связанной таблице
        )

    # __contains — поиск с учётом регистра (Часть 4)
    exact_search = request.GET.get('exact', '').strip()
    if exact_search:
        qs = qs.filter(description__contains=exact_search)

    # filter() по типу (Часть 1)
    type_id = request.GET.get('type')
    if type_id:
        qs = qs.filter(prosthesis_type_id=type_id)

    # exclude() — исключить протезы без цены (Часть 1)
    hide_no_price = request.GET.get('hide_no_price')
    if hide_no_price:
        qs = qs.exclude(price__isnull=True)

    # order_by() — сортировка (Часть 1)
    sort = request.GET.get('sort', 'name')
    allowed_sorts = {'name', '-name', 'price', '-price', 'created_at', '-created_at'}
    if sort in allowed_sorts:
        qs = qs.order_by(sort)

    # count() и exists() (Часть 4)
    total_count = qs.count()
    has_results = qs.exists()

    # values_list() — список только названий для подсказок (Часть 4)
    name_hints = Prosthesis.active.values_list('name', flat=True)[:20]

    # Демонстрация related_name:
    # ProsthesisType.prostheses.all() — все протезы данного типа
    types = ProsthesisType.objects.all()

    return render(request, 'catalog/prosthesis_list.html', {
        'prostheses': qs,
        'types': types,
        'total_count': total_count,
        'has_results': has_results,
        'name_hints': name_hints,
        'search': search,
    })


# ══════════════════════════════════════════════
# ПРОТЕЗЫ — DETAIL
# Демонстрирует:
#   Http404 (Часть 4 — вопросы)
#   get_absolute_url / reverse (Часть 1)
#   related_name: prosthesis.requests.all()
# ══════════════════════════════════════════════

def prosthesis_detail(request, pk):
    # Http404 — если объект не найден, возбуждается исключение Http404
    try:
        prosthesis = Prosthesis.objects.select_related('prosthesis_type').get(pk=pk)
    except Prosthesis.DoesNotExist:
        raise Http404('Протез не найден')

    # related_name в действии: обращаемся к заявкам через обратную связь
    # prosthesis.requests — все заявки на этот протез (related_name='requests')
    related_requests = prosthesis.requests.select_related('status', 'user').all()

    return render(request, 'catalog/prosthesis_detail.html', {
        'prosthesis': prosthesis,
        'related_requests': related_requests,
        # get_absolute_url используется в шаблоне: {{ prosthesis.get_absolute_url }}
    })


# ══════════════════════════════════════════════
# ПРОТЕЗЫ — CREATE / EDIT / DELETE
# Демонстрирует:
#   CRUD (Часть 2)
#   redirect (Часть 3) — после успешного сохранения
#   ImageField — в форме (Часть 3)
# ══════════════════════════════════════════════

def prosthesis_create(request):
    if request.method == 'POST':
        form = ProsthesisForm(request.POST, request.FILES)  # request.FILES — для ImageField
        if form.is_valid():
            prosthesis = form.save()
            # redirect после успешного создания (Часть 3)
            return redirect(prosthesis.get_absolute_url())
    else:
        form = ProsthesisForm()
    return render(request, 'catalog/prosthesis_form.html', {'form': form, 'action': 'Создать'})


def prosthesis_edit(request, pk):
    prosthesis = get_object_or_404(Prosthesis, pk=pk)
    if request.method == 'POST':
        form = ProsthesisForm(request.POST, request.FILES, instance=prosthesis)
        if form.is_valid():
            form.save()
            return redirect(prosthesis.get_absolute_url())
    else:
        form = ProsthesisForm(instance=prosthesis)
    return render(request, 'catalog/prosthesis_form.html', {'form': form, 'action': 'Редактировать'})


def prosthesis_delete(request, pk):
    prosthesis = get_object_or_404(Prosthesis, pk=pk)
    if request.method == 'POST':
        prosthesis.delete()
        # redirect на список после удаления (Часть 3)
        return redirect('catalog:prosthesis_list')
    return render(request, 'catalog/prosthesis_confirm_delete.html', {'prosthesis': prosthesis})


# ══════════════════════════════════════════════
# ЗАЯВКИ — LIST + CREATE
# Демонстрирует:
#   filter() по полям связанной модели: user__last_name__icontains
#   __ (два варианта):
#     created_at__gte  — метод поля (gte = greater than or equal)
#     user__last_name  — обращение к связанной таблице
#   prefetch_related()
#   choices: get_request_type_display()
# ══════════════════════════════════════════════

def request_list(request):
    # prefetch_related: предзагружает связанные объекты для обратных FK/M2M
    # (без него каждый request.status, request.user — отдельный запрос)
    qs = Request.objects.select_related('status', 'user', 'prosthesis').all()

    # filter() с __ к связанной таблице (Часть 1)
    user_search = request.GET.get('user', '').strip()
    if user_search:
        qs = qs.filter(user__last_name__icontains=user_search)

    # filter() c __ методом поля — только заявки за последние 30 дней
    recent_only = request.GET.get('recent')
    if recent_only:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        qs = qs.filter(created_at__gte=thirty_days_ago)

    # filter() по типу заявки (choices)
    req_type = request.GET.get('type')
    if req_type:
        qs = qs.filter(request_type=req_type)

    return render(request, 'catalog/request_list.html', {
        'requests': qs,
        'type_choices': Request.TYPE_CHOICES,
    })


def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            # Автоматически присваиваем первый статус
            req.status = RequestStatus.objects.first()
            req.save()
            return redirect('catalog:request_list')
    else:
        form = RequestForm()
    return render(request, 'catalog/request_form.html', {'form': form})


def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk)
    return render(request, 'catalog/request_detail.html', {'req': req})


# ══════════════════════════════════════════════
# СТАТИСТИКА
# Демонстрирует:
#   aggregate() — Avg, Count, Max, Min, Sum (Часть 1)
#   annotate() — три примера (Часть 1)
#   values() и values_list() (Часть 4)
#   count() и exists() (Часть 4)
#   prefetch_related (Часть 2)
# ══════════════════════════════════════════════

def stats(request):
    # ── aggregate(): одно значение по всему QuerySet ──────────────────────
    price_stats = Prosthesis.objects.aggregate(
        avg_price=Avg('price'),       # средняя цена
        max_price=Max('price'),       # максимальная цена
        min_price=Min('price'),       # минимальная цена
        total_price=Sum('price'),     # сумма всех цен
        total_count=Count('id'),      # количество записей
    )

    # ── annotate(): добавляет вычисляемое поле к каждому объекту ──────────
    # Пример 1: количество протезов по типам
    types_with_count = ProsthesisType.objects.annotate(
        prosthesis_count=Count('prostheses')
    ).order_by('-prosthesis_count')

    # Пример 2: количество заявок по каждому протезу
    prostheses_with_requests = Prosthesis.objects.annotate(
        request_count=Count('requests')
    ).order_by('-request_count')[:10]

    # Пример 3: количество статей у каждого пользователя
    users_with_posts = User.objects.annotate(
        post_count=Count('blog_posts')
    ).filter(post_count__gt=0).order_by('-post_count')

    # ── values(): словари вместо объектов ────────────────────────────────
    # Полезно когда нужны только отдельные поля (экономия памяти)
    prosthesis_values = Prosthesis.objects.values('name', 'price', 'is_active')[:5]

    # ── values_list(): кортежи / flat-список ─────────────────────────────
    # flat=True — возвращает плоский список (не кортежи)
    prosthesis_names = Prosthesis.objects.values_list('name', flat=True)
    type_name_price = Prosthesis.objects.values_list('name', 'price')[:5]

    # ── count() и exists() ───────────────────────────────────────────────
    active_count = Prosthesis.active.count()
    has_expensive = Prosthesis.objects.filter(price__gte=100000).exists()

    # ── prefetch_related: пользователи + роли (M2M) ──────────────────────
    users = User.objects.prefetch_related('roles').all()[:5]

    return render(request, 'catalog/stats.html', {
        'price_stats': price_stats,
        'types_with_count': types_with_count,
        'prostheses_with_requests': prostheses_with_requests,
        'users_with_posts': users_with_posts,
        'prosthesis_values': prosthesis_values,
        'prosthesis_names': prosthesis_names,
        'type_name_price': type_name_price,
        'active_count': active_count,
        'has_expensive': has_expensive,
        'users': users,
    })


# ══════════════════════════════════════════════
# ORM DEMO — update(), delete(), exclude(), order_by()
# Демонстрирует:
#   update() — массовое обновление (Часть 4)
#   delete() — массовое удаление (Часть 4)
#   exclude() (Часть 1)
#   order_by() (Часть 1)
# ══════════════════════════════════════════════

def orm_demo(request):
    results = {}

    # exclude(): все протезы КРОМЕ неактивных (= только активные, другой способ)
    active_via_exclude = Prosthesis.objects.exclude(is_active=False)
    results['exclude_count'] = active_via_exclude.count()

    # order_by(): сортировка по нескольким полям
    sorted_prostheses = Prosthesis.objects.order_by('-price', 'name')[:5]
    results['sorted'] = list(sorted_prostheses.values('name', 'price'))

    # values() + filter + order_by цепочкой
    recent_names = (
        Prosthesis.objects
        .filter(is_active=True)
        .order_by('-created_at')
        .values('name', 'created_at')[:5]
    )
    results['recent'] = list(recent_names)

    # update(): массовое обновление — POST-запрос для безопасности
    update_result = None
    if request.method == 'POST' and request.POST.get('action') == 'deactivate_no_price':
        # update() возвращает количество обновлённых строк
        updated_count = Prosthesis.objects.filter(
            price__isnull=True, is_active=True
        ).update(is_active=False)
        update_result = f'Деактивировано {updated_count} протезов без цены'

    # delete(): массовое удаление неактивных протезов — POST-запрос для безопасности
    # Возвращает кортеж: (кол-во_удалённых, {'catalog.Prosthesis': кол-во})
    delete_result = None
    if request.method == 'POST' and request.POST.get('action') == 'delete_inactive':
        count, details = Prosthesis.objects.filter(is_active=False).delete()
        delete_result = f'Удалено {count} протезов. Детали: {details}'

    # Количество неактивных (для отображения перед удалением)
    inactive_count = Prosthesis.objects.filter(is_active=False).count()

    return render(request, 'catalog/orm_demo.html', {
        'results': results,
        'update_result': update_result,
        'delete_result': delete_result,
        'inactive_count': inactive_count,
    })


# ══════════════════════════════════════════════
# ДОПОЛНИТЕЛЬНЫЕ DETAIL-ВЬЮХИ
# ══════════════════════════════════════════════

def blogpost_detail(request, pk):
    post = get_object_or_404(BlogPost.objects.select_related('author'), pk=pk)
    return render(request, 'catalog/blogpost_detail.html', {'post': post})


def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('author'), pk=pk)
    return render(request, 'catalog/event_detail.html', {'event': event})


def document_detail(request, pk):
    doc = get_object_or_404(Document.objects.select_related('uploaded_by'), pk=pk)
    return render(request, 'catalog/document_detail.html', {'doc': doc})
