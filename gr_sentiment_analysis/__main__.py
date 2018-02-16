import sys
import books_db
import gr_book_info
import gr_features
import gr_reviews

def main():
    # Create database
    books_db.build_db()

    # Get book info from Goodreads for 100,000 random books
    # this step might take a while
    gr_book_info.get_book_info(100000)

    # Clean up book info data
    gr_book_info.clean_book_info()
    
    # get reviews for eligable books
    gr_reviews.get_reviews()

    # extract features
    gr_features.extract_features()


if __name__ == '__main__':
    main()