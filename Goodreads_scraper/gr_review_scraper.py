import requests
from bs4 import BeautifulSoup as bs

#api_key = 'P1uRR4YWIS1HzT627Maw'
#api_secret = 'fnlRuVhwhNuyRqk1GNz7t48hKKWS9yh8GNA9O0pnnp8'

def get_html_source(url):
    """gets HTML page from URL and returns a BeautifulSoup object"""
    html_source = requests.get(url).text
    soup = bs(html_source, 'html.parser')
    return soup

def get_rating(soup):
    """Extracts rating from BeautifulSoup object and returns as string"""
    rating = soup.find(itemprop='ratingValue').get('content')
    return rating

def get_title(soup):
    """Extracts book title from BeautifulSoup object and returns as string"""
    title = soup.find(itemprop='name').get('content')
    return title

def get_review_text(soup):
    """Extracts review text from BeautifulSoup object and returns as string"""
    review_text = soup.find(itemprop='reviewBody').get_text()
    return review_text

def get_review_by_id(id):
    """Gets Goodreads book review by ID number, returns dictionary
    with title, rating, and review text
    """
    url = 'https://www.goodreads.com/review/show/{0}'.format(str(id))
    soup = get_html_source(url)
    ret = {'title':get_title(soup),
           'rating':get_rating(soup), 
           'review':get_review_text(soup)}
    return ret



#soup = get_html_source("https://www.goodreads.com/review/show/2348449")
#rating = get_rating(soup)
#review_text = get_review_text(soup)
#print(review_text)
#pass

dune = get_review_by_id(2348449)
print(dune['review'])
pass