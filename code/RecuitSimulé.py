# Rédoudre Sudoku avec le Recuit Simulé (Simulated Annealing), par Souhail AHD et Nouhaila MZIGUEL
# Master Big Data et Cloud Computing

import numpy as np
from math import exp, trunc
from random import choice
from statistics import pstdev
sudokuInitial = """
                    006057820
                    210006750
                    753004009
                    960005300
                    000700402
                    300928006
                    020540001
                    001070948
                    009001070
                """

sudoku = np.array([[int(i) for i in ligne] for ligne in sudokuInitial.split()])

def AfficherSudoku(sudoku):
    print("\n")
    for i in range(len(sudoku)):
        ligne = ""
        if i == 3 or i == 6:
            print("---------------------")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                ligne += "| "
            ligne += str(sudoku[i,j])+" "
        print(ligne)

def FixerSudokuValeurs(fixedSudoku):
    for i in range (0,9):
        for j in range (0,9):
            if fixedSudoku[i,j] != 0:
                fixedSudoku[i,j] = 1
    return(fixedSudoku)
  
def CalculerNombreErreurs(sudoku):
    nombreErreurs = 0 
    for i in range (0,9):
        nombreErreurs += CalculerNombreErreursLigneColonne(i, i, sudoku)
    return(nombreErreurs)

def CalculerNombreErreursLigneColonne(ligne, colonne, sudoku):
    nombreErreurs = (9 - len(np.unique(sudoku[:,colonne]))) + (9 - len(np.unique(sudoku[ligne,:])))
    return(nombreErreurs)

def CreerListe3x3Blocs():
    listeBlocs = []
    for r in range (0,9):
        tmpListe = []
        bloc1 = [i + 3*((r)%3) for i in range(0,3)]
        bloc2 = [i + 3*trunc((r)/3) for i in range(0,3)]
        for x in bloc1:
            for y in bloc2:
                tmpListe.append([x,y])
        listeBlocs.append(tmpListe)
    return(listeBlocs)

def Remplir3x3Blocs(sudoku, listeBlocs):
    for bloc in listeBlocs:
        for box in bloc:
            if sudoku[box[0],box[1]] == 0:
                blocActuel = sudoku[bloc[0][0]:(bloc[-1][0]+1),bloc[0][1]:(bloc[-1][1]+1)]
                sudoku[box[0],box[1]] = choice([i for i in range(1,10) if i not in blocActuel])
    return sudoku

def SommeBloc (sudoku, bloc):
    somme = 0
    for box in bloc:
        somme += sudoku[box[0], box[1]]
    return(somme)

def TwoRandomBoxesWithinBlock(fixedSudoku, bloc):
    while (1):
        firstBox = choice(bloc)
        secondBox = choice([box for box in bloc if box is not firstBox ])

        if fixedSudoku[firstBox[0], firstBox[1]] != 1 and fixedSudoku[secondBox[0], secondBox[1]] != 1:
            return([firstBox, secondBox])

def FlipBoxes(sudoku, boxesToFlip):
    proposedSudoku = np.copy(sudoku)
    placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
    proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
    proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
    return (proposedSudoku)

def ProposedState (sudoku, fixedSudoku, listeDeBlocs):
    randomBloc = choice(listeDeBlocs)

    if SommeBloc(fixedSudoku, randomBloc) > 6:  
        return(sudoku, 1, 1)
    boxesToFlip = TwoRandomBoxesWithinBlock(fixedSudoku, randomBloc)
    proposedSudoku = FlipBoxes(sudoku,  boxesToFlip)
    return([proposedSudoku, boxesToFlip])

def ChoisirNouvelEtat (sudokuCourant, fixedSudoku, listeDeBlocs, temperature):
    proposition = ProposedState(sudokuCourant, fixedSudoku, listeDeBlocs)
    nouveauSudoku = proposition[0]
    boxesToCheck = proposition[1]
    coutActuel = CalculerNombreErreursLigneColonne(boxesToCheck[0][0], boxesToCheck[0][1], sudokuCourant) + CalculerNombreErreursLigneColonne(boxesToCheck[1][0], boxesToCheck[1][1], sudokuCourant)
    nouveauCout = CalculerNombreErreursLigneColonne(boxesToCheck[0][0], boxesToCheck[0][1], nouveauSudoku) + CalculerNombreErreursLigneColonne(boxesToCheck[1][0], boxesToCheck[1][1], nouveauSudoku)
    #coutActuel = CalculerNombreErreurs(sudokuCourant)
    #nouveauCout = CalculerNombreErreurs(nouveauSudoku)
    differenceCout = nouveauCout - coutActuel
    rho = exp(-differenceCout/temperature)
    if(np.random.uniform(1,0,1) < rho):
        return([nouveauSudoku, differenceCout])
    return([sudokuCourant, 0])

def ChoisirNombreIterations(fixedSudoku):
    nombreIterations = 0
    for i in range (0,9):
        for j in range (0,9):
            if fixedSudoku[i,j] != 0:
                nombreIterations += 1
    return nombreIterations

def CalculerTemperatureInitiale (sudoku, fixedSudoku, listeBlocs):
    listeDeDifferences = []
    tmpSudoku = sudoku
    for i in range(1,10):
        tmpSudoku = ProposedState(tmpSudoku, fixedSudoku, listeBlocs)[0]
        listeDeDifferences.append(CalculerNombreErreurs(tmpSudoku))
    return (pstdev(listeDeDifferences))

def resoudreSudoku (sudoku):

    solutionTrouvee = False

    while (not solutionTrouvee):

        tauxDeRefroidissement = 0.99
        stuckCount = 0
        fixedSudoku = np.copy(sudoku)
        #PrintSudoku(sudoku)
        FixerSudokuValeurs(fixedSudoku)
        listeDeBlocs = CreerListe3x3Blocs()
        tmpSudoku = Remplir3x3Blocs(sudoku, listeDeBlocs)
        temperature = CalculerTemperatureInitiale(sudoku, fixedSudoku, listeDeBlocs)
        score = CalculerNombreErreurs(tmpSudoku)
        iterations = ChoisirNombreIterations(fixedSudoku)

        if score <= 0:
            solutionTrouvee = True

        cpt = 0
        while (not solutionTrouvee):
            scorePrecedent = score
            for i in range (0, iterations):
                nouvelEtat = ChoisirNouvelEtat(tmpSudoku, fixedSudoku, listeDeBlocs, temperature)
                tmpSudoku = nouvelEtat[0]
                scoreDiff = nouvelEtat[1]
                score += scoreDiff
                cpt += 1
                #print("Score = {}, T = {:.5f}, Iteration = {}".format(score, temperature, cpt))

                if score <= 0:
                    solutionTrouvee = True
                    break

            temperature *= tauxDeRefroidissement

            if score <= 0:
                solutionTrouvee = True
                break
            if score >= scorePrecedent:
                stuckCount += 1
            else:
                stuckCount = 0
            if (stuckCount > 80):
                temperature += 2
            if(CalculerNombreErreurs(tmpSudoku)==0):
                AfficherSudoku(tmpSudoku)
                break
    return(tmpSudoku)

AfficherSudoku(sudoku)
print("\n")
print("Le resultat est".center(50,'-'))
solution = resoudreSudoku(sudoku)
AfficherSudoku(solution)
