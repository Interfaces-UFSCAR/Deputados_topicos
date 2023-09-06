import networkx as nx
import igraph as ig
import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import netgraph

class Converter():
    def __init__(self) -> None:
        """This initializer instanciate a clean converter, without topics, without edgelist or any other object internally"""
        self.topics = None
        self.edgelist = None
        self.G = None
        self.palavras = None

    def set_topics(self, topics: pd.DataFrame) -> None:
        try:
            # Tenta realizar o drop dos índices
            topicos = topics.drop("Unnamed: 0", inplace=False, axis=1)
        except:
            topicos = topics
        self.topics = topicos

    def set_topics_calc(self, topics: pd.DataFrame):
        self.set_topics(topics)
        self.convert_to_edge_list()
        self.dataframe_to_networkx()

    def convert_to_edge_list(self, topicos: pd.DataFrame = None):
        if self.topics is None:
            if topicos is None:
                raise AttributeError("You need to use set_topics method or set the edgelist in this function")
        if topicos is not None:
            self.set_topics(topicos)
        topics = self.topics.values.tolist()
        topics = [sorted(topico) for topico in topics]

        edgelist = []
        for linha in topics:
            for i, palavra in enumerate(linha):
                for palavra_ in linha[i+1:len(linha)]:
                    edgelist.append([palavra, palavra_])
        df_edgelist = pd.DataFrame(edgelist)
        df_edgelist.columns = ["From", "To"]

        df_edgelist = df_edgelist.groupby(df_edgelist.columns.tolist(), as_index=False).size()

        unique_words = set()

        unique_words.update(df_edgelist["From"].unique().tolist())
        unique_words.update(df_edgelist["To"].unique().tolist())

        self.palavras = unique_words
        self.edgelist = df_edgelist
        return self
    
    def dataframe_to_networkx(self, topics: pd.DataFrame = None) -> nx.Graph:
        if (self.edgelist is None and self.topics is None and topics is None):
            raise AttributeError("Topics should be informed, with set_topics or topics parameter")
        if topics:
            self.topics = topics
            self.convert_to_edge_list()

        G = nx.from_pandas_edgelist(self.edgelist, "From", "To")
        self.G = G
        return G

def create_big_graph(graphs: list[nx.Graph]):
    G = nx.Graph()
    for graph in graphs:
        G = nx.compose(G.copy(), graph)
    return G

def main_partido():
    file_path = pathlib.Path("./topics/pbg/pos_pandemia/topics_PT.csv")
    topics = pd.read_csv(file_path)
    converter = Converter().convert_to_edge_list(topics)

    edge_list = converter.edgelist
    agg_fun = {"size":"sum"}
    edge_list = edge_list.groupby(edge_list.columns.tolist(), as_index=False).aggregate(agg_fun)

    edge_list.columns = ["From", "To", "weight"]

    G=nx.from_pandas_edgelist(edge_list, "From", "To", edge_attr="weight")

    pos = nx.layout.spring_layout(G, k=0.5)

    nx.draw(G, pos=pos, 
            with_labels=True, 
            node_color="red", 
            node_size=3, 
            font_size=5, 
            width=1, 
            edge_color="gainsboro")
    
    plt.savefig("PT_PBG_graph.pdf")

def main_orientacao():
    files_path = list(pathlib.Path("./topics/lda/legis56/oposição/").iterdir())

    files = [pd.read_csv(file) for file in files_path]
    converters = [Converter().convert_to_edge_list(topicos) for topicos in files]

    edge_list = [converter.edgelist for converter in converters]
    edge_list = pd.concat(edge_list)
    agg_fun = {"size": "sum"}
    edge_list = edge_list.groupby(edge_list.columns.tolist(), as_index=False).aggregate(agg_fun) # Sum repeating edges summing "size" column
    edge_list.columns = ["From", "To", "weight"]

    G = nx.from_pandas_edgelist(edge_list,"From", "To", edge_attr="weight")

    pos = nx.layout.spring_layout(G=G, iterations=25, k=0.2, scale=2)

    nx.draw(G, 
            pos=pos, 
            edge_color="gainsboro", 
            node_size=4, 
            font_size=2,
            width=0.1,
            with_labels=True)
    plt.savefig("grafo_oposição.pdf")

def main():
    files_path = list(pathlib.Path("./topics/lda/pos_pandemia").iterdir())
#    file_names = [path.name for path in files_path] # somente usável eu for fazer as polaridades através de regex
    polarities = pathlib.Path("./polarities_pos.txt").read_text("utf-8").splitlines()
    polarities = [-1*int(polarity.split()[1]) for polarity in polarities] # para que as cores fiquem mais intuitivas
    files = [pd.read_csv(file) for file in files_path]
    converters = [Converter().convert_to_edge_list(topicos) for topicos in files]

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
    words_unique = words_unique.reindex(G.nodes())

    pos = nx.layout.spring_layout(G, k=3, iterations=1000, threshold=1e-6)

    nx.draw(G, with_labels=True, 
            node_color=words_unique["Peso"].astype(int), 
            cmap=plt.cm.coolwarm, 
            width=0.001, 
            edge_color="gainsboro", 
            node_size=2, 
            font_size=1, 
            pos=pos)

    plt.savefig("big_graph.pdf")

if __name__ == "__main__":
    main()