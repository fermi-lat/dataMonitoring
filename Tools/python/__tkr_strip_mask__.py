

STRIP_MASK_DICT = {
    #  Tower        0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
    'Pre-launch': [18,  4,  8,  7,  3, 10, 18, 15, 13,  9, 21, 15, 26,  8, 18, 10],
    'OBCONF-49' : [ 0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0]
    }


# Tempo/data
# 1\ vedi moduletto time di python
# http://docs.python.org/modindex.html
# http://docs.python.org/library/time.html#module-time

# Scrivere funzioni per:
# 1\ accedere al numero di strip mascherate (per torre e sul LAT) ad ogni passo.
# 2\ contare il numero totale di strip mascherate ad ogni passo (di nuovo per ogni singola torre e sul LAT).
# 3\ contare il numero totale di strip mascherate dall'inizio del lancio (per torre e sul LAT).
# 4\ vedere se c'e` una correlazione tra questi numeri e le pendenze delle efficienze di rivelazione.

# Fare i plot del numero di strip mascherate in funzione del tempo per tutte le 16 torri.
# Convertire il numero di strip mascherate in frazione di strip mascherate.


def getNumMaskedStrips(key, tower):
    return STRIP_MASK_DICT[key][tower]

def getTotalNumMaskedStrips(key):
    return sum(STRIP_MASK_DICT[key])



if __name__ == '__main__':
    print getNumMaskedStrips('Pre-launch', 15)
    print getTotalNumMaskedStrips('Pre-launch')
