import os
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report, ConfusionMatrixDisplay
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

# Папки с правильными и неправильными аудио
correct_dirs = ['dataset/new/correct', 'dataset/new/correct_augmented']
incorrect_dirs = ['dataset/new/incorrect', 'dataset/new/incorrect_augmented']


def extract_mfcc(audio_path, n_mfcc=13, n_fft=1024):
    audio, sr = librosa.load(audio_path, sr=None)
    target_length = max(n_fft, len(audio))
    if len(audio) < target_length:
        audio = np.pad(audio, (0, target_length - len(audio)), mode='constant')
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft)
    return np.mean(mfcc, axis=1)


def process_folder(folder_path, label, mfccs, labels):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".wav"):
            file_path = os.path.join(folder_path, file_name)
            mfcc_features = extract_mfcc(file_path)
            mfccs.append(mfcc_features)
            labels.append(label)


mfccs, labels = [], []
for correct_dir in correct_dirs:
    process_folder(correct_dir, 1, mfccs, labels)
for incorrect_dir in incorrect_dirs:
    process_folder(incorrect_dir, 0, mfccs, labels)

mfccs, labels = np.array(mfccs), np.array(labels)
scaler = StandardScaler()
mfccs_scaled = scaler.fit_transform(mfccs)

X_train, X_test, y_train, y_test = train_test_split(mfccs_scaled, labels, test_size=0.25, random_state=42, stratify=labels)


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
y_pred = pnn.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Точность модели: {accuracy * 100:.2f}%")
print(f"F1-мера модели: {f1 * 100:.2f}%")
print("\nОтчет о классификации:")
print(classification_report(y_test, y_pred, target_names=["Неправильные", "Правильные"]))

ConfusionMatrixDisplay.from_predictions(y_test, y_pred, display_labels=["Неправильные", "Правильные"], cmap='Blues')
plt.title("Матрица ошибок")
plt.show()
