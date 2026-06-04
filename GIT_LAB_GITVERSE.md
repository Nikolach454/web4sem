# Лабораторная работа: Продвинутый GIT
## Инструкция по выполнению на реальном репозитории

> Репозиторий: https://github.com/Nikolach454/web4sem
> Ветка: master
> Папка проекта: `c:\Users\User\Desktop\веб 4 сем`

Все команды выполнять в **терминале VS Code** (`Ctrl+\``) или **PowerShell** в папке проекта.

---

## Часть 1 — Конспект и демонстрация команд

---

### 1) Устройство рабочего каталога, индекса, репозитория, HEAD и веток

**Конспект:**

Git работает с тремя областями:

| Область | Где находится | Что содержит |
|---------|--------------|--------------|
| **Working directory** (рабочий каталог) | Папка проекта | Реальные файлы на диске |
| **Index / Staging area** (индекс) | `.git/index` | Снимок файлов, подготовленных к коммиту |
| **Repository** (репозиторий) | `.git/objects/` | История всех коммитов в виде объектов |

- **HEAD** — указатель на текущий коммит или ветку. Хранится в `.git/HEAD`
- **Ветка** — файл в `.git/refs/heads/` с хэшем последнего коммита
- Путь изменений: `рабочий каталог → git add → индекс → git commit → репозиторий`

**Демонстрация:**
```bash
git status
```

---

### 2) Файл .gitignore

**Конспект:**
Файл `.gitignore` содержит шаблоны путей, которые Git не отслеживает.
Применяется для временных файлов, секретов, артефактов сборки.

Синтаксис:
- `*.log` — все файлы с расширением .log
- `build/` — папка build
- `!important.log` — исключение из правила
- `#` — комментарий

**Демонстрация:**
```bash
# Посмотреть текущий .gitignore
cat .gitignore

# Создать тестовый файл
echo "DB_PASSWORD=secret" > secret.txt

# Добавить в gitignore
echo "secret.txt" >> .gitignore

# Убедиться что файл игнорируется
git status
# secret.txt не появится в untracked files

# Проверить почему игнорируется
git check-ignore -v secret.txt

# Откатить изменения .gitignore
git checkout -- .gitignore
rm secret.txt
```

---

### 3) Переход к конкретному коммиту: `git checkout <hash>`

**Конспект:**
`git checkout <hash>` переводит в **detached HEAD** — HEAD указывает на коммит напрямую, а не на ветку. Используется для просмотра старого состояния кода.

**Демонстрация:**
```bash
# Посмотреть хэши коммитов
git log --oneline
# db9a019 Initial commit: Django web project (веб 4 сем)
# 0e5b7bd делаю

# Перейти к первому коммиту
git checkout db9a019

# HEAD is now at db9a019 (detached HEAD)
cat .git/HEAD
# Вывод: db9a019... (хэш напрямую)

# Вернуться на ветку master
git checkout master
```

---

### 4) Переход на другую ветку: `git checkout <branch>`, `git switch <branch>`

**Конспект:**
- `git checkout <branch>` — классическая команда
- `git switch <branch>` — современная альтернатива (Git 2.23+), только для веток
- `git switch -c <новая_ветка>` — создать и переключиться

**Демонстрация:**
```bash
# Создать ветку
git branch feature/test-branch

# Переключиться через checkout
git checkout feature/test-branch

# Вернуться
git checkout master

# Переключиться через switch
git switch feature/test-branch
git switch master

# Создать и сразу переключиться
git switch -c feature/another-test
git switch master

# Убрать тестовые ветки
git branch -d feature/test-branch
git branch -d feature/another-test
```

---

### 5) Отмена изменений через новый коммит: `git revert <hash>`

**Конспект:**
`git revert` создаёт **новый коммит**, отменяющий изменения указанного. Безопасен для общей истории — не переписывает прошлые коммиты.

**Демонстрация:**
```bash
# Создать коммит который потом отменим
echo "# тест revert" > revert_test.txt
git add revert_test.txt
git commit -m "Добавить revert_test.txt (будет отменён)"

git log --oneline -3

# Отменить последний коммит без открытия редактора
git revert HEAD --no-edit

# Файл исчез, но оба коммита видны в истории
git log --oneline -4
```

---

### 6) Режимы `--soft` и `--hard` для `git reset`

**Конспект:**

| Режим | Коммит | Индекс | Рабочий каталог |
|-------|--------|--------|-----------------|
| `--soft` | Отменяет | Сохраняет | Сохраняет |
| `--mixed` (по умолчанию) | Отменяет | Сбрасывает | Сохраняет |
| `--hard` | Отменяет | Сбрасывает | **Сбрасывает** |

**Демонстрация:**
```bash
# --- --soft ---
echo "soft test" > soft_test.txt
git add soft_test.txt
git commit -m "Тест --soft"

# Откатить коммит, изменения остаются в индексе
git reset --soft HEAD~1
git status
# Вывод: Changes to be committed: new file: soft_test.txt

git restore --staged soft_test.txt
rm soft_test.txt

# --- --hard ---
echo "hard test" > hard_test.txt
git add hard_test.txt
git commit -m "Тест --hard"

# Полный сброс — файл исчезнет
git reset --hard HEAD~1
git status
# Рабочий каталог чист, файл удалён
```

---

### 7) Изменить сообщение последнего коммита: `git commit --amend`

**Конспект:**
`git commit --amend` изменяет последний коммит — его сообщение и/или содержимое. Создаёт новый коммит с новым хэшем. Не использовать для уже запушенных коммитов.

**Демонстрация:**
```bash
# Создать коммит с опечаткой
echo "amend test" > amend_test.txt
git add amend_test.txt
git commit -m "Добавить amend_test.tx"

# Исправить сообщение
git commit --amend -m "Добавить amend_test.txt"

# Проверить
git log --oneline -3

# Также можно добавить забытые файлы
echo "доп. изменение" >> amend_test.txt
git add amend_test.txt
git commit --amend --no-edit

# Убрать тестовый коммит
git reset --hard HEAD~1
```

---

### 8) Содержимое HEAD: `cat .git/HEAD`

**Конспект:**
`.git/HEAD` содержит либо ссылку на ветку (`ref: refs/heads/master`), либо прямой хэш коммита (detached HEAD).

**Демонстрация:**
```bash
# На ветке
cat .git/HEAD
# Вывод: ref: refs/heads/master

# В detached HEAD
git checkout db9a019
cat .git/HEAD
# Вывод: db9a019... (полный хэш)

# Вернуться
git checkout master
cat .git/HEAD
# Снова: ref: refs/heads/master
```

---

### 9) Куда указывает ветка: `cat .git/refs/heads/master`

**Конспект:**
Каждая ветка — текстовый файл в `.git/refs/heads/` с хэшем последнего коммита. При новом коммите файл обновляется.

**Демонстрация:**
```bash
# Хэш последнего коммита ветки master
cat .git/refs/heads/master

# Сравнить с git log
git log --oneline -1
# Хэши совпадают

# Создать ветку и посмотреть её файл
git branch demo-branch
cat .git/refs/heads/demo-branch
# Тот же хэш что и master

git branch -d demo-branch
```

---

### 10) Команда `git log --oneline`

**Конспект:**
`git log` показывает историю коммитов. `--oneline` сжимает до одной строки: `короткий_хэш сообщение`.

**Демонстрация:**
```bash
# Базовый вывод
git log --oneline

# С ветками и тегами
git log --oneline --decorate

# Граф всех веток
git log --oneline --graph --all

# Последние 5 коммитов
git log --oneline -5

# Поиск по сообщению
git log --oneline --grep="Initial"

# По автору
git log --oneline --author="Nikolach454"
```

---

### 11) Команды `git diff` и `git diff <hash>`

**Конспект:**
- `git diff` — рабочий каталог vs индекс
- `git diff --staged` — индекс vs последний коммит
- `git diff <hash1> <hash2>` — между двумя коммитами

**Демонстрация:**
```bash
# Внести изменение
echo "# тест diff" >> manage.py

# Diff рабочего каталога
git diff

# Добавить в индекс
git add manage.py

# Diff индекса vs коммит
git diff --staged

# Diff между двумя коммитами (использовать реальные хэши)
git diff db9a019 0e5b7bd

# Diff конкретного файла
git diff db9a019 HEAD -- manage.py

# Откатить
git restore --staged manage.py
git restore manage.py
```

---

### 12) Команда `git rm --cached <файл>`

**Конспект:**
`git rm --cached` удаляет файл из индекса (Git перестаёт отслеживать), но оставляет на диске. После — добавить в `.gitignore`.

**Демонстрация:**
```bash
# Создать файл который случайно попал в репозиторий
echo "DB_PASSWORD=secret123" > .env
git add .env
git commit -m "Случайно добавить .env"

# Убрать из отслеживания
git rm --cached .env
# Файл остался на диске
ls .env

# Добавить в .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Убрать .env из отслеживания"

# Убрать тестовые данные
rm .env
git reset --hard HEAD~2
```

---

### 13) Команда `git stash`

**Конспект:**
`git stash` временно прячет незакоммиченные изменения в стек, возвращая рабочий каталог к чистому состоянию. Удобно для срочного переключения веток.

**Демонстрация:**
```bash
# Сделать незакоммиченное изменение
echo "# незаконченная работа" >> manage.py

# Спрятать с названием
git stash push -m "незаконченная работа в manage.py"

# Каталог чист
git status

# Посмотреть список
git stash list
# stash@{0}: On master: незаконченная работа в manage.py

# Ещё один stash
echo "другое изменение" >> requirements.txt
git stash push -m "изменения в requirements"

git stash list

# Восстановить последний и удалить из стека
git stash pop

# Восстановить конкретный без удаления
git stash apply stash@{0}

# Создать ветку из stash
git stash branch feature/from-stash stash@{0}
git switch master

# Очистить
git stash clear
git restore manage.py requirements.txt
git branch -d feature/from-stash 2>/dev/null || true
```

---

### 14) Восстановление удалённого коммита: `git reflog`

**Конспект:**
`git reflog` — журнал всех перемещений HEAD. Коммиты хранятся ~30 дней даже после `reset --hard`. Через reflog можно найти хэш «потерянного» коммита.

**Демонстрация:**
```bash
# Создать коммит
echo "важный код" > important.txt
git add important.txt
git commit -m "Важный коммит который удалим"

# Потерять через reset --hard
git reset --hard HEAD~1

# important.txt удалён
git log --oneline

# Найти потерянный коммит
git reflog
# Найти строку: commit: Важный коммит который удалим

# Вариант 1: вернуть ветку master к потерянному коммиту
git reset --hard <хэш_из_reflog>

# Вариант 2: создать новую ветку с восстановленным коммитом
git switch -c recovered <хэш_из_reflog>
git switch master

# Вариант 3: восстановить только файл
git restore --source=<хэш_из_reflog> important.txt

# Убрать тестовые данные
git reset --hard HEAD~1 2>/dev/null || true
git branch -d recovered 2>/dev/null || true
rm important.txt 2>/dev/null || true
```

---

### 15) Команда `git cherry-pick`

**Конспект:**
`git cherry-pick <hash>` применяет изменения конкретного коммита другой ветки к текущей, создавая новый коммит с теми же изменениями.

**Демонстрация:**
```bash
# Создать ветку с полезным коммитом
git switch -c feature/cherry

echo "def useful_function(): pass" > useful.py
git add useful.py
git commit -m "Добавить useful_function"

# Запомнить хэш этого коммита
git log --oneline -2

# Вернуться на master
git switch master

# Применить только один коммит с feature/cherry
git cherry-pick <хэш_первого_коммита>

# Проверить
git log --oneline -3

# Убрать тестовые данные
git reset --hard HEAD~1
git branch -d feature/cherry
rm useful.py 2>/dev/null || true
```

---

### 16) Объединение нескольких коммитов в один (squash)

**Конспект:**
Squash — слияние нескольких коммитов в один для чистоты истории.
- `git reset --soft HEAD~N` + `git commit` — быстрый способ
- `git rebase -i HEAD~N` — интерактивный (pick/squash/fixup)
- `git merge --squash <branch>` — при слиянии ветки

**Демонстрация:**
```bash
# Создать несколько мелких коммитов
echo "строка 1" > squash_test.txt && git add . && git commit -m "Добавить строку 1"
echo "строка 2" >> squash_test.txt && git add . && git commit -m "Добавить строку 2"
echo "строка 3" >> squash_test.txt && git add . && git commit -m "Добавить строку 3"

git log --oneline -5

# --- Способ 1: reset --soft ---
git reset --soft HEAD~3
git commit -m "Добавить squash_test.txt (три строки)"
git log --oneline -3

# --- Способ 2: merge --squash ---
git switch -c feature/squash-demo
echo "d" >> squash_test.txt && git add . && git commit -m "добавить d"
echo "e" >> squash_test.txt && git add . && git commit -m "добавить e"
git switch master
git merge --squash feature/squash-demo
git commit -m "Все изменения feature/squash-demo одним коммитом"
git branch -d feature/squash-demo

# Убрать тестовые данные
git reset --hard HEAD~2
rm squash_test.txt 2>/dev/null || true
```

---

### 17) Перенос коммитов: `git rebase --onto`

**Конспект:**
`git rebase --onto <новая_база> <старая_база> <ветка>` переносит коммиты ветки на новое основание.

```
До:  A - B - C (master)
          \
           D - E (feature)

После rebase --onto master B feature:
A - B - C (master)
         \
          D - E (feature)
```

**Демонстрация:**
```bash
# Создать базовую ветку
git switch -c base-branch
echo "base work" > base.txt
git add base.txt
git commit -m "Работа в base-branch"

# Создать feature от base-branch
git switch -c feature/onto-demo
echo "feature 1" > feature1.txt && git add . && git commit -m "Фича 1"
echo "feature 2" > feature2.txt && git add . && git commit -m "Фича 2"

# Перенести feature прямо на master (минуя base-branch)
git rebase --onto master base-branch feature/onto-demo

git log --oneline --graph --all

# Убрать тестовые данные
git switch master
git branch -d base-branch
git branch -d feature/onto-demo
rm base.txt feature1.txt feature2.txt 2>/dev/null || true
```

---

### 18) Команда `git blame`

**Конспект:**
`git blame <файл>` показывает для каждой строки: хэш коммита, автора, дату последнего изменения. Используется для поиска автора конкретного кода.

**Демонстрация:**
```bash
# Посмотреть кто написал каждую строку manage.py
git blame manage.py

# Только строки 1-10
git blame -L 1,10 manage.py

# Игнорировать пробельные изменения
git blame -w manage.py

# Blame на конкретном коммите
git blame db9a019 -- manage.py
```

---

### 19) Команда `git bisect`

**Конспект:**
`git bisect` выполняет **бинарный поиск** по истории для нахождения коммита, сломавшего что-то. Указываете «хороший» и «плохой» коммит — Git переключается на середину, вы говорите `good`/`bad`.

**Демонстрация:**
```bash
# Создать историю с «поломанным» коммитом
echo "version 1" > bisect_test.txt && git add . && git commit -m "bisect v1 - OK"
echo "version 2" > bisect_test.txt && git add . && git commit -m "bisect v2 - OK"
echo "BROKEN"    > bisect_test.txt && git add . && git commit -m "bisect v3 - BROKEN"
echo "version 4" > bisect_test.txt && git add . && git commit -m "bisect v4 - OK"

git log --oneline -5

# Начать поиск
git bisect start

# Текущий коммит плохой
git bisect bad HEAD

# Первый коммит хороший (использовать реальный хэш)
git bisect good db9a019

# Git переключится на середину — проверить файл
cat bisect_test.txt

# Если нормально:
git bisect good

# Если сломано:
git bisect bad

# Git найдёт виновный коммит и покажет его

# Завершить bisect
git bisect reset

# Убрать тестовые данные
git reset --hard HEAD~4
rm bisect_test.txt 2>/dev/null || true
```

---

## Часть 2 — Пуш изменений на GitHub

```bash
# Убедиться что всё чисто
git status
git log --oneline

# Запушить на GitHub
git push origin master
```

---

## Советы по скриншотам

Для каждого пункта снимать так, чтобы были видны:
1. Выполненная команда
2. Её вывод в терминале
3. Дополнительно: `git log --oneline` или `git status` после изменений

Использовать **встроенный терминал VS Code** (`Ctrl+\``) — он хорошо читается на скриншотах.

---

## Шпаргалка — все команды подряд

```
cat .git/HEAD                        # пп. 8
cat .git/refs/heads/master           # пп. 9
git status                           # пп. 1
git log --oneline --graph --all      # пп. 10
git diff / git diff --staged         # пп. 11
git checkout <hash>                  # пп. 3
git checkout master                  # пп. 3
git switch -c branch                 # пп. 4
git revert HEAD --no-edit            # пп. 5
git reset --soft HEAD~1              # пп. 6
git reset --hard HEAD~1              # пп. 6
git commit --amend -m "сообщение"    # пп. 7
git rm --cached файл                 # пп. 12
git stash push -m "название"         # пп. 13
git stash list / pop / apply         # пп. 13
git reflog                           # пп. 14
git reset --hard <hash>              # пп. 14
git switch -c recovered <hash>       # пп. 14
git cherry-pick <hash>               # пп. 15
git reset --soft HEAD~N              # пп. 16
git rebase -i HEAD~N                 # пп. 16
git rebase --onto master base feat   # пп. 17
git blame -L 1,20 файл               # пп. 18
git bisect start/good/bad/reset      # пп. 19
git push origin master               # пп. 2
```
