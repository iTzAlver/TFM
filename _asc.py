# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
import spacy
from nltk import Tree
sp = spacy.load('es_core_news_lg')

sample = 'El Banco de Rusia admite el daño de las sanciones: "El periodo en el que la economía puede vivir de sus ' \
         'reservas es finito". Elvira Nabiulina, gobernadora del Banco Central de Rusia, asegura que los principales ' \
         'problemas se ' \
         'encuentran '\
         'asociados a las restricciones a la importación y a la logística del comercio exterior. ' \
		 'Yulia Timoshenko: "La UE está financiando la futura guerra que Putin librará contra ella; es suicida". '\
		 'La ex primera ministra ucraniana pide a los países occidentales que "no repitan" su error y solicita el ' \
         'cese inmediato de la compra de gas y petróleo ruso que, dice, está "financiando" la "futura guerra" ' \
         'que Putin ' \
         'lanzará contra el resto de Europa. '\
		 'El pesimismo por la economía se contagia a las criptomonedas: ¿Hasta cuánto va a seguir cayendo el '\
         'Bitcoin? '\
		 'La pandemia hizo que muchas personas optasen por divisas virtuales para proteger su dinero, pero ahora se '\
         'acumulan los factores negativos y los temores se han contagiado al criptomercado.'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
	sentence = sp(sample)
	ents = [ent.lemma_ for ent in sentence.ents]
	for index, token in enumerate(sentence):
		refered_to = token.head
		labeled_to = token.pos_
		if index == 0:
			print('Inicio.')
	[to_nltk_tree(sent.root).pretty_print() for sent in sentence.sents]
	return None


def to_nltk_tree(node):
	retval = None
	if node.n_lefts + node.n_rights > 0:
		retval = Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
	else:
		retval = node.orth_
	return retval


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class NodeGenerator:
	def __init__(self):
		pass


class NodeConnector:
	def __init__(self):
		pass


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
if __name__ == '__main__':
	main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
