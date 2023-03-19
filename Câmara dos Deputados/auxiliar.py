import requests
import requests.structures
import time

def reqURL(s: requests.Session, url: str):
    _not_got = True
    while _not_got:
        response = s.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            _not_got = False
        elif response.status_code == 429:
            retry_after = int(response.headers["retry-after"])
            time.sleep(retry_after)
        else:
            break
    else:
        return response
    return None

def reqDadosDeputado(Id):
    """Funciton to retrieve informtaion from a """
    url_base = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id}"
    url = url_base.format(id = Id)
    headers = requests.structures.CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)
    response = reqURL(s = s, url=url)
    return response.json()

class Deputado():
    def __init__(self, Id) -> None:
        """Creates a class of a deputy. Raises an ValueError if the Id passed is not valid"""
        data = reqDadosDeputado(Id)
        if data == None:
            raise ValueError("The value of Id is not a valid number.")
        self.Id = data["dados"]["id"]
        self.cpf = data["dados"]["cpf"]
        self.dataFalecimento = data["dados"]["dataFalecimento"]
        self.dataNascimento = data["dados"]["dataNascimento"]
        self.url = data["dados"]["uri"]
        self.nomeCivil = data["dados"]["nomeCivil"]
        self.ultimoStatus = data["dados"]["ultimoStatus"]
        self.sexo = data["dados"]["sexo"]
        self.urlWebsite = data["dados"]["urlWebsite"]
        self.redeSocial = data["dados"]["redeSocial"]
        self.ufNascimento = data["dados"]["ufNascimento"]
        self.municipioNascimento = data["dados"]["municipioNascimento"]
        self.escolaridade = data["dados"]["escolaridade"]

print(reqDadosDeputado(74057))

