import unittest
from unittest.mock import patch

# Lightweight parameterized.expand replacement to avoid extra dependency
def parameterized_expand(cases):
	def decorator(func):
		def wrapper(*args, **kwargs):
			raise RuntimeError('parameterized decorator should not be called directly')
		wrapper._parameterized_cases = cases
		wrapper.__name__ = func.__name__
		wrapper._wrapped = func
		return wrapper
	return type('parameterized', (), {'expand': staticmethod(parameterized_expand)})

parameterized = parameterized_expand

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
	def test_access_nested_map(self):
		cases = [
			({"a": 1}, ("a",), 1),
			({"a": {"b": 2}}, ("a",), {"b": 2}),
			({"a": {"b": 2}}, ("a", "b"), 2),
		]
		for nested_map, path, expected in cases:
			with self.subTest(nested_map=nested_map, path=path):
				self.assertEqual(access_nested_map(nested_map, path), expected)

	def test_access_nested_map_exception(self):
		cases = [
			({}, ("a",)),
			({"a": 1}, ("a", "b")),
		]
		for nested_map, path in cases:
			with self.subTest(nested_map=nested_map, path=path):
				with self.assertRaises(KeyError) as ctx:
					access_nested_map(nested_map, path)
				# Ensure exception message matches missing key
				self.assertEqual(str(ctx.exception), repr(path[-1]))


class TestGetJson(unittest.TestCase):
	def test_get_json(self):
		cases = [
			("http://example.com", {"payload": True}),
			("http://holberton.io", {"payload": False}),
		]
		for test_url, test_payload in cases:
			with self.subTest(test_url=test_url):
				mock_resp = unittest.mock.Mock()
				mock_resp.json.return_value = test_payload
				with patch('utils.requests.get', return_value=mock_resp) as mock_get:
					result = get_json(test_url)
					mock_get.assert_called_once_with(test_url)
					self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
	def test_memoize(self):
		class TestClass:
			def a_method(self):
				return 42

			@memoize
			def a_property(self):
				return self.a_method()

		obj = TestClass()
		with patch.object(TestClass, 'a_method', return_value=42) as mock_meth:
			self.assertEqual(obj.a_property(), 42)
			self.assertEqual(obj.a_property(), 42)
			mock_meth.assert_called_once()


if __name__ == '__main__':
	unittest.main()

