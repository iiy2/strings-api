from flask import Flask, jsonify, make_response, Response, request
from urllib.parse import quote
from functools import wraps
import requests, json, operator

app = Flask(__name__)


def check_auth(username, password):
    return username == 'admin' and password == 'secret'


def authenticate():
    return Response(
        'Please login to use API', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    return "Available API\'s:<br/>" \
           '<ul>' \
           '    <li>/get - returns a random word using http://setgetgo.com/randomword/get.php</li>' \
           '    <li>/wiki/word - returns a wiki page for requested word</li>' \
           '    <li>/popular/n - returns top requested words for the wiki API</li>' \
           '    <li>/jokes/firstname/lastname - returns a random joke according to given firstname/lastname</li>'


@app.route('/get')
@requires_auth
def get():
    url = 'http://setgetgo.com/randomword/get.php'
    response = requests.get(url)
    errors = []
    if response.status_code == 200:
        result = response.text
    else:
        result = ''
        errors.append({'message': 'External API not found'})
    return make_response(jsonify({
        'result': result,
        'errors': errors
    }), response.status_code)


@app.route('/wiki/<string:word>')
@requires_auth
def wiki(word):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=parse&prop=text&page=' + quote(word)
    response = requests.get(url)
    errors = []
    result = ''
    if response.status_code == 200:
        if 'parse' in response.json():
            try:
                with open('words.txt', 'r') as f:
                    read_content = f.read()
            except FileNotFoundError as err:
                errors.append({'message': 'File not found'})
            else:
                if len(read_content) > 0:
                    words_stat = json.loads(read_content)
                else:
                    words_stat = dict()
                if word in words_stat:
                    words_stat[word] += 1
                else:
                    words_stat[word] = 1
                with open('words.txt', 'w') as f:
                    json.dump(words_stat, f)
                result = response.json()['parse']['text']
        else:
            errors.append(response.json()['error']['info'])
    else:
        errors.append({'message': 'External API not found'})
        result = ''
    return make_response(jsonify({
        'result': result,
        'errors': errors
    }), response.status_code)


@app.route('/popular/', defaults={'n': -1})
@app.route('/popular/<int:n>')
@requires_auth
def popular(n):
    errors = []
    result = ''
    try:
        with open('words.txt', 'r') as f:
            read_content = f.read()
    except FileNotFoundError as err:
        errors.append({'message': 'File not found'})
    else:
        if len(read_content) > 0:
            words_stat = json.loads(read_content)
        else:
            words_stat = dict()
        words_sorted = sorted(words_stat.items(), key=operator.itemgetter(1), reverse=True)
        if n == -1:
            n = len(words_sorted)
        result = [dict([i]) for i in words_sorted[:n]]
    return make_response(jsonify({
        'result': result,
        'errors': errors
    }), 200)


@app.route('/jokes/', defaults={'firstname': 'Chuck', 'lastname': 'Norris'})
@app.route('/jokes/<string:firstname>/', defaults={'lastname': ''})
@app.route('/jokes/<string:firstname>/<string:lastname>')
@requires_auth
def joke(firstname, lastname):
    errors = []
    result = ''
    url = 'http://api.icndb.com/jokes/random?firstName=' + quote(firstname) + '&lastName=' + quote(lastname)
    response = requests.get(url)
    if response.status_code == 404:
        errors.append({'message': 'External API not found'})
    else:
        result = response.json()['value']['joke']
    return make_response(jsonify({
        'result': result,
        'errors': errors
    }), response.status_code)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({
        'errors': [{'message': 'Api not found'}],
        'result': ''
    }), 404)
