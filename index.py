import os, re, sys, lucene
from BeautifulSoup import BeautifulSoup
import lxml.html

SYMBOL ='[-_\s\n,.<>/?:;\"\'\[\]{ }\\\|`~!@#$%^&*()=\+]+'
pattern = re.compile(SYMBOL)

# Pretreatment
INDEX_DIR = 'index'
lucene.initVM()
directory = lucene.SimpleFSDirectory(lucene.File(INDEX_DIR))
analyzer = lucene.StandardAnalyzer(lucene.Version.LUCENE_CURRENT)

writer = lucene.IndexWriter(directory,analyzer,True,lucene.IndexWriter.MaxFieldLength.UNLIMITED)

def visible(element):
	if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
		return False
	elif re.match('<!--.*-->', str(element)):
		return False
	return True

def get_page_num(file):
	tmp = file.split('/')
	return tmp[1]+'/'+tmp[2]

def get_data(file):
	data = {}
	page_num = get_page_num(file)
	#print "get page num: ",page_num
	input_file = open(file,'r')

	#print "in Get data"

	#print 'PAGE IN HTML FORMAT'
	try:
		visible_texts = filter(visible, BeautifulSoup(input_file).findAll(text=True))
		string_list = []
		for text in visible_texts:
			if '\n' != text:
				string_list.append(text.encode('ascii', 'ignore').lower())

		for string in string_list:
			tmp_word_list = pattern.split(string)
			for word in tmp_word_list:
				if len(word) > 2:
					if word not in data.keys():
						data[word] = page_num
	except UnicodeEncodeError:
		print "UnicodeEncodeError occur"
#	else:
#		print "PAGE NOT IN HTML FORMAT"


	return data

	
def build_index(data, num_doc):
	for word, page_num in data.items():
		doc = lucene.Document()
		doc.add(lucene.Field('word', word, lucene.Field.Store.YES, lucene.Field.Index.ANALYZED))
		doc.add(lucene.Field('page_num', page_num, lucene.Field.Store.YES, lucene.Field.Index.NOT_ANALYZED))
		writer.addDocument(doc)
		num_doc += 1
	return num_doc


if __name__ == '__main__':
	# data = {word:[page_num]]}
	num_doc = 0
	for root, dirs, files in os.walk("WEBPAGES_RAW"):
		for file in files:
			if (file[0] != '.') and ('json' not in file) and ('tsv' not in file):
				path = ''
				path = root+'/'+file
				print "processing : ", path
				data = get_data(path)
				num_doc = build_index(data, num_doc)

	writer.optimize()
	writer.close()
	print "Processed ", num_doc, " documents"
	#print "collected: ", len(data), " unique words"
