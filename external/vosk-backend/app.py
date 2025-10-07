import os
import librosa
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import shutil
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import soundfile as sf
import uuid


app = Flask(__name__)
CORS(app)

# Папка для сохранения загруженных файлов
UPLOAD_FOLDER_BASE = 'uploads'
os.makedirs(UPLOAD_FOLDER_BASE, exist_ok=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Папка с правильными и неправильными аудио для обучения модели
correct_dir = 'dataset/correct'
incorrect_dirs = ['dataset/incorrect', 'dataset/incorrect_augmented']

# Загрузка модели Wav2Vec2 для распознавания
model_name = "bond005/wav2vec2-large-ru-golos-with-lm"
model = Wav2Vec2ForCTC.from_pretrained(model_name)
processor = Wav2Vec2Processor.from_pretrained(model_name)

# Функция для извлечения MFCC из аудиофайла
def extract_mfcc(audio_path, n_mfcc=13, n_fft=1024):
    audio, sr = librosa.load(audio_path, sr=None)  # Загружаем аудио без изменения частоты дискретизации
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft)
    mfcc_mean = np.mean(mfcc, axis=1)  # Берем среднее значение по времени
    return mfcc_mean

# Функция для извлечения временных меток для буквы "р"
def extract_r_fragments(audio_path, output_dir):
    audio, rate = librosa.load(audio_path, sr=16000)  # Приведение к 16kHz

    # Подготовка входных данных
    input_values = processor(audio, return_tensors="pt", sampling_rate=rate).input_values

    # Получение логитов модели
    with torch.no_grad():
        logits = model(input_values).logits  # (batch_size, sequence_length, vocab_size)

    # Применяем Softmax для получения вероятностей и находим индексы максимальных значений
    predicted_ids = torch.argmax(logits, dim=-1).squeeze().tolist()

    # Получение карты символов
    vocab = processor.tokenizer.get_vocab()
    id_to_char = {v: k.replace("|", " ") for k, v in vocab.items()}  # Преобразуем в символы

    # Вычисляем временные метки
    time_stamps = np.linspace(0, len(audio) / rate, logits.shape[1])  # Временные метки для каждого логита

    # Список для хранения результатов (буква, начало, конец)
    decoded_output = []

    for i in range(len(predicted_ids) - 1):
        char_id = predicted_ids[i]
        char = id_to_char.get(char_id, "")

        if char and char != processor.tokenizer.pad_token:  # Исключаем пробелы и пустые символы
            start_time = time_stamps[i]
            end_time = time_stamps[i + 1]
            decoded_output.append((char, start_time, end_time))

    # Обрезка и сохранение фрагментов с буквой "р"
    os.makedirs(output_dir, exist_ok=True)
    fragments = []
    for idx, (char, start, end) in enumerate(decoded_output):
        if char.lower() == 'р':  # Проверка на букву "р"
            # Обрезка и сохранение фрагмента
            start_sample = int(start * rate)
            end_sample = int(end * rate)

            fragment = audio[start_sample:end_sample]
            output_path = os.path.join(output_dir, f"fragment_{idx}_р.wav")
            sf.write(output_path, fragment, rate)
            fragments.append(output_path)
            logger.info(f"Сохранен фрагмент: {output_path}")

    return fragments

# Функция для обработки всех файлов в папке и получения признаков
def process_folder(folder_path, label, mfccs, labels):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".wav"):
            file_path = os.path.join(folder_path, file_name)
            mfcc_features = extract_mfcc(file_path)
            mfccs.append(mfcc_features)
            labels.append(label)

# Список для хранения MFCC и меток
mfccs = []
labels = []

# Обработка правильных аудио
process_folder(correct_dir, 1, mfccs, labels)  # Метка 1 для правильных

# Обработка неправильных аудио
for incorrect_dir in incorrect_dirs:
    process_folder(incorrect_dir, 0, mfccs, labels)  # Метка 0 для неправильных

# Преобразуем список в массивы NumPy
mfccs = np.array(mfccs)
labels = np.array(labels)

# Масштабируем данные
scaler = StandardScaler()
mfccs_scaled = scaler.fit_transform(mfccs)

# Обучение классификатора Random Forest
clf = RandomForestClassifier(n_estimators=1000, random_state=42)
clf.fit(mfccs_scaled, labels)

# Папка для сохранения загруженных файлов
os.makedirs(UPLOAD_FOLDER_BASE, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    logger.info("Received a request")

    if 'file' not in request.files:
        logger.error("No file provided in the request")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        logger.error("No selected file in the request")
        return jsonify({"error": "No selected file"}), 400

    # Создаем уникальную папку для данного запроса
    unique_folder = os.path.join(UPLOAD_FOLDER_BASE, str(uuid.uuid4()))
    os.makedirs(unique_folder)

    try:
        # Генерируем путь для сохранения файла
        file_path = os.path.join(unique_folder, file.filename)
        file.save(file_path)
        logger.info(f"File saved successfully at {file_path}")

        # Извлекаем фрагменты с буквой "р"
        fragments = extract_r_fragments(file_path, unique_folder)

        if not fragments:
            predicted_label = 'incorrect'
            logger.info(f"No 'р' fragments found. Classifying as incorrect.")
            shutil.rmtree(unique_folder)  # Удаляем временные данные
            return jsonify({"message": "File processed successfully", "results": predicted_label}), 200


        results = []
        for fragment_path in fragments:
            mfcc_features = extract_mfcc(fragment_path)
            mfcc_features_scaled = scaler.transform([mfcc_features])
            prediction = clf.predict(mfcc_features_scaled)
            predicted_label = 'correct' if prediction[0] == 1 else 'incorrect'
            results.append({"fragment": fragment_path, "prediction": predicted_label})

        logger.info(f"Prediction results: {results}")
        return jsonify({"message": "File processed successfully", "results": results}), 200

    except Exception as e:
        logger.error(f"Error while processing the file: {str(e)}")
        return jsonify({"error": "File could not be processed"}), 500
    finally:
        # Удаляем временную папку после завершения обработки
        shutil.rmtree(unique_folder, ignore_errors=True)


if __name__ == '__main__':
    app.run(debug=True)
