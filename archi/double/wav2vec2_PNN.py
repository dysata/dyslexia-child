import os

import librosa
import matplotlib.pyplot as plt
import numpy as np
import torch
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score, classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from transformers import Wav2Vec2Processor, Wav2Vec2Model

# Загрузка предобученной модели Wav2Vec2
processor = Wav2Vec2Processor.from_pretrained("dysata/Wav2Vec2-Ru-Child")
model = Wav2Vec2Model.from_pretrained("dysata/Wav2Vec2-Ru-Child")

# Папки с правильными и неправильными аудио
correct_dirs = ['dataset/new/correct', 'dataset/new/correct_augmented']
incorrect_dirs = ['dataset/new/incorrect', 'dataset/new/incorrect_augmented']


# Функция для извлечения Wav2Vec2 признаков
def extract_features(audio_path):
    audio, sr = librosa.load(audio_path, sr=16000)  # Wav2Vec2 требует 16kHz
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    features = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()  # Среднее по времени
    return features


# Функция для обработки всех файлов в папке
def process_folder(folder_path, label, features_list, labels_list):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".wav"):
            file_path = os.path.join(folder_path, file_name)
            features = extract_features(file_path)
            features_list.append(features)
            labels_list.append(label)


# Списки для хранения признаков и меток
features, labels = [], []

# Обработка аудиофайлов
for correct_dir in correct_dirs:
    process_folder(correct_dir, 1, features, labels)

for incorrect_dir in incorrect_dirs:
    process_folder(incorrect_dir, 0, features, labels)

# Преобразуем в NumPy-массив
features = np.array(features)
labels = np.array(labels)

# Масштабирование признаков
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Применение PCA для уменьшения размерности до 50
pca = PCA(n_components=50)  # Количество компонент можно подобрать
features_pca = pca.fit_transform(features_scaled)

# Разделение данных
X_train, X_test, y_train, y_test = train_test_split(features_pca, labels, test_size=0.25, random_state=42, stratify=labels)

# Обучение PNN
class PNNClassifier:
    def __init__(self, sigma=0.1):
        self.sigma = sigma
        self.class_kdes = {}

    def fit(self, X, y):
        self.class_kdes = {}
        for label in np.unique(y):
            self.class_kdes[label] = gaussian_kde(X[y == label].T, bw_method=self.sigma)

    def predict(self, X):
        probs = np.array([self.class_kdes[label].pdf(X.T) for label in self.class_kdes])
        return np.argmax(probs, axis=0)


pnn = PNNClassifier(sigma=0.3)
pnn.fit(X_train, y_train)

# Предсказание
y_pred = pnn.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)

# Оценка
accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Точность: {accuracy * 100:.2f}%")
print(f"F1-мера: {f1 * 100:.2f}%")
print("\nОтчет о классификации:\n", classification_report(y_test, y_pred, target_names=["Неправильные", "Правильные"]))

# Построение матрицы ошибок
ConfusionMatrixDisplay.from_predictions(y_test, y_pred, display_labels=["Неправильные", "Правильные"], cmap='Blues')
plt.title("Матрица ошибок")
plt.show()
