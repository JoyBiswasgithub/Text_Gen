# -*- coding: utf-8 -*-
"""text.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RpNwEec4veK2maykR0yPClbt9mmZz37T
"""

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/

!kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset

import zipfile
zip_ref = zipfile.ZipFile('/content/fake-and-real-news-dataset.zip', 'r')
zip_ref.extractall('/content')
zip_ref.close()

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense, LSTM, Activation
from tensorflow.keras.models import Sequential, load_model

from nltk.tokenize import RegexpTokenizer

real_news = pd.read_csv("/content/True.csv")

real_news

real_news['text'][0]

text=list (real_news.text.values)

join_text=" ".join(text)

partial_text = join_text[:10000]

tokenizer=RegexpTokenizer(r"\w+")

token = tokenizer.tokenize(partial_text.lower())

#token

unique_token = np.unique(token)

unique_token_index={tokens : idx for idx , tokens in enumerate(unique_token)}

n_word=10
input_word=[]
next_word=[]

for i in range(len(token)-n_word):
  input_word.append(token[i:i+n_word])
  next_word.append(token[i+n_word])

x= np.zeros((len(input_word), n_word, len(unique_token)), dtype=bool)
y=np.zeros((len(next_word), len(unique_token)), dtype=bool)

for i , words in enumerate(input_word):
  for j, word in enumerate(words):
    x[i, j, unique_token_index[word]]=1
  y[i, unique_token_index[next_word[i]]]=1

model=Sequential()

model.add(LSTM(128, input_shape=(n_word, len(unique_token)), return_sequences=True))
model.add(LSTM(128))
model.add(Dense(len(unique_token)))
model.add(Activation("softmax"))

from tensorflow.keras.optimizers import RMSprop

model.compile(loss="categorical_crossentropy", optimizer=RMSprop(learning_rate=0.01), metrics=['accuracy'])

model.fit(x,y,batch_size=128,epochs=100, shuffle=True)

model.save('textGen.h5')

model=load_model("/content/textGen.h5")

def predict_text_word(input_text, n_best):
  input_text= input_text.lower()
  x=np.zeros((1, n_word, len(unique_token)))
  for i, word in enumerate(input_text.split()):
    x[0,i,unique_token_index[word]] = 1
  prediction = model.predict(x)[0]

  return np.argpartition(prediction, n_best)[-n_best:]

possible = predict_text_word("he will have to took in this think and he ", 10)

possible

print([unique_token[idx] for idx in possible])

import random

from logging import exception
def generate_sentence(input_text, text_length, creativity=3):
  word_sequence=input_text.split()
  current=0
  for i in range(text_length):
    sub_sequence=" ".join(tokenizer.tokenize(" ".join(word_sequence)))[current:current+n_word]
    try:
      choice= unique_token[random.choice(predict_text_word(sub_sequence, creativity))]
    except:
      choice=random.choice(unique_token)
    word_sequence.append(choice)
    current+=1
  return " ".join(word_sequence)

generate_sentence("how ", 2)

