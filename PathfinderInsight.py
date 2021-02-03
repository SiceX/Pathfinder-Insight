import PySimpleGUI as sg


class Gui:
	""" Create a GUI object """

	def __init__(self):
		sg.theme('DarkBlue3') #Reddit

		self.layout: list = [
			[sg.Text('Search', size=(11, 1)),
             sg.Input(size=(40, 1), focus=True, key="TERM"),
             sg.Checkbox('Synimous', size=(8, 1), default=False, key='syn_search')],
			[sg.Text('Data Path', size=(11, 1)),
             sg.Input(None, size=(40, 1), key="PATH"),
             sg.FolderBrowse('Browse', size=(10, 1)),
             sg.Button('Build Index', size=(10, 1), key="_INDEX_"),
             sg.Button('Search', size=(10, 1), bind_return_key=True, key="_SEARCH_")],
			[sg.Output(size=(96, 30))]]

		self.window: object = sg.Window('Pathfinder Insight', self.layout, element_justification='left')


def main():
	""" The main loop for the program """
	g = Gui()

	event, values = g.window.read()


main()
