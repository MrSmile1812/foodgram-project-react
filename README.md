# Проект Foodgram
### Описание проекта:

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.


### Стек технологий:
- Python 3.9
- Django 4.2.2
- Django Rest Framework
- Docker
- Nginx
- Gunicorn
- PostgreSQL

### Развернуть проект на удаленном сервере:
- Клонировать репозиторий:
```
https://github.com/MrSmile1812/foodgram-project-react
```
- Установить на сервере Docker, Docker Compose:
```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```
- Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):
```
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```
- Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

POSTGRES_DB             # django
POSTGRES_USER           # django_user
POSTGRES_PASSWORD       # mysecretpassword
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```
- Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):
```
sudo docker compose -f docker-compose.production.yml up -d
```
- Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```
- Наполнить базу данных содержимым из файла ingredients.json:
```
sudo docker compose exec backend python manage.py load_ingredients_data
```
- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

### После каждого обновления репозитория (push в ветку master) будет происходить:
1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend и backend на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

Проект доступен по ссылке: https://myfoodgram.ddnsking.com
- Данные админа:
Почта: prokofev987@yandex.ru
Пароль: 11119999!

### Запуск проекта на локальной машине:
- Клонировать репозиторий:
```
https://github.com/MrSmile1812/foodgram-project-react
```
- В директории infra файл example.env переименовать в .env и заполнить своими данными:
```
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
DEBUG=True
ALLOWED_HOSTS=84.201.177.135,backend,localhost,127.0.0.1
```
- Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, созданию суперпользователя, как указано выше.
```
docker-compose -f docker-compose-local.yml up -d
```
- После запуска проект будут доступен по адресу: http://localhost/
- Документация будет доступна по адресу: http://localhost/api/docs/

### Автор
George Prokofev (MrSmile1812)


