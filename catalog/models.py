from django.db import models
from django.utils import timezone
from django.urls import reverse


# ──────────────────────────────────────────────
# КАСТОМНЫЙ МЕНЕДЖЕР  (Часть 1)
# Демонстрация: собственный модельный менеджер
# ──────────────────────────────────────────────

class ActiveManager(models.Manager):
    """Возвращает только активные записи (is_active=True)."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


# ──────────────────────────────────────────────
# СПРАВОЧНИКИ
# ──────────────────────────────────────────────

class Role(models.Model):
    """Роль пользователя (справочник)."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название роли',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Тег / ключевое слово для протеза (справочник)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Тег',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProsthesisType(models.Model):
    """Тип протеза (справочник)."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название типа',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Тип протеза'
        verbose_name_plural = 'Типы протезов'
        ordering = ['name']

    def __str__(self):
        return self.name


class RequestStatus(models.Model):
    """Статус заявки (справочник)."""

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название статуса',
    )

    class Meta:
        verbose_name = 'Статус заявки'
        verbose_name_plural = 'Статусы заявок'
        ordering = ['name']

    def __str__(self):
        return self.name


# ──────────────────────────────────────────────
# ОСНОВНЫЕ СУЩНОСТИ
# ──────────────────────────────────────────────

class User(models.Model):
    """Пользователь системы."""

    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='Email',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Телефон',
    )
    password_hash = models.CharField(
        max_length=255,
        verbose_name='Хэш пароля',
    )
    # M:N связь с ролями через промежуточную таблицу UserRole
    # Демонстрация: ManyToManyField с параметром through (Часть 2)
    roles = models.ManyToManyField(
        Role,
        through='UserRole',
        blank=True,
        verbose_name='Роли',
        related_name='users',  # related_name: Role.users.all() — все пользователи с этой ролью
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
    )
    # Демонстрация timezone (Часть 1, пример 1):
    # created_at — дата регистрации пользователя.
    # Используется: фильтрация новых пользователей за последние N дней,
    # отправка приветственных писем через N дней после регистрации.
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата регистрации',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.email})'

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'


class UserRole(models.Model):
    """Промежуточная таблица связи пользователей и ролей (M:N)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='user_roles',
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='Роль',
        related_name='user_roles',
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата назначения',
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ('user', 'role')
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.user} — {self.role}'


class Prosthesis(models.Model):
    """Протез."""

    prosthesis_type = models.ForeignKey(
        ProsthesisType,
        on_delete=models.PROTECT,
        verbose_name='Тип протеза',
        related_name='prostheses',  # related_name: ProsthesisType.prostheses.all()
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Цена (руб.)',
    )
    # Демонстрация: models.ImageField (Часть 3)
    # Для работы требует: pip install Pillow
    image = models.ImageField(
        upload_to='prostheses/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )
    # M:N без промежуточной таблицы — демонстрация filter_horizontal в admin
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        verbose_name='Теги',
        related_name='prostheses',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
    )
    # Демонстрация timezone (Часть 1, пример 2):
    # created_at — дата добавления протеза в каталог.
    # Используется: новинки за последний месяц, сортировка по дате добавления.
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата добавления',
    )

    # Менеджеры:
    # objects — стандартный (все записи)
    # active  — только активные (is_active=True)
    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        verbose_name = 'Протез'
        verbose_name_plural = 'Протезы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.prosthesis_type})'

    # Демонстрация: get_absolute_url + reverse (Часть 1)
    def get_absolute_url(self):
        return reverse('catalog:prosthesis_detail', args=[self.pk])


class Request(models.Model):
    """Заявка от пользователя или гостя."""

    TYPE_PROSTHESIS = 'prosthesis'
    TYPE_INVESTOR = 'investor'
    # Демонстрация: choices в поле модели (Часть 1)
    TYPE_CHOICES = [
        (TYPE_PROSTHESIS, 'На протез'),
        (TYPE_INVESTOR, 'Инвестор'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь',
        related_name='requests',  # related_name: user.requests.all() — все заявки пользователя
        help_text='Оставьте пустым для гостевых заявок',
    )
    prosthesis = models.ForeignKey(
        Prosthesis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Протез',
        related_name='requests',  # related_name: prosthesis.requests.all() — заявки на этот протез
    )
    status = models.ForeignKey(
        RequestStatus,
        on_delete=models.PROTECT,
        verbose_name='Статус',
        related_name='requests',
    )
    request_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип заявки',
    )
    contact_name = models.CharField(
        max_length=200,
        verbose_name='Имя контакта',
    )
    contact_email = models.EmailField(
        max_length=255,
        verbose_name='Email контакта',
    )
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Сообщение',
    )
    # Демонстрация timezone (Часть 1, пример 3):
    # created_at — дата создания заявки.
    # Используется: SLA-контроль (заявки без ответа более 3 дней),
    # статистика по периодам, автоматическое закрытие старых заявок.
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка №{self.pk} | {self.get_request_type_display()} | {self.contact_name}'

    def get_absolute_url(self):
        return reverse('catalog:request_detail', args=[self.pk])


class BlogPost(models.Model):
    """Статья блога."""

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Автор',
        related_name='blog_posts',  # related_name: user.blog_posts.all()
    )
    title = models.CharField(
        max_length=300,
        verbose_name='Заголовок',
    )
    content = models.TextField(
        verbose_name='Содержание',
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата публикации',
    )
    # Демонстрация: models.ImageField (Часть 3)
    image = models.ImageField(
        upload_to='blog/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликована',
    )

    class Meta:
        verbose_name = 'Статья блога'
        verbose_name_plural = 'Статьи блога'
        ordering = ['-published_at']

    def __str__(self):
        status = 'опубл.' if self.is_published else 'черновик'
        return f'[{status}] {self.title}'

    def get_absolute_url(self):
        return reverse('catalog:blogpost_detail', args=[self.pk])


class Event(models.Model):
    """Мероприятие."""

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Организатор',
        related_name='events',
    )
    title = models.CharField(
        max_length=300,
        verbose_name='Название',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    event_date = models.DateTimeField(
        verbose_name='Дата и время проведения',
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='Место проведения',
    )
    # Демонстрация: models.URLField (Часть 4)
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='Сайт мероприятия',
    )
    # Демонстрация: models.ImageField (Часть 3)
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True,
        verbose_name='Изображение',
    )

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-event_date']

    def __str__(self):
        return f'{self.title} ({self.event_date.strftime("%d.%m.%Y")})'

    def get_absolute_url(self):
        return reverse('catalog:event_detail', args=[self.pk])


class Document(models.Model):
    """Документ или сертификат."""

    TYPE_CERTIFICATE = 'certificate'
    TYPE_LICENSE = 'license'
    TYPE_OTHER = 'other'
    # Демонстрация: choices (Часть 1)
    DOC_TYPE_CHOICES = [
        (TYPE_CERTIFICATE, 'Сертификат'),
        (TYPE_LICENSE, 'Лицензия'),
        (TYPE_OTHER, 'Прочее'),
    ]

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Загрузил',
        related_name='documents',
    )
    title = models.CharField(
        max_length=300,
        verbose_name='Название документа',
    )
    # Демонстрация: models.FileField (Часть 3)
    file = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Файл',
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        default=TYPE_OTHER,
        verbose_name='Тип документа',
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата загрузки',
    )

    class Meta:
        verbose_name = 'Документ / сертификат'
        verbose_name_plural = 'Документы и сертификаты'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.get_doc_type_display()} — {self.title}'

    def get_absolute_url(self):
        return reverse('catalog:document_detail', args=[self.pk])
