#!/usr/bin/env python

def reformat(nbr):
    strNbr = str(nbr)
    for i in range(6 - len(strNbr)):
        strNbr = " " + strNbr
    return strNbr

def drawTable(profile, TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2):
    for i in range(8 - len(profile)):
        profile += " "

    error11 = FN1 / (TP1 + FN1)
    error12 = FP1 / (TN1 + FP1)

    precision1 = TP1 / (TP1 + FP1)
    recall1 = TP1 / (TP1 + FN1)
    Fscore1 = 2 * precision1 * recall1 / (precision1 + recall1)

    accuracy1 = (TP1 + TN1) / (TP1 + FN1 + TN1 + FP1)

    BIA1 = 1 - (error11 + error12) / 2

    error21 = FN2 / (TP2 + FN2)
    error22 = FP2 / (TN2 + FP2)

    precision2 = TP2 / (TP2 + FP2)
    recall2 = TP2 / (TP2 + FN2)
    Fscore2 = 2 * precision2 * recall2 / (precision2 + recall2)

    accuracy2 = (TP2 + TN2) / (TP2 + FN2 + TN2 + FP2)

    BIA2 = 1 - (error21 + error22) / 2

    TP1 = reformat(int(TP1))
    FN1 = reformat(int(FN1))
    TN1 = reformat(int(TN1))
    FP1 = reformat(int(FP1))
    TP2 = reformat(int(TP2))
    FN2 = reformat(int(FN2))
    TN2 = reformat(int(TN2))
    FP2 = reformat(int(FP2))
    error11 = reformat(str(round(error11 * 100, 2)) + '%')
    error12 = reformat(str(round(error12 * 100, 2)) + '%')
    error21 = reformat(str(round(error21 * 100, 2)) + '%')
    error22 = reformat(str(round(error22 * 100, 2)) + '%')
    Fscore1 = reformat(round(Fscore1, 5))
    Fscore2 = reformat(round(Fscore2, 5))
    accuracy1 = reformat(str(round(accuracy1 * 100, 2)) + '%')
    accuracy2 = reformat(str(round(accuracy2 * 100, 2)) + '%')
    BIA1 = reformat(str(round(BIA1 * 100, 2)) + '%')
    BIA2 = reformat(str(round(BIA2 * 100, 2)) + '%')

    toBePrinted = ' | ' + profile + '   |   TP   |   FN   |   TN   |   FP   |   TP   |   FN   |   TN   |   FP   |\n'
    toBePrinted += ' |            |--------|--------|--------|--------|--------|--------|--------|--------|\n'
    toBePrinted += ' |            | ' + TP1 + ' | ' + FN1 + ' | ' + TN1 + ' | ' + FP1 + ' | ' + TP2 + ' | ' + FN2 + ' | ' + TN2 + ' | ' + FP2 + ' |\n'
    toBePrinted += ' |------------|-----------------|-----------------|-----------------|-----------------|\n'
    toBePrinted += ' | Error rate |      ' + error11 + '     |      ' + error12 + '     |      ' + error21 + '     |      ' + error22 + '     |\n'
    toBePrinted += ' |------------|-----------------------------------|-----------------------------------|\n'
    toBePrinted += ' | F-score    |              ' + Fscore1 + '              |              ' + Fscore2 + '              |\n'
    toBePrinted += ' |------------|-----------------------------------|-----------------------------------|\n'
    toBePrinted += ' | Accuracy   |               ' + accuracy1 + '              |               ' + accuracy2 + '              |\n'
    toBePrinted += ' |------------|-----------------------------------|-----------------------------------|\n'
    toBePrinted += ' | BIA        |               ' + BIA1 + '              |               ' + BIA2 + '              |\n'
    toBePrinted += ' |============|===================================|===================================|\n'

    return toBePrinted

TTP1 = 0.
TFN1 = 0.
TTN1 = 0.
TFP1 = 0.
TTP2 = 0.
TFN2 = 0.
TTN2 = 0.
TFP2 = 0.

output  = ' |============|===================================|===================================|\n'
output += ' | Profiles   |         Face Verification         |      Weighted Cross-Matching      |\n'
output += ' |============|===================================|===================================|\n'

f= open("./Abrha/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Abrha', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2



f= open("./Astraat/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Astraat', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Bonji/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Bonji', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Heeda/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Heeda', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Hickam/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Hickam', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Hmouda/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Hmouda', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Holu/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Holu', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Khufu/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Khufu', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Laghbesh/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Laghbesh', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Mekah/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Mekah', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Mimyth/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Mimyth', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Sakis/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Sakis', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Sierra/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Sierra', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Sokhoi/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Sokhoi', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

f= open("./Yakouza/results/part-00000","r")
line = f.readline()
f.close()
line = line.strip()
line = line.split(',')
TP1 = float(line[0])
FN1 = float(line[1])
TN1 = float(line[2])
FP1 = float(line[3])
TP2 = float(line[4])
FN2 = float(line[5])
TN2 = float(line[6])
FP2 = float(line[7])
output += drawTable('Yakouza', TP1, FN1, TN1, FP1, TP2, FN2, TN2, FP2)
TTP1 += TP1
TFN1 += FN1
TTN1 += TN1
TFP1 += FP1
TTP2 += TP2
TFN2 += FN2
TTN2 += TN2
TFP2 += FP2

output += drawTable('Global', TTP1, TFN1, TTN1, TFP1, TTP2, TFN2, TTN2, TFP2)
print output
f= open("./report.txt","w+")
f.write(output)
f.close()