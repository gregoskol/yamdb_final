[![Django-app workflow](https://github.com/gregoskol/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/gregoskol/yamdb_final/actions/workflows/yamdb_workflow.yml)
# API YaMDb
## _Проект для обмена данными с сервисом YaMDb через API_
## Описание:
Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»).
Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

## Подготовка к установке:
Клонировать репозиторий:
```sh
git clone git@github.com:gregoskol/yamdb_final.git
```
Подключиться к удаленному серверу:
```sh
ssh <USER>@<HOST>
```
Установить docker и docker-compose:
```sh
sudo apt install docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
Скопировать файлы docker-compose.yaml, nginx/default.conf из проекта на сервер в home/<USER>/docker-compose.yaml и home/<USER>/nginx/default.conf соответственно
```sh
scp ./<FILENAME> <USER>@<HOST>:/home/<USER>/...
```
Добавить в Secrets GitHub Actions переменные окружения (пример в infra/.env.sample), а также:
*DOCKER_USERNAME, DOCKER_PASSWORD  - логин и пароль с DockerHub
*USER, HOST, PASSPHRASE, SSH_KEY - имя пользователя, пароль, ключ SSH и ip удаленного сервера
*TELEGRAM_TO, TELEGRAM_TOKEN - токены чата и бота в Telegram

## Установка:
При пуше в ветку main запустится Workflow:
*Проверка кода на соответствие PEP8
*Проверка pytest
*Сборка и пуш образов на Docker Hub
*Деплой проекта на сервер
*Уведомление в Telegram об успешном завершении Workflow
После завершения Workflow:
Подключиться к удаленному серверу:
```sh
ssh <USER>@<HOST>
```
Собрать статические файлы:
```sh
docker-compose exec web python manage.py collectstatic --no-input
```
Выполнить миграции:
```sh
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate --noinput
```
Создать суперпользователя:
```sh
docker-compose exec web python manage.py createsuperuser
```