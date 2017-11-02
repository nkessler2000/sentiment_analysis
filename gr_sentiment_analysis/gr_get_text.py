import requests

bookurl = 'https://www.goodreads.com/book/show/234225'
shelfurl = 'https://www.goodreads.com/work/shelves/3634639'

with open('./data/dune.html', 'w',  encoding='utf-8') as file:
    text = requests.get(bookurl).text
    file.write(text)

with open('./data/dune_shelves.html', 'w', encoding='utf-8') as file:
    text = requests.get(shelfurl).text
    file.write(text)
