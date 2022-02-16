import spacy
nlp = spacy.load('es_core_news_lg')  # Load spacy.


if __name__ == '__main__':
    xd = nlp('No hay descanso.  Desde hace más de 24 horas se trabaja sin tregua  para encontrar a Julen.  El niño de 2 años se cayó en un pozo en Totalán, en Málaga.  Las horas pasan, los equipos de rescate luchan contrarreloj  y buscan nuevas opciones en un terreno escarpado  y con riesgo de derrumbes bajo tierra.  Buenas noches.  Arrancamos este Telediario, allí, en el lugar del rescate.  ¿Cuáles son las opciones para encontrar a Julen?  ¿Cuáles son las opciones para encontrar a Julen?  Se trabaja en 3 frentes  retirar la arena que está taponando el pozo de prospección. ')
    log_ = xd.similarity(nlp('Y en los deportes Nadal gana en Australia, Sergio.  Esa imagen es lo que se ve desde la superficie  Esa imagen es lo que se ve desde la superficie  y esto es lo que no se ve. Así es la estructura del pozo. '))
    print(log_)