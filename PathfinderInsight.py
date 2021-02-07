import re
import json
import PySimpleGUI as sg
import whoosh.index as index
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet


class Gui:
	""" Create a GUI object """

	def __init__(self):
		sg.theme('DarkBlue3')  # Reddit

		self.layout: list = [
			[sg.Text('Search', size=(11, 1)),
			 sg.Input(size=(40, 1), focus=True, key="TERM"),
			 sg.Checkbox('Synonyms', size=(8, 1), default=False, key='syn_search')],
			[  # sg.Text('Data Path', size=(11, 1)),
				# sg.Input(None, size=(40, 1), key="PATH"),
				# sg.FolderBrowse('Browse', size=(10, 1)),
				# sg.Button('Build Index', size=(10, 1), key="_INDEX_"),
				sg.Button('Search', size=(10, 1), bind_return_key=True, key="_SEARCH_")],
			# TODO [sg.Output(size=(96, 30), key="_output_")]
		]

		self.window: object = sg.Window('Pathfinder Insight', self.layout, element_justification='left')


def main():
	""" The main loop for the program """
	g = Gui()
	ix = index.open_dir("indexdir")

	while True:
		event, values = g.window.read()
		# TODO g.window["_output_"]('')

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

			term = values['TERM']
			print("Searching for >>> " + str(term))

			with open(r"logs\cronologia.txt", "w") as f:
				f.write(term)

			# TODO make scoring prefer category and topics hits?
			qp = MultifieldParser(["docTitle","topics","category","procContent"], schema=ix.schema)
			q = qp.parse(term)

			with ix.searcher() as searcher:
				correction = searcher.correct_query(q=q,qstring=term,maxdist=4)
				if term != correction.string:
					print("Did you mean >>> " + correction.string)
				results = searcher.search(q)

				numb = 1
				# print(results[0])
				if not results.is_empty():
					for elem in results:
						print(elem)
						# print("Result n.{} >>> ".format(numb) + "Page: " + str(elem[0]) + " Score: " + str(elem[1]) + "\n")
						numb += 1
				else:
					print("Non è stato trovato nessun risultato rilevante")


if __name__ == '__main__':
	main()
