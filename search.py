#!/usr/bin/python
import cgi
import lucene
import json
import sys

# Pretreatment
INDEX_DIR = 'index'
lucene.initVM()
directory = lucene.SimpleFSDirectory(lucene.File(INDEX_DIR))
analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)

def ascii_encode_dict(data):
    ascii_encode = lambda x: x.encode('ascii')
    return dict(map(ascii_encode, pair) for pair in data.items())

def search(input_q, web_data):
	numberOfHits = 5
	collector = lucene.TopScoreDocCollector.create(numberOfHits, True)
	searcher = lucene.IndexSearcher(directory, True)
	qp = lucene.QueryParser(lucene.Version.LUCENE_CURRENT,'word',analyzer)
	qp.setDefaultOperator(lucene.QueryParser.Operator.OR)
	query = qp.parse(input_q)

	searcher.search(query, collector)
	score_docs = collector.topDocs().scoreDocs

	count = 0
	url_list = []
	for my_doc in score_docs:
		#print my_doc.score
		doc = searcher.doc(my_doc.doc)
		# count,'|', doc['page_num'] ,'|',web_data[doc['page_num']]
		url_list.append('http://' + web_data[doc['page_num']])
		count += 1
	return url_list


if __name__ == '__main__':
	form = cgi.FieldStorage()
	searchterm = form.getvalue('keyword')

	with open("bookkeeping.json") as data_file:
		web_data = json.load(data_file, object_hook=ascii_encode_dict)

	query = str(searchterm)
	url_list = search(query, web_data)

	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<style>"
	print ".textbox {width: 300px; height: 30px;font-size: 18px;}"
	print ".go_btn{ width: 55px;height: 80px;font-size: 20px;}"
	print "</style>"
	print"<meta charset=\"UTF-8\"><title>Search Engine</title>"
	print "</head>"
	print "<body>"
	print "<form name=\"search\" action=\"search.py\" method=\"get\">"
	print "<input name=\"keyword\" type=\"text\" value=\""+str(searchterm)+"\" class=\"textbox\"><input type=\"submit\" name=\"submit\" value=\"go!\" class=\"go_btn\">"
	print "</form>"
	if len(url_list) == 0:
		print "<h1> No website found about this query."
	else:
		print "<h1> Top 5 hits about search query:"
		for url in url_list:
			print "<h2><a href="+str(url)+">"+str(url)+"</a>"	
	print "</body>"
	print "</html>"