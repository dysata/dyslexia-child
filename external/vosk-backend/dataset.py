from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa
import numpy as np
import soundfile as sf
import os

# Параметры
input_dir = "D:/неправильные р"
model_name = "bond005/wav2vec2-large-ru-golos-with-lm"
output_dir = "dataset/incorrect"

# Загрузка модели и процессора
model = Wav2Vec2ForCTC.from_pretrained(model_name)
processor = Wav2Vec2Processor.from_pretrained(model_name)

# Процесс обработки каждого аудиофайла из папки
for audio_filename in os.listdir(input_dir):
    audio_path = os.path.join(input_dir, audio_filename)

    # Проверяем, что это аудиофайл (например, .wav)
    if audio_filename.endswith(".wav"):
        print(f"Обрабатываем файл: {audio_filename}")

        # Загрузка аудиофайла
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
        for idx, (char, start, end) in enumerate(decoded_output):
            if char.lower() == 'р':  # Проверка на букву "р"
                # Обрезка и сохранение фрагмента
                start_sample = int(start * rate)
                end_sample = int(end * rate)

                fragment = audio[start_sample:end_sample]
                output_path = os.path.join(output_dir, f"{audio_filename}_fragment_{idx}_р.wav")
                sf.write(output_path, fragment, rate)
                print(f"Сохранен фрагмент: {output_path}")