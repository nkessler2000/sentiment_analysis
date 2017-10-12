import gr_review_scraper as gr
import pandas as pd
import regex as re

def words_to_list(str):
    """separate out space separated words from input string. Strip all control characters and punctioation except ' and -.
    Change each word to lower-case. Returns words as a list."""
    try:
        # strip out control characters and punctuation from words 
        words_list = ''.join(c for c in re.sub("[^\P{P}-']+", '', str) if ord(c) >= 32).split(' ')
        # remove blanks and convert to lower-case
        words_list = [word.lower() for word in words_list if word != '']
        return words_list
    except Exception as e:
        print("Error converting words in input string to list:\n{0}".format(e))


def main():
    # read AFINN words list to pandas DF
    try:
        afinn = pd.read_csv('./AFINN-111.txt', sep='\t', names=['word', 'score'])
        # convert score column to int
        afinn['score'] = afinn['score'].astype('int')
    except FileExistsError:
        print("AFINN-111.txt file not found. Exiting...")
        return
    except Exception as e:
        print("Error importing AFINN-111.txt:\n {0}".format(e))
        return
    
    # get book review for Dune
    try:
        review = gr.get_review_by_id(2348449)
    except Exception as e:
        print("Error retrieving review:\n {0}".format(e))

    # extract words into list and convert to panda DF
    review_words = pd.DataFrame({'word':words_to_list(review['review_text'])})
    # join words to sentiment score DF
    review_word_scores = pd.merge(review_words, afinn, how='inner', on='word')

    # print results
    print(review_word_scores)
    print("Sum of word scores: {0}".format(review_word_scores['score'].sum()))


if __name__ == "__main__":
    main()