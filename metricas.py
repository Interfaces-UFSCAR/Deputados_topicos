'''This module contains classes that calculates som edata from the data.

The main thing in this module is the DBAnalyzer class'''

import string
import pathlib
import time

import pandas as pd
from nltk.corpus import stopwords
import numpy as np
import nltk
import spacy

from preprocess import preprocess


class DBAnalyzer():
    '''
    This class is made to calculate some calculations from the Data.
    Like the different words, the most used words and the word count
    for each party'''
    def __init__(self,
                 ll_discursos: list[list[str]],
                 partidos: list[str]) -> None:
        self.stop_words = set(stopwords.words("portuguese"))
        self.stop_words.update(pathlib.Path("./stop_words.txt")
                               .read_text("utf-8").splitlines())
        self.discursos = [preprocess(discursos) for discursos in ll_discursos]
        self.partidos = partidos
        self.words_diff = None
        self.words_diff_num: list[int]
        self.most_used_words: list[str]
        self.word_count: list[float]
        self.treated_discursos: list[list[str]]

    def treat_discursos(self):
        """This function treat the speaches provided doing lemmatization
        and removing stopwords and punctuation"""
        lemmatized_discurso = self.lemmatization()
        discursos_lower = [[discurso.lower() for discurso in discursos]
                           for discursos in lemmatized_discurso]
        discursos_tokenized = [[nltk.word_tokenize(discurso)
                                for discurso in discursos]
                               for discursos in discursos_lower]
        treated_discursos = [self.remove_stopwords_punct(discursos)
                             for discursos in discursos_tokenized]
        self.treated_discursos = treated_discursos

    def lemmatization(self):
        '''Makes the lemmatization on the text for all parties.'''
        nlp = spacy.load("pt_core_news_lg")
        lemmatized_discursos = [self.__lemmatization(discursos,
                                                     nlp=nlp,
                                                     allowed_postags=None)
                                for discursos in self.discursos]
        return lemmatized_discursos

    def __lemmatization(self,
                        texts: list,
                        nlp: spacy.language.Language,
                        allowed_postags: list[str] | None = None):
        if allowed_postags is None:
            allowed_postags = ["NOUN", "ADJ", "VERB", "ADV"]
        texts_out = []
        for sent in texts:
            doc = nlp(sent)
            texts_out.append(" ".join([token.lemma_
                                       if token.lemma_ not in ["-PRON-"]
                                       else ""
                                       for token in doc if token.pos_
                                       in allowed_postags]))
        return texts_out

    def remove_stopwords_punct(self, discursos: list[list[str]]) -> list[str]:
        '''Remove stopwords and punctuation from the data in discursos.'''
        novos_discursos = []
        for discurso in discursos:
            novo_discurso = []
            for token in discurso:
                if ((token not in string.punctuation)
                        and (token not in self.stop_words)):
                    novo_discurso.append(token)
            novo_discurso_str = " ".join(novo_discurso)
            novos_discursos.append(novo_discurso_str)
        return novos_discursos

    def medium_word_count(self):
        """This uses the ll_discursos class atributte
        to create a atributte of
        medium word counting for each party"""
        self.word_count = [self.__medium_word_count(discurso)
                           for discurso in self.treated_discursos]

    def __medium_word_count(self, discursos) -> float:
        '''This function creates the medium word count for a single party'''
        soma_palavras = 0
        for discurso in discursos:
            list_discurso = discurso.split()
            soma_palavras += len(list_discurso)
        return soma_palavras/len(discursos)

    def diff_words(self):
        """Creates two different attributes in the class,
        being one of them a list of set of unique words used by each party
        The second attribute created is the attribute
        of the count of number of different words by party."""
        self.words_diff = [self.__diff_words(discurso)
                           for discurso in self.treated_discursos]
        self.words_diff_num = [len(word_diff) for word_diff in self.words_diff]

    def __diff_words(self, discursos) -> set:
        palavras = set()
        for discurso in discursos:
            list_discurso = discurso.split()
            palavras.update(list_discurso)
        return palavras

    def most_used_word(self):
        '''Calculate the most used word for all parties'''
        if self.words_diff is None:
            raise AttributeError("""words_diff must be setted.
                                 Run diff_words method previously to do so""")
        most_used = [self.__most_used_words(discursos=discursos,
                                            words=self.words_diff[i])
                     for i, discursos in enumerate(self.treated_discursos)]
        self.most_used_words = most_used

    def __most_used_words(self, discursos: list[str], words: set) -> str:
        '''Calculate the most used word for a single party'''
        words_count = {word: 0 for word in words}
        for discurso in discursos:
            discurso_split = discurso.split()
            for word in words_count:
                count_word = discurso_split.count(word)
                words_count[word] += count_word
        most_common = max(words_count, key=lambda word: word.get)
        return most_common

    def calculate(self) -> pd.DataFrame:
        '''Calculate all the implemented metrics.

        1. Words count

        2. Different words count

        3. Most used word

        4. Quantity of speeches'''
        self.medium_word_count()
        self.diff_words()
        self.most_used_word()
        discursos_quantity = [len(discursos)
                              for discursos in self.treated_discursos]
        dados = [self.partidos, self.word_count,
                 self.words_diff_num, self.most_used_words,
                 discursos_quantity]
        dados_np = np.array(dados)     # Necessário para fazer a transposição
        # Mais eficiente
        dados = np.transpose(dados_np).tolist()
        dados_columns = ["Partidos", "mediumWordsNumber",
                         "NumberOfDiffWords", "MostUsedWord",
                         "discursosQuantity"]
        df_dados = pd.DataFrame(dados)
        df_dados.columns = pd.Index(dados_columns)
        df_dados = df_dados.set_index('Partidos')
        return df_dados


def main():
    '''Function to be used for collecting the metrics from the discursos.'''
    path = pathlib.Path("./discursos/")
    path_pre_pos = pathlib.Path("./pre_pandemia/")
    path = path.joinpath(path_pre_pos)
    files = path.iterdir()
    df_list = [pd.read_csv(file) for file in files]
    partidos = []
    discursos = []
    for df in df_list:
        partidos.extend(df["sigla"].unique().tolist())
        discursos.append(df["transcricao"].tolist())

    analyzer = DBAnalyzer(ll_discursos=discursos, partidos=partidos)
    timeinit = time.time()
    analyzer.treat_discursos()
    timeend = time.time()
    print("Elapsed time: " + str(timeend - timeinit))
    dados = analyzer.calculate()
    metricas_path = pathlib.Path("./metricas/")
    metricas_path.mkdir(parents=True, exist_ok=True)
    dados.to_csv(pathlib.Path.joinpath(metricas_path.joinpath(path_pre_pos),
                                       "metricas.csv"))


def main_orientacao():
    '''
    Collect the metrics from the speeches based on polarity.
    This method was made to analyze the code looking by polarity of the party.
    '''
    path = pathlib.Path("./discursos/legis_56/")
    path_gov_opo = pathlib.Path("./governista/")
    path = path.joinpath(path_gov_opo)
    files = path.iterdir()
    df_list = [pd.read_csv(file) for file in files]
    partidos = []
    discursos = []
    for df in df_list:
        partidos.extend(df["sigla"].unique().tolist())
        discursos.append(df["transcricao"].tolist())

    analyzer = DBAnalyzer(ll_discursos=discursos, partidos=partidos)
    print("Tratando discursos")
    analyzer.treat_discursos()
    print("Calculando ...")
    dados = analyzer.calculate()
    metricas_path = pathlib.Path("./metricas/legis_56/").joinpath(path_gov_opo)
    metricas_path.mkdir(parents=True, exist_ok=True)
    dados.to_csv(pathlib.Path.joinpath(metricas_path, "metricas.csv"))


if __name__ == "__main__":
    main()
