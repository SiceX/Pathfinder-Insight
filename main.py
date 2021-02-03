import json
import os
from scrapy import cmdline
#from pdfreader import SimplePDFViewer

cmdline.execute("scrapy crawl pfsrd".split())

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

