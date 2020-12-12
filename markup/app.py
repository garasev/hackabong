import flask
import pickle
import os
import pandas as pd

port = int(os.getenv("PORT", 6969))
app = flask.Flask(__name__, template_folder='./')
file_name = ''

def current_pos(fname):
    res_i = 0
    try:
        f = open(fname, 'r', encoding='utf-8')
        res_i = len(f.readlines())
        f.close()
    except IOError:
        res_i = 0
    return res_i

def current_phrase(fname, pos):
    f = open(fname, 'r', encoding='utf-8')
    
    all_str = f.readlines()
    if pos < len(all_str):
        res_str = all_str[pos]
        res_str = res_str.split('\n')[0]
    else:
        res_str = None
    f.close()
    
    return res_str

def insert_row(fname, row):
    try:
        f = open(fname, 'a', encoding='utf-8')
    except IOError:
        f = open(fname, 'w', encoding='utf-8')
    print(row, file=f)
    f.close()

def dest_fname(s_fname):
    return 'res_' + s_fname.split('.')[0] + '.csv'

def get_next(s_fname):
    d_fname = dest_fname(s_fname)
    res_i = current_pos(d_fname)
    return current_phrase(s_fname, res_i)

def add_next(s_fname, result):
    d_fname = dest_fname(s_fname)
    pos = current_pos(d_fname)
    phrase = current_phrase(s_fname, pos)
    insert_row(d_fname, phrase + ',' + result)


@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return (flask.render_template('index.html', output='hello world'))

@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if flask.request.method == 'POST':
        input_f = flask.request.form['input']
        return (flask.render_template('index.html', output=get_next(input_f), f_name=input_f))

@app.route('/da', methods=['GET', 'POST'])    
def da():
    if flask.request.method == 'POST':
        input_f = flask.request.form['input']
        add_next(input_f, '1')
        return (flask.render_template('index.html', output=get_next(input_f), f_name=input_f))
    
@app.route('/net', methods=['GET', 'POST'])    
def net():
    if flask.request.method == 'POST':
        input_f = flask.request.form['input']
        add_next(input_f, '0')
        return (flask.render_template('index.html', output=get_next(input_f), f_name=input_f))


    
if __name__ == '__main__':
    app.run(host='192.168.1.1', port=port)