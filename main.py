#from scrapy import cmdline
#cmdline.execute("scrapy crawl pfsrd".split())

class A:
	def __getattribute__(self,x):
		try:
			return self.__dict__[x]
		except AttributeError:
			self.__dict__[x] = None

a = A()
a.foo