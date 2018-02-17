# Goodreads Sentiment Analysis
#### Springboard Data Science - Capstone Project 1

The purpose of this project is to perform sentiment analysis on user reviews retrieved from Goodreads.com review database. Using four sentiment lexicons, I attempt to gague the reviewer's opinion based on the sentiment scores of the review words and predict the reviewer's final score (on a 1-5 scale).

Files in this repo:

- `README.md` - This file
- `Goodreads Sentiment Analysis` - Report.pdf|Report detailing methods and findings
- `Goodreads Sentiment Analysis` - Slides.pdf|Presentationb slides with findings summary
- `gr_sentiment_analysis.sln` - Visual Studio Solution file
- `books_db.py` - Creates SQLite database for storing project data
- `gr_book_info.py` - Module for extracting book information from Goodreads.com
- `gr_book_reviews.py` - Modules for extracting book reviews from Goodreads.com
- `gr_features.py` - Module for extracting and saving feature information from reviews for analysis
- `__main__.py` - Program entry point
- `gr_sentiment_analysis.pyproj` - Visual Studio Project file
- `AFINN-111.txt` - AFINN sentiment lexicon text file
- `bing-negative-words.txt` - Negative words from the Bing Liu sentinment Lexicon text file
- `bing-positive-words.txt` - Positive Words from the Bing Liu sentiment Lexicon text file
- `subjclueslen1-HLTEMNLP05.tff` - MPQA sentiment lexicon text file
- `inquirerbasic.xls` - Harvard Inquirer sentiment lexicon Excel file
- `Review Stats Data Exploration.ipynb` - Jupyter notebook for exploratory data analysis
- `DecisionTrees.ipynb` - Jupyer notebook for Decision Trees classificaiton model
- `KNN.ipynb` - Jupyer notebook for Decision Trees classificaiton model
- `MLP.ipynb` - Jupyer notebook for MLP classificaiton model
- `MLP - One Hot.ipynb` - Jupyer notebook for MLP classificaiton model using 2 category classification 
- `Naive Bayes.ipynb` - Jupyer notebook for Naive Bayes classificaiton model
- `Random Forest.ipynb` - Jupyer notebook for Random Forest classificaiton model



Usage: From command line enter -<br>
`python gr_sentiment_analysis`

This will run the `__main__.py` file containing the program entry point. The `__main__.py` file will execute all the steps to build the database, retrieve book information, get reviews for eligable titles, and extract features. All data is saved to the `books.db` file in the `data` subfolder.