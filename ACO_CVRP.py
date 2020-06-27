#This file contain a copy of the python code used in the notebook. 
#To see how it works, it might be interesting to use the notebook in Jupyter.



alfa = 1
beta = 2
ro = .1 #Taux d'évaporation
iterations=1000
ants = 40
filename='matrix.json'
filedata='data_conv.json'
bestSolPerIt = {}

#Fonction récupérant des données du json pour les utiliser :
def generateGraph():
    capacityLimit=150 #Encombrement max des camions
    depot=1 #Numéro de la ville correspondant au dépot
    trucks=3 #Nombre de camion
    
    #Extraction des données du json
    with open(filename) as f:
        data = json.load(f)
    
    demand = [data[str(i+1)]["demande"] for i in range(len(data))] #demande relative à chaque ville

    graph = [data[str(i+1)]["poids"] for i in range(len(data))] #matrice d'adjacence du graphe
    
    cities = [data[str(i+1)]["ville"] for i in range(len(data))] #liste des noms des villes
    edges=np.array(graph)
    pheromones= np.ones((len(graph), len(graph))) #matrice de pheromones du graphe
    for i in range(len(graph)):
        pheromones[i][i]=0
    
    vertices=[i for i in range(1, len(graph) + 1)] #liste des villes
    vertices.remove(depot) #On ne considère pas le dépot dans la recherche
    
    return vertices, pheromones, edges, capacityLimit, demand, depot, trucks, cities
    
#Fonction déterminant le chemin emprunté par chaque fourmi :
def solutionOfOneAnt(vertices, edges, capacityLimit, demand, pheromones, depot):
    solution = list() #Liste des tournées
    
    #Tant que toutes les villes n'ont pas été ajoutées à la solution
    while(len(vertices)!=0):
        path=list() #Chemin d'une tournée
        city=depot #Début de la tournée au dépôt
        capacity=capacityLimit #Initialisation de la capicité du camion sur la tournée
        path.append(city) #Ajout du point de départ à la tournée
        
        #Tant que toutes les villes n'ont pas été ajoutées à la solution
        while(len(vertices)!=0):
            probabilities = list(map(lambda x: ((pheromones[city-1][x-1])**alfa)*((1/edges[city-1][x-1])**beta), vertices)) #Liste des probabilités pour chaque arrête disponibles
            probabilities = probabilities/np.sum(probabilities)
            city = np.random.choice(vertices, p=probabilities) #Choix de la ville
            capacity = capacity - np.prod(demand[city-1]) #Diminution de la capacité du camion en fonction de la demande de la ville
    
            #Si la capacité est toujours positive on ajoute la ville
            if(capacity>0):
                path.append(city)
                vertices.remove(city)
            #Sinon fin de tournée
            else:
                break
        path.append(depot) #Retour au dépot à la fin de la tournée
        solution.append(path) #Ajout de la tournée à la solution complète
    return solution
    
#Fonction retournant le coût total d'une solution :
def rateSolution(solution, edges, depot):
    cost = 0 #initialisation du coût de la solution

    #Pour chaque tournée de la solution
    for i in solution:
        #Pour chaque ville de la tournée
        for j in i:
            a=j #Prend la valeur de la ville courante
            b = i[i.index(j)+1] #Prend la valeur de la ville visitée ensuite
            cost = cost + edges[a-1,b-1] #On ajoute au coût le coût de l'arête entre a et b
            
            if b==depot: #Si la prochaine ville est le dépot, on sort de la boucle pour passer à la tournée suivante
                break
    return cost
    
#Fonction permettant d'actualiser le taux de phéromones à chaque itération :
def updatePheromones(pheromones, solutions):
    count=0
    pheromones = pheromones*(1-ro) #On applique l'évaporation sur toutes les valeurs de la matrice de phéromones
    #Pour chaque solution
    for i in solutions:
        length=i[1] #On récupère la longueur de la solution
        #Pour chaque tournée
        for j in range(len(solutions[count][0])):
            #Pour chaque ville
            for k in range(len(solutions[count][0][j])-1):
                a=solutions[count][0][j][k] #valeur de la ville actuelle
                b=solutions[count][0][j][k+1] #valeur de la ville suivante
                pheromones[a-1][b-1]=pheromones[a-1][b-1]+1/length #On dépose les phéromones sur l'arête entre a et b
        count+=1 #Compteur du numéro de la solution traitée
 
    return pheromones
    
#Fonction qui retourne le meilleur chemin, son coût parmis un ensemble de solutions et le coût de chacune de ses tournées :
def getBestSolution(solutions):
    bestIndex=0 #On initialise le meilleur index
    bestRate=solutions[bestIndex][1] #On initialise le meilleur coût
    
    #Pour chaque solution
    for i in range(1, len(solutions)):
        #Si le coût de la solution est inférieur au coût de la meilleure solution
        if solutions[i][1]<bestRate:
            bestIndex=i #bestIndex prend la nouvelle valeur
            bestRate=solutions[bestIndex][1] #bestRate prend la nouvelle valeur
    bestSolution=solutions[bestIndex][0]
    
    return bestSolution, bestRate
    
#Fonction qui permet de retourner le poids de chaque tournée d'une solution :
def rateTour(solution):
    tours=list() #Liste contenant toutes les tournées et leur coût respectif de la solution
    #Pour chaque tournée
    for i in range(len(solution)):
        cost=0
        #Pour chaque ville
        for j in range(len(solution[i])):
            a = solution[i][j] #Prend la valeur de la ville courante
            b = solution[i][j+1] #Prend la valeur de la ville visitée ensuite
            cost = cost + edges[a-1,b-1] #On ajoute au coût le coût de l'arête entre a et b
            
            if b==depot: #Si la prochaine ville est le dépot, on sort de la boucle pour passer à la tournée suivante
                break
        
        tours.append((solution[i], cost))#On ajoute le couple tournée, coût à la liste des tournées de la solution
    
    return tours
    
#Fonction permettant d'associer les tournées aux camions :
def toursDivision(detailedCost, trucks):
    costPerTour=list() #Liste des coûts des tournées
    costPerTruck=list() #Liste qui associe les coûts à chaque camion
    tourPerTruck=list() #Liste des tournées associées à chaque camion
    Avg=0 #Initialisation de la moyenne du coût par camion


    #Pour chaque tournée
    for i in range(len(detailedCost)):
        Avg=Avg+detailedCost[i][1] #On ajoute le coût de la tournée aux autres coût de tournée pour en faire la moyenne par camion ensuite
        costPerTour.append(detailedCost[i][1]) #On récupère le coût de la tournée pour les trier ensuite
    Avg=Avg/trucks #On fait la moyenne du coût par camion
    
    #Pour chaque camion, on créé une sous liste contenant le poids des tournées qui lui seront attribuées et une contenant les tournées
    for j in range(trucks):
        costPerTruck.append([])
        tourPerTruck.append([])
        
    costPerTour.sort(reverse=True) #On trie la liste des coûts des tournées dans l'ordre décroissant
    costPerTruck[0].append(costPerTour[0]) #On affecte la valeur la plus élevée au premier camion
    costPerTour.remove(costPerTour[0]) #On retire la valeur la plus élevée de la liste
    
    #Tant que la liste des coûts n'est pas vide
    while len(costPerTour)>0:
        currentMin=0 #index du camion qui possède le coût le plus faible
        currentMinSum=sum(costPerTruck[currentMin]) #coût le plus faible parmis les camions
        
        #Pour chaque camion
        for k in range(trucks):
            #Si le coût du camion est plus faible que le coût actuel
            if sum(costPerTruck[k])<currentMinSum:
                currentMin=k #currentMin prend la nouvelle valeur
                currentMinSum=sum(costPerTruck[currentMin]) #currentMinSum prend la nouvelle valeur
        costPerTruck[currentMin].append(costPerTour[0]) #On ajoute le coût au camion avec le plus faible coût
        costPerTour.remove(costPerTour[0]) #On retire le coût de la liste des coûts

    #Tant que la liste des tournées/coût n'est pas vide
    while(len(detailedCost)>0):
        #Pour chaque liste de coût des camions
        for l in range(len(costPerTruck)):
            #Pour chaque coût de la liste
            for m in range(len(costPerTruck[l])):
                #Pour chaque tournée
                for n in range(len(detailedCost)):
                    #Si le coût de la tournée du camion est égal au coût de la tournée de la liste détaillée
                    if costPerTruck[l][m]==detailedCost[n][1]:
                        tourPerTruck[l].append(detailedCost[n]) #La tournée est associée au camion
                        detailedCost.remove(detailedCost[n]) #On retire la tournée de la liste détaillée
                        break #On passe au prochain coût
    
    return tourPerTruck
    
#Fonction qui transforme les numéros des sommets d'une solution en noms de villes
def nbToCity(solution, cities):
    solutionWName=list() #On créé la liste contenant les solutions avec les noms
    #Pour chaque tournée
    for i in range(len(solution)):
        solutionWName.append([]) #On ajoute le bon nombre de tournée à la nouvelle ville
        #Pour chaque ville
        for j in range(len(solution[i])):
            solutionWName[i].append(cities[solution[i][j]-1]) #On remplace le numéro de ville par son nom dans le nouveau tableau
    return solutionWName
    
#Programme principal réalisant le nombre d'itération défini précedement :
vertices, pheromones, edges, capacityLimit, demand, depot, trucks, cities = generateGraph()
date=datetime.now()
bestRate=-1

print('Progression du nombre d\'itérations: ')
f = IntProgress(min=0, max=iterations) # instancie la barre de progression
display(f) # Affiche la barre

try:

    #Pour chaque itération
    for i in range(iterations):
        solutions = list() #Liste contenant l'ensemble des solutions de l'itération

        #Pour chaque fourmi
        for j in range(ants):
            solution = solutionOfOneAnt(vertices.copy(), edges, capacityLimit, demand, pheromones, depot) #On récupère la solution d'une fourmi
            solutions.append((solution, rateSolution(solution, edges, depot))) #On ajoute la solution et son poids à la liste des solutions

        pheromones=updatePheromones(pheromones, solutions) #On modifie le taux de pheromones
        bestCurSol,bestCurRate = getBestSolution(solutions) #Récupération de la meilleure solution de l'itération
        if bestCurRate<bestRate or bestRate<0:
            bestRate=bestCurRate #Récupération de la meilleure solution
            bestSolution=bestCurSol #Récupération du meilleur coût
        bestSolPerIt.update({i: {"Temps": float((datetime.now()-date).total_seconds()), "Cout": int(bestCurRate)}}) #Ajout des données au tableau

        f.value= i+1 #Augmente la barre de progression

except ValueError:
    print('Arrêt au bout de %s itérations, les valeurs des probabilités sont devenues trop petites pour pouvoir être gérées par le langage python.' %str(i))
    f.value=iterations

detailedCost=rateTour(bestSolution) #Coût détaillé des tournées
tourPerTruck=toursDivision(detailedCost, trucks) #Liste des tournées associées aux camions
bestSolutionName=nbToCity(bestSolution, cities)

#Génération des données au format JSON
with open(filedata, 'w') as f:
    json.dump(bestSolPerIt, f, indent=4)

#Affichage
print('--------------------')
print('Affichage de la solution avec le numéro des sommets: \n')
print("La meilleure solution est composée des tournées suivantes: ")
for k in range(len(bestSolution)):
    print(bestSolution[k])
print("\nLe coût de cette solution est de %s. " %bestRate)
print("\nLa répartition des tournées par camion est la suivante:")
maxCostTruck=0
for l in range(len(tourPerTruck)):
    if len(tourPerTruck[l])!=0:
        print("Les tournées associées au camion %s sont: " %str(l+1))
        costTruck=0
        for m in range(len(tourPerTruck[l])):
            print(str(tourPerTruck[l][m][0]) + " dont le coût est " + str(tourPerTruck[l][m][1])+ ".")
            costTruck=costTruck+tourPerTruck[l][m][1]
        print("Le coût total des tournées associées au camion %s est %s. \n" %(str(l+1), str(costTruck)))
        if costTruck>maxCostTruck:
            maxCostTruck=costTruck
            maxCostIndex=l

print("Le dernier camion qui rentrera au dépôt sera le camion %s, dont le coût des arêtes est %s." %(str(maxCostIndex+1),str(maxCostTruck)))

# Version pratique pour l'entreprise affichant le nom des villes à la place des index des sommets
#Affichage
print('--------------------')
print('Affichage de la solution avec le nom des villes: \n')
print("La meilleure solution est composée des tournées suivantes: ")
for k in range(len(bestSolutionName)):
    print(bestSolutionName[k])
print("\nLe coût de cette solution est de %s. " %bestRate)
print("\nLa répartition des tournées par camion est la suivante:")
for l in range(len(tourPerTruck)):
    if len(tourPerTruck[l])!=0:
        print("Les tournées associées au camion %s sont: " %str(l+1))
        costTruck=0
        tourTrucks=list()

        for m in range(len(tourPerTruck[l])):
            tourTrucks.append([])
            tourTrucks[m].append(tourPerTruck[l][m][0])

        for n in range(len(tourPerTruck[l])):
            tourTruckName = nbToCity(tourTrucks[n], cities)
            print(str(tourTruckName) + " dont le coût est " + str(tourPerTruck[l][n][1])+ ".")
            costTruck=costTruck+tourPerTruck[l][n][1]
        print("Le coût total des tournées associées au camion %s est %s. \n" %(str(l+1), str(costTruck)))

print("Le dernier camion qui rentrera au dépôt sera le camion %s, dont le coût des arêtes est %s." %(str(maxCostIndex+1),str(maxCostTruck)))
