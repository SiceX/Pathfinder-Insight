import os
import json
import string

import unicodedata
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.writing import AsyncWriter
from whoosh.analysis import RegexTokenizer
from whoosh.analysis import StandardAnalyzer, StemmingAnalyzer, CharsetFilter
from whoosh.support.charset import accent_map
from whoosh.support.charset import default_charset, charset_table_to_dict

import nltk
from nltk.corpus import stopwords

charmap = charset_table_to_dict(default_charset)


def processText(text, filterStopwords=False, stemming=False, normalizeAccents=False):
    """ Questo metodo si occupa di processare il testo prima di inserirlo nell'index.
        Nello specifico, elimina le stopwords, esegue lo stemming delle parole e normalizza
        le lettere accentate ed altre lettere in testo appartenente all'ASCII
        :rtype: str
    """
    # tokenizzazione
    # tokens = nltk.wordpunct_tokenize(text)

    # tokenizer = RegexTokenizer()

    if stemming:
        if filterStopwords:
            analyzer = StemmingAnalyzer()
        else:
            analyzer = StemmingAnalyzer(stoplist=None)
    else:
        if filterStopwords:
            analyzer = StandardAnalyzer()
        else:
            analyzer = StandardAnalyzer(stoplist=None)
    if normalizeAccents:
        analyzer = analyzer | CharsetFilter(charmap) #accent_map

    # Eliminazione di stopwords e punteggiatura
    processedText = ""
    for token in analyzer(text):
        processedText = processedText + ' ' + token.text.translate(str.maketrans('', '', string.punctuation))
    return processedText.lstrip()


def createSearchableData(docsDirectory):
    # definizione dello schema dell'indice
    schema = Schema(docTitle=STORED,
					procTitle=KEYWORD,
					topics=KEYWORD(stored=True, lowercase=True),
					category=ID(stored=True),
					pageUrl=ID(stored=True),
					path=ID(stored=True),
					# markdownContent=STORED,
					procContent=TEXT)

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

        # regex per trovare le frasi "chiave" nella pagina, ovvero quelle usate come inizio di una sezione nel markdown
        topicSearch = re.compile(r"\n####.*\n")

        fp = open(path, 'r', encoding="utf-8")
        entry = json.loads(fp.read())
        fp.close()

        docTitle = entry["title"]

        # Titolo tokenizzato, con attenzione a possibili caratteri unicode da trasformare in caratteri ASCII
        processedTitle = processText(docTitle, filterStopwords=True, stemming=True, normalizeAccents=True)
        # processedTitle = unicodedata.normalize('NFKD', processedTitle).encode('ascii', 'ignore').decode('utf-8')

        pageUrl = entry["url"]

        # Contenuto in markdown della pagina
        markdownContent = entry["content"]

        # preprocessing (filtro stopwords e normalizzazione) delle frasi usate come argomento della pagina
        topicSet = set()
        for match in topicSearch.findall(markdownContent):
            topic = str(match).strip(r'\n').strip('#')
            topicSet = topicSet.union(set(processText(topic, filterStopwords=True, normalizeAccents=True).split(' ')))
        topics = ' '.join(list(topicSet))

        # la categoria è la pagina padre più alta dopo la homepage
        category = str(pageUrl).split(r'/')[3]
        category = processText(category, filterStopwords=True, normalizeAccents=True)

        # la sezione contentData è data dal contenuto preprocessato: stemming e normalizzazione
        procContent = processText(markdownContent, filterStopwords=True, stemming=True, normalizeAccents=True)
        # procContent = unicodedata.normalize('NFKD', procContent).encode('ascii', 'ignore').decode('utf-8')

        # Aggiunta dell'entry all'indice
        writer.add_document(docTitle=docTitle,
							procTitle=processedTitle,
							topics=topics,
							category=category,
							path=path,
							pageUrl=pageUrl,
							# markdownContent=markdownContent,
							procContent=procContent)
    writer.commit()


cwd = os.getcwd()
docsDir = r"F:\RepoHDD\Progetti\Gestione dell'Informazione\Pathfinder-Insight\documents"  # r"..\documents" "\prova"
createSearchableData(docsDir)
