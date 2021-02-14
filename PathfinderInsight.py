import string

import PySimpleGUI as sg
import whoosh.index as index
from whoosh.analysis import StemmingAnalyzer, CharsetFilter
from whoosh.qparser import MultifieldParser
from whoosh.qparser import FuzzyTermPlugin
from whoosh.query import Variations
from whoosh.lang.porter import stem
from whoosh.support.charset import default_charset, charset_table_to_dict

# from nltk.corpus import stopwords
#
# from nltk.stem import PorterStemmer
# from nltk.corpus import wordnet


class Gui:
	""" Create a GUI object """

	def __init__(self):
		sg.theme('DarkBlue3')

		self.layout: list = [
			[sg.Text('Search', size=(11, 1)),
			 sg.Input(size=(40, 1), focus=True, key="TERM"),
			# TODO sg.Checkbox('Synonyms', size=(8, 1), default=False, key='syn_search')],
			 sg.Button('Search', size=(10, 1), bind_return_key=True, key="_SEARCH_")],
            [sg.Text('Legend:\n'
                     'It\'s possible to search by simple keywords, or to narrow it down with boolean operators and '
                     'specifying the fields to search in.\n'
                     'Boolean operators: AND, OR, ANDNOT, ANDMAYBE, NOT\n'
                     'Available fields: title, category, topic, content\n'
                     'Syntax example: title:wizard AND category:core ANDNOT category:archetype', size=(90, 5), background_color=('#336699'))],
			[sg.Output(size=(100, 40), key="_output_")]
		]

		self.window: object = sg.Window('Pathfinder Insight', self.layout, element_justification='left')


charmap = charset_table_to_dict(default_charset)


def tokenize(text):
	""" Questo metodo si occupa di processare la query prima di eseguire la ricerca.
		Nello specifico, elimina le stopwords, esegue lo stemming delle parole e normalizza
		le lettere accentate ed altre lettere in testo appartenente all'ASCII
		:rtype: str
	"""

	analyzer = StemmingAnalyzer() | CharsetFilter(charmap)  # accent_map

	# Eliminazione di stopwords e punteggiatura
	processedText = ""
	for token in analyzer(text):
		processedText = processedText + ' ' + token.text.translate(str.maketrans('', '', string.punctuation)) + '~'
	return processedText.lstrip()


def main():
	""" The main loop for the program """
	g = Gui()
	ix = index.open_dir("indexdir")

	while True:
		event, values = g.window.read()
		g.window["_output_"]('')

		# close windows
		if event is None:
			break

		if event == '_SEARCH_' and values['TERM'] is not None:
			# 	# TODO utilizzo di wordnet per sinonimi
			# 	# if values['syn_search']:
			# 	# 	syn = list()
			# 	# 	for synset in wordnet.synsets(term):
			# 	# 		for lemma in synset.lemmas():
			# 	# 			if lemma.name() != term:
			# 	# 				syn.append(lemma.name())
			# 	# 	syn.insert(0, term)
			# 	# 	print(syn)
			# 	# 	# write every term in the cronologia.txt
			# 	# 	for item in syn:
			# 	# 		f.write("%s\n" % item)

			# il parametro 'fieldboosts' regola quanta importanza dare ai match nei vari campi
			qp = MultifieldParser(["procTitle", "topics", "categories", "procContent"], termclass=Variations,
								  schema=ix.schema, fieldboosts={"procTitle": 1.5, "categories": 1.3})
			qp.add_plugin(FuzzyTermPlugin())

			terms = str(values['TERM'])
			terms = terms.replace("title", "procTitle").replace("topic", "topics") \
				    .replace("category", "categories").replace("content", "procContent")
			print("Searching for >>> " + str(terms))

			with open(r"logs\cronologia.txt", "w") as f:
				f.write(terms)

			# stemming dei termini della query e aggiunta della tilda per ricerca "fuzzy" a quelle effettivamente modificate
			words = terms.split(' ')
			stemmedWords = list()
			for word in words:
				# if word not in stopwords.words('english'):
				stemmed = stem(word)
				if word != stemmed:
					stemmedWords.append(stemmed + '~')
				else:
					stemmedWords.append(stemmed)

			q = qp.parse(' '.join(stemmedWords))

			with ix.searcher() as searcher:
				correction = searcher.correct_query(q=q, qstring=terms, maxdist=3)
				if terms != correction.string:
					print("Did you mean >>> " + correction.string)
				results = searcher.search(q, terms=True)

				numb = 1
				# print(results[0])
				if not results.is_empty():
					for elem in results:
						# print(elem)
						print(f"Result n.{numb} >>> Title: {str(elem['docTitle'])}\n\tScore: {str(elem.score)}\n"
							  f"\tLink to the page: {str(elem['pageUrl'])}\n")
						numb += 1
				else:
					print("No relevant result has been found")


if __name__ == '__main__':
	main()
