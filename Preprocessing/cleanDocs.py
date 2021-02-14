import json
import os
import time

import requests


def cleanUnavailablePages(docsDirectory):
	cwd = os.getcwd()
	print(cwd)

	headers = {
		'authority': 'scrapeme.live',
		'dnt': '1',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'sec-fetch-site': 'none',
		'sec-fetch-mode': 'navigate',
		'sec-fetch-user': '?1',
		'sec-fetch-dest': 'document',
		'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
	}

	# Lista dei file da scannare
	filepaths = [os.path.join(docsDirectory, i) for i in os.listdir(docsDirectory) if i.split(".")[-1] == "json"]

	if not os.path.exists(fr"{docsDirectory}\notValid"):
		os.mkdir(fr"{docsDirectory}\notValid")

	num = 1
	# per ogni percorso trovato...
	for path in filepaths:
		print(f'{num}/{len(filepaths)}')
		num += 1
		if num > 0:
			filename = path.split('\\')[-1]

			url = None
			with open(path, 'r', encoding="utf-8") as fp:
				url = json.loads(fp.read())["url"]

			if url is not None:
				r = requests.get(url, headers=headers)
				if r.status_code == 404:
					print(f"ERRORE {r.status_code}: {filename}")
					os.rename(path, fr"{docsDirectory}\notValid\{filename}")
				elif r.status_code != 200:
					print(f"ERRORE {r.status_code}: {filename}")
					with open("errori.log", 'a') as flog:
						print(f"ERRORE {r.status_code}: {filename}", file=flog)

			if num % 3 == 0:
				time.sleep(1)


def cleanCopyrightNotices(docsDirectory):
	cwd = os.getcwd()
	print(cwd)

	# Lista dei file da scannare
	filepaths = [os.path.join(docsDirectory, i) for i in os.listdir(docsDirectory) if i.split(".")[-1] == "json"]

	num = 1
	# per ogni percorso trovato...
	for path in filepaths:
		print(f'{num}/{len(filepaths)}')
		num += 1

		with open(path, 'r', encoding="utf-8") as fp:
			entry = json.loads(fp.read())
		content = str(entry["content"])
		copyrightPlace = content.find("Copyright Notice")
		if copyrightPlace != -1:
			content = content[:copyrightPlace]
			lastNewline = content.rfind("\n\n")
			content = content[:lastNewline]
			entry["content"] = content
			with open(path, 'w', encoding="utf-8") as fp:
				json.dump(entry, fp)


# cwd = os.getcwd()
docDir = r"..\documents"
# cleanUnavailablePages(docsDirectory)
cleanCopyrightNotices(docDir)
