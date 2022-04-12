"""..."""
from urllib.parse import urlsplit, urlunsplit

def remove_query_params_and_fragment(url):
    return urlunsplit(urlsplit(url)._replace(query="", fragment=""))

