-- ============================================================
-- ЛАБОРАТОРНАЯ РАБОТА: PostgreSQL для портала протезирования
-- Предметная область: интернет-портал реабилитационных протезов
-- ============================================================

-- ============================================================
-- РАЗДЕЛ 0: СОЗДАНИЕ ТАБЛИЦ И ТЕСТОВЫЕ ДАННЫЕ
-- ============================================================

DROP SCHEMA IF EXISTS prosthetics CASCADE;
CREATE SCHEMA prosthetics;
SET search_path = prosthetics;

-- Роли пользователей
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Пользователи
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    last_name     VARCHAR(100) NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    phone         VARCHAR(20),
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Связь пользователь — роль
CREATE TABLE user_roles (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id     INT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, role_id)
);

-- Типы протезов
CREATE TABLE prosthesis_types (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Теги
CREATE TABLE tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Протезы (каталог)
CREATE TABLE prostheses (
    id                  SERIAL PRIMARY KEY,
    prosthesis_type_id  INT NOT NULL REFERENCES prosthesis_types(id) ON DELETE RESTRICT,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    price               NUMERIC(12,2),
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- M:N протез — тег
CREATE TABLE prosthesis_tags (
    prosthesis_id INT NOT NULL REFERENCES prostheses(id) ON DELETE CASCADE,
    tag_id        INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (prosthesis_id, tag_id)
);

-- Статусы заявок
CREATE TABLE request_statuses (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Заявки клиентов и инвесторов
CREATE TABLE requests (
    id            SERIAL PRIMARY KEY,
    user_id       INT REFERENCES users(id) ON DELETE SET NULL,
    prosthesis_id INT REFERENCES prostheses(id) ON DELETE SET NULL,
    status_id     INT NOT NULL REFERENCES request_statuses(id) ON DELETE RESTRICT,
    request_type  VARCHAR(20) NOT NULL CHECK (request_type IN ('prosthesis','investor')),
    contact_name  VARCHAR(200) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    message       TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Блог
CREATE TABLE blog_posts (
    id           SERIAL PRIMARY KEY,
    author_id    INT REFERENCES users(id) ON DELETE SET NULL,
    title        VARCHAR(300) NOT NULL,
    content      TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    is_published BOOLEAN DEFAULT FALSE
);

-- Мероприятия
CREATE TABLE events (
    id          SERIAL PRIMARY KEY,
    author_id   INT REFERENCES users(id) ON DELETE SET NULL,
    title       VARCHAR(300) NOT NULL,
    description TEXT,
    event_date  TIMESTAMPTZ NOT NULL,
    location    VARCHAR(300),
    website     VARCHAR(500)
);

-- Документы (сертификаты, лицензии)
CREATE TABLE documents (
    id            SERIAL PRIMARY KEY,
    uploaded_by   INT REFERENCES users(id) ON DELETE SET NULL,
    title         VARCHAR(300) NOT NULL,
    doc_type      VARCHAR(20) NOT NULL CHECK (doc_type IN ('certificate','license','other')),
    uploaded_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ── Тестовые данные ──────────────────────────────────────────

INSERT INTO roles(name, description) VALUES
    ('Администратор', 'Полный доступ к системе'),
    ('Менеджер',      'Управление заявками'),
    ('Редактор',      'Публикация контента'),
    ('Клиент',        'Просмотр каталога и оформление заявок');

INSERT INTO users(last_name, first_name, email, phone) VALUES
    ('Иванов',    'Алексей',   'ivanov@mail.ru',    '+7-900-111-22-33'),
    ('Петрова',   'Мария',     'petrova@mail.ru',   '+7-900-222-33-44'),
    ('Сидоров',   'Дмитрий',   'sidorov@mail.ru',   NULL),
    ('Козлова',   'Анна',      'kozlova@mail.ru',   '+7-900-444-55-66'),
    ('Новиков',   'Иван',      'novikov@mail.ru',   '+7-900-555-66-77'),
    ('Морозов',   'Сергей',    'morozov@mail.ru',   NULL),
    ('Волкова',   'Елена',     'volkova@mail.ru',   '+7-900-777-88-99'),
    ('Захаров',   'Николай',   'zakharov@mail.ru',  '+7-900-888-99-00');

INSERT INTO user_roles(user_id, role_id) VALUES
    (1,1),(1,2),(2,2),(3,3),(4,4),(5,4),(6,4),(7,4),(8,4);

INSERT INTO prosthesis_types(name, description) VALUES
    ('Протез руки',     'Протезы верхних конечностей'),
    ('Протез ноги',     'Протезы нижних конечностей'),
    ('Экзоскелет',      'Внешние каркасные устройства'),
    ('Протез пальца',   'Протезы отдельных пальцев'),
    ('Косметический',   'Силиконовые косметические протезы');

INSERT INTO tags(name) VALUES
    ('биоэлектрический'),('водонепроницаемый'),('детский'),
    ('реабилитационный'),('лёгкий'),('спортивный'),('микропроцессорный'),('3D-печать');

INSERT INTO prostheses(prosthesis_type_id, name, description, price, is_active) VALUES
    (1,'ПротезАрм Pro',    'Биоэлектрический протез руки с 5 захватами', 450000, TRUE),
    (1,'КистьЛёгкая',      'Лёгкий протез кисти для активного образа жизни', 120000, TRUE),
    (2,'КоленоМакс',       'Микропроцессорный коленный протез', 890000, TRUE),
    (2,'СтопаСпорт',       'Спортивный карбоновый протез стопы', 210000, TRUE),
    (3,'ЭкзоСпина',        'Экзоскелет для реабилитации после инсульта', 1200000, TRUE),
    (4,'ПалецМини',        'Миниатюрный протез пальца на 3D-принтере', 35000, TRUE),
    (5,'КосметикаСиликон', 'Косметический силиконовый протез кисти', 95000, FALSE),
    (1,'КистьДетская',     'Лёгкий детский протез кисти', 85000, TRUE);

INSERT INTO prosthesis_tags(prosthesis_id, tag_id) VALUES
    (1,1),(1,4),(2,5),(2,4),(3,7),(3,4),(4,6),(4,5),
    (5,4),(5,3),(6,8),(6,5),(7,1),(8,3),(8,5);

INSERT INTO request_statuses(name) VALUES
    ('Новая'),('В работе'),('Ожидает документов'),
    ('Одобрена'),('Отклонена'),('Завершена');

INSERT INTO requests(user_id, prosthesis_id, status_id, request_type, contact_name, contact_email, message, created_at) VALUES
    (4, 1, 1, 'prosthesis', 'Козлова Анна',   'kozlova@mail.ru',  'Нужна консультация по протезу руки', NOW() - INTERVAL '2 days'),
    (5, 3, 2, 'prosthesis', 'Новиков Иван',   'novikov@mail.ru',  'Интересует протез колена', NOW() - INTERVAL '10 days'),
    (6, 5, 4, 'prosthesis', 'Морозов Сергей', 'morozov@mail.ru',  'Запрос по экзоскелету', NOW() - INTERVAL '30 days'),
    (7, 2, 5, 'prosthesis', 'Волкова Елена',  'volkova@mail.ru',  'Отменила заявку', NOW() - INTERVAL '60 days'),
    (8, 4, 6, 'prosthesis', 'Захаров Николай','zakharov@mail.ru', 'Протез оформлен', NOW() - INTERVAL '400 days'),
    (NULL, NULL, 1, 'investor', 'ИП Романов', 'romanov@biz.ru',   'Хочу инвестировать', NOW() - INTERVAL '1 day'),
    (4, 8, 2, 'prosthesis', 'Козлова Анна',   'kozlova@mail.ru',  'Детский протез для ребёнка', NOW() - INTERVAL '5 days'),
    (NULL, NULL, 1, 'investor', 'ООО ПротезПром','invest@pp.ru',   'Коммерческое предложение', NOW() - INTERVAL '3 days');

INSERT INTO blog_posts(author_id, title, content, published_at, is_published) VALUES
    (3,'Как выбрать протез руки','Подробное руководство по выбору...', NOW()-INTERVAL '20 days', TRUE),
    (3,'Реабилитация после ампутации','Этапы восстановления...', NOW()-INTERVAL '15 days', TRUE),
    (1,'Новинки 2025: биоэлектрика','Обзор новых технологий...', NOW()-INTERVAL '5 days', TRUE),
    (3,'3D-печать в протезировании','Как работает технология...', NULL, FALSE),
    (3,'Спортивные протезы','Для активного образа жизни...', NOW()-INTERVAL '45 days', TRUE);

INSERT INTO events(author_id, title, event_date, location) VALUES
    (1,'Выставка реабилитационных технологий', NOW()+INTERVAL '30 days', 'Москва, ЦВК Экспоцентр'),
    (2,'Семинар: подбор протеза',              NOW()+INTERVAL '7 days',  'Онлайн'),
    (1,'День открытых дверей клиники',          NOW()+INTERVAL '14 days', 'Москва, ул. Ленина 10'),
    (3,'Конференция по экзоскелетам',           NOW()-INTERVAL '10 days', 'Санкт-Петербург'),
    (2,'Мастер-класс по уходу за протезом',     NOW()+INTERVAL '21 days', 'Онлайн');

-- ============================================================
-- БЛОК 1: ФУНКЦИИ И ПРОЦЕДУРЫ (5 примеров)
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 1.1 ФУНКЦИЯ: get_user_request_summary(p_user_id INT)
--
-- Кейс: менеджер открывает карточку клиента и видит сводку
-- по его заявкам — сколько в каком статусе. Используется в
-- личном кабинете и CRM-интерфейсе администратора.
-- Синтаксис: RETURNS TABLE, JOIN, GROUP BY внутри функции
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_user_request_summary(p_user_id INT)
RETURNS TABLE (
    status_name  VARCHAR,
    request_count BIGINT,
    last_updated  TIMESTAMPTZ
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT
            rs.name::VARCHAR         AS status_name,
            COUNT(r.id)              AS request_count,
            MAX(r.updated_at)        AS last_updated
        FROM requests r
        JOIN request_statuses rs ON rs.id = r.status_id
        WHERE r.user_id = p_user_id
        GROUP BY rs.name
        ORDER BY request_count DESC;
END;
$$;

-- Вызов:
SELECT * FROM get_user_request_summary(4);


-- ──────────────────────────────────────────────────────────────
-- 1.2 ПРОЦЕДУРА: reject_request(p_request_id INT, p_reason TEXT)
--
-- Кейс: менеджер отклоняет заявку. Нельзя отклонить уже
-- завершённую или уже отклонённую заявку — только «Новая»
-- и «В работе» допускают перевод в статус «Отклонена».
-- Синтаксис: PROCEDURE, IF/ELSIF, RAISE EXCEPTION, транзакция
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE reject_request(
    p_request_id INT,
    p_reason     TEXT DEFAULT 'Причина не указана'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_current_status VARCHAR;
    v_rejected_id    INT;
BEGIN
    SELECT rs.name INTO v_current_status
    FROM requests r
    JOIN request_statuses rs ON rs.id = r.status_id
    WHERE r.id = p_request_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Заявка с ID % не найдена', p_request_id;
    END IF;

    IF v_current_status NOT IN ('Новая', 'В работе') THEN
        RAISE EXCEPTION
            'Нельзя отклонить заявку со статусом "%". Допустимо только для "Новая" и "В работе".',
            v_current_status;
    END IF;

    SELECT id INTO v_rejected_id FROM request_statuses WHERE name = 'Отклонена';

    UPDATE requests
    SET status_id  = v_rejected_id,
        message    = COALESCE(message, '') || E'\n[Отклонено]: ' || p_reason,
        updated_at = NOW()
    WHERE id = p_request_id;

    RAISE NOTICE 'Заявка % переведена в статус "Отклонена"', p_request_id;
END;
$$;

-- Вызов — допустимый статус:
CALL reject_request(1, 'Клиент не отвечает');
-- Вызов — попытка отклонить уже отклонённую (ошибка):
CALL reject_request(4, 'Тест ошибки');


-- ──────────────────────────────────────────────────────────────
-- 1.3 ФУНКЦИЯ: get_catalog_stats(p_type_name VARCHAR)
--
-- Кейс: страница «Статистика каталога» в админ-панели.
-- Менеджер выбирает тип протеза и видит сводку: количество
-- моделей, ценовой диапазон, средняя цена.
-- Синтаксис: RETURNS RECORD, ILIKE, агрегаты
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_catalog_stats(p_type_name VARCHAR)
RETURNS TABLE (
    type_name   VARCHAR,
    total       BIGINT,
    active_cnt  BIGINT,
    min_price   NUMERIC,
    max_price   NUMERIC,
    avg_price   NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT
            pt.name::VARCHAR,
            COUNT(p.id),
            COUNT(p.id) FILTER (WHERE p.is_active),
            MIN(p.price),
            MAX(p.price),
            ROUND(AVG(p.price), 2)
        FROM prostheses p
        JOIN prosthesis_types pt ON pt.id = p.prosthesis_type_id
        WHERE pt.name ILIKE '%' || p_type_name || '%'
        GROUP BY pt.name;
END;
$$;

-- Вызов:
SELECT * FROM get_catalog_stats('протез руки');
SELECT * FROM get_catalog_stats('');  -- вся статистика


-- ──────────────────────────────────────────────────────────────
-- 1.4 ПРОЦЕДУРА: archive_stale_requests()
--
-- Кейс: плановая ночная задача (cron). Все заявки старше
-- 1 года со статусом «Новая» или «В работе» автоматически
-- переводятся в «Завершена» — чтобы не засорять рабочую очередь.
-- Синтаксис: PROCEDURE, массовый UPDATE, RAISE NOTICE с числом
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE archive_stale_requests()
LANGUAGE plpgsql AS $$
DECLARE
    v_archived_id INT;
    v_count       INT;
BEGIN
    SELECT id INTO v_archived_id
    FROM request_statuses WHERE name = 'Завершена';

    UPDATE requests
    SET status_id  = v_archived_id,
        updated_at = NOW()
    WHERE status_id IN (
              SELECT id FROM request_statuses WHERE name IN ('Новая', 'В работе')
          )
      AND created_at < NOW() - INTERVAL '1 year';

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Архивировано % заявок', v_count;
END;
$$;

-- Вызов:
CALL archive_stale_requests();


-- ──────────────────────────────────────────────────────────────
-- 1.5 ФУНКЦИЯ: get_prostheses_by_budget(p_min NUMERIC, p_max NUMERIC)
--
-- Кейс: API-метод для фильтрации каталога по бюджету клиента.
-- Возвращает активные протезы в ценовом диапазоне с тегами
-- в виде JSON-массива (удобно для REST API).
-- Синтаксис: RETURNS TABLE, JSON_AGG, subquery, COALESCE
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_prostheses_by_budget(
    p_min NUMERIC DEFAULT 0,
    p_max NUMERIC DEFAULT 9999999
)
RETURNS TABLE (
    prosthesis_id  INT,
    prosthesis_name VARCHAR,
    type_name      VARCHAR,
    price          NUMERIC,
    tags_json      JSON
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT
            p.id,
            p.name::VARCHAR,
            pt.name::VARCHAR,
            p.price,
            COALESCE(
                (SELECT JSON_AGG(t.name ORDER BY t.name)
                 FROM prosthesis_tags ptg
                 JOIN tags t ON t.id = ptg.tag_id
                 WHERE ptg.prosthesis_id = p.id),
                '[]'::JSON
            )
        FROM prostheses p
        JOIN prosthesis_types pt ON pt.id = p.prosthesis_type_id
        WHERE p.is_active = TRUE
          AND p.price BETWEEN p_min AND p_max
        ORDER BY p.price;
END;
$$;

-- Вызов:
SELECT * FROM get_prostheses_by_budget(50000, 300000);


-- ============================================================
-- БЛОК 2: ЦИКЛЫ (3 примера — WHILE, FOR, LOOP…EXIT WHEN)
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 2.1 ЦИКЛ WHILE: пакетная генерация тестовых инвесторских заявок
--
-- Кейс: нагрузочное тестирование — нужно быстро наполнить
-- таблицу до заданного количества investor-заявок.
-- Цикл WHILE проверяет текущее количество и добавляет по одной
-- записи, пока не достигнет целевого числа.
-- ──────────────────────────────────────────────────────────────
DO $$
DECLARE
    v_current_count INT;
    v_target        INT := 15;
    v_counter       INT := 0;
    v_new_id        INT;
    v_status_id     INT;
BEGIN
    SELECT id INTO v_status_id FROM request_statuses WHERE name = 'Новая';

    SELECT COUNT(*) INTO v_current_count
    FROM requests WHERE request_type = 'investor';

    WHILE v_current_count < v_target LOOP
        v_counter := v_counter + 1;
        INSERT INTO requests(status_id, request_type, contact_name, contact_email, message)
        VALUES (
            v_status_id,
            'investor',
            'Тестовый инвестор #' || v_counter,
            'test_investor_' || v_counter || '@example.com',
            'Автоматически сгенерированная заявка для тестирования'
        )
        RETURNING id INTO v_new_id;

        v_current_count := v_current_count + 1;
        RAISE NOTICE 'Добавлена заявка ID=%, всего investor-заявок: %', v_new_id, v_current_count;
    END LOOP;

    RAISE NOTICE 'Готово. Добавлено % новых заявок', v_counter;
END;
$$;

-- Проверка результата:
SELECT COUNT(*) FROM requests WHERE request_type = 'investor';


-- ──────────────────────────────────────────────────────────────
-- 2.2 ЦИКЛ FOR (по курсору/результату запроса):
-- Автоматическое назначение скидки на протезы без продаж
--
-- Кейс: маркетинговая акция — снизить цену на 10% для всех
-- активных протезов, по которым ещё не было заявок.
-- FOR перебирает результат SELECT без явного объявления курсора.
-- ──────────────────────────────────────────────────────────────
DO $$
DECLARE
    rec          RECORD;
    v_new_price  NUMERIC;
    v_discount   NUMERIC := 0.10;
    v_cnt        INT := 0;
BEGIN
    FOR rec IN
        SELECT p.id, p.name, p.price
        FROM prostheses p
        WHERE p.is_active = TRUE
          AND p.price IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM requests r
              WHERE r.prosthesis_id = p.id
          )
    LOOP
        v_new_price := ROUND(rec.price * (1 - v_discount), 2);

        UPDATE prostheses
        SET price = v_new_price
        WHERE id = rec.id;

        v_cnt := v_cnt + 1;
        RAISE NOTICE 'Протез "%" (ID=%): цена % → %',
            rec.name, rec.id, rec.price, v_new_price;
    END LOOP;

    IF v_cnt = 0 THEN
        RAISE NOTICE 'Нет протезов без заявок — скидка не применена';
    ELSE
        RAISE NOTICE 'Скидка 10%% применена к % протезам', v_cnt;
    END IF;
END;
$$;


-- ──────────────────────────────────────────────────────────────
-- 2.3 ЦИКЛ LOOP … EXIT WHEN: генерация уникального логина
--
-- Кейс: при регистрации нового пользователя система
-- автоматически генерирует уникальный email-логин вида
-- user.N@prosthetics.ru, увеличивая N до тех пор, пока не
-- найдёт свободный адрес. LOOP + EXIT WHEN — аналог do-while.
-- ──────────────────────────────────────────────────────────────
DO $$
DECLARE
    v_base_name  VARCHAR := 'user';
    v_domain     VARCHAR := '@prosthetics.ru';
    v_candidate  VARCHAR;
    v_counter    INT := 1;
    v_exists     BOOLEAN;
BEGIN
    LOOP
        v_candidate := v_base_name || '.' || v_counter || v_domain;

        SELECT EXISTS(
            SELECT 1 FROM users WHERE email = v_candidate
        ) INTO v_exists;

        EXIT WHEN NOT v_exists;   -- выходим как только нашли свободный

        v_counter := v_counter + 1;

        IF v_counter > 9999 THEN
            RAISE EXCEPTION 'Не удалось найти свободный логин после 9999 попыток';
        END IF;
    END LOOP;

    RAISE NOTICE 'Свободный логин: % (проверено % вариантов)', v_candidate, v_counter;

    -- Создать пользователя с найденным логином
    INSERT INTO users(last_name, first_name, email)
    VALUES ('Новый', 'Пользователь', v_candidate);

    RAISE NOTICE 'Пользователь зарегистрирован: %', v_candidate;
END;
$$;


-- ============================================================
-- БЛОК 3: ИНДЕКСЫ (2 примера + EXPLAIN ANALYZE)
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 3.1 Составной индекс: ускорение фильтрации заявок по статусу и дате
--
-- Типичный запрос менеджера: все «Новые» заявки за последние 7 дней
-- ──────────────────────────────────────────────────────────────

-- ШАГ 1: план без индекса
EXPLAIN ANALYZE
SELECT r.id, r.contact_name, r.contact_email, r.created_at, rs.name AS status
FROM requests r
JOIN request_statuses rs ON rs.id = r.status_id
WHERE rs.name = 'Новая'
  AND r.created_at >= NOW() - INTERVAL '7 days'
ORDER BY r.created_at DESC;

-- ШАГ 2: создать индексы
CREATE INDEX idx_requests_status_date
    ON requests (status_id, created_at DESC);

CREATE INDEX idx_request_statuses_name
    ON request_statuses (name);

-- ШАГ 3: план с индексами (должен появиться Index Scan)
EXPLAIN ANALYZE
SELECT r.id, r.contact_name, r.contact_email, r.created_at, rs.name AS status
FROM requests r
JOIN request_statuses rs ON rs.id = r.status_id
WHERE rs.name = 'Новая'
  AND r.created_at >= NOW() - INTERVAL '7 days'
ORDER BY r.created_at DESC;

-- Оценка: сравнить Seq Scan → Index Scan, время выполнения


-- ──────────────────────────────────────────────────────────────
-- 3.2 Полнотекстовый индекс: поиск по каталогу протезов
--
-- Кейс: строка поиска на сайте — пользователь вводит «детский лёгкий»
-- ──────────────────────────────────────────────────────────────

-- ШАГ 1: план без полнотекстового индекса
EXPLAIN ANALYZE
SELECT id, name, description, price
FROM prostheses
WHERE to_tsvector('russian', name || ' ' || COALESCE(description,''))
        @@ to_tsquery('russian', 'детский & лёгкий');

-- ШАГ 2: создать индекс GIN на tsvector
CREATE INDEX idx_prostheses_fts
    ON prostheses
    USING GIN (to_tsvector('russian', name || ' ' || COALESCE(description, '')));

-- ШАГ 3: план с индексом
EXPLAIN ANALYZE
SELECT id, name, description, price
FROM prostheses
WHERE to_tsvector('russian', name || ' ' || COALESCE(description,''))
        @@ to_tsquery('russian', 'детский & лёгкий');

-- Дополнительно: поиск через массив тегов
-- Индекс для фильтрации по JSON/массивам
CREATE INDEX idx_prostheses_type
    ON prostheses (prosthesis_type_id)
    WHERE is_active = TRUE;   -- частичный индекс — только активные

-- Запрос с частичным индексом
EXPLAIN ANALYZE
SELECT id, name, price
FROM prostheses
WHERE prosthesis_type_id = 1 AND is_active = TRUE;


-- ============================================================
-- БЛОК 4: ПРЕДСТАВЛЕНИЯ И ПРАВА ДОСТУПА
-- ============================================================

-- ──────────────────────────────────────────────────────────────
-- 4.1 Обычное представление: активный каталог с типами и тегами
-- Используется на главной странице сайта
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_active_catalog AS
    SELECT
        p.id,
        p.name,
        p.description,
        p.price,
        pt.name  AS type_name,
        STRING_AGG(t.name, ', ' ORDER BY t.name) AS tags
    FROM prostheses p
    JOIN prosthesis_types pt ON pt.id = p.prosthesis_type_id
    LEFT JOIN prosthesis_tags ptg ON ptg.prosthesis_id = p.id
    LEFT JOIN tags t ON t.id = ptg.tag_id
    WHERE p.is_active = TRUE
    GROUP BY p.id, p.name, p.description, p.price, pt.name
    ORDER BY pt.name, p.name;

-- Запрос через представление:
SELECT * FROM vw_active_catalog;
SELECT * FROM vw_active_catalog WHERE type_name = 'Протез руки';


-- ──────────────────────────────────────────────────────────────
-- 4.2 Временное представление: протезы в ценовом диапазоне
-- Кейс: фильтрация каталога клиентом по бюджету
-- ──────────────────────────────────────────────────────────────
CREATE TEMP VIEW tmp_budget_catalog AS
    SELECT id, name, type_name, price, tags
    FROM vw_active_catalog
    WHERE price BETWEEN 50000 AND 300000;

SELECT * FROM tmp_budget_catalog;


-- ──────────────────────────────────────────────────────────────
-- 4.3 Временное представление: статистика заявок по статусам
-- Кейс: дашборд менеджера — обзор воронки продаж
-- ──────────────────────────────────────────────────────────────
CREATE TEMP VIEW tmp_requests_funnel AS
    SELECT
        rs.name                                   AS status,
        COUNT(r.id)                               AS total,
        COUNT(r.id) FILTER (WHERE r.request_type = 'prosthesis') AS prosthesis_reqs,
        COUNT(r.id) FILTER (WHERE r.request_type = 'investor')   AS investor_reqs,
        MAX(r.created_at)                         AS latest
    FROM request_statuses rs
    LEFT JOIN requests r ON r.status_id = rs.id
    GROUP BY rs.name
    ORDER BY total DESC;

SELECT * FROM tmp_requests_funnel;


-- ──────────────────────────────────────────────────────────────
-- 4.4 Временное представление: клиенты с активными заявками
-- на ближайший месяц (для уведомлений)
-- ──────────────────────────────────────────────────────────────
CREATE TEMP VIEW tmp_active_clients AS
    SELECT DISTINCT
        u.id,
        u.first_name || ' ' || u.last_name AS full_name,
        u.email,
        u.phone,
        COUNT(r.id) OVER (PARTITION BY u.id) AS open_requests
    FROM users u
    JOIN requests r ON r.user_id = u.id
    JOIN request_statuses rs ON rs.id = r.status_id
    WHERE rs.name IN ('Новая', 'В работе')
      AND r.created_at >= NOW() - INTERVAL '30 days';

SELECT * FROM tmp_active_clients;


-- ──────────────────────────────────────────────────────────────
-- 4.5 Материализованное представление: статистика по месяцам
-- Кейс: отчёт руководства — сколько заявок поступало по месяцам
-- Обновляется раз в сутки через REFRESH
-- ──────────────────────────────────────────────────────────────
CREATE MATERIALIZED VIEW mv_monthly_requests AS
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        COUNT(*)                         AS total_requests,
        COUNT(*) FILTER (WHERE request_type = 'prosthesis') AS prosthesis_reqs,
        COUNT(*) FILTER (WHERE request_type = 'investor')   AS investor_reqs
    FROM requests
    GROUP BY DATE_TRUNC('month', created_at)
    ORDER BY month;

SELECT * FROM mv_monthly_requests;

-- Обновление:
REFRESH MATERIALIZED VIEW mv_monthly_requests;


-- ──────────────────────────────────────────────────────────────
-- 4.6 Материализованное представление: топ протезов по заявкам
-- ──────────────────────────────────────────────────────────────
CREATE MATERIALIZED VIEW mv_top_prostheses AS
    SELECT
        p.id,
        p.name,
        pt.name  AS type_name,
        p.price,
        COUNT(r.id) AS request_count
    FROM prostheses p
    JOIN prosthesis_types pt ON pt.id = p.prosthesis_type_id
    LEFT JOIN requests r ON r.prosthesis_id = p.id
    GROUP BY p.id, p.name, pt.name, p.price
    ORDER BY request_count DESC;

SELECT * FROM mv_top_prostheses;

-- ──────────────────────────────────────────────────────────────
-- 4.7 Рекурсивное представление (CTE): иерархия ролей
-- Для демонстрации создадим таблицу иерархии ролей
-- ──────────────────────────────────────────────────────────────
ALTER TABLE roles ADD COLUMN IF NOT EXISTS parent_role_id INT REFERENCES roles(id);

UPDATE roles SET parent_role_id = NULL  WHERE name = 'Администратор';
UPDATE roles SET parent_role_id = (SELECT id FROM roles WHERE name = 'Администратор')
    WHERE name = 'Менеджер';
UPDATE roles SET parent_role_id = (SELECT id FROM roles WHERE name = 'Администратор')
    WHERE name = 'Редактор';
UPDATE roles SET parent_role_id = (SELECT id FROM roles WHERE name = 'Менеджер')
    WHERE name = 'Клиент';

CREATE OR REPLACE VIEW vw_role_hierarchy AS
WITH RECURSIVE role_tree AS (
    -- Якорь: корневые роли (без родителя)
    SELECT
        id,
        name,
        parent_role_id,
        0            AS depth,
        name::TEXT   AS path
    FROM roles
    WHERE parent_role_id IS NULL

    UNION ALL

    -- Рекурсивная часть: дочерние роли
    SELECT
        r.id,
        r.name,
        r.parent_role_id,
        rt.depth + 1,
        rt.path || ' → ' || r.name
    FROM roles r
    JOIN role_tree rt ON rt.id = r.parent_role_id
)
SELECT depth, REPEAT('  ', depth) || name AS role_with_indent, path
FROM role_tree
ORDER BY path;

SELECT * FROM vw_role_hierarchy;


-- ──────────────────────────────────────────────────────────────
-- 4.8 Права доступа: роль только для чтения (менеджер каталога)
-- ──────────────────────────────────────────────────────────────
-- Создать роль (если не существует)
DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'catalog_readonly') THEN
        CREATE ROLE catalog_readonly;
    END IF;
END $$;

-- Предоставить права только на чтение каталога
GRANT USAGE ON SCHEMA prosthetics TO catalog_readonly;
GRANT SELECT ON prostheses, prosthesis_types, tags, prosthesis_tags TO catalog_readonly;
GRANT SELECT ON vw_active_catalog TO catalog_readonly;

-- Запрет на изменение (явный, для документации)
REVOKE INSERT, UPDATE, DELETE ON prostheses FROM catalog_readonly;

-- Проверка прав:
SELECT grantee, privilege_type, table_name
FROM information_schema.role_table_grants
WHERE grantee = 'catalog_readonly'
  AND table_schema = 'prosthetics';


-- ============================================================
-- БЛОК 5: ТРИГГЕРЫ (4 примера)
-- ============================================================

-- Таблица аудита для триггера 5.4
CREATE TABLE IF NOT EXISTS audit_log (
    id          SERIAL PRIMARY KEY,
    table_name  VARCHAR(100) NOT NULL,
    column_name VARCHAR(100) NOT NULL,
    old_value   TEXT,
    new_value   TEXT,
    changed_at  TIMESTAMPTZ DEFAULT NOW(),
    changed_by  TEXT DEFAULT CURRENT_USER
);

-- ──────────────────────────────────────────────────────────────
-- 5.1 BEFORE INSERT: валидация цены протеза
--
-- Кейс: защита от ошибок ввода — цена не может быть
-- отрицательной или равной нулю. BEFORE позволяет отклонить
-- вставку до изменения данных.
-- Тип: BEFORE INSERT OR UPDATE, ROW-level
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION trg_validate_prosthesis_price()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.price IS NOT NULL AND NEW.price <= 0 THEN
        RAISE EXCEPTION
            'Цена протеза должна быть положительной. Получено: %', NEW.price;
    END IF;
    -- Нормализация: убрать лишние пробелы из имени
    NEW.name := TRIM(NEW.name);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_prosthesis_price_check
    BEFORE INSERT OR UPDATE OF price, name ON prostheses
    FOR EACH ROW
    EXECUTE FUNCTION trg_validate_prosthesis_price();

-- Тест триггера — нормальная вставка:
INSERT INTO prostheses(prosthesis_type_id, name, price)
VALUES (1, '  Тест пробелы  ', 50000);
-- Убедиться что имя обрезано:
SELECT id, name, price FROM prostheses WHERE name = 'Тест пробелы';

-- Тест триггера — отрицательная цена (должна быть ошибка):
-- INSERT INTO prostheses(prosthesis_type_id, name, price)
-- VALUES (1, 'Ошибочный протез', -1000);

-- Почему BEFORE ROW: нужно проверить и изменить данные ДО записи.
-- Через представление можно решить задачу проверки без изменения
-- (CHECK constraint), но нормализацию NEW.name через CHECK не сделать.


-- ──────────────────────────────────────────────────────────────
-- 5.2 AFTER UPDATE: автосмена статуса заявки на «Завершена»
-- при установке статуса «Одобрена» + прошло > 30 дней
--
-- Кейс: после одобрения заявки, если прошёл месяц и
-- менеджер снова обновляет запись — система автоматически
-- завершает заявку без ручного вмешательства.
-- Тип: AFTER UPDATE, ROW-level
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION trg_auto_complete_request()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_approved_id  INT;
    v_completed_id INT;
    v_status_name  VARCHAR;
BEGIN
    SELECT id INTO v_approved_id  FROM request_statuses WHERE name = 'Одобрена';
    SELECT id INTO v_completed_id FROM request_statuses WHERE name = 'Завершена';

    SELECT name INTO v_status_name FROM request_statuses WHERE id = NEW.status_id;

    IF NEW.status_id = v_approved_id
        AND NEW.created_at < NOW() - INTERVAL '30 days'
    THEN
        UPDATE requests
        SET status_id = v_completed_id, updated_at = NOW()
        WHERE id = NEW.id;

        RAISE NOTICE 'Заявка % автоматически завершена (одобрена >30 дней назад)', NEW.id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_request_auto_complete
    AFTER UPDATE ON requests
    FOR EACH ROW
    EXECUTE FUNCTION trg_auto_complete_request();

-- Почему AFTER ROW: не нужно менять исходную запись через RETURN NEW,
-- а нужно реагировать на факт изменения и выполнить побочное действие.


-- ──────────────────────────────────────────────────────────────
-- 5.3 BEFORE INSERT: защита от дублирования email пользователя
-- с нормализацией (привод к нижнему регистру)
--
-- Кейс: пользователь может ввести "User@Mail.RU" или "user@mail.ru" —
-- оба варианта должны считаться одним адресом.
-- Тип: BEFORE INSERT OR UPDATE, ROW-level
-- ──────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION trg_normalize_user_email()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Нормализация: нижний регистр и удаление пробелов
    NEW.email := LOWER(TRIM(NEW.email));

    -- Проверка дубликата (кроме самой же записи при UPDATE)
    IF EXISTS (
        SELECT 1 FROM users
        WHERE email = NEW.email
          AND id IS DISTINCT FROM NEW.id
    ) THEN
        RAISE EXCEPTION 'Email "%" уже зарегистрирован в системе', NEW.email;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_user_email_normalize
    BEFORE INSERT OR UPDATE OF email ON users
    FOR EACH ROW
    EXECUTE FUNCTION trg_normalize_user_email();

-- Тест: нормализация
INSERT INTO users(last_name, first_name, email)
VALUES ('Тест', 'Триггер', '  TestTrigger@MAIL.RU  ');
SELECT email FROM users WHERE last_name = 'Тест' AND first_name = 'Триггер';
-- Ожидаем: testtrigger@mail.ru

-- Тест: дублирование (должна быть ошибка):
-- INSERT INTO users(last_name, first_name, email)
-- VALUES ('Другой', 'Юзер', 'TESTTRIGGER@mail.ru');


-- ──────────────────────────────────────────────────────────────
-- 5.4 AFTER UPDATE/DELETE: универсальный аудит изменений
-- (задание 3 из раздела триггеров — логирование)
--
-- Кейс: отслеживание кто и когда изменил статус заявки
-- или данные о протезе. Хранит: таблицу, атрибут, старое,
-- новое значение, дату.
-- Тип: AFTER UPDATE, ROW-level
-- ──────────────────────────────────────────────────────────────
-- Функция аудита для таблицы requests (отслеживает status_id)
CREATE OR REPLACE FUNCTION trg_audit_requests()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF OLD.status_id IS DISTINCT FROM NEW.status_id THEN
            INSERT INTO audit_log(table_name, column_name, old_value, new_value)
            VALUES ('requests', 'status_id', OLD.status_id::TEXT, NEW.status_id::TEXT);
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, column_name, old_value, new_value)
        VALUES ('requests', 'id', OLD.id::TEXT, NULL);
    END IF;

    RETURN NEW;
END;
$$;

-- Функция аудита для таблицы prostheses (отслеживает price)
CREATE OR REPLACE FUNCTION trg_audit_prostheses()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF OLD.price IS DISTINCT FROM NEW.price THEN
            INSERT INTO audit_log(table_name, column_name, old_value, new_value)
            VALUES ('prostheses', 'price', OLD.price::TEXT, NEW.price::TEXT);
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, column_name, old_value, new_value)
        VALUES ('prostheses', 'id', OLD.id::TEXT, NULL);
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_requests_audit
    AFTER UPDATE OR DELETE ON requests
    FOR EACH ROW
    EXECUTE FUNCTION trg_audit_requests();

CREATE TRIGGER trg_prostheses_audit
    AFTER UPDATE OR DELETE ON prostheses
    FOR EACH ROW
    EXECUTE FUNCTION trg_audit_prostheses();

-- Тест аудита:
UPDATE requests SET status_id = 2 WHERE id = 1;
UPDATE prostheses SET price = 460000 WHERE id = 1;
SELECT * FROM audit_log ORDER BY changed_at DESC;


-- ──────────────────────────────────────────────────────────────
-- 5.5 ALTER TABLE + каскадное удаление (задание 2 из раздела триггеров)
--
-- Кейс: при удалении пользователя автоматически удалять
-- все его назначенные роли (уже настроено ON DELETE CASCADE
-- при создании таблицы user_roles).
-- Демонстрируем добавление каскада через ALTER TABLE.
-- ──────────────────────────────────────────────────────────────

-- Сначала пересоздадим FK с каскадом (пример ALTER TABLE):
ALTER TABLE user_roles
    DROP CONSTRAINT IF EXISTS user_roles_user_id_fkey;

ALTER TABLE user_roles
    ADD CONSTRAINT user_roles_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Тест каскадного удаления:
INSERT INTO users(last_name, first_name, email) VALUES('Удалить','Меня','delete_me@test.ru');
INSERT INTO user_roles(user_id, role_id)
    VALUES((SELECT id FROM users WHERE email='delete_me@test.ru'), 4);

-- До удаления:
SELECT u.email, r.name AS role
FROM users u
JOIN user_roles ur ON ur.user_id = u.id
JOIN roles r ON r.id = ur.role_id
WHERE u.email = 'delete_me@test.ru';

-- Удалить пользователя → роль удалится каскадно:
DELETE FROM users WHERE email = 'delete_me@test.ru';

-- После удаления (должно быть пусто):
SELECT * FROM user_roles WHERE user_id NOT IN (SELECT id FROM users);


-- ============================================================
-- ИТОГОВЫЕ ПРОВЕРОЧНЫЕ ЗАПРОСЫ
-- ============================================================

-- Полная статистика по каталогу
SELECT type_name, COUNT(*) AS total, ROUND(AVG(price),0) AS avg_price
FROM vw_active_catalog
GROUP BY type_name ORDER BY avg_price DESC;

-- Все триггеры в схеме
SELECT trigger_name, event_manipulation, event_object_table, action_timing
FROM information_schema.triggers
WHERE trigger_schema = 'prosthetics'
ORDER BY event_object_table, trigger_name;

-- Все индексы в схеме
SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE schemaname = 'prosthetics'
ORDER BY tablename;

-- Журнал аудита
SELECT * FROM audit_log ORDER BY changed_at DESC LIMIT 20;
