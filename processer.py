"""Module that contains the Text Processer for the application

This module contains the [Processer] class."""

import pathlib
import string
import spacy
from nltk.corpus import stopwords
import nltk


class Processer():
    """
    This class processes the text inserted

    It lemmatizes, lower and remove stop_words of all the text."""
    def __init__(self, discursos) -> None:
        self.nlp: spacy.language.Language
        self.discursos = discursos
        stop_words_path = pathlib.Path("./stop_words.txt")
        stop_words = set(stopwords.words("portuguese"))
        stop_words.update(stop_words_path.read_text("utf-8").splitlines())
        self.stop_words = stop_words

    def lemmatization(self, allowed_postags):
        """Makes the lemmatization on the code of all the speeches"""
        lemmatized_discursos = [self.__lemmatization(
            discursos,
            self.nlp,
            allowed_postags=allowed_postags)
            for discursos in self.discursos]
        return lemmatized_discursos

    def __lemmatization(self,
                        texts: list[str],
                        nlp, allowed_postags: list[str] | None = None):
        if allowed_postags is None:
            allowed_postags = ["NOUN", "ADJ", "VERB", "ADV"]
        texts_out = []
        for sent in texts:
            doc = nlp(sent)
            texts_out.append(" ".join([token.lemma_
                                       if token.lemma_ not in ["-PRON-"]
                                       else ""
                                       for token in doc
                                       if token.pos_ in allowed_postags]))
        return texts_out

    def __remove_stop_words_punct(self, discursos: list[list[str]]) -> list[str]:
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

    def process_text(self,
                     allowed_postags: list[str] | None = None) -> list[list[str]]:
        """Processes the text before it can enter the process of vectorizing.
        Parameters:
            allowed_postags:Says which type of postags are permitted.
            If ommitted all post tags are used.

            The types are:
            * Noun (NOUN),
            * Adjective (ADJ),
            * Adverb (ADV),
            * Verb (VERB),
            * Punctuation (PUNCT)
        Returns:
            None. To get treated discursos use get_processed_text method"""
        self.nlp = spacy.load("pt_core_news_lg")
        lemmatized_discursos = self.lemmatization(allowed_postags)
        discursos_lower = [[discurso.lower()
                            for discurso in discursos]
                           for discursos in lemmatized_discursos]
        discursos_tokenized = [[nltk.word_tokenize(discurso)
                                for discurso in discursos]
                               for discursos in discursos_lower]
        treated_discursos = [self.__remove_stop_words_punct(
            discursos=discursos)
            for discursos in discursos_tokenized]
        return treated_discursos
