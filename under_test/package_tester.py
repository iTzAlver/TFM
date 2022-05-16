# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import newsegmentation as ns


# -----------------------------------------------------------
def validation() -> None:
    # mns = ns.Segmentation(r'../db/news_text/esp/Julen/1.txt')
    mns = ns.Segmentation(r'../db/vtt_files/Julen/1.vtt')
    print(mns)
    ns.info()
    ns.about()
    mns.plotmtx(0, 1, 2, 3)
    for news in mns:
        print(news)
    return


if __name__ == '__main__':
    validation()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
