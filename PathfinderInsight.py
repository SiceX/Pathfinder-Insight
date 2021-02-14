import PySimpleGUI as sg
import whoosh.index as index
from whoosh.qparser import MultifieldParser
from whoosh.qparser import FuzzyTermPlugin
from whoosh.query import Variations
from whoosh.lang.porter import stem
from whoosh.lang.wordnet import Thesaurus
from whoosh.support.charset import default_charset, charset_table_to_dict


class Gui:
	""" Create a GUI object """

	def __init__(self):
		sg.theme('DarkBlue3')

		self.layout: list = [
			[sg.Text('Search', size=(11, 1)),
			 sg.Input(size=(40, 1), focus=True, key="TERM"),
			 sg.Checkbox('Synonyms', size=(8, 1), default=False, key='syn_search'),
			 sg.Button('Search', size=(10, 1), bind_return_key=True, key="_SEARCH_")],
            [sg.Text('Legend:\n'
                     'It\'s possible to search by simple keywords, or to narrow it down with boolean operators and '
                     'specifying the fields to search in. It\'s also possible to extend the search to synonyms, with an '
					 'added cost on query time.\n'
                     'Boolean operators: AND, OR, ANDNOT, ANDMAYBE, NOT\n'
                     'Available fields: title, category, topic, content\n'
                     'Syntax example: title:wizard AND category:core ANDNOT category:archetype', size=(90, 5), background_color=('#336699'))],
			[sg.Output(size=(100, 40), key="_output_")]
		]

		self.window: object = sg.Window('Pathfinder Insight', self.layout, element_justification='left')


charmap = charset_table_to_dict(default_charset)
booleanTokens = {"AND", "OR", "ANDNOT", "ANDMAYBE", "NOT"}


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

			# il parametro 'fieldboosts' regola quanta importanza dare ai match nei vari campi
			qp = MultifieldParser(["procTitle", "topics", "categories", "procContent"], termclass=Variations,
								  schema=ix.schema, fieldboosts={"procTitle": 1.5, "categories": 1.3})
			qp.add_plugin(FuzzyTermPlugin())

			terms = str(values['TERM'])
			terms = terms.replace("title", "procTitle").replace("topic", "topics") \
				    .replace("category", "categories").replace("content", "procContent")

			# Modifica della query immessa con aggiunta dei sinonimi nel caso l'opzione sia abilitata, con attenzione
			# al riportare i token booleani senza modifiche ed a tradurre correttamente la definizione dei campi in cui
			# ricercare i termini se richiesti.
			if values['syn_search']:
				with open("utils/wn_s.pl", "r") as f:
					thesaurus = Thesaurus.from_file(f)
				termsWithSynonyms = []
				for term in terms.split(" "):
					field = None
					if ":" in term:
						field = term.split(":")[0]
						term = term.split(":")[1]
					if term not in booleanTokens:
						termSynonyms = thesaurus.synonyms(term)
						if field is not None:
							termSynonyms = [f"{field}:{t}" for t in termSynonyms]
							termSynonyms.append(f"{field}:{term}")
						else:
							termSynonyms.append(term)
						termsWithSynonyms.append(" OR ".join(termSynonyms))
					else:
						termsWithSynonyms.append(term)
				terms = ' '.join(termsWithSynonyms)

			print("- Searching for >>> " + str(terms))

			# stemming dei termini della query e aggiunta della tilde per ricerca "fuzzy" a quelle effettivamente modificate
			words = terms.split(' ')
			stemmedWords = list()
			for word in words:
				stemmed = stem(word)
				if word != stemmed:
					stemmedWords.append(stemmed + '~')
				else:
					stemmedWords.append(stemmed)

			q = qp.parse(' '.join(stemmedWords))

			with ix.searcher() as searcher:
				correction = searcher.correct_query(q=q, qstring=terms, maxdist=2)
				if terms != correction.string:
					print("- Did you mean >>> " + correction.string)
				results = searcher.search(q, terms=True)

				numb = 1
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
