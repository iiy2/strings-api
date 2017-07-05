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
    word = requests.get(url)
    errors = []
    if word.status_code == 404:
        errors.append({'message': 'External API not found'})
        result = ''
    else:
        result = word.text
    return jsonify({
        'result': result,
        'errors': errors
    })


@app.route('/wiki/<string:word>')
def wiki(word):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=parse&prop=text&page=' + word
    page = requests.get(url)
    errors = []
    result = ''
    print(page.status_code)
    if page.status_code == 404:
        abort(404)
    if 'parse' in page.json():
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
            print(words_stat)
            with open('words.txt', 'w') as f:
                json.dump(words_stat, f)
            if 'parse' in page.json():
                result = page.json()['parse']['text']
            f.close()
    else:
        errors.append(page.json()['error']['info'])
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
    return jsonify({
        'result': result,
        'errors': errors
    })


@app.route('/jokes/', defaults={'firstname': 'Chuck', 'lastname': 'Norris'})
@app.route('/jokes/<string:firstname>/', defaults={'lastname': ''})
@app.route('/jokes/<string:firstname>/<string:lastname>')
def joke(firstname, lastname):
    url = 'http://api.icndb.com/jokes/random?firstName=' + firstname + '&lastName=' + lastname
    word = requests.get(url)
    if word.status_code == 404:
        abort(404)
    return jsonify({
        'result': word.json()['value']['joke'],
        'errors': []
    })


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'errors': [{'message': 'Api not found'}], 'result': ''}), 404)
