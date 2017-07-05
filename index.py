from flask import Flask, jsonify, abort, make_response
import requests, json, operator

app = Flask(__name__)


@app.route('/')
def index():
    return "Available API\'s:<br/>" \
           '<ul>' \
           '    <li>/get - returns a random word using http://setgetgo.com/randomword/get.php</li>' \
           '    <li>/wiki/word - returns a wiki page for requested word</li>' \
           '    <li>/popular/n - returns top requested words for the wiki API</li>' \
           '    <li>/jokes/firstname/lastname - returns a random joke according to given firstname/lastname</li>'


@app.route('/get')
def get():
    url = 'http://setgetgo.com/randomword/get.php'
    response = requests.get(url)
    errors = []
    if response.status_code == 404:
        errors.append({'message': 'External API not found'})
        result = ''
    else:
        result = response.text
    return jsonify({
        'result': result,
        'errors': errors
    })


@app.route('/wiki/<string:word>')
def wiki(word):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=parse&prop=text&page=' + word
    response = requests.get(url)
    errors = []
    result = ''
    if response.status_code == 404:
        errors.append({'message': 'External API not found'})
        result = ''
    if 'parse' in response.json():
        try:
            f = open('words.txt', 'r')
        except FileNotFoundError as err:
            errors.append({'message': 'File not found'})
        else:
            read_content = f.read()
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
    return jsonify({
        'result': result,
        'errors': errors
    })


@app.route('/popular/', defaults={'n': -1})
@app.route('/popular/<int:n>')
def popular(n):
    errors = []
    result = ''
    try:
        f = open('words.txt', 'r')
    except FileNotFoundError as err:
        errors.append({'message': 'File not found'})
    else:
        read_content = f.read()
        if len(read_content) > 0:
            words_stat = json.loads(read_content)
        else:
            words_stat = dict()
        words_sorted = sorted(words_stat.items(), key=operator.itemgetter(1), reverse=True)
        if n == -1:
            n = len(words_sorted)
        result = [dict([i]) for i in words_sorted[0:n]]
        f.close()
    return jsonify({
        'result': result,
        'errors': errors
    })


@app.route('/jokes/', defaults={'firstname': 'Chuck', 'lastname': 'Norris'})
@app.route('/jokes/<string:firstname>/', defaults={'lastname': ''})
@app.route('/jokes/<string:firstname>/<string:lastname>')
def joke(firstname, lastname):
    errors = []
    result = ''
    url = 'http://api.icndb.com/jokes/random?firstName=' + firstname + '&lastName=' + lastname
    response = requests.get(url)
    if response.status_code == 404:
        errors.append({'message': 'External API not found'})
    else:
        result = response.json()['value']['joke']
    return jsonify({
        'result': result,
        'errors': errors
    })


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({
        'errors': [{'message': 'Api not found'}],
        'result': ''
    }), 404)
