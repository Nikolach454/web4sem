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
    help = 'Заполняет базу данных тестовыми данными (минимум 10 записей в каждой таблице)'

    def handle(self, *args, **kwargs):
        self.stdout.write('>> Очистка старых данных...')
        self._clear()

        self.stdout.write('>> Создание справочников...')
        roles    = self._create_roles()
        types    = self._create_prosthesis_types()
        statuses = self._create_statuses()
        tags     = self._create_tags()

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

    # ── Справочники ───────────────────────────────────────────────────────

    def _create_roles(self):
        data = [
            ('Администратор', 'Полный доступ к системе'),
            ('Менеджер',      'Управление заявками и клиентами'),
            ('Редактор',      'Публикация статей и новостей'),
            ('Клиент',        'Обычный пользователь сайта'),
            ('Техник',        'Технический персонал центра'),
        ]
        roles = []
        for name, desc in data:
            r = Role.objects.create(name=name, description=desc)
            roles.append(r)
            self.stdout.write(f'  OK: Роль: {name}')
        return roles

    def _create_prosthesis_types(self):
        data = [
            ('Протез руки',      'Протезы верхних конечностей — кисть, предплечье, плечо'),
            ('Протез ноги',      'Протезы нижних конечностей — стопа, голень, бедро'),
            ('Экзоскелет',       'Активные экзоскелетные системы для реабилитации'),
            ('Протез пальца',    'Частичные протезы пальцев кисти'),
            ('Косметический',    'Косметические протезы без функциональной нагрузки'),
            ('Миоэлектрический', 'Протезы с управлением через мышечные сигналы'),
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
            'детский', 'водоотталкивающий', 'лёгкий', 'спортивный',
            'титановый', 'силиконовый',
        ]
        tags = []
        for name in names:
            t = Tag.objects.create(name=name)
            tags.append(t)
            self.stdout.write(f'  OK: Тег: {name}')
        return tags

    # ── Пользователи (10) ─────────────────────────────────────────────────

    def _create_users(self, roles):
        raw_users = [
            ('Иванов',     'Алексей',    'ivanov@example.com',    '+7 900 111-22-33', [0, 3]),
            ('Петрова',    'Мария',      'petrova@example.com',   '+7 900 222-33-44', [1, 2]),
            ('Сидоров',    'Дмитрий',    'sidorov@example.com',   '+7 900 333-44-55', [3]),
            ('Козлова',    'Анна',       'kozlova@example.com',   None,               [3]),
            ('Новиков',    'Игорь',      'novikov@example.com',   '+7 900 555-66-77', [1]),
            ('Морозова',   'Светлана',   'morozova@example.com',  '+7 900 666-77-88', [2]),
            ('Волков',     'Андрей',     'volkov@example.com',    None,               [3]),
            ('Лебедева',   'Ольга',      'lebedeva@example.com',  '+7 900 888-99-00', [3]),
            ('Зайцев',     'Михаил',     'zaitsev@example.com',   '+7 901 123-45-67', [4]),
            ('Соколова',   'Юлия',       'sokolova@example.com',  '+7 901 234-56-78', [1, 2]),
            ('Попов',      'Виталий',    'popov@example.com',     '+7 901 345-67-89', [3]),
            ('Григорьева', 'Наталья',    'grigoryeva@example.com','+7 901 456-78-90', [2, 3]),
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

    # ── Протезы (12) ──────────────────────────────────────────────────────

    def _create_prostheses(self, types, tags):
        data = [
            (0, 'Биоэлектрический протез кисти i-Limb',
             'Многофункциональный протез с 5 независимыми пальцами и управлением через миоэлектрические сигналы мышц.',
             890000, True, [0, 4]),
            (0, 'Механический протез предплечья Ottobock',
             'Надёжный тяговый протез предплечья с крюковым захватом для активного образа жизни.',
             120000, True, [1]),
            (1, 'Протез голени с углеродной стопой',
             'Динамический протез голени с энергоаккумулирующей стопой из углеволокна. Подходит для спорта.',
             350000, True, [2, 5, 9]),
            (1, 'Протез бедра с микропроцессорным коленом C-Leg',
             'Интеллектуальный протез бедра с гидравлическим управлением и датчиками угла.',
             1500000, True, [3]),
            (2, 'Реабилитационный экзоскелет Ekso Bionics',
             'Активный экзоскелет для восстановления ходьбы у пациентов с парезами ног.',
             2800000, False, [5]),
            (3, 'Косметический протез пальца силиконовый',
             'Силиконовый косметический протез пальца с индивидуальным окрашиванием под тон кожи.',
             45000, True, [4, 11]),
            (4, 'Косметический протез кисти',
             'Реалистичный силиконовый протез кисти, точно подобранный по цвету кожи.',
             180000, True, [4, 11]),
            (1, 'Протез стопы SACH',
             'Классический протез стопы с деревянным сердечником. Надёжность и доступная цена.',
             None, True, [1]),
            (5, 'Миоэлектрический протез предплечья BeBionic',
             'Передовой протез с 14 вариантами захвата и интуитивным управлением через мышцы.',
             1100000, True, [0, 2]),
            (0, 'Детский протез кисти Hero Arm',
             'Лёгкий и красочный биоэлектрический протез для детей 8–18 лет.',
             650000, True, [0, 6, 7]),
            (1, 'Спортивный протез голени Flex-Foot',
             'Углеродный протез для занятий спортом — бег, прыжки, плавание.',
             420000, True, [2, 9]),
            (2, 'Экзоскелет для верхних конечностей Myomo',
             'Носимый роботизированный ортез руки для восстановления моторики после инсульта.',
             950000, True, [5, 10]),
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
            self.stdout.write(f'  OK: Протез: {name[:55]}')
        return prostheses

    # ── Заявки (12) ───────────────────────────────────────────────────────

    def _create_requests(self, users, prostheses, statuses):
        data = [
            (2, 0, 0, 'prosthesis', 'Сидоров Дмитрий',   'sidorov@example.com',
             'Интересует биоэлектрический протез кисти. Потерял руку год назад.'),
            (3, 2, 1, 'prosthesis', 'Козлова Анна',       'kozlova@example.com',
             'Нужна консультация по протезу голени после ампутации.'),
            (6, 3, 3, 'prosthesis', 'Волков Андрей',      'volkov@example.com',
             'Хочу записаться на примерку протеза бедра.'),
            (7, 5, 4, 'prosthesis', 'Лебедева Ольга',     'lebedeva@example.com',
             'Прошу рассмотреть заявку на косметический протез пальца.'),
            (None, 1, 0, 'prosthesis', 'Кузнецов Павел',  'kuznetcov@mail.ru',
             'Узнать стоимость механического протеза предплечья.'),
            (None, None, 1, 'investor', 'ООО ТехноПротез', 'invest@technoprot.ru',
             'Рассматриваем возможность инвестирования в производство.'),
            (None, None, 0, 'investor', 'Фонд помощи',     'fond@help.org',
             'Благотворительный фонд хочет поддержать ваш проект.'),
            (2, 6, 5, 'prosthesis', 'Сидоров Дмитрий',   'sidorov@example.com',
             'Повторная заявка — интерес к косметическому протезу кисти.'),
            (8, 8, 1, 'prosthesis', 'Зайцев Михаил',      'zaitsev@example.com',
             'Интересует миоэлектрический протез для активной жизни.'),
            (9, 9, 2, 'prosthesis', 'Соколова Юлия',      'sokolova@example.com',
             'Хочу подобрать детский протез для дочери, 10 лет.'),
            (10, 10, 0, 'prosthesis', 'Попов Виталий',     'popov@example.com',
             'Интересует спортивный протез голени — занимаюсь бегом.'),
            (None, None, 1, 'investor', 'МедИнвест Групп', 'info@medinvest.ru',
             'Хотим обсудить партнёрство в развитии линейки экзоскелетов.'),
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

    # ── Блог (10) ─────────────────────────────────────────────────────────

    def _create_blog_posts(self, users):
        data = [
            (1, 'Современные биоэлектрические протезы: как это работает',
             'Биоэлектрические протезы используют электрические сигналы мышц для управления. '
             'Датчики на культе улавливают миоэлектрические импульсы и передают команды моторам пальцев. '
             'Современные системы позволяют выполнять до 14 различных захватов.',
             True, timezone.now() - timedelta(days=30)),
            (5, 'Реабилитация после ампутации: первые шаги',
             'После ампутации важнейший этап — психологическая адаптация и физическая реабилитация. '
             'Протезирование начинается с временного протеза уже через 4–6 недель после операции.',
             True, timezone.now() - timedelta(days=15)),
            (1, 'Экзоскелеты в медицине: настоящее и будущее',
             'Экзоскелеты помогают пациентам с травмами спинного мозга восстановить способность ходить. '
             'Современные системы оснащены датчиками баланса и интерфейсами нейрообратной связи.',
             True, timezone.now() - timedelta(days=7)),
            (5, 'Как выбрать протез: советы специалиста',
             'Выбор протеза зависит от уровня ампутации, образа жизни и физической активности пациента. '
             'Важно учитывать профессию, хобби и долгосрочные цели реабилитации.',
             True, timezone.now() - timedelta(days=45)),
            (1, 'Детское протезирование: особенности и подходы',
             'Дети растут быстро, поэтому детские протезы требуют замены каждые 1–2 года. '
             'Современные производители создают яркие и лёгкие модели, которые нравятся детям.',
             True, timezone.now() - timedelta(days=3)),
            (9, 'Углеродные протезы стопы: почему они лучше?',
             'Углеродное волокно — идеальный материал для протезов стопы. Оно лёгкое, прочное '
             'и обладает отличными пружинящими свойствами, позволяя бегать и прыгать.',
             True, timezone.now() - timedelta(days=20)),
            (5, 'Жизнь с протезом: истории наших пациентов',
             'Александр Новиков вернулся к работе механика через 8 месяцев после протезирования. '
             'Его история — пример того, как современные технологии меняют жизнь людей.',
             True, timezone.now() - timedelta(days=10)),
            (1, 'Как ухаживать за протезом: практическое руководство',
             'Правильный уход продлевает срок службы протеза на годы. '
             'Ежедневная чистка, еженедельная проверка крепёжных элементов и ежегодный сервис.',
             True, timezone.now() - timedelta(days=5)),
            (9, 'Страховое покрытие протезов в России',
             'Государство компенсирует часть стоимости протезов через систему ФСС. '
             'Рассказываем, какие документы нужны и как подать заявление на получение протеза.',
             True, timezone.now() - timedelta(days=25)),
            (5, 'Новые разработки 2025: что нас ждёт',
             'Обзор ключевых новинок в области протезирования, представленных на выставках 2025 года. '
             'Нейроинтерфейсы, тактильная обратная связь и автономные источники питания.',
             False, None),
        ]
        for author_idx, title, content, is_pub, pub_at in data:
            BlogPost.objects.create(
                author=users[author_idx],
                title=title,
                content=content,
                is_published=is_pub,
                published_at=pub_at,
            )
            self.stdout.write(f'  OK: Статья: {title[:55]}')

    # ── Мероприятия (10) ──────────────────────────────────────────────────

    def _create_events(self, users):
        data = [
            (4, 'Выставка протезных технологий 2025',
             'Ежегодная выставка новинок протезирования и реабилитационного оборудования.',
             timezone.now() + timedelta(days=30),
             'Москва, ВДНХ, павильон 75', 'https://expo.example.com/2025'),
            (4, 'Семинар: жизнь с протезом',
             'Открытый семинар для пользователей протезов и их родственников.',
             timezone.now() + timedelta(days=14),
             'Санкт-Петербург, ул. Ленина 10', 'https://seminar.example.com'),
            (1, 'Мастер-класс по уходу за протезом',
             'Практический мастер-класс по чистке, обслуживанию и мелкому ремонту.',
             timezone.now() + timedelta(days=7),
             'Онлайн (Zoom)', 'https://zoom.example.com/masterclass'),
            (4, 'День открытых дверей в центре протезирования',
             'Посетите наш центр, познакомьтесь с командой и современным оборудованием.',
             timezone.now() - timedelta(days=10),
             'Москва, ул. Медицинская 5', None),
            (1, 'Конференция реабилитологов 2025',
             'Международная конференция по вопросам реабилитации и протезирования.',
             timezone.now() + timedelta(days=60),
             'Казань, МВЦ «Казань Экспо»', 'https://conf.example.com/rehab2025'),
            (9, 'Вебинар: выбор протеза для детей',
             'Онлайн-встреча с ортопедом-протезистом. Ответы на вопросы родителей.',
             timezone.now() + timedelta(days=5),
             'Онлайн (YouTube Live)', None),
            (4, 'Паралимпийская эстафета — Москва',
             'Благотворительное спортивное мероприятие с участием пользователей протезов.',
             timezone.now() + timedelta(days=45),
             'Москва, Лужники', 'https://paralimpic.example.com'),
            (1, 'Обучение сотрудников: новые модели 2025',
             'Внутреннее обучение персонала центра работе с новыми моделями протезов.',
             timezone.now() + timedelta(days=20),
             'Москва, офис ПротезМед', None),
            (9, 'Встреча клуба пользователей протезов',
             'Ежемесячная встреча клуба — обмен опытом, поддержка и общение.',
             timezone.now() + timedelta(days=10),
             'Москва, Центр реабилитации', None),
            (4, 'Медицинский форум «Ортопедия будущего»',
             'Ежегодный форум ведущих специалистов в области ортопедии и протезирования.',
             timezone.now() - timedelta(days=5),
             'Москва, Экспоцентр', 'https://ortho-forum.example.com'),
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
            self.stdout.write(f'  OK: Мероприятие: {title[:55]}')

    # ── Документы (10) ────────────────────────────────────────────────────

    def _create_documents(self, users):
        data = [
            (0, 'Лицензия на медицинскую деятельность №ЛО-77-01-12345', 'license'),
            (0, 'Сертификат ISO 13485:2016 Медицинские изделия', 'certificate'),
            (4, 'Сертификат соответствия протеза кисти i-Limb', 'certificate'),
            (4, 'Регистрационное удостоверение Росздравнадзора №РЗН 2024/1234', 'license'),
            (1, 'Договор с поставщиком Ottobock GmbH', 'other'),
            (0, 'Сертификат системы менеджмента качества ISO 9001', 'certificate'),
            (8, 'Техническое задание на разработку нового изделия', 'other'),
            (9, 'Лицензия на право осуществления медицинской деятельности (обновление)', 'license'),
            (1, 'Соглашение о конфиденциальности с партнёрами', 'other'),
            (0, 'Сертификат CE для протеза голени (Европейский рынок)', 'certificate'),
            (4, 'Регистрационное удостоверение на экзоскелет Ekso', 'license'),
        ]
        for uploader_idx, title, doc_type in data:
            Document.objects.create(
                uploaded_by=users[uploader_idx],
                title=title,
                doc_type=doc_type,
                uploaded_at=timezone.now() - timedelta(days=random.randint(1, 180)),
            )
            self.stdout.write(f'  OK: Документ: {title[:55]}')
