# dyslexia-telegrambot

# prerequisites

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



