import requests
import requests.structures
import time

# Criação de classes para manter uma estrutura coesa internamente ao código como um todo

def reqURL(s: requests.Session, url: str):
    _not_got = True
    while _not_got:
        response = s.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            _not_got = False
        elif response.status_code == 429:
            retry_after = int(response.headers["retry-after"])
            time.sleep(retry_after)
        elif response.status_code == 404:
            break
    else:
        return response
    return None

def reqDadosDeputado(Id:int):
    """Funciton to retrieve informtaion from a specific deputy, utilized internally by the class Deputado"""
    url_base = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id}"
    url = url_base.format(id = Id)
    headers = requests.structures.CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)
    response = reqURL(s = s, url=url) # Para além de abstração, manter coerência com o que tem sido feito em diversas outras áreas do código
    return response.json()

def reqDadosPartido(Id: int):
    """Function made to retrieve information from a specific party, utilized internally by the class Partido"""
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos/{id}"
    url = url_base.format(id = Id)
    headers = requests.structures.CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)
    response = reqURL(s = s, url=url) # Para além de abstração, manter coerência com o que tem sido feito em diversas outras áreas do código
    return response.json()

class DeputadoultimoStatus():
    def __init__(self, ultimoStatus: dict) -> None:
        self.condicaoEleitoral = ultimoStatus["condicaoEleitoral"]
        self.data = ultimoStatus["data"]
        self.descricaoStatus = ultimoStatus["descricaoStatus"]
        self.email = ultimoStatus["email"]
        self.gabinete = ultimoStatus["gabinete"]

class Deputado():
    def __init__(self, Id: int) -> None:
        """Creates a class of a deputy. Raises an ValueError if the Id passed is not valid"""
        data = reqDadosDeputado(Id)
        if data == None:
            raise ValueError("The value of Id is not a valid number for deputies.")
        self.Id = data["dados"]["id"]
        self.cpf = data["dados"]["cpf"]
        self.dataFalecimento = data["dados"]["dataFalecimento"]
        self.dataNascimento = data["dados"]["dataNascimento"]
        self.url = data["dados"]["uri"]
        self.nomeCivil = data["dados"]["nomeCivil"]
        self.ultimoStatus = DeputadoultimoStatus(data["dados"]["ultimoStatus"])
        self.sexo = data["dados"]["sexo"]
        self.urlWebsite = data["dados"]["urlWebsite"]
        self.redeSocial = data["dados"]["redeSocial"]
        self.ufNascimento = data["dados"]["ufNascimento"]
        self.municipioNascimento = data["dados"]["municipioNascimento"]
        self.escolaridade = data["dados"]["escolaridade"]

    def setDiscursos(self, discursos: list):
        """Function to set discurses for a deputy once it has loaded or change """
        self.discursos = discursos

class PartidoLider():
    
    def __init__(self, lider:dict) -> None:
        """Creates a party lider"""
        self.idLegislatura = lider["idLegislatura"]
        self.nome = lider["nome"]
        self.siglaPartido = lider["siglaPartido"]
        self.uf = lider["uf"]
        self.uri = lider["uri"]
        self.uriPartido = lider["uriPartido"]
        self.urlFoto = lider["urlFoto"]

class PartidoStatus():
    def __init__(self, status:dict) -> None:
        """"""
        self.data = status["data"]
        self.idLegislatura = status["idLegislatura"]
        self.lider = PartidoLider(status["lider"])

class Partido():
    def __init__(self, Id: int) -> None:
        """Creates a class of a party. Raises a ValueError if the parameter Id is not valid"""
        data = reqDadosPartido(Id=Id)
        if data == None:
            raise ValueError("The value of Id is not a valid number for parties.")
        data = data["dados"]
        self.Id = data["id"]
        self.nome = data["nome"]
        self.numeroEleitoral = data["numeroEleitoral"]
        self.sigla = data["sigla"]
        self.status = PartidoStatus(data["status"])
        self.uri = data["uri"]
        self.urlFacebook = data["urlFacebook"]
        self.urlLogo = data["urlLogo"]
        self.urlWebsite = data["urlWebsite"]

class faseEventoDiscurso():
    def __init__(self, faseEvento: dict) -> None:
        self.dataHoraFim = faseEvento["dataHoraFim"]
        self.dataHoraInicio = faseEvento["dataHoraInicio"]
        self.titulo = faseEvento["titulo"]

class Discurso():
    def __init__(self, discurso: dict) -> None:
        self.dataHoraFim = discurso["dataHoraFim"]
        self.dataHoraInicio = discurso["dataHoraInicio"]
        self.faseEvento = faseEventoDiscurso(discurso["faseEvento"])
        self.keywords = discurso["keywords"]
        self.sumario = discurso["suamario"]
        self.tipoDiscurso = discurso["tipoDiscurso"]
        self.transcricao = discurso["transcricao"]
        self.uriEvento = discurso["uriEvento"]
        self.urlAudio = discurso["urlAudio"]
        self.urlTexto = discurso["urlTexto"]
        self.urlVideo = discurso["urlVideo"]

print(Partido(36779).nome)