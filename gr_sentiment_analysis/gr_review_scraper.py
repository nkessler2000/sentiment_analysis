import requests
from bs4 import BeautifulSoup
import regex as re


def get_html_source(url):
    """gets HTML page from URL and returns a BeautifulSoup object"""
    html_source = requests.get(url).text
    soup = BeautifulSoup(html_source, 'html.parser')
    return soup

#def get_rating(soup):
#    """Extracts rating from BeautifulSoup object and returns as string"""
#    rating = soup.find(itemprop='ratingValue').get('content')
#    return rating

#def get_title(soup):
#    """Extracts book title from BeautifulSoup object and returns as string"""
#    title = soup.find(itemprop='name').get('content')
#    return title

#def get_review_text(soup):
#    """Extracts review text from BeautifulSoup object and returns as string"""
#    review_text = soup.find(itemprop='reviewBody').get_text()
#    return review_text

#def get_review_by_id(id):
#    """Gets Goodreads book review by ID number, returns dictionary
#    with title, rating, and review text
#    """
#    url = 'https://www.goodreads.com/review/show/{0}'.format(str(id))
#    soup = get_html_source(url)
#    ret = {'title':get_title(soup),
#           'rating':get_rating(soup), 
#           'review_text':get_review_text(soup)}
#    return ret

def extract_ratings(r_list):
    """Gets the values of even numbered elements from the input list. Extract the rating text and convert to a
    numerical score"""
    review_ratings = [r for r in r_list[0::2]]
    review_ratings = [re.search('rated it\n\s{8}(.*)\n', r).group(1) for r in review_ratings]
    review_ratings = [rating_text_to_num(r) for r in review_ratings]
    return review_ratings

def rating_text_to_num(rating):
    """convert the text rating of a book into a numerical 'star' rating"""
    ret = int()
    if rating == 'did not like it':
        ret = 1
    elif rating == 'it was ok':
        ret = 2
    elif rating == 'liked it':
        ret = 3
    elif rating == 'really liked it':
        ret = 4
    elif rating == 'it was amazing':
        ret = 5
    return ret


def extract_review_text(r_list):
    """Gets the values of odd numbered elements from the input list. Return the reviews as a list"""
    review_text = [r for r in r_list[1::2]] 
    return review_text

def get_review_ids(soup):
    """Gets the review ID numbers of the top 30 reviews from a book's front page. Returns a list"""
    try:
        review_urls = [u.get('href') for u in soup.find_all('a', attrs={'class':'reviewDate createdAt right'})]
        review_ids = [int(''.join(re.findall('[\d]+', r))) for r in review_urls]
        return review_ids  
    except:
        raise

def top30_reviews_by_id(id):
    """Gets top 30 reviews for a book ID. Returns a dictionary with review ID, score number, and review text"""

    # set URL using book ID
    url = 'https://www.goodreads.com/book/show/{0}'.format(str(id))

    # get the page
    soup = get_html_source(url)
    # get the review count. We only want to look at books with more than 30 reviews.
    review_count = soup.find('span', attrs={'class', 'value-title'}).get_text().replace(',','')
    
    
    if int(review_count) > 30:
        # select the top 30 reviews from page
        review_tags = soup.select('#reviews .stacked')
        # get the ID numbers
        review_ids = get_review_ids(soup) 

        # extract the review text. Because of the structure of the data, there will be two list
        # entries for each review. The first has review metadata and the second the review text
        reviews = [tag.get_text() for tag in review_tags]
        review_ratings = extract_ratings(reviews)
        review_text = extract_review_text(reviews)

        # join review IDs, rating, and review text together as a dictionary
        ret = {
            'id':review_ids,
            'rating':review_ratings,
            'text':review_text
            }

        return ret


def main():
    dune_id = 234225
    dune_top_reviews = top30_reviews_by_id(dune_id)
    #dune = get_review_by_id(2348449)
    #print(dune['review_text'])
    pass

if __name__ == "__main__":
    main()


