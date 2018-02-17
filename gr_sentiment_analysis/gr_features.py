import pandas as pd
import numpy as np
import string
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sqlite3


def words_to_list(str):
    """separate out space separated words from input string. Strip all control characters and punctioation except ' and -.
    Change each word to lower-case. Returns words as a list."""
    try:
        # strip out control characters and punctuation from words 
        letter_set = set(string.ascii_letters + "'- ")
        words_list = ''.join(c for c in str if c in letter_set).split(' ')
        # remove blanks and convert to lower-case
        words_list = [word.lower() for word in words_list if word != '']
        return words_list
    except:
        raise

def words_to_rows(review_text, id):
    """ Convert review text words for the given ID to a list. Exclude reviews with fewer than 30 words. Returns a dataframe."""
    if type(review_text) == float:
        return pd.DataFrame()
    words = words_to_list(review_text)
    if len(words) < 30:
        return pd.DataFrame()
    # returna new dataframe 
    df = pd.DataFrame({
        'review_id':id,
        'word':words
        }
    )
    return df

def review_features(row):
    """For use with apply, takes a row from the reviews table and returns the number of uppercase words with a length > 1 and number of 
    exclamation points. Returns as a pandas Series"""
    letter_set = set(string.ascii_uppercase + " ")
    upper_words = ''.join(c for c in row[1] if c in letter_set).split(' ')
    upper_words = [w for w in upper_words if len(w) > 1]
    exclamation_count = row[1].count('!')
    ret = pd.Series({'review_id':row[0], 'cap_words_count':len(upper_words), 'exclamation_count':exclamation_count})
    return ret

def extract_features():
    # set up database connection and get data
    dir = os.path.dirname(__file__)
    db_file = os.path.join(dir, 'data/books.db')
    conn = sqlite3.connect(db_file)
            
    # get review words for each review and return as a table of words
    sql = '''SELECT review_id, review_text FROM reviews 
        WHERE review_id > (SELECT IFNULL(MAX(review_id), 0) FROM review_words) 
        AND review_text IS NOT NULL
        AND review_id NOT IN (SELECT DISTINCT review_id FROM review_words)
        ORDER BY review_id'''
        
    reviews_df = pd.read_sql_query(sql, con=conn, chunksize=10000)

    for chunk in reviews_df:
        for row in chunk.itertuples(index=False):
            rev_id = row[0]
            rev_text = row[1]

            df = words_to_rows(rev_text, int(rev_id))
            if len(df) > 0:
                df.to_sql(con=conn, name='review_words', index=False, if_exists='append')

    # get features (num of cap words, num of ! characters) from review text

    sql = '''SELECT review_id, review_text FROM reviews 
        WHERE review_id > (SELECT IFNULL(MAX(review_id), 0) FROM review_features) 
        AND review_text IS NOT NULL 
        AND review_id NOT IN (SELECT DISTINCT review_id FROM review_features) 
        ORDER BY review_id'''

    reviews_df = pd.read_sql_query(sql,con=conn,chunksize=10000)
    
    for chunk in reviews_df:
        result = chunk.apply(review_features, axis='columns')
        result.to_sql(con=conn, name='review_features', index=False, if_exists='append')

    # now that we have all our words and all our sentiment scores in the database, now is the time to actually pull the data out and do some computations
    word_sentiment_sql = word_sentiment_sql = '''SELECT rw.review_id, 
			a.score AS afinn_score, 
			o.sentiment AS bing_sentiment,
			m.polarity AS mpqa_polarity,
			i.polarity AS inq_polarity
        FROM review_words rw
        LEFT JOIN afinn_lexicon a ON a.word = rw.word
        LEFT JOIN bing_lexicon o ON o.word = rw.word
        LEFT JOIN mpqa_lexicon m ON m.word = rw.word
        LEFT JOIN inquirer_lexicon i ON i.word = rw.word
        '''

    word_sentiment_df = pd.read_sql_query(word_sentiment_sql, con=conn)
    # group by review ID
    words_by_id = word_sentiment_df.groupby('review_id')
    
    # get mean, median, and sum
    words_mean = words_by_id[['afinn_score', 'bing_sentiment', 'mpqa_polarity', 'inq_polarity']].mean()
    words_mean.columns = ['afinn_mean', 'bing_mean', 'mpqa_mean', 'inq_mean']
    
    words_median = words_by_id[['afinn_score', 'bing_sentiment', 'mpqa_polarity', 'inq_polarity']].median()
    words_median.columns = ['afinn_median', 'bing_median', 'mpqa_median', 'inq_median']
    
    words_sum = words_by_id[['afinn_score', 'bing_sentiment', 'mpqa_polarity', 'inq_polarity']].sum()
    words_sum.columns = ['afinn_sum', 'bing_sum', 'mpqa_sum', 'inq_sum']
    
    pos_afinn_count = word_sentiment_df[word_sentiment_df['afinn_score'] > 0].groupby('review_id')[['review_id']].count()
    pos_afinn_count.columns = ['pos_afinn_count']
    
    neg_afinn_count = word_sentiment_df[word_sentiment_df['afinn_score'] < 0].groupby('review_id')[['review_id']].count()
    neg_afinn_count.columns = ['neg_afinn_count']
    
    pos_bing_count = word_sentiment_df[word_sentiment_df['bing_sentiment'] == 1].groupby('review_id')[['review_id']].count()
    pos_bing_count.columns = ['pos_bing_count']
    
    neg_bing_count = word_sentiment_df[word_sentiment_df['bing_sentiment'] == 0].groupby('review_id')[['review_id']].count()
    neg_bing_count.columns = ['neg_bing_count']   
    
    pos_mpqa_count = word_sentiment_df[word_sentiment_df['mpqa_polarity'] == 1].groupby('review_id')[['review_id']].count()
    pos_mpqa_count.columns = ['pos_mpqa_count']
    
    neg_mpqa_count = word_sentiment_df[word_sentiment_df['mpqa_polarity'] == 0].groupby('review_id')[['review_id']].count()
    neg_mpqa_count.columns = ['neg_mpqa_count']   
    
    pos_inq_count = word_sentiment_df[word_sentiment_df['inq_polarity'] == 1].groupby('review_id')[['review_id']].count()
    pos_inq_count.columns = ['pos_inq_count']
    
    neg_inq_count = word_sentiment_df[word_sentiment_df['inq_polarity'] == 0].groupby('review_id')[['review_id']].count()
    neg_inq_count.columns = ['neg_inq_count']   

    word_counts = words_by_id[['review_id']].count()
    word_counts.columns = ['word_count']
            
    # join results together
    review_stats = pd.read_sql('SELECT review_id, rating FROM reviews WHERE review_id IN (SELECT DISTINCT review_id FROM review_words)', con=conn)
    review_stats = review_stats.join(word_counts, on='review_id', how='left')
    review_stats = review_stats.join(words_mean, on='review_id', how='left')
    review_stats = review_stats.join(words_median, on='review_id', how='left')
    review_stats = review_stats.join(words_sum, on='review_id', how='left')
    review_stats = review_stats.join(pos_afinn_count, on='review_id', how='left')
    review_stats = review_stats.join(neg_afinn_count, on='review_id', how='left')
    review_stats = review_stats.join(pos_bing_count, on='review_id', how='left')
    review_stats = review_stats.join(neg_bing_count, on='review_id', how='left')
    review_stats = review_stats.join(pos_mpqa_count, on='review_id', how='left')
    review_stats = review_stats.join(neg_mpqa_count, on='review_id', how='left')
    review_stats = review_stats.join(pos_inq_count, on='review_id', how='left')
    review_stats = review_stats.join(neg_inq_count, on='review_id', how='left')

    # replace NaNs in the pos/neg count columns with zeros 
    review_stats['pos_afinn_count'].fillna(0, inplace=True)
    review_stats['neg_afinn_count'].fillna(0, inplace=True)
    review_stats['pos_bing_count'].fillna(0, inplace=True)
    review_stats['neg_bing_count'].fillna(0, inplace=True)
    review_stats['pos_mpqa_count'].fillna(0, inplace=True)
    review_stats['neg_mpqa_count'].fillna(0, inplace=True)
    review_stats['pos_inq_count'].fillna(0, inplace=True)
    review_stats['neg_inq_count'].fillna(0, inplace=True)

    # add totals columns
    review_stats['total_afinn_count'] = review_stats['pos_afinn_count'] + review_stats['neg_afinn_count']
    review_stats['total_bing_count'] = review_stats['pos_bing_count'] + review_stats['neg_bing_count']
    review_stats['total_mpqa_count'] = review_stats['pos_mpqa_count'] + review_stats['neg_mpqa_count']
    review_stats['total_inq_count'] = review_stats['pos_inq_count'] + review_stats['neg_inq_count']

    # include ratios of positive to negative counts for AFINN score and Bing sentiment
    review_stats['pos_afinn_ratio'] = review_stats['pos_afinn_count'] / review_stats['total_afinn_count']
    review_stats['pos_bing_ratio'] = review_stats['pos_bing_count'] / review_stats['total_bing_count']
    review_stats['pos_mpqa_ratio'] = review_stats['pos_mpqa_count'] / review_stats['total_mpqa_count']
    review_stats['pos_inq_ratio'] = review_stats['pos_inq_count'] / review_stats['total_inq_count']
    
    review_stats['neg_afinn_ratio'] = review_stats['neg_afinn_count'] / review_stats['total_afinn_count']
    review_stats['neg_bing_ratio'] = review_stats['neg_bing_count'] / review_stats['total_afinn_count']
    review_stats['neg_mpqa_ratio'] = review_stats['neg_mpqa_count'] / review_stats['total_mpqa_count']
    review_stats['neg_inq_ratio'] = review_stats['neg_inq_count'] / review_stats['total_inq_count']

    # replace inf values resultsint from division by 
    review_stats['pos_afinn_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['neg_afinn_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['pos_bing_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['neg_bing_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['pos_mpqa_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['neg_mpqa_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['pos_inq_ratio'].replace(np.inf, np.NaN, inplace=True)
    review_stats['neg_inq_ratio'].replace(np.inf, np.NaN, inplace=True)

    # other calculated columns
    review_stats['pos_afinn_density'] = review_stats['pos_afinn_count'] / review_stats['word_count']
    review_stats['pos_bing_density'] = review_stats['pos_bing_count'] / review_stats['word_count']
    review_stats['pos_mpqa_density'] = review_stats['pos_mpqa_count'] / review_stats['word_count']
    review_stats['pos_inq_density'] = review_stats['pos_inq_count'] / review_stats['word_count']
    
    review_stats['neg_afinn_density'] = review_stats['neg_afinn_count'] / review_stats['word_count']
    review_stats['neg_bing_density'] = review_stats['neg_bing_count'] / review_stats['word_count']
    review_stats['neg_mpqa_density'] = review_stats['neg_mpqa_count'] / review_stats['word_count']
    review_stats['neg_inq_density'] = review_stats['neg_inq_count'] / review_stats['word_count']
    
    review_stats['afinn_words_ratio'] = review_stats['afinn_sum'] / review_stats['word_count']
    review_stats['bing_words_ratio'] = review_stats['bing_sum'] / review_stats['word_count']
    review_stats['mpqa_words_ratio'] = review_stats['mpqa_sum'] / review_stats['word_count']
    review_stats['afinn_words_ratio'] = review_stats['inq_sum'] / review_stats['word_count']

    # add in review features data of ! and all caps word counts
    review_features = pd.read_sql('SELECT review_id, cap_words_count, exclamation_count FROM review_features', con=conn)
    review_stats = pd.merge(review_stats, review_features, on='review_id', how='left')
    review_stats['all_caps_density'] = review_stats['cap_words_count'] / review_stats['word_count']
    
    # insert into database
    review_stats.to_sql(con=conn, name='review_stats', index=False, if_exists='replace')

def main():
    extract_features()

if __name__ == "__main__":
    main()