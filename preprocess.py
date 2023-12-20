'''This module has the preprocess function for the code.'''


import re


def preprocess(lista_discursos: list) -> list:
    '''Function that preprocesses the text.

    Takes out \\r\\n for \\n

    Also removes the (Name - Party) and it's found alternatives.'''
    discursos = [discurso.replace("\r\n", "\n")
                 for discurso in lista_discursos]

    # Removes the (name - party )
    discursos = [re.sub(r"\b[A-Z]+(?:\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ'.]+)*\s\([\s\w\-\./]+\)\s\-\s|\b[A-Z]+(?:\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ'.]+)*\s\([\w\s]+\.\s\w+\s\-\s\w+\)\s\-\s",
                        "", discurso)
                 for discurso in discursos]
    discursos = [re.sub(r"\b[Ss]r[as]*\.", "", discurso)
                 for discurso in discursos]
    discursos = [re.sub(r"\d+(?:[.,]\d+)*", "", discurso)
                 for discurso in discursos]
    return discursos
