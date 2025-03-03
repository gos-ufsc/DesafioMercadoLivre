import gurobipy as gp
from gurobipy import GRB
#import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
#import math
import time

from read import parse_input

example = "datasets/a/instance_0018.txt"
parsed_data = parse_input(example)

#print("numero de itens:", parsed_data['num_items'])
#print("Número de pedidos:", parsed_data['num_orders'])
##print("Primeiro pedido:", parsed_data['orders'][0])
#print("Todos pedidos")
#for i in parsed_data['orders']:
#    print(i)
#print("Primeiro pedido:", parsed_data['orders'][0])
#print("Número de corredores:", parsed_data['num_aisles'])
##print("Primeiro corredor:", parsed_data['aisles'][0])
#print("Todos corredores")
#for i in parsed_data['aisles']:
#    print(i)
#print("Limites da wave:", "LB:", parsed_data['LB'], "UB:", parsed_data['UB'])

#gurobi model

model  = gp.Model()

n_pedidos  = parsed_data['num_orders']
n_itens = parsed_data['num_items']
n_corredores = parsed_data['num_aisles']
LB = parsed_data['LB']
UB = parsed_data['UB']

quantidade_pedidos = parsed_data['soma_pedidos']

# Seria para considerar uma quantidade menor de corredores
# False -> Estou desconsiderando isso e deixando o problema completo
if False:
    from read import best_n_corredores
    nnn = 300
    if n_corredores > nnn:
        n_corredores = nnn
        parsed_data['aisles'], indices_anteriores, quantidade_corredor = best_n_corredores(parsed_data,n_corredores)
    else:
        quantidade_corredor = parsed_data['soma_corredor']
else:
    quantidade_corredor = parsed_data['soma_corredor']

#variaveis de decisao

pedido_X = model.addVars(n_pedidos, vtype=GRB.BINARY, name="pedido_X")
corredor_Y = model.addVars(n_corredores, vtype=GRB.BINARY, name="corredor_Y")

#funcao objetivo
#vai ser variavel
model.setObjective(gp.quicksum(quantidade_pedidos[i] * pedido_X[i] for i in range(n_pedidos)), GRB.MAXIMIZE)

#restricoes


#quero que a soma de itens dos pedidos seja maior ou igual ao LB
model.addConstr(gp.quicksum(quantidade_pedidos[i] * pedido_X[i] for i in range(n_pedidos)) >= LB)

#quero que a soma de itens dos pedidos seja menor ou igual ao UB
model.addConstr(gp.quicksum(quantidade_pedidos[i] * pedido_X[i] for i in range(n_pedidos)) <= UB)

#quero que a quantidade de itens do pedido_X seja menor ou igual aos corredores corredor_Y selecionados
#lembrando que podemos ter quantidade de pedidos diferentes de quantidade de corredores
model.addConstr(gp.quicksum(pedido_X[i] * quantidade_pedidos[i] for i in range(n_pedidos))
                <= gp.quicksum(corredor_Y[i] * quantidade_corredor[i] for i in range(n_corredores)))


#restrição GERAL considerando os itens em cada pedido separadamente
for itens in range(n_itens):
    model.addConstr(gp.quicksum(pedido_X[i] * parsed_data['orders'][i][itens] for i in range(n_pedidos) if parsed_data['orders'][i][itens] > 0) 
                    <= gp.quicksum(corredor_Y[j] * parsed_data['aisles'][j][itens] for j in range(n_corredores)))
        
#solucoes = []
#solucoes_dict = {}
best = 0
best_A = 0
melhor_solucao = []
model.setParam('OutputFlag', 0)  # Desativa os prints

total_temp = time.time()
for a in range(n_corredores):
    #quero que só tenha 1 corredor
    restricao_temporaria = model.addConstr(gp.quicksum(corredor_Y[i] for i in range(n_corredores)) == a+1)
    t = time.time()

    #model.reset()
    model.optimize()
    if model.status == GRB.OPTIMAL:
        #solucoes.append(model.objVal/(a+1))
        print('Obj:', (model.objVal)/(a+1), "A = ", a +1) 
        print("Tempo = %.4f" % (time.time() - t))
        if model.objVal/(a+1) > best:
            best = model.objVal/(a+1)
            best_A = a+1
            pedidos = []
            #print("Pedidos")
            for i in range(n_pedidos):
                if pedido_X[i].x == 1:
                    #print(parsed_data['orders'][i])
                    pedidos.append(parsed_data['orders'][i])

            corredores = []
            #print("Corredores")
            for i in range(n_corredores):
                if corredor_Y[i].x == 1:
                    #print(parsed_data['aisles'][i])
                    corredores.append(parsed_data['aisles'][i])
            #solucoes_dict[a] = [pedidos, corredores]
            melhor_solucao = [pedidos, corredores]
    else:
        print("Nao tem solucao", "A = ", a + 1, end=" | ")
        print("Tempo = %.4f" % (time.time() - t))
        #solucoes.append(0)
    model.remove(restricao_temporaria)

total_temp = time.time() - total_temp
print("Tempo total:", total_temp)

print("MELHOR SOLUCAO")
print("valor = ",  best)
print("Corredores = ", best_A)
if False:
    print("PEDIDOS")
    for i in melhor_solucao[0]:
        print(i)
    print("CORREDORES")
    for i in melhor_solucao[1]:
        print(i)


# função para validar resultado
# def validar_resultado(pedido, corredor, parsed_data = parsed_data):
#    itens_invalid = []
#    itens_temp = [0 for i in range(parsed_data['num_items'])]
#    for i in pedido:
#        for j in i:
#            itens_temp[j[0]] += j[1]
#
#    for i in corredor:
#        for j in i:
#            itens_temp[j[0]] -= j[1]
#    for i in range(len(itens_temp)):
#        if itens_temp[i] > 0:
#            itens_invalid.append(i)
#    print(itens_invalid)
#    return itens_invalid
#
#    
#validar  = validar_resultado(pedidos, corredores)
    
