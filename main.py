import igraph as ig
import networkx as nx
import numpy as np
import csv
import math
import matplotlib.pyplot as plt

disciplinas = []
dict = {}
previous = {}
edges = []

class Vertex:
    def __init__(self, name, degree, betweenness,pagerank,closeness):
        self.name = name
        self.degree = degree
        self.betweenness = betweenness
        self.pagerank = pagerank
        self.closeness = closeness


with open("catalogo_disciplinas.csv", 'r', encoding='UTF8') as file:
    csvreader = csv.reader(file)
    header = next(csvreader)
    allCursos = ['BC&T - BACHARELADO EM CIENCIA E TECNOLOGIA (OBR)','']
    for currentCurso in allCursos:
        for row in csvreader:
            if currentCurso in row or currentCurso == '':
                disciplina = {}
                for col in row:
                    if col.strip() != "":
                        if header[row.index(col)] == "":
                            if type( disciplina[title]) == list:
                                disciplina[title].append(col)
                            else:
                                disciplina[title] = [disciplina[title],col]
                        else:
                            disciplina[header[row.index(col)]]=col
                            title = header[row.index(col)]
                
                disciplinas.append(disciplina)
                dict[disciplina['DISCIPLINA']] = len(disciplinas) -1
        name = []
        tpi = []
        cursos = []

        for item in disciplinas:
            name.append(item['DISCIPLINA'])
            # print(item)
            tpi.append(item['TPEI'])
            if 'CURSOS' in item:   
                cursos.append(item['CURSOS'])
            if 'RECOMENDACOES' in item:
                if type( item['RECOMENDACOES']) == list:
                    for recomendacao in item['RECOMENDACOES']:  
                        if recomendacao in dict:     
                                edges.append((disciplinas.index(item),dict[recomendacao]))
                else:
                    if item['RECOMENDACOES'] in dict: 
                            edges.append((disciplinas.index(item),dict[item['RECOMENDACOES']]))

        n_vertices = len(disciplinas)
        g = ig.Graph(n_vertices, edges, directed=True)

        g.vs["TPI"] = tpi
        g.vs["name"] = name
        g.vs["cursos"] = cursos

        def get_hex(value):
            convert_string = int(value, base=16)
            convert_hex = hex(convert_string)
            return convert_hex, convert_string

        communities = g.community_edge_betweenness()
        communities = communities.as_clustering()

        for i, community in enumerate(communities):
            print(f"Community {i}:")
            for v in community:
                print(f"\t{g.vs[v]['name']}")

        num_communities = len(communities)
        palette = ig.RainbowPalette(n=num_communities)
        for i, community in enumerate(communities):
            g.vs[community]["color"] = i
            community_edges = g.es.select(_within=community)
            community_edges["color"] = i
     
        fig, ax = plt.subplots(figsize=(16,9))
        g.simplify()

        cluster_graph = communities.cluster_graph(
            combine_vertices={
                "x": "mean",
                "y": "mean",
                "color": "first",
                "size": "sum",
            },
            combine_edges={
                "size": "sum",
            },
        )

        gl = g.linegraph()

        ig.plot(
            communities,
            mark_groups=True,
            target=ax,
            is_directed = True,
            vertex_size=0.5,
            palette=palette,
            vertex_frame_width=0.5,
            vertex_frame_color="black",
            vertex_label=g.vs["name"],
            vertex_label_size=4,
            edge_width= 0.5,
            edge_color="black"
        )
        print("Number of vertices in the graph:", g.vcount())
        print('\n')
        print("Number of edges in the graph", g.ecount())
        print('\n')
        print("Is the graph directed:", g.is_directed())
        print('\n')
        print("Maximum degree in the graph:", g.maxdegree())

        plt.show()


        with open(f'{currentCurso}stats.txt', 'w') as f:
            vertices = []
            for i, community in enumerate(communities):
                for v in community:
                    vertices.append(Vertex(g.vs[v]['name'],g.vs[v].degree(),g.vs[v].betweenness(),g.pagerank()[len(vertices)], g.vs[v].closeness()))
                    f.write(f"\t{g.vs[v]['name']}\n")
                    f.write(f"\t\tDegree: {g.vs[v].degree()}\n")
                    f.write(f"\t\tBetweenness: {g.vs[v].betweenness()}\n")

            vertices.sort(key=lambda x: x.betweenness, reverse=True)
            f.write(f"\n\n\nORDENADO POR BETWEENNESS:\n")
            for v in vertices:
                f.write(f"\t{v.name}\n")
                f.write(f"\t\tBetweenness: {v.betweenness}\n")

            vertices.sort(key=lambda x: x.degree, reverse=True)
            f.write(f"\n\n\nORDENADO POR GRAU:\n")
            for v in vertices:
                f.write(f"\t{v.name}\n")
                f.write(f"\t\tDegree: {v.degree}\n")
                
            vertices.sort(key=lambda x: x.pagerank, reverse=True)
            f.write(f"\n\n\nORDENADO POR PAGERANK:\n")
            for v in vertices:
                f.write(f"\t{v.name}\n")
                f.write(f"\t\tPagerank: {v.pagerank}\n")
                    
            vertices.sort(key=lambda x: x.closeness, reverse=True)
            f.write(f"\n\n\nORDENADO POR CLOSENESS:\n")
            for v in vertices:
                if not math.isnan(v.closeness):
                    f.write(f"\t{v.name}\n")
                    f.write(f"\t\tCloseness: {v.closeness}\n")

        fig.savefig(f'{currentCurso}network.jpg')
        fig.savefig(f'{currentCurso}network.pdf')
