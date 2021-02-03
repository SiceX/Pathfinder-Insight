import os
import json
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.writing import AsyncWriter

import nltk
from nltk.corpus import stopwords


def tokenize(text):
	# tokenizzazione
	tokens = nltk.word_tokenize(text)

	# Eliminazione di stopwords e punteggiatura
	tokens2 = []
	for t in tokens:
		if t not in stopwords.words('english') and t.isalnum():
			tokens2.append(t)
	return tokens2


def createSearchableData(docsDirectory):
	# definizione dello schema dell'indice
	schema = Schema(docTitle=KEYWORD(stored=True),
					topics=KEYWORD(stored=True, lowercase=True),
					category=ID(stored=True),
					pageUrl=ID(stored=True),
					path=ID(stored=True),
					procContent=TEXT(stored=True),
					markdownContent=STORED)

	# creazione della directory indexdir
	if not os.path.exists("../indexdir"):
		os.mkdir("../indexdir")

	cwd = os.getcwd()
	print(cwd)

	# Creazione indexWriter, per aggiungere i documenti secondo lo schema
	ix = create_in("indexdir", schema)
	writer = AsyncWriter(ix)

	# Lista dei file da indicizzare
	filepaths = [os.path.join(docsDirectory, i) for i in os.listdir(docsDirectory) if i.split(".")[-1] == "json"]

	num = 1
	# per ogni percorso trovato...
	for path in filepaths:
		print(f'{num}/{len(filepaths)}')
		num += 1

		#regex per trovare le frasi "chiave" nella pagina, ovvero quelle usate come inizio di una sezione nel markdown
		topicSearch = re.compile(r"\n####.*\n")

		fp = open(path, 'r', encoding="utf-8")
		entry = json.loads(fp.read())
		fp.close()

		#Titolo tokenizzato
		processedTitle = ' '.join(tokenize(entry["title"]))

		pageUrl = entry["url"]

		# Contenuto in markdown della pagina
		markdownContent = entry["content"]

		#estrazione, "pulizia" e tokenizzazione delle frasi usate come argomento della pagina
		topicSet = set()
		for match in topicSearch.findall(markdownContent):
			topic = str(match).strip(r'\n').strip('#')
			topicSet = topicSet.union(set(tokenize(topic)))
		topics = ' '.join(list(topicSet))

		#la categoria è la pagina padre
		category = str(pageUrl).split(r'/')[3]

		# la sezione contentData è data dal contenuto preprocessato (tokenizzato)
		procContent = ' '.join(tokenize(markdownContent))

		# Aggiunta dell'entry all'indice
		writer.add_document(docTitle=processedTitle,
							topics=topics,
							category=category,
							path=path,
							pageUrl=pageUrl,
							markdownContent=markdownContent,
							procContent=procContent)
	writer.commit()


cwd = os.getcwd()
docsDirectory = r"F:\RepoHDD\Progetti\Gestione dell'Informazione\Pathfinder-Insight\documents" #r"..\documents"
createSearchableData(docsDirectory)
