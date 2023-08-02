# praktikum_new_diplom


### О проекте:

Позволяет создавать, редактировать, смотреть рецепты.

Указывать их ингредиенты, теги, время приготовления, прикреплять фотографию.

### Как запустить проект без докера:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:MakarochkinIA/foodgram-project-react.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Как запустить проект используя докер:

В разработке

### Примеры запросов к API:

GET, POST /api/users/

GET, POST /api/recipes/
GET, PATCH, DELETE  /api/recipes/{recipe_id}/

### Основные используемые технологии:
GIT
Docker

--backend--
Python
Django
Django REST Framework

--frontend--
JavaScript
React

### Информация об авторе:
Код фронтенда - Яндекс.Практикум
Код бэкенда  - Илья Макарочкин
