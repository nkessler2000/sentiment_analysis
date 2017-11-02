import requests
import os
import re
import time
from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
from dateutil.parser import parse

class gr_book_info:

    info = OrderedDict()

    def __init__(self, id):
        url = self.__build_url(id)
        self.info = self.__extract_book_info(url)

    def __build_url(self, id):
        # Build URL from id value. Can accept specific book ID or 'random' for a random GR page
        url = ''
        if id == 'random':
            url = 'https://www.goodreads.com/book/random'
        elif str.isnumeric(id):
            url = 'https://www.goodreads.com/book/show/{0}'.format(str(id))
        else:
            raise ValueError("Invalid book ID. Must be numeric value or 'random'")
        return url

    def __get_html_source(self, url, retries=0):
        """gets HTML page from URL and returns a BeautifulSoup object"""
        try:
            html_source = requests.get(url).text
            soup = BeautifulSoup(html_source, 'html.parser')
            return soup
        except requests.exceptions.ConnectionError:
            # retry up to 3 times
            if retries < 3:
                retry = retries + 1
                time.sleep(5)
                self.__get_html_source(url, retry)
            else:
                raise
    
    def __extract_title(self, soup):
        """Gets the book title from a Goodreads page BeautifulSoup object"""
        try:
            title = (soup.select('#bookTitle'))[0].get_text()
            # Strip out Series Identifiers in parentheses
            title = re.sub(r'(\(|\[)(.*)(\)|\])','', title).strip()
            return title
        except IndexError:
            return ''

    def __extract_orig_title(self, soup):
        """gets the book original title from a Goodreads page BeautifulSoup object"""
        try:
            box_title = (soup.select('#bookDataBox > div:nth-of-type(1) > div.infoBoxRowTitle'))[0].get_text().strip()
            if box_title == 'Original Title':
                orig_title = (soup.select('#bookDataBox > div:nth-of-type(1) > div.infoBoxRowItem'))[0].get_text().strip()
                return orig_title
            else:
                return ''
        except IndexError:
            return ''

    def __extract_book_id(self, soup):
        """Gets the Goodreads book ID from a Goodreads page BeautifulSoup object"""
        try:
            book_id = soup.find('meta', attrs={'property':'al:ios:url'}).get('content')
            book_id = re.sub('com.goodreads.https://book/show/', '', book_id)
            return book_id.strip()
        except AttributeError:
            return ''
    
    def __extract_author(self, soup):
        """Gets the book author from a Goodreads page BeautifulSoup object"""
        try:
            author = (soup.select('#bookAuthors > span:nth-of-type(2) > a > span'))[0].get_text()
            return author.strip()
        except IndexError:
            return ''
    
    def __extract_book_language(self, soup):
        """Gets the book's language from a Goodreads page BeautifulSoup object"""
        try:
            databox = soup.select('#bookDataBox')
            language = databox[0].find('div', attrs={'class':'infoBoxRowItem', 'itemprop':'inLanguage'}).get_text()
            return language.strip()
        except (IndexError, AttributeError):
            return ''

    def __extract_pub_date(self, soup):
        """Gets the book's publication date from a Goodreads page BeautifulSoup object"""
        # check for a First Published date and if none, use the Published date. This is for books
        # with multiple editions.
        try:
            pub_date = (soup.select('#details > div:nth-of-type(2) > nobr'))[0].get_text()
            pub_date = re.sub('[()]|first published', '', pub_date).strip()
        except IndexError:
            # If there's no 'First Published', choose the Published date value
            try:
                pub_date = (soup.select('#details > div:nth-of-type(2)'))[0].get_text()
                pub_date = re.sub('Published|by[\s\S]*$', '', pub_date).strip()
            except IndexError:
                return ''
        # convert day from ordinal
        try:
            pub_date = parse(pub_date)
            pub_date = datetime.strftime(pub_date, '%Y-%m-%d')
            return pub_date
        except (TypeError, ValueError):
            return ''
        
    
    def __extract_avg_rating(self, soup):
        """Gets the book's avearge review score from a Goodreads page BeautifulSoup object"""
        try:
            rating = (soup.select('#bookMeta > span.value.rating > span'))[0].get_text()
            return rating.strip()
        except IndexError:
            return ''
    
    def __extract_ratings_count(self, soup):
        """Gets the number of reviews a book has from a Goodreads page BeautifulSoup object"""
        try:
            ratings_count = soup.find('span', attrs={'class':'votes value-title'}).get('title')
            return ratings_count.strip()
        except AttributeError:
            return ''
    
    def __extract_reviews_count(self, soup):
        """Gets the number of reviews a book has from a Goodreads page BeautifulSoup object"""
        try:
            review_count = soup.find('span', attrs={'class':'count value-title'}).get('title')
            return review_count.strip()
        except AttributeError:
            return ''

    def __extract_top_genres(self, soup):
        """Gets the top 3 genres for a book from a Goodreads page Beautiful soup object. Returns 
        a list. If there are less than three top genres, empty strings will be in the position 
        that no value is present"""
        # create a list of 3 empty strings
        ret = ['', '', '']
        try:
            right_container = soup.select('div.rightContainer')
            # figure out how to search through only the right container to improve performance
            top_genres = right_container[0].find_all('a', attrs={'class':'actionLinkLite bookPageGenreLink'})
            for i in range(len(top_genres)):
                # Only want the top 3, so if there are more than 3 top genres, break after the third
                if i > 2:
                    break
                ret[i] = top_genres[i].get_text()
            return ret
        except (IndexError, AttributeError):
            return ret

    def __extract_top_shelves(self, id):
        """Gets the counts for shelfs favorites, to-read, and have-read. Returns a dict"""
        ret = {
            'to-read':'',
            'currently-reading':'',
            'favorites':'',
            }

        url = 'https://www.goodreads.com/book/shelves/{0}'.format(id)
        soup = self.__get_html_source(url)

        try:
            pattern = re.compile('.shelf=to-read$')
            to_read = soup.find('a', attrs={'rel':'nofollow', 'href':pattern}).get_text()
            ret['to-read'] = re.sub('[^\d]', '', to_read)
        except AttributeError:
            pass
        try:
            pattern = re.compile('.shelf=currently-reading$')
            currently_reading = soup.find('a', attrs={'rel':'nofollow', 'href':pattern}).get_text()
            ret['currently-reading'] = re.sub('[^\d]', '', currently_reading)
        except AttributeError:
            pass
        try:
            pattern = re.compile('.shelf=favorites$')
            favorites = soup.find('a', attrs={'rel':'nofollow', 'href':pattern}).get_text()
            ret['favorites'] = re.sub('[^\d]', '', favorites)
        except AttributeError:
            pass
        return ret
        
    def __extract_book_info(self, url):
        """Gets the book title, book ID, author, genre, pages, number of reviews, and average rating. Returns a dict"""
        soup = self.__get_html_source(url)

        try:
            book_id = self.__extract_book_id(soup)
            book_title = self.__extract_title(soup)
            book_orig_title = self.__extract_orig_title(soup)
            book_author = self.__extract_author(soup)
            page_language = self.__extract_book_language(soup)
            first_published = self.__extract_pub_date(soup)
            avg_rating = self.__extract_avg_rating(soup)
            ratings_count = self.__extract_ratings_count(soup)
            reviews_count = self.__extract_reviews_count(soup)
            
            ret_dict = OrderedDict({
                'id':book_id,
                'title':book_title,
                'orig_title':book_orig_title,
                'author':book_author,
                'published':first_published,
                'language':page_language,
                'avg_rating': avg_rating,
                'ratings_count':ratings_count,
                'review_count':reviews_count,
                'genre_1':'',
                'genre_2':'',
                'genre_3':'',
                'to_read':'',
                'currently_reading':'', 
                'favorites':''
            })

            # get genres and shelves only if the book has more than 200 ratings. This is to improve performance
            # by not getting info for books with too low ratings.
            if int(ratings_count) > 200:
                top_genres = self.__extract_top_genres(soup)
                top_shelves = self.__extract_top_shelves(book_id)

                ret_dict['genre_1'] = top_genres[0]
                ret_dict['genre_2'] = top_genres[1]
                ret_dict['genre_3'] = top_genres[2]
                ret_dict['to_read'] = top_shelves['to-read']
                ret_dict['currently_reading'] = top_shelves['currently-reading']
                ret_dict['favorites'] = top_shelves['favorites']

            return ret_dict
        except:
            raise
            #return None

def main():
    # check if the CSV exists and if not, create and write header
    file_path = './data/book_info.tsv'
    if not os.path.isfile(file_path):
        with open(file_path, mode='w', encoding='utf-8') as file:
            columns = ['id', 'title', 'orig_title', 'author', 'language', 
                       'published', 'avg_rating', 'ratings_count', 'review_count', 
                       'genre_1', 'genre_2', 'genre_2', 
                       'to_read', 'currently_reading', 'favorites']
            file.write('\t'.join(columns) + '\n')

    # get info for 5000 random books    
    for i in range(5000):
        book_info = gr_book_info('random')
        if book_info.info != None:
            book_info_values = list(book_info.info.values())
            with open(file_path, mode='a', encoding='utf-8') as file:
                line = '\t'.join(book_info_values) + '\n'
                file.write(line)
                file.close()

if __name__ == '__main__':
    main()