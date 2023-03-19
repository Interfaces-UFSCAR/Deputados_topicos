import requests
from requests.structures import CaseInsensitiveDict
import urllib.parse
import time
import os
import sys
import platform

def get_script_path() -> str:
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def reqURL(s: requests.Session, url: str):
    _not_got = True
    while _not_got:
        response = s.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            _not_got = False
        elif response.status_code == 429:
            retry_after = int(response.headers["retry-after"])
            time.sleep(retry_after)
    return response

def reqDiscursos(deputados: list, idLegislatura: list = [], dataInicio: str = "", dataFim: str = "", ordenarPor: str = "dataHoraInicio", ordem: str = "ASC") -> list:
    if deputados is []:
        raise Exception("Th list of deputies to get the speeches must not be empty")
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/discursos"
    url_list.append(url_base)

    params = {}

    if idLegislatura is not reqDiscursos.__defaults__[0]:
        params["idLegislatura"] = [str(Id) for Id in idLegislatura]

    if dataInicio is not reqDiscursos.__defaults__[1]:
        params["dataInicio"] = dataInicio

    if dataFim is not reqDiscursos.__defaults__[2]:
        params["dataFim"] = dataFim

    if ordenarPor is not reqDiscursos.__defaults__[3]:
        params["ordenarPor"] = ordenarPor

    params["ordem"] = ordem

    query =  urllib.parse.urlencode(params, doseq=True)
    if query != '':
        url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)

    s = requests.Session()
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s.headers.update(headers)

    for deputado in deputados:
        url = url_id.format(id = deputado)
        i = 0
        headers = CaseInsensitiveDict()
        headers["accept"] = "application/json"
        response = reqURL(s=s, url=url)
        resps.append(response)

        while "next" in resps[i].links:
            next_request = resps[i].links["next"]["url"]
            response = reqURL(s=s, url=next_request)
            resps.append(response)
            i += 1

def reqMembros(idsPartidos: int, dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordenarPor: str = "", ordem: str = "ASC"):
    if idsPartidos == None:
        raise Exception("The list of parties IDs must not be empty")
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos/{id}/membros"
    url_list.append(url_base)
    params = {}

    if dataInicio is not reqMembros.__defaults__[0]:
        params["dataInicio"] = dataInicio

    if dataFim is not reqMembros.__defaults__[1]:
        params["dataFim"] = dataFim

    if idLegislatura is not reqMembros.__defaults__[2]:
        params["idLegislatura"] = [str(Id) for Id in idLegislatura]

    if ordenarPor is not reqMembros.__defaults__[3]:
        params["ordenarPor"] = ordenarPor

    params["ordem"] = ordem

    query = urllib.parse.urlencode(params, doseq=True)
    if query != '':
        url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)
    for idPartido in idsPartidos:
        url = url_id.format(id = idPartido)
        response = reqURL(s = s, url=url)
        resps.append(response)

        i = 0

        while "next" in resps[i].links:
            url = resps[i].links["next"]["url"]
            response = reqURL(s=s, url=url)
            resps.append(response)
            i += 1
    
    lista_deputados = []

    for i in resps:
        for j in i.json()["dados"]:
            lista_deputados.append(j["id"])
    return lista_deputados

def reqPartidos(sigla: list = [], dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordem: str = "ASC", ordenarPor: str = "sigla"):
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos"
    url_list.append(url_base)

    params = {}

    # Se os parâmetros não forem default eles são adicionados aos parêmetros da URL
    if sigla is not reqPartidos.__defaults__[0]:
        params["sigla"] = sigla

    if dataInicio is not reqPartidos.__defaults__[1]:
        params["dataInicio"] = dataInicio

    if dataFim is not reqPartidos.__defaults__[2]:
        params["dataFim"] = dataFim

    if idLegislatura is not reqPartidos.__defaults__[3]:
        params["idLegislatura"] = [str(id) for id in idLegislatura]

    params["ordenarPor"] = ordenarPor
    params["ordem"] = ordem
    query = urllib.parse.urlencode(params, doseq=True)
    if query != "":
        url_list.append("?")
    url_list.append(query)
    url = ''.join(url_list)

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)

    # Criação do primeiro request de partido
    response = reqURL(s=s, url=url)
    resps.append(response)
    i = 0

    # Enquanto houverem partidos, continue a realizar o scrap
    while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = reqURL(s=s, url=url)
        resps.append(response)
        i += 1

    ids = []
    for resp in resps:
        for Id in resp.json()["dados"]:
            ids.append(Id["id"])
    # Necessidade de criar um sistema para a criação do sistema de arquivos da coleta 
    # Ideia de um sistema de árvore em profundidade
    for Id in ids:
        reqMembros(idsPartidos=Id, dataInicio=dataInicio, dataFim=dataFim, idLegislatura=idLegislatura, ordenarPor=ordenarPor, ordem=ordem)
