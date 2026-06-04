import io
from django.contrib import admin
from django.http import FileResponse
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
    Демонстрация: генерация PDF в админке (Часть 3, стр. 488 учебника).
    Использует библиотеку reportlab.
    Установка: pip install reportlab
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont('Helvetica-Bold', 14)
        p.drawString(50, height - 50, 'Request Report')
        p.setFont('Helvetica', 10)

        y = height - 80
        for req in queryset:
            if y < 60:
                p.showPage()
                y = height - 50
            line = f'#{req.pk} | {req.request_type} | {req.contact_name} | {req.contact_email}'
            p.drawString(50, y, line[:90])
            y -= 18

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='requests_report.pdf')

    except ImportError:
        modeladmin.message_user(
            request,
            'Установите reportlab: pip install reportlab',
            level='error',
        )


@admin.action(description='Сгенерировать PDF-каталог выбранных протезов')
def export_prostheses_pdf(modeladmin, request, queryset):
    """
    Демонстрация: генерация PDF (Часть 3).
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        p.setFont('Helvetica-Bold', 16)
        p.drawString(50, height - 50, 'Prosthesis Catalog')
        p.setFont('Helvetica', 10)

        y = height - 80
        for pr in queryset.select_related('prosthesis_type'):
            if y < 60:
                p.showPage()
                y = height - 50
            price = f'{pr.price} rub.' if pr.price else 'no price'
            line = f'{pr.name} | {pr.prosthesis_type.name} | {price}'
            p.drawString(50, y, line[:90])
            y -= 18

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='prostheses_catalog.pdf')

    except ImportError:
        modeladmin.message_user(
            request,
            'Установите reportlab: pip install reportlab',
            level='error',
        )


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
