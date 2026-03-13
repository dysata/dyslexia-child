# Note:
The list of words presented in the game1 is in `static/game1/scripts/game1words.js`. It is a short list of words (20) for demonstration. In real applications substitute this file with
`static/game1/scrits/game1words_full.js` (about 400 words):
```
nv static/game1/scripts/game1words_full.js static/game1/scripts/game1words.js
```

The same holds for other games too.

#TODO
- check saved word indices
- 

# SpeechSimulator

## Getting started

### Requirements
ffmpeg is required (install if missing: sudo apt install ffmpeg)

Other requirements are in requirements.txt, see below.

### Installing Python packages and starting the service

```
git clone .. 
cd speechsimulator
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python ./main.py
```

See help for command line arguments:
```
python ./main.py --help
```

Some settings can be also changed in config/config.yaml

### Audio Settings
You may wish to change audio quality parameters in static/game/js/client.js in two places (audio settings and sdp settings) according to 
        //https://stackoverflow.com/questions/46063374/is-it-really-possible-for-webrtc-to-stream-high-quality-audio-without-noise
TODO: move these settings to config/config.yaml, read them in app/settings.py

### Using the app

Navigate to http://localhost:8080/ (change the port number to what was set for the service) in your browser

Find stored wav files in storage/game

### To note
The service will download models (> 1 GB) at the first run.
-- this NN analysis is outcommented for now, is not used

In Russian
1) получение кода

1.1) распаковка из архива:
tar xjf game.tar.bz2

1.2) или клонирование репозитория
git clone --branch game репозиторий

2) Установка зависимостей

2.1) если отсутствует пакет ffmpeg в системе, может потребоваться установить:
sudo apt install ffmpeg

2.2) создание и активация виртуальной среды Python
cd speechsimulator
python3.10 -m venv .venv
source .venv/bin/activate

2.3) установка модулей Python
pip install -r requirements.txt

3) запуск сервиса
python main.py --port=8080
порт по умолчанию -- 8080

4) открываем приложение в браузере
http://<адрес сервера>:8080

интерфейс предлагает на выбор 3 "игры", в 1 и 2 играх имеется возможность выбрать список для здоровых ("базовый вариант") и для дислексиков:

1. Называние слов по тексту и картинкам: базовый вариант | дислексия
2. Называние слов по тексту и картинкам, различение живое/неживое: базовый вариант | дислексия
3. Тренировка слоги-слова-фразы: перейти

Далее инструкции даны на соответствующих страницах по ссылкам.

5) Настройка заданий

5.1) игра 1, базовый вариант (game1):

5.1.1) список слов находится в файле static/game1/scripts/game1words.js, индекс слова определяется порядком в списке, нумерация начинается с 0.

5.1.2) список слов, для которых имеются изображения: static/game1/scripts/game1images.js

5.1.3) файлы с изображениями согласно списку 5.1.2 должны быть размещены в static/game1/images, название файлов -- <номер слова в списке 5.1.1>.jpg

5.2) игра 1, вариант для дислексиков (game1d), структурно все так же, список слов -- тот же, что в 5.1, потому что другого нет -- нужно заменить.

5.2.1) список слов находится в файле static/game1d/scripts/game1dwords.js, индекс слова определяется порядком в списке, нумерация начинается с 0. 

5.2.2) список слов, для которых имеются изображения: static/game1d/scripts/game1dimages.js

5.2.3) файлы с изображениями согласно списку 5.2.2 должны быть размещены в static/game1d/images, название файлов -- <номер слова в списке 5.2.1>.jpg

5.3) игра 2, базовый вариант (game2) -- все аналогично в static/game2

5.4) игра 2, вариант для дислексиков (game2d) -- все аналогично в static/game2d

5.5) игра 3 (game3)
в файле static/game3/scripts/game3tasks.js
можно задать массив из нескольких упражнений. Каждое упражнение -- это массив из трех списков: слоги, слова, фразы.

6) Сохранение результатов
Результаты сохраняются в виде wav и json (метаданные) файлов в каталоге storage в подкаталогах игр.
В играх 1,1d,2,2d в названии файла присутствует индекс слова в массиве слов и признак - что предъявлялось: картинка или слово. В игре 3 название файла начинается с номера упражнения и номера шага (0 - слоги, 1 - слова, 2 - фразы). Полная информация -- в соответствующих json файлах.

7) Инструкции испытуемым

7.1) Общее

Нужно проинструктировать испытуемых, чтобы не нажимали кнопки до того, как полностью произнесут слово, иначе  обрезается запись. Вставлена небольшая задержка в переходах между заданиями для защиты от этого.

7.2) По игре 3
В начале игры нужно выбрать номер упражнения из списка, в настоящее время есть 2 упражнения (см. п. 5.5), нумерация с 0: упражнения 0 и 1.

8) Качество аудио
Можно экспериментировать с параметрами audio и sdp в файлах *upoad.js

