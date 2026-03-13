"""
Обучает CatBoost классификатор на parquet с фильтром prob > 0.8.
"""
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from catboost import CatBoostClassifier

sys.stdout.reconfigure(encoding='utf-8')

# Загрузка всех parquet из текущей директории
import glob
parquet_files = sorted(glob.glob('*.parquet.gzip'))
print(f"Найдено parquet: {parquet_files}")
dfs = []
for pf in parquet_files:
    part = pd.read_parquet(pf)
    print(f"  {pf}: {len(part)} строк, a=1: {(part['a']==1).sum()}, a=0: {(part['a']==0).sum()}")
    dfs.append(part)
df = pd.concat(dfs, ignore_index=True)
# Убираем нечисловые столбцы (filename и т.п.)
drop_cols = [c for c in df.columns if c not in ['a', 'prob'] and not str(c).isdigit()]
if drop_cols:
    df = df.drop(columns=drop_cols)
print(f"Итого: {len(df)} строк, a=1: {(df['a']==1).sum()}, a=0: {(df['a']==0).sum()}")

# Фильтр: только фреймы с prob > 0.8
df = df[df['prob'] > 0.8]
print(f"После фильтра prob > 0.8: {len(df)} строк, a=1: {(df['a']==1).sum()}, a=0: {(df['a']==0).sum()}")

X = df.drop(columns=['a'])
y = df['a']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# Обучение
model = CatBoostClassifier(
    iterations=1000,
    depth=6,
    learning_rate=0.1,
    loss_function='Logloss',
    eval_metric='Accuracy',
    random_seed=42,
    verbose=100,
)

model.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=50)

# Оценка
y_pred = model.predict(X_test)
print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=['notgood (0)', 'good (1)']))

# Топ-20 важных признаков
importances = model.get_feature_importance()
top_idx = np.argsort(importances)[-20:][::-1]
print("Топ-20 признаков:")
for i in top_idx:
    print(f"  [{X.columns[i]}]: {importances[i]:.2f}")

# Сохранение модели
model.save_model('catboost_r_model80.cbm')
print("\nМодель сохранена: catboost_r_model80.cbm")
