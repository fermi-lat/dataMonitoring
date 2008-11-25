acdMapFile = file('acd_map.txt')
garcTableFile = file('garc_table.txt')

garcTableFile.next()
garcDict = {}
for line in garcTableFile:
    garc, board = line.strip('\n').split()
    garcDict[board] = garc

acdMapFile.next()
tileDictA = {}
tileDictB = {}
for line in acdMapFile:
    t, fA, cA, chA, fB, cB, chB, id, type, a = line.strip('\n').split('\t')
    id = int(id)
    if id >= 0:
        print id, fA, fB, garcDict[fA], garcDict[fB]
        tileDictA[id] = garcDict[fA]
        tileDictB[id] = garcDict[fB]

outputFile = file('__tile_map__.py', 'w')
outputFile.writelines('GARC_DICT = %s\n\n' % garcDict)
outputFile.writelines('TILE_DICT_A = %s\n\n' % tileDictA)
outputFile.writelines('TILE_DICT_B = %s\n\n' % tileDictB)
outputFile.close()
