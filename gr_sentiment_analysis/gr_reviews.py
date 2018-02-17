import pandas as pd
import requests
import re
import os
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup

import time
from gr_book_info import gr_book_info

class gr_reviews:

    reviews = pd.DataFrame()

    def __init__(self, id, count):
        self.__get_reviews(id, count)
        self.reviews.reset_index()
        # add the book ID
        self.reviews['book_id'] = id
        # reorder columns
        self.reviews = self.reviews[['review_id', 'book_id', 'review_date', 'rating', 'review_text']]

    def __get_reviews(self, id, count):
        """Gets reviews for a given book id"""
        pages_to_parse = count // 30 + 1 if count % 30 != 0 else count // 30 
        for i in range(1, int(pages_to_parse + 1)):
            url = 'https://www.goodreads.com/book/reviews/{0}?page={1}&sort=default&text_only=true'.format(str(id), str(i))
            soup = self.__get_html_source(url)

            # extract the review IDs 
            review_ids = self.__extract_review_ids(soup)
            # extract the review dates
            review_dates = self.__extract_review_dates(soup)
            # extract ratings
            ratings = self.__extract_ratings(soup)
            # extract the review text
            review_text = self.__extract_review_text(soup)
            
            # create a DataFrame
            try:
                page_df = pd.DataFrame({
                    'review_id':review_ids,
                    'review_date':review_dates,
                    'rating':ratings,
                    'review_text':review_text
                    })

                # append to reviews DataFrame
                self.reviews = pd.concat([self.reviews,page_df])
            except ValueError as v:
                print('Failed to load book info for book ID {0}: {1}'.format(id, v))
                dir = os.path.dirname(__file__)
                fail_file = os.path.join(dir, 'data/failed.txt')
                with open(fail_file, 'a') as file:
                    file.write('{0}\n'.format(str(id)))

    def __get_html_source(self, url, retries=0):
        """gets HTML page from URL and returns a BeautifulSoup object"""
        try:
            html_source = requests.get(url).text
            # decode unicode escape characters
            html_source = bytes(html_source, 'utf-8').decode('unicode-escape')
            soup = BeautifulSoup(html_source, 'html.parser').find('div', attrs={'id':'bookReviews'})
            return soup
        except ConnectionError:
            # retry up to 3 times
            if retries <= 3:
                retry = retries + 1
                time.sleep(5)
                self.__get_html_source(url, retries = retry)
            else:
                raise

    def __extract_review_text(self, soup):
        """Gets the review text from the input BeautifulSoup object. Return the reviews as a list"""
        review_text_tags = soup.find_all('div', attrs={'class':'reviewText stacked'})
        review_text = [''.join(c for c in tag.get_text().strip() if ord(c) >= 32) for tag in review_text_tags]
        return review_text

    def __extract_ratings(self, soup):
        """Gets the review ratings from theinput BeautifulSoup objects. Extract the rating text and convert to a
        numerical score. Returns a list"""
        try:
            review_ratings = []
            added_or_rated = soup.find_all('div', attrs={'class':'reviewHeader uitext stacked'})
            for ar in added_or_rated:
                if 'added it' in ar.get_text().strip():
                    rating = 0
                elif 'rated it' in ar.get_text().strip():
                    rating_text = ar.find_next('span', attrs={'class':' staticStars'})
                    rating_text = rating_text.find_next('span').get_text()
                    rating = self.__rating_text_to_num(rating_text)
                else:
                    rating = 0
                review_ratings.append(rating)

            return review_ratings
        except:
            raise

    def __extract_review_ids(self, soup):
        """Gets the review IDs from the input BeautifulSoup object. Returns a list"""
        try:
            id_tags = soup.find_all('div', attrs={'class':'review', 'itemprop':'reviews'})
            review_ids = [int(re.sub('review_', '', tag.get('id'))) for tag in id_tags]
            return review_ids
        except:
            raise

    def __extract_review_dates(self, soup):
        """Gets the review dates from the input BeautifulSoup object. Returns a list"""
        try:
            date_tags = soup.find_all('a', attrs={'class':'reviewDate createdAt right'})
            date_format = '%b %d, %Y'
            review_dates = [datetime.strptime(tag.get_text(), date_format) for tag in date_tags]
            return review_dates
        except:
            raise

    def __rating_text_to_num(self, rating):
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
        else:
            ret = 0
        return ret


def get_info(id):
    book_info = gr_book_info(id)
    return book_info.info

def get_reviews():
    time_start = time.time()

    # set up database connection
    dir = os.path.dirname(__file__)
    db_file = os.path.join(dir, 'data/books.db')
    conn = sqlite3.connect(db_file)

    # load book data from DB 
    #book_info_df = pd.read_csv('./data/book_info_clean.tsv', sep='\t', encoding='utf-8')
    sql = '''SELECT id, title, review_count FROM book_info_clean 
        WHERE id > (SELECT IFNULL(MAX(book_id), 0) FROM reviews)
        AND id NOT IN (SELECT book_id FROM reviews)'''

    books = conn.execute(sql)

    for row in books:
        try:
            book_id = row[0]
            review_count = row[2]
            book_title = row[1]
            # select the min of 300 or review count
            min_val = min([float(review_count), 300])
            
            print('Getting {0} reviews for book {1}:{2}. Start time: {3}'.format(int(min_val), book_id, book_title, datetime.now()))
    
            review_data = gr_reviews(book_id, min_val)
            review_data.reviews.to_sql(con=conn, name='reviews', index=False, if_exists='append')
            #with open(file_path, 'a', encoding='utf-8') as file:
            #    review_data.reviews.to_csv(file, sep='\t', encoding='utf-8', index=False, header=False)

        except Exception as e:
            print('Failed to load book info for book ID {0}: {1}'.format(book_id, e))
            dir = os.path.dirname(__file__)
            fail_file = os.path.join(dir, 'data/failed.txt')
            with open(fail_file, 'a') as file:
                file.write('{0}\n'.format(str(book_id)))

    time_end = time.time()
    print('Finished getting reviews at {0}. Completed in {1} seconds'.format(datetime.now(), time_end - time_start))

def main():
    get_reviews()

if __name__ == '__main__':
    main()