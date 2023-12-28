import unittest

from extractor import model


class TestModel(unittest.TestCase):
    def test_to_json_empty(self):
        updates = []
        actual = model.to_json(updates, "", compact=True)
        self.assertEqual(actual, '{"url":"","updates":[]}')

    def test_to_json_empty_update(self):
        updates = [model.ColorUpdate([], [], 0.0)]
        actual = model.to_json(updates, "", compact=True)
        self.assertEqual(
            actual, '{"url":"","updates":[{"time":0.0,"hue":[],"temp":[]}]}')

    def test_to_json(self):
        updates = [model.ColorUpdate([(1.0, 1.0, 1.0)], [1.0], 0.0)]
        actual = model.to_json(updates, "www.example.com", compact=True)
        self.assertEqual(
            actual, '{"url":"www.example.com","updates":[{"time":0.0,"hue":[[1.0,1.0,1.0]],"temp":[1.0]}]}')

    def test_from_json_empty(self):
        url, updates = model.from_json('{"url":"","updates":[]}')
        self.assertEqual(updates, [])
        self.assertEqual(url, "")

    def test_from_json_empty_update(self):
        url, updates = model.from_json(
            '{"url":"","updates":[{"time":0.0,"hue":[],"temp":[]}]}')
        self.assertEqual(updates, [model.ColorUpdate([], [], 0.0)])
        self.assertEqual(url, "")

    def test_from_json(self):
        url, updates = model.from_json(
            '{"url":"www.example.com","updates":[{"time":0.0,"hue":[[1.0,1.0,1.0]],"temp":[1.0]}]}')
        self.assertEqual(
            updates, [model.ColorUpdate([(1.0, 1.0, 1.0)], [1.0], 0.0)])
        self.assertEqual(url, "www.example.com")

    def test_from_json_invalid(self):
        with self.assertRaises(ValueError):
            model.from_json('{"url":123,"updates":[]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,1.0,1.0]]}]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,"abc"]]}]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,-1.0]]}]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,1.0]],"temp":["abc"]}]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,1.0]],"temp":[-1.0]}]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,1.0]],"temp":[1.0],"time":"abc"}]}')
        with self.assertRaises(ValueError):
            model.from_json(
                '{"url":"www.example.com","updates":[{"hue":[[1.0,1.0,1.0]],"temp":[1.0],"time":-1.0}]}')


if __name__ == '__main__':
    unittest.main()
