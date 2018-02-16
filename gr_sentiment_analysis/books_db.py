import sqlite3
import pandas as pd

# This script is used for creating the SQLite database and tables which are used for data storage for this project.
# The script also imports the sentiment lexicons from flat files into database tables

# Create table SQL DDL
bookinfo_tbl = '''CREATE TABLE IF NOT EXISTS book_info (
    id INT NOT NULL,
    title TEXT,
    orig_title TEXT,
    author TEXT,
    published DATE,
    language TEXT,
    avg_rating REAL,
    ratings_count INT,
    review_count INT,
    genre_1 TEXT,
    genre_2 TEXT,
    genre_3 TEXT,
    to_read INT,
    currently_reading INT,
    favorites INT
    )
'''

bookinfo_clean_tbl = '''CREATE TABLE IF NOT EXISTS book_info_clean (
    id INT PRIMARY KEY NOT NULL,
    title TEXT, 
    author TEXT,
    published DATE,
    language TEXT,
    avg_rating REAL,
    ratings_count INT,
    review_count INT,
    genre_1 TEXT,
    genre_2 TEXT,
    genre_3 TEXT,
    to_read INT,
    currently_reading INT,
    favorites INT
    )
'''

reviews_tbl = '''CREATE TABLE IF NOT EXISTS reviews (
    review_id INT PRIMARY KEY NOT NULL,
    book_id INT NOT NULL,
    review_date DATE,
    rating INT,
    review_text TEXT
    )
'''


review_words_tbl = '''CREATE TABLE IF NOT EXISTS review_words (
    review_id INT NOT NULL,
    word TEXT NOT NULL
    )
'''

review_features_tbl = '''CREATE TABLE IF NOT EXISTS review_features (
        review_id INT NOT NULL PRIMARY KEY,
        cap_words_count INT, 
        exclamation_count INT
        )
'''

def build_db():
    # create connection. Creates DB file if doesn't exit
    conn = sqlite3.connect('./data/books.db')

    # Build database tables
    conn.execute(bookinfo_tbl)
    conn.execute(bookinfo_clean_tbl)
    conn.execute(reviews_tbl)
    conn.execute(review_words_tbl)
    conn.execute(review_features_tbl)
    
    
    # read AFINN words list to DF and load to database table
    try:
        afinn = pd.read_csv('./data/AFINN-111.txt', sep='\t', names=['word', 'score'])
        # convert score column to int
        afinn['score'] = afinn['score'].astype('int')
        # create table and load
        conn.execute(afinn_tbl)
        afinn.to_sql(con = conn, name='afinn_lexicon', index=False, if_exists='replace')
    except Exception as e:
        print("Error importing AFINN-111.txt:\n {0}".format(e))
        quit()
    
    # read Opinion Lexicon data into database
    try:
        positive_words = pd.read_csv('./data/positive-words.txt', names=['word'], encoding='latin-1', header=None, skiprows=34)
        negative_words = pd.read_csv('./data/negative-words.txt', names=['word'], encoding='latin-1', header=None, skiprows=34)
        # set positive words to a score of 1, and negative to -1
        positive_words['sentiment'] = 1
        negative_words['sentiment'] = 0
        # merge positive and negatives into a signle DF
        opinion_lexicon_df = pd.merge(positive_words, negative_words, how='outer')
        opinion_lexicon_df.sort_values('word', inplace=True)
        opinion_lexicon_df.reset_index(inplace=True, drop=True)
        # create table and load
        conn.execute(opinion_lexicon_tbl)
        opinion_lexicon_df.to_sql(con=conn, name='bing_lexicon', index=False, if_exists='replace')
    except Exception as e:
        print('Error importing Opinion Lexicon file:\n {0}'.format(e))
        quit()
    
    # read MPQA lexicon data into database
    try:
        mpqa_df = pd.DataFrame(columns=['word', 'polarity'])
        mpqa_file = 'c:/users/nick/onedrive/documents/springboard/sentiment_analysis/gr_sentiment_analysis/data/subjclueslen1-HLTEMNLP05.tff'
        
        with open(mpqa_file, mode='r') as file:
            words = []
            polarities = []
            for line in file.readlines():
                # extract the words and sentiment polarity score from each line of the input file
                words.append(re.search(".*word1=(.*)\s{1}pos1",line).group(1))
                polarities.append(1 if re.search('.*priorpolarity=(.*)',line).group(1) == 'positive' else 0)
                
            mpqa_df['word'] = words
            mpqa_df['polarity'] = polarities
    except Exception as e:
        print('Error importing MPQA file:\n {0}'.format(e))
        quit()
    
    # Read Harvard Inquirer lexicon data into database
    try:
        inquirer_file = 'c:/users/nick/onedrive/documents/springboard/sentiment_analysis/gr_sentiment_analysis/data/inquirerbasic.xls'
        inquirer_df = pd.read_excel(inquirer_file)
        
        inquirer_df_new = pd.DataFrame(columns=['word', 'polarity'])
        inquirer_df_new['word'] = inquirer_df['Entry'].str.lower()
        
        # define function for setting polarity value based on Positiv and Negativ column values
        def get_inquirer_polarity(row):
            if row['Positiv'] == 'Positiv':
                return 1
            elif row['Negativ'] == 'Negativ':
                return 0
            else:
                return -1
        
        # then create a polarity column by applying our function to the original DF
        inquirer_df_new['polarity'] = inquirer_df.apply(get_inquirer_polarity, axis=1)
        
        # drop words with a polarity of -1 (i.e. neither postivie nor negative)
        inquirer_df_new = inquirer_df_new[inquirer_df_new['polarity'] != -1]
        
        # get rid of #s in the words and remove duplicates
        inquirer_df_new['word'] = inquirer_df_new['word'].str.replace(r'#\d+', '')
        inquirer_df_new.drop_duplicates('word', inplace=True)
        
        # then  write that to a table
        inquirer_df_new.to_sql(con=conn, name='inquirer_lexicon', index=False, if_exists='replace')
    except Exception as e:
        print('Error importing Harvard Inquirer file:\n {0}'.format(e))
        quit()

def main():
    build_db()

if __name__ == '__main__':
    main()
