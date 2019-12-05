#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 16:06:16 2019

@author: dominic
"""

import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

df = pd.read_csv('Sentiment.csv', index_col = 0).dropna()

#setup stopwords for the wordcloud
stopwords = set(STOPWORDS)
stopwords.update(["Bitcoin", "crypto", "blockchain", "BTC", "cryptocurrency", "via", "will"])

#wordcloud generation
wordcloud = WordCloud(stopwords = stopwords).generate(" ".join(t for t in df.text))

#plotting the wordcloud
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()    