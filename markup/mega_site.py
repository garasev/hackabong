import json
import re
import requests
import os
import glob
import nltk
nltk.download('stopwords')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing  import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import f1_score
from IPython.core.display import HTML, display
import pymorphy2


print("Кибербуллинг на низком старте")

path = 'res_threads'
all_file = open('train.csv', mode='w', encoding='utf8')
for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
        with open(dirpath + "//" + file, mode='r', encoding='utf8') as f:
            all_file.write(f.read())

train_df = pd.read_csv("train.csv", names = ['Text', 'Target'])
train_df.dropna(axis=0, inplace=True)

list_corpus = train_df["Text"].tolist()
list_labels = train_df["Target"].tolist()
X_train, X_test, y_train, y_test = train_test_split(list_corpus, list_labels, test_size=0.3, 
                                                                                random_state=40)

def tfidf(data):
    tfidf_vectorizer = TfidfVectorizer()

    train = tfidf_vectorizer.fit_transform(data)

    return train, tfidf_vectorizer

X_train_tfidf, tfidf_vectorizer = tfidf(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

####
clf_tfidf = LogisticRegression(C=30.0, class_weight='balanced', solver='newton-cg', 
                         multi_class='multinomial', n_jobs=-1, random_state=40)
clf_tfidf.fit(X_train_tfidf, y_train)

y_predicted_tfidf = clf_tfidf.predict(X_test_tfidf)

df_res = pd.DataFrame({'Text': X_test, 'Target': y_predicted_tfidf})
df_comp = pd.DataFrame({'Text': X_test, 'Target': y_test})


morph = pymorphy2.MorphAnalyzer()
def normalize(x):
    p = morph.parse(x)[0]
    return p.normal_form

def is_cyberbullying(input_str):
    input_str = [' '.join(list(map(normalize , input_str[0].split())))]
    input_str_test = tfidf_vectorizer.transform(input_str)
    result = clf_tfidf.predict(input_str_test)
    return result[0] == 1

print("Кибербуллинг вышел на охоту")


#######################################################################################################
                                 ################## KEKITA ##################
#######################################################################################################
import requests
from bs4 import BeautifulSoup
import re

def clean_site(site_link):
    def delete_artifacts(text):
        filters = [r'</*\w+>', r'>>\d+', r'\(OP\)', r'https:\S+', r'\n'] #
        for filter_ in filters:
            text = re.sub(filter_, ' ', text)
        return text

    space_delimiters = '.', '!', '?', ';', '\n', '\t', ' ', ',', ' '
    spaceRegexPattern = '|'.join(map(re.escape, space_delimiters))
    def delete_space(text):
        return str(' '.join(re.split(spaceRegexPattern, text)))

    def delete_punctuation(text):
        punctuation = r'[,=->«»()"\*\+❤️]'
        text = re.sub(punctuation, ' ', text)
        return text


    def split_to_sentences(text):
        separators = '.!?\n@'
        final_separator = '~'

        for separator in separators:
            text = text.replace(separator, final_separator)
        text = delete_punctuation(text)

        return text.split(final_separator)

    # site_link = 'https://2ch.hk/b/res/235160692.html'
    
    r = requests.get(site_link)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'lxml')

    for link in soup.findAll('link'):
        link['href'] = "https://cdn.discordapp.com/attachments/494556593807949827/786998635103125554/makaba.css"
    

    for leaf in soup.findAll('article'):
        value = leaf.text
        values = split_to_sentences(delete_punctuation(delete_artifacts(value)))

        is_bullying = False
        not_bullying = []
        bullying = []
        for value_ in values:
            tmp = delete_space(value_)
            if not len(tmp):
                continue

            if is_cyberbullying([value_]):          
                is_bullying = True
                bullying.append(value_)
            else:
                not_bullying.append(value_)

        if is_bullying:
            leaf.name = 'img'
            leaf['src'] = 'https://i.pinimg.com/originals/9e/95/f7/9e95f705c6496ea2dec88339a37fef46.jpg'
            leaf['title'] = '. '.join(bullying) #leaf.text
            leaf['width'] = 100
            leaf['height'] = 75
            leaf.string = '. '.join(not_bullying)
    
    with open('archivach/'+site_link.split('/')[-1], 'w', encoding='utf-8') as file:
        print(soup, file=file)



#######################################################################################################
                                 ################## SITE ##################
#######################################################################################################

import flask
import pickle
import os
import pandas as pd

port = int(os.getenv("PORT", 1420))
app = flask.Flask(__name__, template_folder='./')
file_name = ''


@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return (flask.render_template('mega.html', input_phrase='Я люблю Россию!', output_res='Не кибербуллинг', sents=[]))

@app.route('/check', methods=['GET', 'POST'])    
def check():
    if flask.request.method == 'POST':
        input_f = str(flask.request.form['input'])
        
        cyber_flag = False
        sent_arr = []
        
        #input_f.split('.')
        delimiters = '.', '!', '?', ';', '\n'
        regexPattern = '|'.join(map(re.escape, delimiters))
        for st in re.split(regexPattern, input_f): 
            if len(st.split()) ==0:
                continue
            
            if is_cyberbullying([st]):
                ans = 'poggers'
                cyber_flag = True
            else:
                ans = 'not_poggers'
            
            sent_arr.append({'text': st,
                            'ctype': ans})
          
        ans = 'Найден кибербуллинг!' if cyber_flag else 'Кибербуллинг не обнаружен'
        return (flask.render_template('mega.html', output_res=ans, input_phrase=input_f, sents=sent_arr))


@app.route('/enter', methods=['GET', 'POST'])    
def enter():
    if flask.request.method == 'POST':
        link = str(flask.request.form['link_input'])
        clean_site(link)
        return (flask.render_template('archivach/'+link.split('/')[-1]))
    

if __name__ == '__main__':
    app.run(host='192.168.1.1', port=port)