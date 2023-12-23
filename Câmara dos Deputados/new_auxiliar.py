'''This module defines some classes to be used in other classes
The classes here implemented are data classes'''


class Partido():
    '''This class is made to represent a party from the deputies chamber
    This class is a data class.'''
    def __init__(self, requisicao) -> None:
        self.Id = requisicao["id"]
        self.sigla = requisicao["sigla"]
        self.nome = requisicao["nome"]
        self.uri = requisicao["uri"]

    def to_list(self) -> list:
        """This method returns a list of the object Partido

        Parameters: None
        Returns:
        [Id, sigla, nome, uri]"""
        return [self.Id, self.sigla, self.nome, self.uri]

    @classmethod
    def get_variables(cls) -> list:
        '''Returns a list of names for the Partidos attributes
        The attributes themselves should be retrieved using the to_list method
        '''
        return ["IdPartido", "sigla", "nome", "uri"]


class Deputado():
    '''This class represents a deputy from the deputies chamber.

    This class is made as a data class.'''
    def __init__(self, requisicao) -> None:
        self.Id = requisicao["id"]
        self.uri = requisicao["uri"]
        self.nome = requisicao["nome"]
        self.sigla_partido = requisicao["siglaPartido"]
        self.uri_partido = requisicao["uriPartido"]
        self.sigla_uf = requisicao["siglaUf"]
        self.id_legislatura = requisicao["idLegislatura"]
        self.url_foto = requisicao["urlFoto"]
        self.email = requisicao["email"]

    def to_list(self):
        """This method returns a list of the object Deputado"""
        return [self.Id,
                self.uri,
                self.nome,
                self.sigla_partido,
                self.uri_partido,
                self.sigla_uf,
                self.id_legislatura,
                self.url_foto,
                self.email]

    @classmethod
    def get_variables(cls):
        '''Returns a list of names for the Deputado attributes
        The attributes themselves should be retrieved using the to_list method
        '''
        return ["IdDeputado",
                "uri",
                "nome",
                "siglaPartido",
                "uriParitdo",
                "siglaUf",
                "idLegislatura",
                "urlFoto",
                "email"]


class FaseEvento():
    '''This data class holds the phase of the event that a speech was made.

    This class is a data class'''
    def __init__(self, requisicao) -> None:
        self.data_hora_fim = requisicao["dataHoraFim"]
        self.data_hora_inicio = requisicao["dataHoraInicio"]
        self.titulo = requisicao["titulo"]


class Discurso():
    '''This data class contains the infomation from a speech.
    This is a data class.'''
    def __init__(self, requisicao) -> None:
        self.data_hora_fim = requisicao["dataHoraFim"]
        self.data_hora_inicio = requisicao["dataHoraInicio"]
        self.fase_evento = FaseEvento(requisicao=requisicao["faseEvento"])
        self.keywords = requisicao["keywords"]
        self.sumario = requisicao["sumario"]
        self.tipo_discurso = requisicao["tipoDiscurso"]
        self.transcricao = requisicao["transcricao"]
        self.uri_evento = requisicao["uriEvento"]
        self.url_audio = requisicao["urlAudio"]
        self.url_texto = requisicao["urlTexto"]
        self.url_video = requisicao["urlVideo"]

    def to_list(self):
        """This method returns a list of the object Discurso,
        including FaseEvento."""
        return [self.data_hora_fim,
                self.data_hora_inicio,
                self.fase_evento.data_hora_fim,
                self.fase_evento.data_hora_inicio,
                self.fase_evento.titulo,
                self.keywords,
                self.sumario,
                self.tipo_discurso,
                self.transcricao,
                self.uri_evento,
                self.url_audio,
                self.url_texto,
                self.url_video]

    @classmethod
    def get_variables(cls):
        '''Returns a list of names for the Discurso class.
        To obtain the attributes themselves, use the to_list method.'''
        return ["dataHoraFim",
                "dataHoraInicio",
                "faseVento.dataHoraFim",
                "faseEvento.dataHoraInicio",
                "faseEvento.titulo",
                "keywords",
                "sumario",
                "tipoDiscurso",
                "transcricao",
                "uriEvento",
                "urlAudio",
                "urlTexto",
                "urlVideo"]
