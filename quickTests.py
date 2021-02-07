import json
import os
#from scrapy import cmdline
#from pdfreader import SimplePDFViewer

#cmdline.execute("scrapy crawl pfsrd".split())
#import nltk
#from nltk.corpus import stopwords

#
# def tokenize(text):
# 	# tokenizzazione
# 	tokens = nltk.wordpunct_tokenize(text)
#
#
# 	# Eliminazione di stopwords e punteggiatura
# 	tokens2 = []
# 	for t in tokens:
# 		if t not in stopwords.words('english') and t.isalnum():
# 			tokens2.append(t)
# 	return tokens2
#
#
#
# print(tokenize("basics-ability-scores"))


#extract text content from .pdf files and generate it's json file

# cwd = os.getcwd()
# root = cwd + "\\documents"
# filepaths = [os.path.join(root, i) for i in os.listdir(root) if i.split(".")[1] == "pdf"]
# num = 1
# for path in filepaths:
#     filename = path.split("\\")[-1]
#     print(f'{filename}, {num}/{len(filepaths)}')
#     jsonFile = {
#         "title": filename.split(".")[0],
#         "url": path,
#         "content": None
#     }
#     with open(path, "rb") as fd:
#         text = ''
#         viewer = SimplePDFViewer(fd)
#         page = 1
#         for canvas in viewer:
#             print(f'{filename}, {num}/{len(filepaths)}: page {viewer.current_page_number}')
#             text = text + ' ' + canvas.text_content
#         jsonFile["content"] = text
#
#     with open(f'{root}\\{filename}.json', 'x') as newFile:
#         json.dump(jsonFile, newFile)

# from whoosh import index
# ix = index.open_dir("indexdir")
# searcher = ix.searcher()
# #list(searcher.lexicon("procContent"))
# with open("Preprocessing/pathfinderWords.txt", 'w') as file:
# 	lexicon = list(searcher.lexicon("procContent"))
# 	lessicono = ""
# 	for e in lexicon:
# 		if e.decode("utf-8").isalpha():
# 			lessicono = f'{lessicono} {e.decode("utf-8")}'
# 	#lexicon = ' '.join(e) for e in lexicon
# 	#print(lexicon)
# 	file.write(lessicono)

# from autocorrect.word_count import count_words
# count_words("utils/pathfinderWords.txt", 'en')

