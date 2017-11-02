import gr_review_scraper as gr
import pandas as pd
import numpy as np
import regex as re
import matplotlib.pyplot as plt
#import seaborn as sns
import os


def words_to_list(str):
    """separate out space separated words from input string. Strip all control characters and punctioation except ' and -.
    Change each word to lower-case. Returns words as a list."""
    try:
        # strip out control characters and punctuation from words 
        words_list = ''.join(c for c in re.sub("[^\P{P}-']+", ' ', str) if ord(c) >= 32).split(' ')
        # remove blanks and convert to lower-case
        words_list = [word.lower() for word in words_list if word != '']
        return words_list
    except:
        raise

def words_to_rows(reviews, id):
    # convert review text words for the given ID to a list
    rating = int(reviews.loc[reviews['id'] == id, 'rating'])
    review_text = np.array(reviews.loc[reviews['id'] == id, 'text'])
    words = words_to_list(review_text[0])
    # returna new dataframe 
    df = pd.DataFrame({
        'review_id':id,
        'rating':rating,
        'word':words
        }
    )
    return df


def main():
    # read AFINN words list to pandas DF
    try:
        afinn = pd.read_csv('./AFINN-111.txt', sep='\t', names=['word', 'score'])
        # convert score column to int
        afinn['score'] = afinn['score'].astype('int')
    except Exception as e:
        print("Error importing AFINN-111.txt:\n {0}".format(e))
        return
    
    # download Dune reviews and save as CSV if not present
    # get top 30 reviews for Dune. Save to a CSV so we don't have to keep downloading it! 
    if not os.path.isfile('./data/dune.csv'):
        try:
            reviews = gr.top30_reviews_by_id(234225)
            pd.DataFrame(reviews).to_csv('./data/dune.csv', encoding='utf-8', index=False)
        except Exception as e:
            print("Error retrieving top 30 reviews:\n {0}".format(e))
            return

    # load Dune CSV
    reviews = pd.read_csv('./data/dune.csv')

    # reshape the dataframe. We want one word per row for each word in our reviews
    words_df = pd.DataFrame(columns=['review_id', 'rating', 'word'])

    for id in reviews['id']:
        df = words_to_rows(reviews, id)
        words_df = words_df.append(df)

    # sort by ID and reset index
    words_df.sort_values('review_id').reset_index()

    words_df = pd.merge(words_df, afinn, how='left', on='word')

    # group by ID and do some aggregation
    review_median_sentiment = words_df[pd.notnull(words_df['score'])].groupby(['review_id', 'rating'], as_index=False).mean()
    print(review_median_sentiment)

    # take a look at a boxplot
    #sns.boxplot(data=review_median_sentiment, x='rating', y='score')
    plt.show()

if __name__ == "__main__":
    main()