import os
import json
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.writing import AsyncWriter
import sys

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


def tokenize(text):
	# tokenizzazione
	tokens = nltk.word_tokenize(text)

	# Eliminazione di stopwords e punteggiatura
	tokens2 = []
	for t in tokens:
		if t not in stopwords.words('english') and t.isalnum():
			tokens2.append(t)
	return tokens2


def createSearchableData(root):
	# definizione dello schema dell'indice
	schema = Schema(title=TEXT(stored=True),
					# genre=KEYWORD(stored=True), \
					link=ID(stored=True),
					path=ID(stored=True),
					content=TEXT(stored=True),
					contentData=TEXT)

	# creazione della directory indexdir
	if not os.path.exists("indexdir"):
		os.mkdir("indexdir")

	cwd = os.getcwd()
	print(cwd)

	# Creazione indexWriter, per aggiungere i documenti secondo lo schema
	ix = create_in("indexdir", schema)
	writer = AsyncWriter(ix)

	# Lista dei file da indicizzare
	filepaths = [os.path.join(root, i) for i in os.listdir(root) if i.split(".")[1] == "json"]

	num = 1
	# per ogni percorso trovato...
	for path in filepaths:
		print(f'{num}/{len(filepaths)}')
		num += 1

		fp = open(path, 'r', encoding="utf-8")
		entry = json.loads(fp.read())
		fp.close()
		# print(path)

		fileTitle = entry["title"]
		# fileGenre = fp.readline()
		fileLink = entry["url"]

		# Contenuto in markdown della pagina
		fileContent = entry["content"]

		# la sezione contentData è data dal contenuto preprocessato (tokenizzato)
		fileData = tokenize(fileContent)

		# Aggiunta delò'entry all'indice
		writer.add_document(title=fileTitle,
							path=path,
							# genre=fileGenre, \
							link=fileLink,
							content=fileContent,
							contentData=fileData)
	writer.commit()


cwd = os.getcwd()
root = cwd + "\\documents"
createSearchableData(root)
