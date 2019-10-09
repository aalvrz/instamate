"""Interactions with Instagram's GraphQL API."""
import re


INSTAGRAM_JAVASCRIPT_FILE_URL = (
    'https://www.instagram.com/static/bundles/es6/Consumer.js/1f67555edbd3.js'
)


def get_graphql_query_hash(browser) -> str:
    """
    Load Instagram JavaScript file, then find and return query hash.
    """

    browser.get(INSTAGRAM_JAVASCRIPT_FILE_URL)
    page_source = browser.page_source

    query_hash = re.findall('[a-z0-9]{32}(?=",n=")', page_source)
    if query_hash:
        return query_hash[0]
