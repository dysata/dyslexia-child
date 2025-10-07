import os
import librosa
import numpy as np
import soundfile as sf
import itertools

# Функции аугментации
def add_noise(audio, noise_level=0.005):
    noise = np.random.randn(len(audio))
    return audio + noise_level * noise

def change_pitch(audio, sampling_rate=16000, pitch_factor=-2):
    return librosa.effects.pitch_shift(audio, sampling_rate, pitch_factor)

def time_stretch(audio, rate=0.8):
    return librosa.effects.time_stretch(audio, rate)

def change_volume(audio, factor=0.5):
    return audio * factor

# Все функции аугментации
augmentations = [add_noise, change_pitch, time_stretch, change_volume]

# Функция для обработки неправильных файлов и применения всех возможных комбинаций аугментаций
def augment_incorrect_files(incorrect_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(incorrect_dir):
        if file_name.endswith('.wav'):
            file_path = os.path.join(incorrect_dir, file_name)
            audio, sr = librosa.load(file_path, sr=None)

            # Перебор всех возможных комбинаций аугментаций
            for num_augmentations in range(1, len(augmentations) + 1):
                for combination in itertools.combinations(range(len(augmentations)), num_augmentations):
                    augmented_audio = audio

                    # Применяем выбранные аугментации
                    for i in combination:
                        augmented_audio = augmentations[i](augmented_audio)

                    # Сохранение аугментированного файла
                    augmented_file_name = f"augmented_{''.join(map(str, combination))}_{file_name}"
                    augmented_file_path = os.path.join(output_dir, augmented_file_name)
                    sf.write(augmented_file_path, augmented_audio, sr)
                    print(f"Сохранен аугментированный файл: {augmented_file_path}")

# Пример использования для аугментации неправильных файлов
augment_incorrect_files('dataset/incorrect', 'dataset/incorrect_augmented')
