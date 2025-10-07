from typing import List
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import nltk
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from datasets import load_dataset, concatenate_datasets,DatasetDict
import librosa.display
import pandas as pd
import numpy as np

import glob  
from GPUtil import showUtilization as gpu_usage

pd.read_parquet('dfname.parquet.gzip')
tgdf=pd.DataFrame(tghs)
tbdf=pd.DataFrame(tbhs)
tdf=pd.concat([tgdf, tbdf], ignore_index=True)
tdf['a']=0
tpdf=pd.DataFrame(tpghs)

tpdf['a']=1
testdf=pd.concat([tdf, tpdf], ignore_index=True)
from catboost import CatBoostClassifier
# «агрузка данных

X_train = df.drop('a', axis=1)
y_train = df['a']

#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# —оздание и обучение модели с автоматической обработкой категориальных данных
modelcb2 = CatBoostClassifier(iterations=195,  learning_rate=0.1, depth=6)
modelcb2.fit(X_train, y_train,eval_set=(X_test, y_test))

accuracy = modelcb2.score(X_test, y_test)
print(f"Accuracy: {accuracy}")
print(modelcb.get_params())

#Accuracy: 0.6890243902439024