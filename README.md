# Проект Blogicum

## Возможности проекта
- Пользователь может создать свою страницу и сделать публикацию по определённой тематике.
- Для каждого поста существует категория — например «путешествия», «кулинария» или «python-разработка», а также опционально можно указать
локацию, с которой связан пост. 
- Пользователь может перейти на страницу любой категории и 
увидеть все посты, которые к ней относятся. 
- Пользователи могут заходить на чужие страницы, читать 
и комментировать чужие посты. 
- Для своей страницы автор может задать имя и уникальный адрес.
- Есть возможность модерировать записи и блокировать пользователей,
рассылающих спам.

##  Технологии
- Python 
- Django
- DRF

## Установка и запуск

**💡 ВЕРСИЯ Python3.9**

Клонировать репозиторий:
```
git clone <https or SSH URL>
```

Перейти в папку проекта:
```
cd django_sprint4
```
Создать и активировать виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
Обновить pip:
```
python3 -m pip install --upgrade pip
```
Установить библиотеки:
```
pip install -r requirements.txt
```

Выполнить миграции:
```
python3 blogicum/manage.py migrate
```

Загрузить фикстуры DB:
```
python3 blogicum/manage.py loaddata db.json
```

Создать суперпользователя:
```
python3 blogicum/manage.py createsuperuser
```

Запустить сервер django:
```
python3 blogicum/manage.py runserver
```