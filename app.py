from flask import Flask, url_for, render_template, redirect, session, Response, jsonify #将内容转换为json
from flask.views import request
from main import get_opinion_from_news
from werkzeug.utils import secure_filename # 文件上传
import os, json

UPLOAD_FOLDER = './data/upload' # 上传文件保存文件夹
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} # 文件扩展格式

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_DIR = './data'

def allowed_file(filename):
    """
    检查文件是否符合格式
    :param filename:文件名
    :return: Bool
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/d3_page')
def d3_page():
    """
    d3可视化
    :return:
    """
    return render_template('d3_page.html')

@app.route('/index')
def index():
    """
    首页
    :return:
    """
    if session.get('is_login', None):
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET','POST'])
def login():
    """
    登录
    :return:
    """
    print('path', request.path)
    print('headers', request.headers)
    print('method', request.method)
    print('url', request.url)
    print('data', request.form)

    if request.method == "POST":
        # username = request.form['username']
        # password = request.form['password']
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        print(username, password)
        if username == "root" and password == "123":
            session['username'] = username
            session['password'] = password
            session['is_login'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid username/password"

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    注销
    :return:
    """
    session.pop('username',None)
    print('logout')
    return redirect(url_for('login'))

@app.route('/submit_news', methods=['GET','POST'])
def get_news_from_input():
    """
    输入方式获取
    :return:
    """
    status = False
    message = "Response Good"
    if request.method == "POST":
        res = dict()
        sub_news = request.form['news']
        try:
            with open(os.path.join(BASE_DIR, 'words.txt'), 'r', encoding='utf-8') as f:
                words_like_say_list = f.read().split(' ')
                extracted_news = get_opinion_from_news(sub_news, words_like_say_list)
            res['news'] = extracted_news
            status = True
            message = "error message"
        except Exception as e:
            print(e)
        res['status'] = status
        res['message'] = message
        return jsonify(res)


@app.route('/submit_file', methods=['GET', 'POST'])
def get_news_from_file():
    """
    文件方式获取
    :return:
    """
    status = False
    message = "Response Good"
    if request.method == "POST":
        res = dict()
        extracted_news = []
        try:
            file = request.files['news_file']
            filename = secure_filename(file.filename)
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r', encoding='utf-8') as f1, \
                open(os.path.join(BASE_DIR, 'words.txt'), 'r', encoding='utf-8') as f2:
                    words_like_say_list = f2.read().split(' ')
                    for line in f1:
                        if line:
                            extracted_news += get_opinion_from_news(line, words_like_say_list)
            res['news'] = extracted_news
            status = True
            message = "error message"
        except Exception as e:
            print(e)
        res['status'] = status
        res['message'] = message
        return jsonify(res)

# set the secret key.  keep this really secret:
app.secret_key = os.urandom(24)


if __name__ == '__main__':
    app.run(host='127.0.0.1',debug=True)
