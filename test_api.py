import index
import unittest
import json


class IndexTestCase(unittest.TestCase):
    test_file = {"test_word1": 2, "test_word2": 1, "test_word3": 1, "test_word4": 1, "test_word5": 34}
    tmp_data = {}

    def setUp(self):
        index.app.testing = True
        index.app.avoid_login = True
        with open('words.txt', 'r') as f:
            read_content = f.read()
            if len(read_content) > 0:
                words_stat = json.loads(read_content)
                self.tmp_data = words_stat
            with open('words.txt', 'w') as f:
                json.dump(self.test_file, f)
        self.app = index.app.test_client()

    def tearDown(self):
        with open('words.txt', 'w') as f:
            json.dump(self.tmp_data, f)

    def test_wrong_url(self):
        response = self.app.get('/wrong_url')
        assert response.status_code == 404

    def test_root(self):
        rv = self.app.get('/')
        assert len(rv.data) > 0
        assert rv.status_code == 200

    def test_get_random_word(self):
        response = self.app.get('/get')
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        assert response.status_code == 200

    def test_get_wiki_page(self):
        response = self.app.get('/wiki')
        assert response.status_code == 404  # no word was provided
        response = self.app.get('/wiki/python')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        response = self.app.get('/wiki/blablablabla')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 1
        assert decoded_data['errors'][0]['message'] == 'The page you specified doesn\'t exist.'
        assert 'result' in decoded_data
        assert len(decoded_data['result']) == 0

    def test_get_popular_words(self):
        response = self.app.get('/popular/some_word')
        assert response.status_code == 404
        response = self.app.get('/popular/')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) == 5
        assert decoded_data['result'] == [
            {"test_word5": 34},
            {"test_word1": 2},
            {"test_word2": 1},
            {"test_word3": 1},
            {"test_word4": 1}
        ]
        response = self.app.get('/popular/4')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) == 4
        assert decoded_data['result'] == [
            {"test_word5": 34},
            {"test_word1": 2},
            {"test_word2": 1},
            {"test_word3": 1}
        ]

    def test_get_jokes(self):
        response = self.app.get('/jokes/')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        assert 'Chuck Norris' in decoded_data['result']
        response = self.app.get('/jokes/test_name/')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        assert 'test_name' in decoded_data['result']
        response = self.app.get('/jokes/test_name/test_lastname')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        assert 'test_name test_lastname' in decoded_data['result']
        response = self.app.get('/jokes/test name/')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        assert 'test name' in decoded_data['result']
        response = self.app.get('/jokes/test name/test lastnam,:\'e')
        assert response.status_code == 200
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        assert 'errors' in decoded_data
        assert len(decoded_data['errors']) == 0
        assert 'result' in decoded_data
        assert len(decoded_data['result']) > 0
        assert 'test name test lastnam,:\'e' in decoded_data['result']


if __name__ == '__main__':
    unittest.main()
