import pymorphy2

lemmatizer_cache = {}
def norm(token):
    if morph.word_is_known(token):
        if token not in lemmatizer_cache:
            lemmatizer_cache[token] = morph.parse(token)[0].normal_form
        return lemmatizer_cache[token]
    return token

s = open('train.csv', 'r', encoding='utf-8')
res = ""
for line in s.readlines():
    l = line.split(',')
    re_line = ' '.join(list(map(norm , l[0].split())))
    # print(re_line, l[1])
    res += re_line + ', '+ l[1] + '\n'
s.close()

d = open('train.csv', 'w', encoding='utf-8')
print(res, file=d)
d.close()
