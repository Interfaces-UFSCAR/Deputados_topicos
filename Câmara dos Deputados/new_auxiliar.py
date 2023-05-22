# Conjunto de classes que recebem um json parsed e retiram deles todas as informações
# Retira a necessidade de realizar mais uma requisição no momento da colet

import pandas as pd

class Partido():
    def __init__(self, requisicao) -> None:
        self.Id = requisicao["id"]
        self.sigla = requisicao["sigla"]
        self.nome = requisicao["nome"]
        self.uri = requisicao["uri"]

    def to_list(self):
        """This method returns a list of the object Partido
        
        Parameters: None
        Returns:
        [Id, sigla, nome, uri]"""
        return [self.Id, self.sigla, self.nome, self.uri]
    
    @classmethod
    def get_variables(cls):
        return ["Id", "sigla", "nome", "uri"]

class Deputado():
    def __init__(self, requisicao) -> None:
        self.Id = requisicao["id"]
        self.uri = requisicao["uri"]
        self.nome = requisicao["nome"]
        self.siglaPartido = requisicao["siglaPartido"]
        self.uriPartido = requisicao["uriPartido"]
        self.siglaUf = requisicao["siglaUf"]
        self.idLegislatura = requisicao["idLegislatura"]
        self.urlFoto = requisicao["urlFoto"]
        self.email = requisicao["email"]

    def to_list(self):
        """This method returns a list of the object Deputado
        
        Parameters: None
        Returns:
        [Id, uri, nome, siglaPartido, uriParitdo, siglaUf, idLegislatura, urlFoto, email]"""
        return [self.Id, self.uri, self.nome, self.siglaPartido, self.uriPartido, self.siglaUf, self.idLegislatura, self.urlFoto, self.email]
    
    @classmethod
    def get_variables(cls):
        return ["Id", "uri", "nome", "siglaPartido", "uriParitdo", "siglaUf", "idLegislatura", "urlFoto", "email"]

class faseEvento():
    def __init__(self, requisicao) -> None:
        self.dataHoraFim = requisicao["dataHoraFim"]
        self.dataHoraInicio = requisicao["dataHoraInicio"]
        self.titulo = requisicao["titulo"]

class Discurso():
    def __init__(self, requisicao) -> None:
        self.dataHoraFim = requisicao["dataHoraFim"]
        self.dataHoraInicio = requisicao["dataHoraInicio"]
        self.faseEvento = faseEvento(requisicao=requisicao["faseEvento"])
        self.keywords = requisicao["keywords"]
        self.sumario = requisicao["sumario"]
        self.tipoDiscurso = requisicao["tipoDiscurso"]
        self.transcricao = requisicao["transcricao"]
        self.uriEvento = requisicao["uriEvento"]
        self.urlAudio = requisicao["urlAudio"]
        self.urlTexto = requisicao["urlTexto"]
        self.urlVideo = requisicao["urlVideo"]

    def to_list(self):
        """This method returns a list of the object Discurso, including FaseEvento
        
        Parameters: None
        Returns
        [dataHoraFim, dataHoraInicio, faseVento.dataHoraFim, faseEvento.dataHoraInicio, faseEvento.titulo, keywords, sumario, tipoDiscurso, transcricao, uriEvento, urlAudio, urlTexto, urlVideo]"""
        return [self.dataHoraFim, self.dataHoraInicio, self.faseEvento.dataHoraFim, self.faseEvento.dataHoraInicio, self.faseEvento.titulo, self.keywords, self.sumario, self.tipoDiscurso, self.transcricao, \
                self.uriEvento, self.urlAudio, self.urlTexto, self.urlVideo]
    
    @classmethod
    def get_variables(cls):
        return ["dataHoraFim", "dataHoraInicio", "faseVento.dataHoraFim", "faseEvento.dataHoraInicio", "faseEvento.titulo", "keywords", "sumario", "tipoDiscurso", "transcricao", "uriEvento", "urlAudio", "urlTexto", "urlVideo"]

def to_csv(estrutura, directory = None):
    lista_partidos = [partido.to_list() for partido in estrutura]
    df_partidos = pd.DataFrame(data=lista_partidos, columns=Partido.get_variables())
    if directory == None:
        path = ""
    else:
        path = directory
    df_partidos.to_csv(path+"/partidos.csv")
    del def_partidos
    