import requests
from bs4 import BeautifulSoup

def get_html_source(url):
    """gets HTML page from URL and returns a BeautifulSoup object"""
    html_source = requests.get(url).text
    soup = BeautifulSoup(html_source, 'html.parser')
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
           'review_text':get_review_text(soup)}
    return ret

def main():
    dune = get_review_by_id(2348449)
    print(dune['review_text'])
    pass

if __name__ == "__main__":
    main()


