import pandas as pd
import pathlib
from preprocess import preprocess
import spacy
from nltk.corpus import stopwords
import nltk
import string
import sklearn.feature_extraction.text as sklearntext
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

from preprocess import preprocess

import pbg

class extractor():
    def __init__(self, discursos, partidos, n_components) -> None:
        """Father class of bow_lda and tfidf_pbg. The methods in here are for most NOT implemented. 
        Trying to call topic extraction methods on this class will result on NotImplementedError.
        This class only implements preprocessing text methods once those are common to both classes."""
        stop_words_path = pathlib.Path("./stop_words.txt")
        self.discursos = [preprocess(discurso) for discurso in discursos]
        self.n_components = n_components
        stop_words = set(stopwords.words("portuguese"))
        stop_words.update(stop_words_path.read_text("utf-8").splitlines())
        self.stop_words = stop_words
        self.treated = False
        self.partidos = partidos

    def process_text(self, allowed_postags:list[str] = ["NOUN", "ADJ", "ADV", "VERB", "PUNCT"]) -> None:
        """This method processes the text before it can enter the process of vectorizing the texts.
        Parameters:
            allowed_postags:Says which type of postags are permitted. The types are:
            * Noun (NOUN),
            * Adjective (ADJ),
            * Adverb (ADV),
            * Verb (VERB),
            * Punctuation (PUNCT)
        Returns:
            None. To get threated discursos use get_processed_text method"""
        if self.treated == True:
            return
        self.nlp = spacy.load("pt_core_news_lg")
        lemmatized_discursos = self.lemmatization(allowed_postags=allowed_postags)
        discursos_lower = [[discurso.lower() for discurso in discursos] for discursos in lemmatized_discursos]
        discursos_tokenized = [[nltk.word_tokenize(discurso) for discurso in discursos] for discursos in discursos_lower]
        treated_discursos = [self.__remove_stop_words_punct(discursos) for discursos in discursos_tokenized]
        self.treated_discursos = treated_discursos
        self.treated = True # Esta implementação ainda está ineficiente e não contempla chamar as funções de modo separado
    
    def get_processed_text(self):
        """Função para não ter que tratar o texto 2 vezes caso esteja-se realizando a extração com LDA e PBG"""
        if self.treated:
            return self.treated_discursos;
    
    def lemmatization(self, allowed_postags):
        lemmatized_discursos = [self.__lemmatization(discursos, self.nlp, allowed_postags=allowed_postags) for discursos in self.discursos]
        return lemmatized_discursos
    
    def __lemmatization(self, texts: list[str], nlp, allowed_postags = ["NOUN", "ADJ", "VERB", "ADV"]):
        texts_out = []
        for sent in texts:
            doc = nlp(sent)
            texts_out.append(" ".join([token.lemma_ if token.lemma_ not in ["-PRON-"] else "" for token in doc if token.pos_ in allowed_postags]))
        return texts_out
    
    def __remove_stop_words_punct(self, discursos: list[list[str]]) -> list[list[str]]:

        novos_discursos = []
        for discurso in discursos:
            novo_discurso = []
            for token in discurso:
                if ((token not in string.punctuation) and (token not in self.stop_words)):
                    novo_discurso.append(token)
            novo_discurso = " ".join(novo_discurso)
            novos_discursos.append(novo_discurso)
        return novos_discursos
    
    def data_vectorizer(self):
        raise NotImplementedError()

    def __data_vectorizer(self, vectorizer, discursos):
        raise NotImplementedError()

class bow_lda(extractor):
    def __init__(self, discursos: list[list[str]], partidos: list[str], n_components: int) -> None:
        """Creates an topic extractor to use BoW and LDA to extract topics"""
        super().__init__(discursos, partidos, n_components)
        self.vectorizer = sklearntext.CountVectorizer(analyzer="word", stop_words=None, lowercase=True)
    
    def topic_extraction(self, n_words):
        """Extracts topics from preprocessed texts utilizing LDA.
        Parameters:
            n_words: Number of words that should be saved at each topic.
        Returns:
            None.
        Be careful, this method consumes large amount of working memory, so do not try to use it with huge datasets on limited RAM machines (RAM < 8GB does not work for 14000+ speeches, empirically tested)"""
        self.lda_models = [self.__lda_transform_fit(data_vectorized_) for data_vectorized_ in self.data_vectorized]
        topics_keywords_lst = [self.__transform_topics(feature_name, self.lda_models[i].components_, n_words) for i, feature_name in enumerate(self.feature_names)]
        self.topics_keywords = [pd.DataFrame(topics_keywords) for topics_keywords in topics_keywords_lst]

    def to_csv(self, path: pathlib.Path | str):
        """The path must be a directory"""
        if type(path) is str:
            save_path = pathlib.Path(path)
        elif (type(path) is pathlib.Path) or (type(path) is pathlib.PosixPath) or (type(path) is pathlib.WindowsPath):
            save_path = path
        else:
            raise TypeError()
        save_path.mkdir(parents=True, exist_ok=True)
        for i, df in enumerate(self.topics_keywords):
            topics_path = save_path.joinpath(f"topics_{self.partidos[i]}.csv")
            df.columns = ["Word " + str(i) for i in range(df.shape[1])]
            df.index = ["Topic " + str(i) for i in range(df.shape[0])]
            df.to_csv(topics_path)

    def data_vectorizer(self):
        """Vectorized the data in the class to create a Bow Matrix of each party."""
        data_vectorized = []
        feature_names = []
        for discursos_ in self.treated_discursos:
            data, feature_name = self.__data_vectorizer(self.vectorizer, discursos=discursos_)
            data_vectorized.append(data)
            feature_names.append(feature_name)
        self.data_vectorized = data_vectorized
        self.feature_names = feature_names

    def __data_vectorizer(self, vectorizer: sklearntext.CountVectorizer, discursos: list):
        matrix_discursos = vectorizer.fit_transform(discursos)
        feature_names = vectorizer.get_feature_names_out()
        return matrix_discursos, feature_names

    def __lda_transform_fit(self, data_vectorized: np.ndarray) -> LatentDirichletAllocation:
        lda_model = LatentDirichletAllocation(learning_method="online", random_state=100, batch_size=128, evaluate_every=-1, n_jobs=-1, n_components=self.n_components)
        lda_output = lda_model.fit_transform(data_vectorized)
        return lda_model
    
    def __transform_topics(self, feature_names:np.ndarray, lda_model_components: np.ndarray, n_words = 20) -> list:
        keywords = np.array(feature_names)
        topic_keywords = []
        for topic_weights in lda_model_components:
            top_keyword_locs = (-topic_weights).argsort()[:n_words]
            topic_keywords.append(keywords.take(top_keyword_locs))
        return topic_keywords
    
class tfidf_pbg(extractor):
    def __init__(self, discursos: list[list[str]], partidos: list[str], n_components: int) -> None:
        """Creates a topic extractor to use TF-IDF and PBG."""
        super().__init__(discursos, partidos, n_components)
        self.vectorizer = sklearntext.TfidfVectorizer()

    def data_vectorizer(self):
        """Vectorize data to create a TF-IDF matrix that will be used to extract topics.
        Parameters:
            None.
        Returns:
            None."""
        data_vectorized = []
        feature_names = []
        for discursos_ in self.treated_discursos:
            data, feature_name = self.__data_vectorizer(self.vectorizer, discursos=discursos_)
            data_vectorized.append(data)
            feature_names.append(feature_name)
        self.data_vectorized = data_vectorized
        self.feature_names = feature_names

    def __data_vectorizer(self, vectorizer, discursos):
        matrix_discursos = vectorizer.fit_transform(discursos)
        feature_names = vectorizer.get_feature_names_out()
        return matrix_discursos, feature_names
    
    def topic_extraction(self, n_words):
        """This function extracts the topics from a corpus of data preprocessed and vectorized utilizing PBG algorithm.
        Parameters:
            n_words: Number of words to be extracted at each topic
        Returns:
            None. Saves the topics at self.topics_keywords as a list of Dataframes."""
        self.pbg = [pbg.PBG(n_components=self.n_components, feature_names=feature_name, save_interval=1) for feature_name in self.feature_names]
        topics_discursos = []
        for i, data_vectorized in enumerate(self.data_vectorized):
            self.pbg[i].fit(data_vectorized)
            topics_discursos.append(self.pbg[i].get_topics(n_top_words=n_words))

        self.topics_keywords = [pd.DataFrame(topics_keywords) for topics_keywords in topics_discursos]

    def to_csv(self, path: pathlib.Path | str):
        """The path must be a directory"""
        if type(path) is str:
            save_path = pathlib.Path(path)
        elif (type(path) is pathlib.Path) or (type(path) is pathlib.PosixPath) or (type(path) is pathlib.WindowsPath):
            save_path = path
        else:
            raise TypeError()
        save_path.mkdir(parents=True, exist_ok=True)
        for i, df in enumerate(self.topics_keywords):
            topics_path = save_path.joinpath(f"topics_{self.partidos[i]}.csv")
            df.columns = ["Word " + str(i) for i in range(df.shape[1])]
            df.index = ["Topic " + str(i) for i in range(df.shape[0])]
            df.to_csv(topics_path)

def main():
    path_reading = pathlib.Path("./discursos/legis_56/p_novo/2022/")
    save_path_lda = pathlib.Path("./topics/lda/legis_56/p_novo/2022/")
    save_path_pbg = pathlib.Path("./topics/pbg/legis_56/p_novo/2022/")
    files = path_reading.iterdir()
    df_list = [pd.read_csv(file) for file in files]
    partidos = []
    discursos =[]
    for df in df_list:
        partidos.extend(df["sigla"].unique().tolist())
        discursos.append(df["transcricao"].tolist())

    lda = bow_lda(discursos=discursos, partidos=partidos, n_components=12)
    print("Processando LDA")
    lda.process_text()
    lda.data_vectorizer()
    print("Extraindo lDA")
    lda.topic_extraction(15)
    print("Salvando LDA")
    lda.to_csv(save_path_lda)
    
    treated_discursos =  lda.get_processed_text()

    del lda

    pbg_ex = tfidf_pbg(discursos=discursos, partidos=partidos, n_components=12)
    print("Processando PBG")
    pbg_ex.treated_discursos = treated_discursos
    pbg_ex.data_vectorizer()
    print("Extraindo PBG")
    pbg_ex.topic_extraction(15)
    print("Salvando PBG")
    pbg_ex.to_csv(save_path_pbg)

def main_oposicao():
    path_reading = pathlib.Path("./discursos/legis_56/oposição/2019/")
    save_path_lda = pathlib.Path("./topics/lda/legis56/oposição/2019/")
    save_path_pbg = pathlib.Path("./topics/pbg/legis_56/oposição/2019/")
    files = path_reading.iterdir()
    df_list = [pd.read_csv(file) for file in files]
    partidos = ["oposição"] # Partido "governista"
    discursos = []
    for df in df_list:
        discursos.extend(df["transcricao"].tolist()) # Faz com que os discursos sejam interpretados como os discursos de um único partido

    discursos = [discursos] # O algoritmo espera receber [[discursosA], [discursosB],...], nesse caso tem-se somente uma lista de discursos
    
    lda = bow_lda(discursos=discursos, partidos=partidos, n_components=30)
    lda.process_text(allowed_postags=["NOUN","VERB", "PUNCT"])
    lda.data_vectorizer()
    lda.topic_extraction(n_words=20)
    lda.to_csv(save_path_lda)
    treated_texts = lda.get_processed_text()

    del lda

    pbg_ex = tfidf_pbg(discursos=discursos, partidos=partidos, n_components=30)
    pbg_ex.treated_discursos = treated_texts
    pbg_ex.data_vectorizer()
    pbg_ex.topic_extraction(20)
    pbg_ex.to_csv(save_path_pbg)

if __name__ == "__main__":
    main()