# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:

# -----------------------------------------------------------
def main() -> None:
    from googletrans import Translator
    import re

    translator = Translator()
    txtorig = u'User "%(first_name)s %(last_name)s (%(email)s)" has been assigned.'

    # temporarily replace variables of format "%(example_name)s" with "__n__" to
    #  protect them during translate()
    VAR, REPL = re.compile(r'%\(\w+\)s'), re.compile(r'__(\d+)__')
    varlist = []

    def replace(matchobj):
        varlist.append(matchobj.group())
        return "__%d__" % (len(varlist) - 1)

    def restore(matchobj):
        return varlist[int(matchobj.group(1))]

    txtorig = VAR.sub(replace, txtorig)
    txttrans = translator.translate(txtorig, src='en', dest='es').text
    txttrans = REPL.sub(restore, txttrans)

    print(txttrans)
    return
    
    
class Default:
    def __init__(self):
        self.default = 0
   
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()

# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
