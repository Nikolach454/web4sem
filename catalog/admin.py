from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Role, ProsthesisType, RequestStatus, Tag,
    User, UserRole,
    Prosthesis, Request,
    BlogPost, Event, Document,
)


# ──────────────────────────────────────────────
# КАСТОМНЫЕ ДЕЙСТВИЯ (Часть 3: добавить действие на сайт администрирования)
# ──────────────────────────────────────────────

@admin.action(description='Пометить заявки как "В обработке"')
def mark_in_progress(modeladmin, request, queryset):
    """
    Демонстрация: кастомное действие в админке (Часть 3).
    Меняет статус выбранных заявок на первый доступный.
    """
    status = RequestStatus.objects.first()
    if status:
        queryset.update(status=status)


@admin.action(description='Сгенерировать PDF-отчёт по выбранным заявкам')
def export_requests_pdf(modeladmin, request, queryset):
    """
    Демонстрация: генерация PDF через ReportLab (Часть 3, стр. 488 учебника).
    Шрифт Arial (Windows) подключается через TTFont — поддержка кириллицы.
    """
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Заголовок
    p.setFont('Arial-Bold', 16)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(50, height - 50, 'АвангардПротез — Отчёт по заявкам')

    p.setFont('Arial', 9)
    p.setFillColorRGB(0, 0, 0)
    generated = timezone.now().strftime('%d.%m.%Y %H:%M')
    p.drawString(50, height - 68, f'Сформирован: {generated}  |  Заявок в отчёте: {queryset.count()}')

    # Шапка таблицы
    y = height - 95
    p.setFillColorRGB(0, 0, 0)
    p.rect(50, y - 4, width - 100, 18, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont('Arial-Bold', 9)
    p.drawString(55, y + 2, '#')
    p.drawString(75, y + 2, 'Тип')
    p.drawString(165, y + 2, 'Контакт')
    p.drawString(295, y + 2, 'Email')
    p.drawString(415, y + 2, 'Статус')
    p.drawString(490, y + 2, 'Дата')
    y -= 20

    qs = queryset.select_related('status', 'prosthesis', 'user')
    for i, req in enumerate(qs):
        if y < 60:
            p.showPage()
            y = height - 50

        # Чередование строк
        if i % 2 == 0:
            p.setFillColorRGB(0.9, 0.9, 0.9)
            p.rect(50, y - 4, width - 100, 16, fill=1, stroke=0)

        p.setFillColorRGB(0, 0, 0)
        p.setFont('Arial', 8)
        p.drawString(55, y + 2, str(req.pk))
        p.drawString(75, y + 2, req.get_request_type_display()[:12])
        p.drawString(165, y + 2, req.contact_name[:16])
        p.drawString(295, y + 2, req.contact_email[:18])
        p.drawString(415, y + 2, (req.status.name if req.status else '—')[:10])
        p.drawString(490, y + 2, req.created_at.strftime('%d.%m.%Y'))
        y -= 18

        # Сообщение (если есть)
        if req.message:
            if y < 60:
                p.showPage()
                y = height - 50
            p.setFont('Arial', 7)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(75, y + 2, f'  {req.message[:90]}')
            y -= 14

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="requests_report.pdf"'
    return response


@admin.action(description='Сгенерировать PDF-каталог выбранных протезов')
def export_prostheses_pdf(modeladmin, request, queryset):
    """
    Демонстрация: генерация PDF через ReportLab (Часть 3).
    Шрифт Arial (Windows) подключается через TTFont — поддержка кириллицы.
    """
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Заголовок
    p.setFont('Arial-Bold', 16)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(50, height - 50, 'АвангардПротез — Каталог протезов')

    p.setFont('Arial', 9)
    p.setFillColorRGB(0, 0, 0)
    generated = timezone.now().strftime('%d.%m.%Y %H:%M')
    p.drawString(50, height - 68, f'Сформирован: {generated}  |  Позиций в отчёте: {queryset.count()}')

    # Шапка таблицы
    y = height - 95
    p.setFillColorRGB(0, 0, 0)
    p.rect(50, y - 4, width - 100, 18, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont('Arial-Bold', 9)
    p.drawString(55, y + 2, '#')
    p.drawString(75, y + 2, 'Название')
    p.drawString(235, y + 2, 'Тип')
    p.drawString(335, y + 2, 'Цена (руб.)')
    p.drawString(425, y + 2, 'Активен')
    p.drawString(490, y + 2, 'Добавлен')
    y -= 20

    qs = queryset.select_related('prosthesis_type')
    for i, pr in enumerate(qs):
        if y < 60:
            p.showPage()
            y = height - 50

        if i % 2 == 0:
            p.setFillColorRGB(0.9, 0.9, 0.9)
            p.rect(50, y - 4, width - 100, 16, fill=1, stroke=0)

        p.setFillColorRGB(0, 0, 0)
        p.setFont('Arial', 8)
        p.drawString(55, y + 2, str(pr.pk))
        p.drawString(75, y + 2, pr.name[:22])
        p.drawString(235, y + 2, pr.prosthesis_type.name[:14])
        price_str = f'{pr.price:,.0f}' if pr.price else 'по запросу'
        p.drawString(335, y + 2, price_str)
        p.drawString(425, y + 2, 'Да' if pr.is_active else 'Нет')
        p.drawString(490, y + 2, pr.created_at.strftime('%d.%m.%Y'))
        y -= 18

        # Описание (если есть)
        if pr.description:
            if y < 60:
                p.showPage()
                y = height - 50
            p.setFont('Arial', 7)
            p.setFillColorRGB(0, 0, 0)
            p.drawString(75, y + 2, pr.description[:95])
            y -= 14

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prostheses_catalog.pdf"'
    return response


# ──────────────────────────────────────────────
# ИНЛАЙНЫ
# ──────────────────────────────────────────────

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    verbose_name = 'Роль'
    verbose_name_plural = 'Роли пользователя'
    raw_id_fields = ('role',)
    readonly_fields = ('assigned_at',)


class RequestInline(admin.TabularInline):
    model = Request
    extra = 0
    fields = ('request_type', 'contact_name', 'status', 'created_at')
    readonly_fields = ('created_at',)
    raw_id_fields = ('prosthesis', 'status')
    show_change_link = True
    verbose_name = 'Заявка'
    verbose_name_plural = 'Заявки пользователя'


class BlogPostInline(admin.TabularInline):
    model = BlogPost
    extra = 0
    fields = ('title', 'is_published', 'published_at')
    readonly_fields = ('published_at',)
    show_change_link = True
    verbose_name = 'Статья блога'
    verbose_name_plural = 'Статьи блога пользователя'


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    fields = ('title', 'doc_type', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    show_change_link = True
    verbose_name = 'Документ'
    verbose_name_plural = 'Загруженные документы'


# ──────────────────────────────────────────────
# СПРАВОЧНИКИ
# ──────────────────────────────────────────────

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'prostheses_count')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    readonly_fields = ('id',)

    @admin.display(description='Кол-во протезов')
    def prostheses_count(self, obj):
        return obj.prostheses.count()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'users_count')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    readonly_fields = ('id',)

    # short_description задаёт заголовок колонки в list_display.
    # Это классический способ — эквивалентен @admin.display(description='...').
    def users_count(self, obj):
        return obj.users.count()
    users_count.short_description = 'Кол-во пользователей'


@admin.register(ProsthesisType)
class ProsthesisTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'prostheses_count', 'description')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    readonly_fields = ('id',)

    @admin.display(description='Кол-во протезов')
    def prostheses_count(self, obj):
        return obj.prostheses.count()


@admin.register(RequestStatus)
class RequestStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'requests_count')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    readonly_fields = ('id',)

    @admin.display(description='Кол-во заявок')
    def requests_count(self, obj):
        return obj.requests.count()


# ──────────────────────────────────────────────
# ПОЛЬЗОВАТЕЛИ
# ──────────────────────────────────────────────

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name_display', 'email', 'phone',
        'is_active', 'roles_list', 'created_at',
    )
    list_display_links = ('id', 'full_name_display')
    list_filter = ('is_active', 'roles', 'created_at')
    search_fields = ('last_name', 'first_name', 'email', 'phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at')
    inlines = [UserRoleInline, RequestInline, BlogPostInline, DocumentInline]

    fieldsets = (
        ('Личные данные', {
            'fields': ('id', 'last_name', 'first_name', 'email', 'phone'),
        }),
        ('Безопасность', {
            'fields': ('password_hash',),
            'classes': ('collapse',),
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at'),
        }),
    )

    @admin.display(description='ФИО', ordering='last_name')
    def full_name_display(self, obj):
        return obj.full_name

    @admin.display(description='Роли')
    def roles_list(self, obj):
        return ', '.join(r.name for r in obj.roles.all()) or '—'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'role', 'assigned_at')
    list_display_links = ('id',)
    list_filter = ('role', 'assigned_at')
    search_fields = (
        'user__last_name', 'user__first_name',
        'user__email', 'role__name',
    )
    date_hierarchy = 'assigned_at'
    raw_id_fields = ('user', 'role')
    readonly_fields = ('id', 'assigned_at')

    @admin.display(description='Пользователь')
    def user_link(self, obj):
        return str(obj.user)


# ──────────────────────────────────────────────
# ПРОТЕЗЫ
# ──────────────────────────────────────────────

@admin.register(Prosthesis)
class ProsthesisAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'prosthesis_type',
        'price', 'is_active', 'image_preview', 'created_at',
    )
    list_display_links = ('id', 'name')
    list_filter = ('is_active', 'prosthesis_type', 'created_at')
    search_fields = ('name', 'description', 'prosthesis_type__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'image_preview')
    # Демонстрация: filter_horizontal — виджет двойного списка для M2M (Часть базовая)
    filter_horizontal = ('tags',)
    # Демонстрация: кастомное действие — генерация PDF (Часть 3)
    actions = [export_prostheses_pdf]

    fieldsets = (
        ('Основное', {
            'fields': ('id', 'name', 'prosthesis_type', 'description'),
        }),
        ('Теги', {
            'fields': ('tags',),
        }),
        ('Цена и изображение', {
            'fields': ('price', 'image', 'image_preview'),
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at'),
        }),
    )

    @admin.display(description='Превью')
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'


# ──────────────────────────────────────────────
# ЗАЯВКИ
# ──────────────────────────────────────────────

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'request_type_badge', 'contact_name', 'contact_email',
        'status', 'user_display', 'prosthesis_display', 'created_at',
    )
    list_display_links = ('id', 'contact_name')
    list_filter = ('request_type', 'status', 'created_at')
    search_fields = (
        'contact_name', 'contact_email', 'message',
        'user__last_name', 'user__first_name', 'user__email',
        'prosthesis__name',
    )
    date_hierarchy = 'created_at'
    raw_id_fields = ('user', 'prosthesis')
    readonly_fields = ('id', 'created_at', 'updated_at')
    # Демонстрация: действия в админке (Часть 3)
    actions = [mark_in_progress, export_requests_pdf]

    fieldsets = (
        ('Контакт', {
            'fields': ('id', 'request_type', 'contact_name', 'contact_email', 'message'),
        }),
        ('Связи', {
            'fields': ('user', 'prosthesis', 'status'),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description='Тип', ordering='request_type')
    def request_type_badge(self, obj):
        color = '#007bff' if obj.request_type == Request.TYPE_PROSTHESIS else '#28a745'
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">{}</span>',
            color,
            obj.get_request_type_display(),
        )

    @admin.display(description='Пользователь')
    def user_display(self, obj):
        return str(obj.user) if obj.user else 'Гость'

    @admin.display(description='Протез')
    def prosthesis_display(self, obj):
        return str(obj.prosthesis) if obj.prosthesis else '—'


# ──────────────────────────────────────────────
# БЛОГ
# ──────────────────────────────────────────────

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'author_display',
        'is_published', 'published_at',
    )
    list_display_links = ('id', 'title')
    list_filter = ('is_published', 'published_at')
    search_fields = ('title', 'content', 'author__last_name', 'author__email')
    date_hierarchy = 'published_at'
    raw_id_fields = ('author',)
    readonly_fields = ('id',)

    fieldsets = (
        ('Контент', {
            'fields': ('id', 'title', 'content', 'image'),
        }),
        ('Публикация', {
            'fields': ('author', 'is_published', 'published_at'),
        }),
    )

    @admin.display(description='Автор')
    def author_display(self, obj):
        return str(obj.author) if obj.author else '—'


# ──────────────────────────────────────────────
# МЕРОПРИЯТИЯ
# ──────────────────────────────────────────────

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'event_date',
        'location', 'author_display', 'website',
    )
    list_display_links = ('id', 'title')
    list_filter = ('event_date',)
    search_fields = ('title', 'description', 'location', 'author__last_name')
    date_hierarchy = 'event_date'
    raw_id_fields = ('author',)
    readonly_fields = ('id',)

    @admin.display(description='Организатор')
    def author_display(self, obj):
        return str(obj.author) if obj.author else '—'


# ──────────────────────────────────────────────
# ДОКУМЕНТЫ
# ──────────────────────────────────────────────

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'doc_type',
        'uploaded_by_display', 'file_link', 'uploaded_at',
    )
    list_display_links = ('id', 'title')
    list_filter = ('doc_type', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__last_name', 'uploaded_by__email')
    date_hierarchy = 'uploaded_at'
    raw_id_fields = ('uploaded_by',)
    readonly_fields = ('id', 'uploaded_at', 'file_link')

    @admin.display(description='Загрузил')
    def uploaded_by_display(self, obj):
        return str(obj.uploaded_by) if obj.uploaded_by else '—'

    @admin.display(description='Файл')
    def file_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">Открыть</a>',
                obj.file.url,
            )
        return '—'
