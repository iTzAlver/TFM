# from transformers import AutoTokenizer, AutoModelForTokenClassification
import matplotlib.pyplot as plt
import networkx as nx
import spacy as sp
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

spanish_model1 = 'hiiamsid/sentence_similarity_spanish_es'
model = SentenceTransformer(spanish_model1)
spacy_model = sp.load('es_core_news_lg')
thresholding = 0.3

DATASET_FOR_TEST = \
[
    'No hay descanso.',# 0
    'Desde hace más de 24 horas se trabaja sin tregua para encontrar a Julen.',# 1
    'El niño de 2 años se cayó en un pozo en Totalán, en Málaga.',# 2
    'Las horas pasan, los equipos de rescate luchan contrarreloj y buscan nuevas opciones en un terreno escarpado y con riesgo de derrumbes bajo tierra.',# 3
    'Buenas noches.',# 4
    '¿Cuáles son las opciones para encontrar a Julen?',# 5
    'Arrancamos este Telediario, allí, en el lugar del rescate.',# 6
    'Se trabaja en 3 frentes retirar la arena que está taponando el pozo de prospección.',# 7
    'Excavar en 2 pozo, y abrir en el lateral de la montaña.',# 8
    'El objetivo rescatar al pequeño.',# 9
    'El proyecto de presupuestos llega al Congreso.',# 10
    'Son las cuentas con más gasto público desde 2010 destacan más partidas para programas sociales, contra la pobreza infantil o la dependencia, y también el aumento de inversiones en Cataluña.',# 11
    'El gobierno necesita entre otros  el apoyo de los independentistas catalanes  que por ahora mantienen el NO a los presupuestos, aunque desde el ejecutivo nacional se escuchan voces más optimistas.',# 12
    'Los pensionistas vascos llevan un año protestando para pedir mejoras en las pensiones.',# 13
    'Hoy, como cada lunes,  han vuelto a salir a las calles de Bilbao. El Gobierno tendrá que pedir de nuevo un crédito de 15.000 millones para pagar las pensiones en 2019.',# 14
    'La familia de Laura Sanz Nombela, fallecida en París por una explosión de gas espera poder repatriar su cuerpo este próximo miércoles.',# 15
    'Hemos hablado con su padre, que está en Francia junto a su yerno  y nos ha contado que se sintieron abandonados  en las primeras horas tras el accidente.',# 16
    'La guardia civil busca en una zona de grutas volcánicas  de difícil acceso  el cuerpo de la joven desaparecida en Lanzarote, Romina Celeste.',# 17
    'Su marido está detenido en relación con su muerte aunque él defiende que no la mató, que solo discutieron  y que luego se la encontró muerta la noche de Año Nuevo.',# 18
    'Dormir poco hace que suba hasta un 27 por ciento el riesgo  de enfermedades cardiovasculares.',# 19
    'Es la conclusión de un estudio que ha realizado durante 10 años el Centro Nacional para estas dolencias.',# 20
    'Y una noticia de esta misma tarde de la que estamos muy pendientes: Un tren ha descarrilado esta tarde cerca de Torrijos en Toledo sin causar heridos.',# 21
    'Había salido de Cáceres con dirección a Madrid.',# 22
    'Los 33 pasajeros han sido trasladados a la capital en otro tren.',#24
    'La circulación en la vía entre Madrid y Extremadura está interrumpida.',# 25
    'Renfe ha organizado un transporte alternativo en autobús  para los afectados.',# 26
    'A 15 días de la gran gala de los Goya hoy se ha entregado ya el primer premio.',# 27
    'La cita es el próximo 2 de febrero en Sevilla, pero hoy, aquí en Madrid, en el Teatro Real gran fiesta de los denominados a los Premios Goya.',# 28
    'Solo uno de ellos se llevará hoy su estatuilla.',# 29
    'Chicho Ibáñez Serrador consigue el Premio Goya de Honor por toda una vida dedicada al cine de terror.',# 30
    'Y en los deportes Nadal gana en Australia, Sergio.',# 31
    'Esa imagen es lo que se ve desde la superficie  y esto es lo que no se ve.',# 32
    'Así es la estructura del pozo.'# 33
]

DATASET_FOR_TESTING = \
[
    'No hay descanso.',# 0
    'Desde hace más de 24 horas se trabaja sin tregua para encontrar a Julen.',# 1
    'El niño de 2 años se cayó en un pozo en Totalán, en Málaga.',# 2
    'Las horas pasan, los equipos de rescate luchan contrarreloj y buscan nuevas opciones en un terreno escarpado y con riesgo de derrumbes bajo tierra.',# 3
    'Buenas noches.',# 4
    '¿Cuáles son las opciones para encontrar a Julen?',# 5
    'Arrancamos este Telediario, allí, en el lugar del rescate.',# 6
    'Se trabaja en 3 frentes retirar la arena que está taponando el pozo de prospección.',# 7
    'Excavar en 2 pozo, y abrir en el lateral de la montaña.',# 8
    'El objetivo rescatar al pequeño.',# 9
    'El proyecto de presupuestos llega al Congreso.',# 10
    'Son las cuentas con más gasto público desde 2010 destacan más partidas para programas sociales, contra la pobreza infantil o la dependencia, y también el aumento de inversiones en Cataluña.',# 11
    'El gobierno necesita entre otros  el apoyo de los independentistas catalanes  que por ahora mantienen el NO a los presupuestos, aunque desde el ejecutivo nacional se escuchan voces más optimistas.',# 12
    'Los pensionistas vascos llevan un año protestando para pedir mejoras en las pensiones.',# 13
    'Hoy, como cada lunes,  han vuelto a salir a las calles de Bilbao. El Gobierno tendrá que pedir de nuevo un crédito de 15.000 millones para pagar las pensiones en 2019.',# 14
    'La familia de Laura Sanz Nombela, fallecida en París por una explosión de gas espera poder repatriar su cuerpo este próximo miércoles.',# 15
    'Hemos hablado con su padre, que está en Francia junto a su yerno  y nos ha contado que se sintieron abandonados  en las primeras horas tras el accidente.',# 16
    'La guardia civil busca en una zona de grutas volcánicas de difícil acceso  el cuerpo de la joven desaparecida en Lanzarote, Romina Celeste.',# 17
    'Su marido está detenido en relación con su muerte aunque él defiende que no la mató, que solo discutieron  y que luego se la encontró muerta la noche de Año Nuevo.',# 18
    'Dormir poco hace que suba hasta un 27 por ciento el riesgo  de enfermedades cardiovasculares.',# 19
    'Es la conclusión de un estudio que ha realizado durante 10 años el Centro Nacional para estas dolencias.',# 20
    'Y una noticia de esta misma tarde de la que estamos muy pendientes: Un tren ha descarrilado esta tarde cerca de Torrijos en Toledo sin causar heridos.',# 21
    'Había salido de Cáceres con dirección a Madrid.',# 22
    'Los 33 pasajeros han sido trasladados a la capital en otro tren.',#24
    'La circulación en la vía entre Madrid y Extremadura está interrumpida.',# 25
    'Renfe ha organizado un transporte alternativo en autobús  para los afectados.',# 26
    'A 15 días de la gran gala de los Goya hoy se ha entregado ya el primer premio.',# 27
    'La cita es el próximo 2 de febrero en Sevilla, pero hoy, aquí en Madrid, en el Teatro Real gran fiesta de los denominados a los Premios Goya.',# 28
    'Solo uno de ellos se llevará hoy su estatuilla.',# 29
    'Chicho Ibáñez Serrador consigue el Premio Goya de Honor por toda una vida dedicada al cine de terror.',# 30
    'Y en los deportes Nadal gana en Australia, Sergio.',# 31
    'Esa imagen es lo que se ve desde la superficie  y esto es lo que no se ve.',# 32
    'Así es la estructura del pozo.'# 33
]

if __name__ == '__main__':
    encoded = model.encode(DATASET_FOR_TESTING)
    mtx = []
    th = []
    cnt = 0

    for sentence, code in zip(DATASET_FOR_TESTING, encoded):
        mtx_row = []
        line_aux = []
        th_row = []
        for sentence2, code2 in zip(DATASET_FOR_TESTING, encoded):
            ask = cosine_similarity(code.reshape(1, -1), code2.reshape(1, -1))[0][0]
            mtx_row.append(ask)
            line_aux.append(ask)

        line_aux[cnt] = 0
        for item in range(len(line_aux)):
            if line_aux[item] == max(line_aux) and line_aux[item] >= thresholding:
                th_row.append(round(line_aux[item], 2))
            else:
                th_row.append(0.0)

        print('Frase' + str(cnt) + ':\t' + sentence)
        cnt = cnt + 1
        th.append(th_row)
        mtx.append(mtx_row)

    head = list(range(len(mtx[0])))
    print(head)
    for line in mtx:
        _text = ''
        for ele in line:
            _text = _text + '  ' + str(round(ele, 2)) + '\t'
        print(_text)
    print('\n')

    connection_mtx = []
    for line in th:
        aux_row = []
        _text = ''
        _text2 = ''
        for ele in line:
            _text = _text + '  ' + str(ele) + '\t'
            if ele >= thresholding:
                aux_row.append(1)
            else:
                aux_row.append(0)
            _text2 = _text2 + '  ' + str(aux_row)
        connection_mtx.append(aux_row)
        print(_text)

    for line in connection_mtx:
        _text = ''
        for ele in line:
            _text = _text + '  ' + str(ele) + '\t'
        print(_text)
    print('\n')

    G = nx.DiGraph()
    lst = list(range(len(connection_mtx[0])))
    for i in range(len(lst)):
        lst[i] = str(lst[i])
    G.add_nodes_from(lst)
    print(lst)

    for i in range(len(connection_mtx)):
        for j in range(len(connection_mtx)):
            if connection_mtx[i][j] == 1:
                G.add_edge(str(i), str(j))

    # A.draw('salida.png')
    nx.draw_networkx(G)
    plt.show()
    print('Adios.')