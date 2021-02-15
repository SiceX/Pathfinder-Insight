import os
import json
import string
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.writing import AsyncWriter
from whoosh.analysis import StandardAnalyzer, StemmingAnalyzer, CharsetFilter
from whoosh.support.charset import default_charset, charset_table_to_dict

charmap = charset_table_to_dict(default_charset)


def processText(text):
	""" Questo metodo si occupa di processare il testo prima di inserirlo nell'index.
        Nello specifico, elimina i caratteri di punteggiatura e scarta le parole lunghe solo una lettera.
        Inoltre, elimina anche le stopwords, esegue lo stemming delle parole e normalizza
        le lettere accentate ed altre lettere in testo appartenente all'ASCII
        :rtype: list
    """

	#(, filterStopwords=False, stemming=False, normalizeAccents=False, minLength=1)

	# tokenizzazione
	# tokens = nltk.wordpunct_tokenize(text)

	# tokenizer = RegexTokenizer()

	# if stemming:
	# 	if filterStopwords:
	# 		analyzer = StemmingAnalyzer()
	# 	else:
	# 		analyzer = StemmingAnalyzer(stoplist=None)
	# else:
	# 	if filterStopwords:
	# 		analyzer = StandardAnalyzer()
	# 	else:
	# 		analyzer = StandardAnalyzer(stoplist=None)
	# if normalizeAccents:

	analyzer = StemmingAnalyzer() | CharsetFilter(charmap)  # accent_map

	# Eliminazione di stopwords e punteggiatura
	processedText = []
	for token in analyzer(text):
		tokenText = token.text.translate(str.maketrans('', '', string.punctuation))
		if len(tokenText) > 1:
			processedText.append(tokenText)
	return processedText


def createSearchableData(docsDirectory):
	# definizione dello schema dell'indice
	schema = Schema(docTitle=STORED,
					procTitle=KEYWORD(lowercase=True),
					topics=KEYWORD(stored=True, lowercase=True),
					categories=KEYWORD(stored=True, lowercase=True),
					pageUrl=ID(stored=True),
					procContent=TEXT)

	cwd = os.getcwd()
	print(cwd)

	# creazione della directory indexdir
	if not os.path.exists("indexdir"):
		os.mkdir("indexdir")

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

		fp = open(path, 'r', encoding="utf-8")
		entry = json.loads(fp.read())
		fp.close()

		docTitle = entry["title"]

		# Titolo tokenizzato, con attenzione a possibili caratteri unicode da trasformare in caratteri ASCII
		processedTitle = list(set(processText(docTitle)))
		#, filterStopwords=True, stemming=True, normalizeAccents=True, minLength=0

		pageUrl = entry["url"]

		# Contenuto in markdown della pagina
		markdownContent = entry["content"]

		# regex per trovare le frasi "chiave" nella pagina, ovvero quelle usate come inizio di una sezione nel markdown
		topicSearch = re.compile(r"\n####.*\n")

		# preprocessing (filtro stopwords e normalizzazione) delle frasi usate come argomento della pagina
		topicSet = set()
		for match in topicSearch.findall(markdownContent):
			topic = str(match).strip(r'\n').strip('#')
			topicSet = topicSet.union(set(processText(topic)))
			#, filterStopwords=True, stemming=True, normalizeAccents=True
		topics = list(topicSet)

		# le categorie sono le pagina padre dopo la homepage. Dopo il processing, vengono fatte passare per un set
		# per eliminare i duplicati.
		categoeries = list(set(processText(' '.join(str(pageUrl).split(r'/')[3:-2]))))
		#, filterStopwords=True, stemming=True, normalizeAccents=True

		# precedentemente:
		# category = processText(category, filterStopwords=True, normalizeAccents=True)

		# la sezione contentData è data dal contenuto preprocessato: stemming e normalizzazione
		procContent = processText(markdownContent)
		#, filterStopwords=True, stemming=True, normalizeAccents=True

		# Aggiunta dell'entry all'indice
		writer.add_document(docTitle=docTitle,
							procTitle=processedTitle,
							topics=topics,
							categories=categoeries,
							pageUrl=pageUrl,
							procContent=procContent)
	writer.commit()


docsDir = "documents"  # "\prova"
createSearchableData(docsDir)
