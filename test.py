# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import package.newsegmentation as ns
DATAPATH = r'./under_test/test.txt'
GTPATH = r'./under_test/gt.txt'


# -----------------------------------------------------------
# Main:
def main():
    myNews = ns.Segmentation(DATAPATH, sdm=(1, 1, 1), lcm=(1,))
    myNews.evaluate(GTPATH)
    print(myNews)


if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
