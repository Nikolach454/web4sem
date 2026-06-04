from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from catalog.models import (
    Role, ProsthesisType, RequestStatus, Tag,
    User, UserRole,
    Prosthesis, Request,
    BlogPost, Event, Document,
)


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('>> Очистка старых данных...')
        self._clear()

        self.stdout.write('>> Создание справочников...')
        roles = self._create_roles()
        types = self._create_prosthesis_types()
        statuses = self._create_statuses()
        tags = self._create_tags()

        self.stdout.write('>> Создание пользователей...')
        users = self._create_users(roles)

        self.stdout.write('>> Создание протезов...')
        prostheses = self._create_prostheses(types, tags)

        self.stdout.write('>> Создание заявок...')
        self._create_requests(users, prostheses, statuses)

        self.stdout.write('>> Создание статей блога...')
        self._create_blog_posts(users)

        self.stdout.write('>> Создание мероприятий...')
        self._create_events(users)

        self.stdout.write('>> Создание документов...')
        self._create_documents(users)

        self.stdout.write(self.style.SUCCESS('>> Тестовые данные успешно загружены!'))

    def _clear(self):
        Document.objects.all().delete()
        Event.objects.all().delete()
        BlogPost.objects.all().delete()
        Request.objects.all().delete()
        Prosthesis.objects.all().delete()
        UserRole.objects.all().delete()
        User.objects.all().delete()
        RequestStatus.objects.all().delete()
        ProsthesisType.objects.all().delete()
        Tag.objects.all().delete()
        Role.objects.all().delete()

    def _create_roles(self):
        data = [
            ('Администратор', 'Полный доступ к системе'),
            ('Менеджер',      'Управление заявками и клиентами'),
            ('Редактор',      'Публикация статей и новостей'),
            ('Клиент',        'Обычный пользователь сайта'),
        ]
        roles = []
        for name, desc in data:
            r = Role.objects.create(name=name, description=desc)
            roles.append(r)
            self.stdout.write(f'  OK: Роль: {name}')
        return roles

    def _create_prosthesis_types(self):
        data = [
            ('Протез руки',   'Протезы верхних конечностей — кисть, предплечье, плечо'),
            ('Протез ноги',   'Протезы нижних конечностей — стопа, голень, бедро'),
            ('Экзоскелет',    'Активные экзоскелетные системы для реабилитации'),
            ('Протез пальца', 'Частичные протезы пальцев кисти'),
            ('Косметический', 'Косметические протезы без функциональной нагрузки'),
        ]
        types = []
        for name, desc in data:
            t = ProsthesisType.objects.create(name=name, description=desc)
            types.append(t)
            self.stdout.write(f'  OK: Тип: {name}')
        return types

    def _create_statuses(self):
        data = [
            'Новая', 'В обработке', 'Ожидает документов',
            'Одобрена', 'Отклонена', 'Завершена',
        ]
        statuses = []
        for name in data:
            s = RequestStatus.objects.create(name=name)
            statuses.append(s)
            self.stdout.write(f'  OK: Статус: {name}')
        return statuses

    def _create_tags(self):
        names = [
            'биоэлектрический', 'механический', 'углеродное-волокно',
            'микропроцессор', 'косметический', 'реабилитация',
            'детский', 'водооталкивающий',
        ]
        tags = []
        for name in names:
            t = Tag.objects.create(name=name)
            tags.append(t)
            self.stdout.write(f'  OK: Тег: {name}')
        return tags

    def _create_users(self, roles):
        raw_users = [
            ('Иванов',   'Алексей',   'ivanov@example.com',   '+7 900 111-22-33', [0, 3]),
            ('Петрова',  'Мария',     'petrova@example.com',  '+7 900 222-33-44', [1, 2]),
            ('Сидоров',  'Дмитрий',   'sidorov@example.com',  '+7 900 333-44-55', [3]),
            ('Козлова',  'Анна',      'kozlova@example.com',  None,               [3]),
            ('Новиков',  'Игорь',     'novikov@example.com',  '+7 900 555-66-77', [1]),
            ('Морозова', 'Светлана',  'morozova@example.com', '+7 900 666-77-88', [2]),
            ('Волков',   'Андрей',    'volkov@example.com',   None,               [3]),
            ('Лебедева', 'Ольга',     'lebedeva@example.com', '+7 900 888-99-00', [3]),
        ]
        users = []
        for i, (last, first, email, phone, role_idxs) in enumerate(raw_users):
            u = User.objects.create(
                last_name=last,
                first_name=first,
                email=email,
                phone=phone,
                password_hash='pbkdf2_sha256$test_hash_' + str(i),
                is_active=True,
                created_at=timezone.now() - timedelta(days=random.randint(10, 365)),
            )
            for ri in role_idxs:
                UserRole.objects.create(user=u, role=roles[ri])
            users.append(u)
            self.stdout.write(f'  OK: Пользователь: {last} {first}')
        return users

    def _create_prostheses(self, types, tags):
        data = [
            (0, 'Биоэлектрический протез кисти i-Limb',
             'Многофункциональный протез с 5 независимыми пальцами и управлением через миоэлектрические сигналы.',
             890000, True, [0, 4]),
            (0, 'Механический протез предплечья Ottobock',
             'Надёжный тяговый протез предплечья с крюковым захватом для активного образа жизни.',
             120000, True, [1]),
            (1, 'Протез голени с углеродной стопой',
             'Динамический протез голени с энергоаккумулирующей стопой из углеволокна.',
             350000, True, [2, 5]),
            (1, 'Протез бедра с микропроцессорным коленом C-Leg',
             'Интеллектуальный протез бедра с гидравлическим управлением и сенсорами.',
             1500000, True, [3]),
            (2, 'Реабилитационный экзоскелет Ekso Bionics',
             'Активный экзоскелет для восстановления ходьбы у пациентов с парезами.',
             2800000, False, [5]),
            (3, 'Косметический протез пальца',
             'Силиконовый косметический протез пальца с индивидуальным окрашиванием.',
             45000, True, [4]),
            (4, 'Косметический протез кисти',
             'Реалистичный силиконовый протез кисти, подходит по цвету кожи.',
             180000, True, [4]),
            (1, 'Протез стопы Sach',
             'Классический протез стопы с деревянным сердечником, доступная цена.',
             None, True, [1]),
        ]
        prostheses = []
        for type_idx, name, desc, price, is_active, tag_idxs in data:
            p = Prosthesis.objects.create(
                prosthesis_type=types[type_idx],
                name=name,
                description=desc,
                price=price,
                is_active=is_active,
                created_at=timezone.now() - timedelta(days=random.randint(1, 200)),
            )
            p.tags.set([tags[i] for i in tag_idxs])
            prostheses.append(p)
            self.stdout.write(f'  OK: Протез: {name[:50]}')
        return prostheses

    def _create_requests(self, users, prostheses, statuses):
        data = [
            (2, 0, 0, 'prosthesis', 'Сидоров Дмитрий',  'sidorov@example.com',
             'Интересует биоэлектрический протез кисти. Потерял руку год назад.'),
            (3, 2, 1, 'prosthesis', 'Козлова Анна',      'kozlova@example.com',
             'Нужна консультация по протезу голени.'),
            (6, 3, 3, 'prosthesis', 'Волков Андрей',     'volkov@example.com',
             'Хочу записаться на примерку протеза бедра.'),
            (7, 5, 4, 'prosthesis', 'Лебедева Ольга',    'lebedeva@example.com',
             'Прошу рассмотреть заявку на косметический протез пальца.'),
            (None, 1, 0, 'prosthesis', 'Кузнецов Павел',  'kuznetcov@mail.ru',
             'Узнать стоимость механического протеза предплечья.'),
            (None, None, 1, 'investor', 'ООО ТехноПротез',  'invest@technoprot.ru',
             'Рассматриваем возможность инвестирования в производство протезов.'),
            (None, None, 0, 'investor', 'Фонд помощи',      'fond@help.org',
             'Благотворительный фонд хочет поддержать ваш проект.'),
            (2, 6, 5, 'prosthesis', 'Сидоров Дмитрий',  'sidorov@example.com',
             'Повторная заявка — интерес к косметическому протезу кисти.'),
        ]
        for i, (u_idx, p_idx, s_idx, rtype, cname, cemail, msg) in enumerate(data):
            Request.objects.create(
                user=users[u_idx] if u_idx is not None else None,
                prosthesis=prostheses[p_idx] if p_idx is not None else None,
                status=statuses[s_idx],
                request_type=rtype,
                contact_name=cname,
                contact_email=cemail,
                message=msg,
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
            self.stdout.write(f'  OK: Заявка #{i+1}: {cname}')

    def _create_blog_posts(self, users):
        data = [
            (1, 'Современные биоэлектрические протезы: как это работает',
             'Биоэлектрические протезы используют электрические сигналы мышц для управления. '
             'Датчики на культе улавливают миоэлектрические импульсы и передают команды моторам пальцев.',
             True, timezone.now() - timedelta(days=30)),
            (5, 'Реабилитация после ампутации: первые шаги',
             'После ампутации важнейший этап — психологическая адаптация и физическая реабилитация. '
             'Протезирование начинается с временного протеза уже через 4–6 недель после операции.',
             True, timezone.now() - timedelta(days=15)),
            (1, 'Экзоскелеты в медицине: настоящее и будущее',
             'Экзоскелеты помогают пациентам с травмами спинного мозга восстановить способность ходить.',
             True, timezone.now() - timedelta(days=7)),
            (5, 'Как выбрать протез: советы специалиста',
             'Выбор протеза зависит от уровня ампутации, образа жизни и физической активности пациента.',
             False, None),
            (1, 'Детское протезирование: особенности и подходы',
             'Дети растут быстро, поэтому детские протезы требуют замены каждые 1–2 года.',
             True, timezone.now() - timedelta(days=3)),
        ]
        for author_idx, title, content, is_pub, pub_at in data:
            BlogPost.objects.create(
                author=users[author_idx],
                title=title,
                content=content,
                is_published=is_pub,
                published_at=pub_at,
            )
            self.stdout.write(f'  OK: Статья: {title[:50]}')

    def _create_events(self, users):
        data = [
            (4, 'Выставка протезных технологий 2025',
             'Ежегодная выставка новинок протезирования и реабилитационного оборудования.',
             timezone.now() + timedelta(days=30), 'Москва, ВДНХ, павильон 75',
             'https://expo.example.com/2025'),
            (4, 'Семинар: жизнь с протезом',
             'Открытый семинар для пользователей протезов и их родственников.',
             timezone.now() + timedelta(days=14), 'Санкт-Петербург, ул. Ленина 10',
             'https://seminar.example.com'),
            (1, 'Мастер-класс по уходу за протезом',
             'Практический мастер-класс по чистке, обслуживанию и мелкому ремонту протезов.',
             timezone.now() + timedelta(days=7), 'Онлайн (Zoom)',
             'https://zoom.example.com/masterclass'),
            (4, 'День открытых дверей в центре протезирования',
             'Посетите наш центр, познакомьтесь с командой и современным оборудованием.',
             timezone.now() - timedelta(days=10), 'Москва, ул. Медицинская 5',
             None),
            (1, 'Конференция реабилитологов 2025',
             'Международная конференция по вопросам реабилитации и протезирования.',
             timezone.now() + timedelta(days=60), 'Казань, МВЦ «Казань Экспо»',
             'https://conf.example.com/rehab2025'),
        ]
        for author_idx, title, desc, event_date, location, website in data:
            Event.objects.create(
                author=users[author_idx],
                title=title,
                description=desc,
                event_date=event_date,
                location=location,
                website=website,
            )
            self.stdout.write(f'  OK: Мероприятие: {title[:50]}')

    def _create_documents(self, users):
        data = [
            (0, 'Лицензия на медицинскую деятельность №ЛО-77-01-12345', 'license'),
            (0, 'Сертификат ISO 13485:2016 Медицинские изделия', 'certificate'),
            (4, 'Сертификат соответствия протеза кисти i-Limb', 'certificate'),
            (4, 'Регистрационное удостоверение Росздравнадзора', 'license'),
            (1, 'Договор с поставщиком Ottobock', 'other'),
            (0, 'Сертификат системы менеджмента качества', 'certificate'),
        ]
        for uploader_idx, title, doc_type in data:
            Document.objects.create(
                uploaded_by=users[uploader_idx],
                title=title,
                doc_type=doc_type,
                uploaded_at=timezone.now() - timedelta(days=random.randint(1, 180)),
            )
            self.stdout.write(f'  OK: Документ: {title[:50]}')
