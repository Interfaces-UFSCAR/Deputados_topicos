import netgraph
import networkx as nx
import pandas as pd
import pathlib
import matplotlib.pyplot as plt

import converte_rede as cr

def main():
    files_path = list(pathlib.Path("./topics/lda/pos_pandemia").iterdir())
#    file_names = [path.name for path in files_path] # somente usável eu for fazer as polaridades através de regex
    polarities = pathlib.Path("./polarities_pos.txt").read_text("utf-8").splitlines()
    polarities = [-1*int(polarity.split()[1]) for polarity in polarities] # Para que as cores fiquem corretas
    files = [pd.read_csv(file) for file in files_path]
    converters = [cr.Converter().convert_to_edge_list(topicos) for topicos in files]

    # Calculate edge_weight total
    edge_list = [converter.edgelist for converter in converters]
    edge_list = pd.concat(edge_list)
    agg_fun = {"size": "sum"}
    edge_list = edge_list.groupby(edge_list.columns.tolist(), as_index=False).aggregate(agg_fun)

    word_list = []
    for i, converter in enumerate(converters):
        for palavra in list(converter.palavras):
            word_list.append([palavra, polarities[i]])

    df_word_list = pd.DataFrame(word_list, columns=["Palavra", "Peso"])
    aggregate_fun = {"Peso": "mean"}
    words_unique = df_word_list.groupby("Palavra").aggregate(aggregate_fun)
    edge_list.columns = ["From", "To", "weight"]

    G = nx.from_pandas_edgelist(edge_list, "From", "To", edge_attr="weight")

    pos = nx.layout.spring_layout(G, k=3, iterations=1000, threshold=1e-5)
    words_unique = words_unique.reindex(G.nodes())
    words_unique_array = words_unique["Peso"].astype(int).tolist()
    cores = plt.cm.ScalarMappable(cmap=plt.cm.coolwarm).to_rgba(words_unique_array)
    dicionario_cores = {node: color for node, color in zip(G.nodes(), cores)}

    fig, ax = plt.subplots()
    netgraph.Graph(graph=G, 
                   node_size=0.5, 
                   node_edge_width=0.1, 
                   node_color=dicionario_cores, 
                   node_labels=True, 
                   edge_width=0.01,
                   edge_alpha=0.5,
                   edge_layout="bundled", 
                   node_layout=pos, 
                   ax=ax)
    plt.savefig("netgraph_graph.pdf")

def main_orientacao():
    files_path = list(pathlib.Path("./topics/lda/legis56/oposição/").iterdir())

    files = [pd.read_csv(file) for file in files_path]
    converters = [cr.Converter().convert_to_edge_list(topicos) for topicos in files]

    edge_list = [converter.edgelist for converter in converters]
    edge_list = pd.concat(edge_list)
    agg_fun = {"size": "sum"}
    edge_list = edge_list.groupby(edge_list.columns.tolist(), as_index=False).aggregate(agg_fun) # Sum repeating edges summing "size" column
    edge_list.columns = ["From", "To", "weight"]

    G = nx.from_pandas_edgelist(edge_list,"From", "To", edge_attr="weight")

    fig, ax = plt.subplots()
    netgraph.Graph(graph=G, 
                   node_layout="spring", 
                   node_layout_kwargs={
                       "edge_weights":{(u,v):weight["weight"] for u, v, weight in G.edges(data=True)},
                       "node_size":0.5, 
                       "k": 0.2
                   }, 
                   node_size=0.5, 
                   node_edge_width=0.1, 
                   node_labels=True, 
                   edge_width=0.1, 
                   edge_alpha=0.7, 
                   edge_layout='bundled',
                   ax=ax)
    plt.savefig("grafo_oposição.pdf")

def main_partido():
    """Realiza a criação de um grafo de um único partido, sem coloração ou nenhuma outro tipo de coisa, utilizando para a realização de testes com a biblioteca netgraph"""
    file_path = pathlib.Path("./topics/pbg/pos_pandemia/topics_PT.csv")
    topics = pd.read_csv(file_path)
    converter = cr.Converter().convert_to_edge_list(topics)

    edge_list = converter.edgelist
    agg_fun = {"size":"sum"}
    edge_list = edge_list.groupby(edge_list.columns.tolist(), as_index=False).aggregate(agg_fun)

    edge_list.columns = ["From", "To", "weight"]

    G=nx.from_pandas_edgelist(edge_list, "From", "To", edge_attr="weight")

    fig, ax = plt.subplots()
    netgraph.Graph(graph=G, 
                   node_size=0.5, 
                   node_edge_width=0.1, 
                   node_labels=True, 
                   edge_width=0.01, 
                   edge_alpha=0.5, 
                   edge_layout='bundled', 
                   ax=ax)
    plt.savefig("netgraph_graph.pdf")

if __name__ == "__main__":
    main_partido()