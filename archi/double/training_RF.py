import os
import librosa
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


# Папки с правильными и неправильными аудио
correct_dirs = ['dataset/new/correct', 'dataset/new/correct_augmented']
incorrect_dirs = ['dataset/new/incorrect', 'dataset/new/incorrect_augmented']
output_dir = 'dataset/new/mfcc_features'

# Функция для извлечения MFCC из аудиофайла
def extract_mfcc(audio_path, n_mfcc=13, n_fft=1024):
    audio, sr = librosa.load(audio_path, sr=None)  # Загружаем аудио без изменения частоты дискретизации
    target_length = max(n_fft, len(audio))  # Удлинение сигнала для соответствия n_fft
    if len(audio) < target_length:
        audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')  # Добавление тишины
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft)
    mfcc_mean = np.mean(mfcc, axis=1)  # Берем среднее значение по времени
    return mfcc_mean

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
for correct_dir in correct_dirs:
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

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(mfccs_scaled, labels, test_size=0.25, random_state=42, stratify=labels)

# Обучение классификатора Random Forest
clf = RandomForestClassifier(n_estimators=1000, random_state=42, class_weight="balanced")
clf.fit(X_train, y_train)

# Предсказания и оценка модели
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
f1_score = f1_score(y_test, y_pred)

print(f"Точность модели: {accuracy * 100:.2f}%")
print(f"F1-мера модели: {f1_score * 100:.2f}%")

# Вывод отчета о классификации
print("\nОтчет о классификации:")
print(classification_report(y_test, y_pred, target_names=["Неправильные", "Правильные"]))

# Построение матрицы ошибок
ConfusionMatrixDisplay.from_estimator(clf, X_test, y_test, display_labels=["Неправильные", "Правильные"])
plt.title("Матрица ошибок")
plt.show()