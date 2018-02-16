import pandas as pd
import numpy as np
import os
from gr_book_info import gr_book_info

def main():
    # load book info from tsv file into DataFrame
    book_info_file = './data/book_info_raw.tsv'
    book_info_raw = pd.read_csv(book_info_file, 
                                header=0, 
                                sep='\t', 
                                parse_dates=['published'],
                                encoding='utf-8') 

    # filter reviews where review count is >= 40
    book_info_40 = book_info_raw.loc[book_info_raw['review_count'] >=40]


	# next, we want to select book IDs for reviews where with 40 or more reviews but where any of the 
	# shelves values (favorites, reading, to_read) are missing
    missing_filter = pd.isnull(book_info_40['to_read']) | pd.isnull(book_info_40['currently_reading']) | pd.isnull(book_info_40['favorites'])
    book_info_missing = book_info_40.loc[missing_filter]
	
	# get a list 
    id_list = list(book_info_missing['id'])
	# get book info and output to a file.
    
    failed = get_book_info(id_list)

    while len(failed) > 0:
    	failed = get_book_info(failed)
		

def get_book_info(id_list):
	failed = []
	file_path = './data/book_info_missing_shelves.tsv'
	
	for book_id in id_list:
		try:
			book_info = gr_book_info(book_id)
		except Exception as e:
			# if there's a problem reading a book info, skip and go to next
			print(e)
			failed.append(book_id)
			continue
		if book_info.info != None:
			book_info_values = list(book_info.info.values())
			with open(file_path, mode='a', encoding='utf-8') as file:
				line = '\t'.join(book_info_values) + '\n'
				file.write(line)
				file.close()
	return failed
	
if __name__ == '__main__':
    main()
