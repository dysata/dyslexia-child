# dyslexia-telegrambot

## Установка с помощью docker compose

1. В dyslexia-data/apps.js вписать актуальный токен телеграм бота (см. как получить в [документации Telegram](https://core.telegram.org/bots/features#botfather)), заменить при необходимости логины и пароли сервисов couchdb, nextcloud, согласовать с настройками в docker-compose.yml, dyslexia-data/Dockerfile 

2. Собрать docker-образ приложения dyslexia-data, скачать образы других контейнеров с сервисами nextcloud, mariadb, couchdb, mongodb, запустить контейнеры. Для этого выполнить команду (от имени пользователя, если он в докер-группе или от рута):

docker compose up --build -d

3. Завершить настройку couchdb

Согласно [инструкции](https://docs.couchdb.org/en/stable/setup/single-node.html) донастроить couchdb: нужно пройти по ссылке в раздел WebGUI CouchDB и ввести логин и пароль (как установлено было выше): [http://127.0.0.1:5984/_utils/#setup](http://127.0.0.1:5984/_utils/#setup).

Далее нужно создать базу данных 'dyslexia', а затем созать view (перейти на страницу базы в WebGUI и в меню выбрать Design Documents -> New View или воспользоваться прямой [ссылкой](http://127.0.0.1:5984/_utils/#/database/dyslexia/new_view). В базе данных dyslexia будут содержаться дескрипторы задач для пользователей (human tasks) и метаданные собираемых и размечаемых аудиофайлов, сами аудиофайлы сохраняются в облачном хранилище NextCloud.

Параметры view:

design document: _design/dyslexia
index name: human_tasks
map function:

```
function (doc) {
  if(doc.human_task) {
    emit(doc.human_task.task_series_id, doc);
  }
}
```
4. Завершить настройку NextCloud

Открыть WebGUI NextCloud по [ссылке](http://localhost:8080), настроить логин и пароль, как было выбрано выше. На облачном диске NextCloud создать папку dyslexia: в ней будут размещаться все аудиофайлы.

В конфигурационном файле NextCloud (обычно /var/lib/docker/volumes/distrib_nextcloud/_data/config/config.php) необходимо добавить параметр "trusted_domains":

```
  'trusted_domains' =>
  array (
          0 => 'localhost',
          1 => 'nextcloud',
          2 => 'dyslexia-data',
  ),
```

5. Перезапустить контейнеры

docker compose down
docker compose up --build -d
docker ps -a

6. Работа с сервисом

Перейдите по [ссылке](http://localhost:3000). Пройдите аутентификацию: пароль и логин по умолчанию -- user, password. Перейдите по ссылке "Все виджеты" (Widgets) и действуйте согласно большой инструкции к сервису.

7. Замечания об аутентификации пользователей сервиса

Реализован простейший вариант аутентификации при котором список пользователей непосредственно задан в файле dyslexia-data/app.js. При необходимости следует заменить этот механизм на какое-либо промышленное решение.

8. Развертывание сервиса в Интернете, удаленный доступ

Скрипты *.js, *.py в dyslexia-data рассчитывают, что сервис отвечает по адресу http://localhost:3000. Если требуется развернуть сервис на удаленной машине для доступа по сети, ввести SSL, то в этих файлах нужно исправить http://localhost:3000 на соответствующий адрес. Также рекомендуется, как обычно, укрыть сервис за полноценным HTTP-сервером (nginx, Apache, ...).

9. Утилиты dyslexia-data/utils
Для работы утилит нужно установить python3. Далее применять по инструкции. Например, скачать все аудиофайлы с метаданными в каталог d:  

python3 ./download.py -password password -login user d

# Manual Installation (no docker)

Install couchdb: https://docs.couchdb.org/en/stable/install/unix.html

Set admin password, change default password 'couchdbadmin' in the code to your password.

Open CouchDB Web-GUI, usually:

http://localhost:5984/_utils

Create database 'dyslexia'. Create view: 

design document: _design/dyslexia
index name: human_tasks
map function:

```
function (doc) {
  if(doc.human_task) {
    emit(doc.human_task.task_series_id, doc);
  }
}
```

Install nextcloud: https://docs.nextcloud.com/server/latest/admin_manual/installation/example_ubuntu.html

Завершите настройку в Web-GUI, обычно http://localhost/nextcloud (если путь другой, замените путь в коде сервиса):
установите логин и пароль (и замените в коде пароли по умолчанию 'nextclouduser', 'nextcloudpassword'), создайте в корневой папке пользователя каталог dyslexia, куда будут сохраняться файлы.

Install Node.js

Recommended: use node version manager https://github.com/nvm-sh/nvm

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install node

# install modules and run service:

git clone .. or tar xzf ... -- get and unpack the codes

cd dyslexia-data
npm install

DEBUG=dyslexia-data:* npm start

or just
npm start


then navigate to http://localhost:3000 in your browser and follow the documentation on the service



