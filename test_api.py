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
        self.assertEqual(response.status_code, 404)

    def test_root(self):
        rv = self.app.get('/')
        self.assertGreater(len(rv.data), 0)
        self.assertEqual(rv.status_code, 200)

    def test_get_random_word(self):
        response = self.app.get('/get')
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        self.assertEqual(response.status_code, 200)

    def test_get_wiki_page(self):
        response = self.app.get('/wiki')
        self.assertEqual(response.status_code, 404)
        response = self.app.get('/wiki/python')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        response = self.app.get('/wiki/blablablabla')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 1)
        self.assertEqual(decoded_data['errors'][0]['message'], 'The page you specified doesn\'t exist.')
        self.assertIn('result', decoded_data)
        self.assertEqual(len(decoded_data['result']), 0)

    def test_get_popular_words(self):
        response = self.app.get('/popular/some_word')
        self.assertEqual(response.status_code, 404)
        response = self.app.get('/popular/')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertEqual(len(decoded_data['result']), 5)
        self.assertEqual(decoded_data['result'], [
            {"test_word5": 34},
            {"test_word1": 2},
            {"test_word2": 1},
            {"test_word3": 1},
            {"test_word4": 1}
        ])
        response = self.app.get('/popular/4')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertEqual(len(decoded_data['result']), 4)
        self.assertEqual(decoded_data['result'], [
            {"test_word5": 34},
            {"test_word1": 2},
            {"test_word2": 1},
            {"test_word3": 1}
        ])

    def test_get_jokes(self):
        response = self.app.get('/jokes/')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        self.assertIn('Chuck Norris', decoded_data['result'])
        response = self.app.get('/jokes/test_name/')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        self.assertIn('test_name', decoded_data['result'])
        response = self.app.get('/jokes/test_name/test_lastname')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        self.assertIn('test_name test_lastname', decoded_data['result'])
        response = self.app.get('/jokes/test name/')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        self.assertIn('test name', decoded_data['result'])
        response = self.app.get('/jokes/test name/test lastnam,:\'e')
        self.assertEqual(response.status_code, 200)
        decoded_data_str = response.data.decode()
        decoded_data = json.loads(decoded_data_str)
        self.assertIn('errors', decoded_data)
        self.assertEqual(len(decoded_data['errors']), 0)
        self.assertIn('result', decoded_data)
        self.assertGreater(len(decoded_data['result']), 0)
        self.assertIn('test name test lastnam,:\'e', decoded_data['result'])


if __name__ == '__main__':
    unittest.main()
