import cplex
from cplex import SparsePair

def definir_modelo(modelo, I, J, S, a, c, k):
    # I es la cantidad de nodos
    # J es la cantidad de productos
    # S es el costo del centro de servicio
    # a es la matriz de alcance (I x J)
    # c es el vector de costos de los nodos (I)
    # k es el vector de capacidades de los nodos (I)
    
    #creamos las variables de decisión
    for j in range(J):
        for i in range(I):
            #creamos variables binarias que representan si el producto j es entregado desde el nodo i
            modelo.variables.add(names=[f"nodo_{i}_{j}"], types=["B"])

        #creamos variables binarias que representan si el producto j es entregado desde el centro de servicio
        modelo.variables.add(names=[f"sc_{j}"], types=["B"])
    
    ### RESTRICCIONES ###

    #restricción: cada producto es entregado desde el sc o desde un nodo
    for j in range(J):
        coeficientes = [1.0] * (I + 1)
        nombres = [f"nodo_{i}_{j}" for i in range(I)] + [f"sc_{j}"]
        modelo.linear_constraints.add(lin_expr=[SparsePair(ind=nombres, val=coeficientes)],
                                     senses=["E"],
                                     rhs=[1.0],
                                     names=[f"entrega_{j}"])
    
    #restricción: un producto solo es entregado desde un nodo si está en su alcance
    for i in range(I):
        for j in range(J):
            modelo.linear_constraints.add(lin_expr=[SparsePair(ind=[f"nodo_{i}_{j}"], val=[1.0])],
                                            senses=["L"],
                                            rhs=[a[i][j]],	
                                            names=[f"alcance_{i}_{j}"])

    #restricción: cada nodo respeta la capacidad de envíos
    for i in range(I):
        coeficientes = [1.0] * J
        nombres = [f"nodo_{i}_{j}" for j in range(J)]
        modelo.linear_constraints.add(lin_expr=[SparsePair(ind=nombres, val=coeficientes)],
                                     senses=["L"],
                                     rhs=[k[i]],
                                     names=[f"capacidad_{i}"])
    ### FUNCIÓN OBJETIVO ###
    coeficientes_objetivo = []  
    nombres_objetivo = []
    for j in range(J):
        coeficientes_objetivo.append(S)  #costo del centro de servicio
        nombres_objetivo.append(f"sc_{j}")
        for i in range(I):
            coeficientes_objetivo.append(c[i])  #costo del nodo i
            nombres_objetivo.append(f"nodo_{i}_{j}")

    modelo.objective.set_sense(modelo.objective.sense.minimize)
    modelo.objective.set_linear(list(zip(nombres_objetivo, coeficientes_objetivo)))
    modelo.objective.set_name("Costo_Total")



def main():
    caso = 1
    while True:
        I,J = map(int, input().split())
        if I == 0 and J == 0:
            break
        S = float(input()) 
        a = [[0 for _j in range(J)] for _i in range(I)]
        c = []
        k = []
        for i in range(I):
            k1,c1 = input().split()
            k.append(int(k1))
            c.append(float(c1))

        for i in range(I):
            cobertura = list(map(int, input().split()))
            cobertura.pop(0)  #eliminamos el primer elemento que indica la cantidad de productos en cobertura   
            for j in cobertura:
                a[i][j] = 1

        problema = cplex.Cplex()
        definir_modelo(problema, I, J,S, a, c, k)
        problema.solve()

        print(f"Caso {caso}")
        print(int(problema.solution.get_objective_value()))
        
        asignacion = problema.solution.get_values()

        for j in range(J):
            if asignacion[problema.variables.get_indices(f"sc_{j}")] > 0.5:
                print(f"{j} -1")
            for i in range(I):
                if asignacion[problema.variables.get_indices(f"nodo_{i}_{j}")] > 0.5:
                    print(f"{j} {i}")
        caso += 1

if __name__ == "__main__":
    main()

"""Ejemplo de entrada:
3 8
12.50
10 5.00
8 7.25
12 4.50
5 0 1 2 3 7
4 2 3 4 5
6 0 2 4 5 6 7
2 5
10.00
20 4.00
15 6.00
3 0 1 2
4 0 1 3 4
0 0
"""

#da bien :D
