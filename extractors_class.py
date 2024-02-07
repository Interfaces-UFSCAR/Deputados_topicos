'''Module that contains the Topic Extrators for the code

The classes to be used in this module are:

1. bow_lda class

    Implements a LDA class to be used for topic extraction

    Implements the processing of the text using BoW

2. pbg_tfidf class

    Implements the PBG class to be used for topic extraction

    Implements the processing of the text using TF-IDF
'''

import pathlib
import pandas as pd
import spacy
import sklearn.feature_extraction.text as sklearntext
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation

import pbg

from preprocess import preprocess
import processer


class Extractor():
    """Father class of bow_lda and tfidf_pbg.
    The methods in here are for most NOT implemented.
    Calling topic extraction methods results on NotImplementedError.
    This class only implements preprocessing text methods
    once those are common to both classes."""
    def __init__(self, discursos, partidos, n_components) -> None:
        self.discursos = [preprocess(discurso) for discurso in discursos]
        self.n_components = n_components
        self.treated = False
        self.partidos = partidos
        self.treated_discursos: list[list[str]]
        self.nlp: spacy.language.Language
        self.processer = processer.Processer(self.discursos)

    def process_text(self, allowed_postags: list[str] | None = None) -> None:
        """Processes the text on the Processer class"""
        treated_discursos = self.processer.process_text(
            allowed_postags=allowed_postags)
        self.treated_discursos = treated_discursos

    def get_processed_text(self):
        """Função para receber o texto pré-processado"""
        if self.treated:
            return self.treated_discursos
        return None

    def data_vectorizer(self):
        '''Vectorizes data'''
        raise NotImplementedError()


class BowLda(Extractor):
    '''This class implements Bag Of Words with LDA.

    This is a more usual approach to the topics extraction'''
    def __init__(self,
                 discursos: list[list[str]],
                 partidos: list[str],
                 n_components: int) -> None:
        """Creates an topic extractor to use BoW and LDA to extract topics"""
        super().__init__(discursos,
                         partidos,
                         n_components)
        self.vectorizer = sklearntext.CountVectorizer(analyzer="word",
                                                      stop_words=None,
                                                      lowercase=True)
        self.topics_keywords: list[pd.DataFrame]
        self.lda_models: list[LatentDirichletAllocation]
        self.data_vectorized: list
        self.feature_names: list

    def topic_extraction(self, n_words):
        """Extracts topics from preprocessed texts utilizing LDA.

        Parameters:

            n_words: Number of words that should be saved at each topic.

        Returns:
            None.

        Be careful, this method consumes large amount of working memory,
        so do not try to use it with huge datasets on limited RAM machines
        (RAM < 8GB does not work for 14000+ speeches, empirically tested)"""
        self.lda_models = [self.__lda_transform_fit(data_vectorized_)
                           for data_vectorized_ in self.data_vectorized]
        topics_keywords_lst = [
            self.__transform_topics(feature_name,
                                    self.lda_models[i].components_,
                                    n_words) for i, feature_name in enumerate(
                                        self.feature_names)]
        self.topics_keywords = [pd.DataFrame(topics_keywords)
                                for topics_keywords in topics_keywords_lst]

    def to_csv(self, path: pathlib.Path | str):
        """The path must be a directory"""
        if isinstance(path, str):
            save_path = pathlib.Path(path)
        elif (isinstance(path, pathlib.Path)) \
            or (isinstance(path, pathlib.PosixPath)) \
                or (isinstance(path, pathlib.WindowsPath)):
            save_path = path
        else:
            raise TypeError()
        save_path.mkdir(parents=True, exist_ok=True)
        for i, df in enumerate(self.topics_keywords):
            topics_path = save_path.joinpath(f"topics_{self.partidos[i]}.csv")
            df.columns = pd.Index(["Word " + str(i)
                                   for i in range(df.shape[1])])
            df.index = pd.Index(["Topic " + str(i)
                                 for i in range(df.shape[0])])
            df.to_csv(topics_path)

    def data_vectorizer(self):
        """Vectorize the data in the class to create a Bow Matrix of each party."""
        data_vectorized = []
        feature_names = []
        for discursos_ in self.treated_discursos:
            data, feature_name = self.__data_vectorizer(self.vectorizer,
                                                        discursos=discursos_)
            data_vectorized.append(data)
            feature_names.append(feature_name)
        self.data_vectorized = data_vectorized
        self.feature_names = feature_names

    def __data_vectorizer(self,
                          vectorizer: sklearntext.CountVectorizer,
                          discursos: list):
        matrix_discursos = vectorizer.fit_transform(discursos)
        feature_names = vectorizer.get_feature_names_out()
        return matrix_discursos, feature_names

    def __lda_transform_fit(self,
                            data_vectorized: np.ndarray
                            ) -> LatentDirichletAllocation:

        lda_model = LatentDirichletAllocation(
            learning_method="online",
            random_state=100,
            batch_size=128,
            evaluate_every=-1,
            n_jobs=-1,
            n_components=self.n_components
        )
        # Applies the data to the model before saving it
        # The result is not captured once it's not used
        lda_model.fit_transform(data_vectorized)
        return lda_model

    def __transform_topics(self,
                           feature_names: np.ndarray,
                           lda_model_components: np.ndarray,
                           n_words=20) -> list:

        keywords = np.array(feature_names)
        topic_keywords = []
        for topic_weights in lda_model_components:
            top_keyword_locs = (-topic_weights).argsort()[:n_words]
            topic_keywords.append(keywords.take(top_keyword_locs))
        return topic_keywords


class TfidfPbg(Extractor):
    '''Implements TF-IDF with PBG.

    A graph approach to the topic extraction problem'''
    def __init__(self,
                 discursos: list[list[str]],
                 partidos: list[str],
                 n_components: int) -> None:
        """Creates a topic extractor to use TF-IDF and PBG."""
        super().__init__(discursos, partidos, n_components)
        self.vectorizer = sklearntext.TfidfVectorizer()
        self.data_vectorized: list
        self.feature_names: list
        self.pbg: list[pbg.PBG]
        self.topics_keywords: list[pd.DataFrame]

    def data_vectorizer(self):
        """Vectorize data to create a TF-IDF matrix that will be used to extract topics.
        Parameters:
            None.
        Returns:
            None."""
        data_vectorized = []
        feature_names = []
        for discursos_ in self.treated_discursos:
            data, feature_name = self.__data_vectorizer(
                self.vectorizer,
                discursos=discursos_)
            data_vectorized.append(data)
            feature_names.append(feature_name)
        self.data_vectorized = data_vectorized
        self.feature_names = feature_names

    def __data_vectorizer(self, vectorizer, discursos):
        matrix_discursos = vectorizer.fit_transform(discursos)
        feature_names = vectorizer.get_feature_names_out()
        return matrix_discursos, feature_names

    def topic_extraction(self, n_words):
        """Extracts the topics from a corpus utilizing PBG algorithm.
        Parameters:
            n_words: Number of words to be extracted at each topic
        Returns:
            None.
            Saves the topics at self.topics_keywords as a list of Dataframes
        """
        self.pbg = [pbg.PBG(n_components=self.n_components,
                            feature_names=feature_name,
                            save_interval=1)
                    for feature_name in self.feature_names]
        topics_discursos = []
        for i, data_vectorized in enumerate(self.data_vectorized):
            self.pbg[i].fit(data_vectorized)
            topics_discursos.append(self.pbg[i].get_topics(n_top_words=n_words))

        self.topics_keywords = [pd.DataFrame(topics_keywords)
                                for topics_keywords in topics_discursos]

    def to_csv(self, path: pathlib.Path | str):
        """The path must be a directory"""
        if isinstance(path, str):
            save_path = pathlib.Path(path)
        elif isinstance(path, (pathlib.Path,
                               pathlib.PosixPath,
                               pathlib.WindowsPath)):
            save_path = path
        else:
            raise TypeError()
        save_path.mkdir(parents=True, exist_ok=True)
        for i, df in enumerate(self.topics_keywords):
            topics_path = save_path.joinpath(f"topics_{self.partidos[i]}.csv")
            df.columns = pd.Index(["Word " + str(i) for i in range(df.shape[1])])
            df.index = pd.Index(["Topic " + str(i) for i in range(df.shape[0])])
            df.to_csv(topics_path)


def main():
    '''
    Extracts topics for a determined party, in this case, Novo.

    The function reads the speeches and save the table of topics
    on the determined path.'''
    path_reading = pathlib.Path("./discursos/legis_56/p_novo/2022/")
    save_path_lda = pathlib.Path("./topics/lda/legis_56/p_novo/2022/")
    save_path_pbg = pathlib.Path("./topics/pbg/legis_56/p_novo/2022/")
    files = path_reading.iterdir()
    df_list = [pd.read_csv(file) for file in files]
    partidos = []
    discursos = []
    for df in df_list:
        # In this case, the only party is Novo,
        # but this code is ready for multiple parties
        # The code isn't ready for multiple parties on a single file
        partidos.extend(df["sigla"].unique().tolist())
        discursos.append(df["transcricao"].tolist())

    lda = BowLda(discursos=discursos, partidos=partidos, n_components=12)
    print("Processando LDA")
    lda.process_text()
    lda.data_vectorizer()
    print("Extraindo lDA")
    lda.topic_extraction(15)
    print("Salvando LDA")
    lda.to_csv(save_path_lda)

    treated_discursos = lda.get_processed_text()

    # Necessary so the memory on the test computer doesn't run empty
    del lda

    pbg_ex = TfidfPbg(discursos=discursos, partidos=partidos, n_components=12)
    print("Processando PBG")
    pbg_ex.treated_discursos = treated_discursos
    pbg_ex.data_vectorizer()
    print("Extraindo PBG")
    pbg_ex.topic_extraction(15)
    print("Salvando PBG")
    pbg_ex.to_csv(save_path_pbg)


def main_oposicao():
    '''
    Extracts the topics for a the oposition to the govern.

    This function extracts the topics for a single year on speeches.
    '''
    path_reading = pathlib.Path("./discursos/legis_56/oposição/2019/")
    save_path_lda = pathlib.Path("./topics/lda/legis56/oposição/2019/")
    save_path_pbg = pathlib.Path("./topics/pbg/legis_56/oposição/2019/")
    files = path_reading.iterdir()
    df_list = [pd.read_csv(file) for file in files]
    partidos = ["oposição"]  # Partido "governista"
    discursos = []
    for df in df_list:
        discursos.extend(df["transcricao"].tolist())
        # Faz com que os discursos sejam interpretados como os discursos de um partido

    discursos = [discursos]
    # O algoritmo espera receber [[discursosA], [discursosB],...],
    # nesse caso tem-se somente uma lista de discursos

    lda = BowLda(discursos=discursos, partidos=partidos, n_components=30)
    lda.process_text(allowed_postags=["NOUN", "VERB", "PUNCT"])
    lda.data_vectorizer()
    lda.topic_extraction(n_words=20)
    lda.to_csv(save_path_lda)
    treated_texts = lda.get_processed_text()

    del lda

    pbg_ex = TfidfPbg(discursos=discursos, partidos=partidos, n_components=30)
    pbg_ex.treated_discursos = treated_texts
    pbg_ex.data_vectorizer()
    pbg_ex.topic_extraction(20)
    pbg_ex.to_csv(save_path_pbg)


if __name__ == "__main__":
    main()
