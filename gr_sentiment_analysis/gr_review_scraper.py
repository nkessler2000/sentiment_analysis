import requests
from bs4 import BeautifulSoup
import re
import os
import time
import csv


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

def extract_title(soup):
    """Gets the book title from a Goodreads page BeautifulSoup object"""
    try:
        title = soup.find('h1', attrs={'class':'bookTitle', 'itemprop':'name'}).get_text()
        title = re.sub(r'(\(|\[)(.*)(\)|\])','', title).strip()
        # Strip out Series Identifiers
        return title
    except AttributeError:
        return ''

def extract_book_id(soup):
    """Gets the Goodreads book ID from a Goodreads page BeautifulSoup object"""
    try:
        book_id = soup.find('meta', attrs={'property':'al:ios:url'}).get('content')
        book_id = re.sub('com.goodreads.https://book/show/', '', book_id)
        return book_id
    except AttributeError:
        return ''

def extract_author(soup):
    """Gets the book author from a Goodreads page BeautifulSoup object"""
    try:
        author = soup.find('a', attrs={'class':'authorName'}).find('span', attrs={'itemprop':'name'}).get_text()
        return author
    except AttributeError:
        return ''

def extract_book_language(soup):
    """Gets the book's language from a Goodreads page BeautifulSoup object"""
    try:
        language = soup.find('div', attrs={'class':'infoBoxRowItem', 'itemprop':'inLanguage'}).get_text()
        return language.strip()
    except AttributeError:
        return ''

def extract_avg_rating(soup):
    """Gets the book's avearge review score from a Goodreads page BeautifulSoup object"""
    try:
        rating = soup.find('span', attrs={'class':'average','itemprop':'ratingValue'}).get_text()
        return rating.strip()
    except AttributeError:
        return ''

def extract_ratings_count(soup):
    """Gets the number of reviews a book has from a Goodreads page BeautifulSoup object"""
    try:
        review_count = soup.find('span', attrs={'class':'votes value-title'}).get_text().replace(',','').replace('\n', '')
        return review_count.strip()
    except AttributeError:
        return ''

def extract_reviews_count(soup):
    """Gets the number of reviews a book has from a Goodreads page BeautifulSoup object"""
    try:
        review_count = soup.find('span', attrs={'class':'count value-title'}).get_text().replace(',','').replace('\n', '')
        return review_count.strip()
    except AttributeError:
        return ''

def extract_book_info(soup):
    """Gets the book title, book ID, author, genre, pages, number of reviews, and average rating. Returns a dict"""
    try:
        ret_dict = {
            'id':extract_book_id(soup),
            'title':extract_title(soup),
            'author':extract_author(soup),
            'language':extract_book_language(soup),
            'avg_rating':extract_avg_rating(soup),
            'ratings_count':extract_ratings_count(soup),
            'review_count':extract_reviews_count(soup)
        }
        return ret_dict
    except:
        return None

def main():
    
    # first check if the CSV exists and if not, create and write header
    file_path = './data/book_info.csv'
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', encoding='utf-8') as file:
            columns = ['id', 'title', 'author', 'language', 'avg_rating', 'ratings_count', 'review_count']
            file.write('\t'.join(columns) + '\n')

    # For 1000 random books, extract the book info and write to a CSV file
    for i in range(10000):
        # get a random book's info
        url = 'https://www.goodreads.com/book/random'
        soup = get_html_source(url)
        book_info = extract_book_info(soup)
        book_info_values = list(book_info.values())
        if book_info != None:
            with open(file_path, mode='a', encoding='utf-8') as file:
                line = '\t'.join(book_info.values()) + '\n'
                file.write(line)

        # sleep 3 seconds
        time.sleep(3)


#def top30_reviews_by_id(id):
#    """Gets top 30 reviews for a book ID. Returns a dictionary with review ID, score number, and review text"""

#    # set URL using book ID
#    url = 'https://www.goodreads.com/book/show/{0}'.format(str(id))

#    # get the page
#    soup = get_html_source(url)
#    soup_text = soup.g

#    # get the review count. We only want to look at books with more than 30 reviews.
#    review_count = soup.find('span', attrs={'class', 'value-title'}).get_text().replace(',','')
    
    
#    if int(review_count) > 30:
#        # select the top 30 reviews from page
#        book_info = extract_book_info(soup)
#        review_tags = soup.select('#reviews .stacked')
#        # get the ID numbers
#        review_ids = get_review_ids(soup) 

#        # extract the review text. Because of the structure of the data, there will be two list
#        # entries for each review. The first has review metadata and the second the review text
#        reviews = [tag.get_text() for tag in review_tags]
#        review_ratings = extract_ratings(reviews)
#        review_text = extract_review_text(reviews)

#        # join review IDs, rating, and review text together as a dictionary
#        ret = {
#            'id':review_ids,
#            'rating':review_ratings,
#            'text':review_text
#            }

#        return ret


#def main():
#    #dune_id = 234225
#    book_id = 13521139
#    top_reviews = top30_reviews_by_id(book_id)
#    print(top_reviews)
#    #dune = get_review_by_id(2348449)
#    #print(dune['review_text'])
#    pass

if __name__ == "__main__":
    main()


