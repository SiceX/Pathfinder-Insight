import scrapy
import html2text
import json
from scrapy.spiders import Spider
from sanitize_filename import sanitize


class PfsrdSpider(Spider):
    name = 'pfsrd'
    allowed_domains = ['www.d20pfsrd.com']
    start_urls = ['https://www.d20pfsrd.com/']

    def __init__(self):
        self.documentsDir = "documents/"
        self.text_maker = html2text.HTML2Text()
        self.text_maker.ignore_links = True
        self.text_maker.ignore_images = True
        self.text_maker.ignore_tables = True
        super().__init__()

    def parse(self, response, **kwargs):
        pagina = {
            "title":None,
            "url":response.url,
            "content":None
        }

        contentType = response.headers["Content-Type"].decode("utf-8").lower()
        if contentType.find("html") != -1:
            page = response.url.split("/")[-2]
            title = response.xpath('//main/section/article/h1/text()').get()
            pagina["title"] = title
            print(title)
            self.log(f'Visited page {title}, {page}')

            # Cerco di prendere solo gli articoli che contengono paragrafi (e quindi probabilmente testo utile)
            articleContent = response.xpath("//div[contains(@class, 'article-content') and p]").get()
            if articleContent:
                filename = sanitize(title).lower().replace(' ','-')
                filename = self.documentsDir + filename + ".json"
                try:
                    with open(filename, 'x') as file:
                        #Parsing dal contenuto html a testo (markdown)
                        contentToText = self.text_maker.handle(articleContent)
                        pagina["content"] = contentToText
                        json.dump(pagina, file)
                        self.log(f'Saved file {filename}')
                except FileExistsError:
                    self.log(f'file {filename} already exists, skipping')

            for href in response.xpath("//main//a[not(contains(@class, 'bread-parent'))]/@href").getall():
                #Evito le chiamate alla stessa pagina e ad ancore nella stessa pagina
                if href != '/' and href != response.url and href[0] != '#':
                    yield scrapy.Request(response.urljoin(href), self.parse)

        elif contentType == "application/pdf":
            page = response.url.split("/")[-1]
            filename = sanitize(page).lower().replace(' ', '-')
            filename = self.documentsDir + filename
            if filename.find(".pdf") == -1:
                filename += ".pdf"
            try:
                with open(filename, 'xb') as file:
                    # Scrittura del pdf scaricato
                    file.write(response.body)
                    self.log(f'Saved file {filename}')
            except FileExistsError:
                self.log(f'file {filename} already exists, skipping')
