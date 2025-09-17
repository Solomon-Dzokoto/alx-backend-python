#!/usr/bin/env python3
import functools
import requests


def access_nested_map(nested_map, path):
    """Access a nested map using path (tuple of keys) and return the value.
    Raise KeyError if any key is missing.
    """
    current = nested_map
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            raise KeyError(key)
    return current


def get_json(url):
    """Get JSON payload from URL using requests.get and return .json()."""
    resp = requests.get(url)
    return resp.json()


def memoize(func):
    """Simple memoize decorator that caches results on the instance.
    Works with instance methods: stores cached values on the instance
    with attribute name '_memoized_<func_name>'.
    """
    attr_name = f"_memoized_{func.__name__}"

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        result = func(self, *args, **kwargs)
        setattr(self, attr_name, result)
        return result

    return wrapper
