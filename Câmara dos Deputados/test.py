import requests
from requests.structures import CaseInsensitiveDict
import urllib.parse
import time

#Este código está utilizando as novas classes, que utilizam todas as informações presentes nas requisições que foram feitas anteriormente
import new_auxiliar

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

def checkResponse(response):
    # Para checar se a resposta obtida é um JSON válido ou se é um HTML que serve como página de ERRO, isso pode acontecer
    pass

def reqDiscursos(deputado: int, idLegislatura: list = [], dataInicio: str = "", dataFim: str = "", ordenarPor: str = "dataHoraInicio", ordem: str = "ASC") -> list:
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/discursos"
    url_list.append(url_base)

    params = {}

    if idLegislatura is not reqDiscursos.__defaults__[0]:
        params["idLegislatura"] = [str(id) for id in idLegislatura]

    if dataInicio is not reqDiscursos.__defaults__[1]:
        params["dataInicio"] = dataInicio

    if dataFim is not reqDiscursos.__defaults__[2]:
        params["dataFim"] = dataFim

    if ordenarPor is not reqDiscursos.__defaults__[3]:
        params["ordenarPor"] = ordenarPor

    params["ordem"] = ordem

    query = urllib.parse.urlencode(params, doseq=True)
    if query != '':
        url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)

    url = url_id.format(id=deputado)
    i = 0
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)
    response = reqURL(s=s, url=url)
    resps.append(response)

    while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = reqURL(s=s, url=url) # Colocar validação para ver se o sistema da câmara não está sobrecarregado, mesmo erro do próximo comentário
        resps.append(response)
        i += 1
    lista_discursos = []
    for i in resps:
        try:
            lista_discursos.extend(list(map(new_auxiliar.Discurso, i.json()["dados"]))) # Tratar o fato de que pode haver corpos vazios
        except:
            pass
    return lista_discursos

def reqMembros(idPartido: int, dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordenarPor: str = "", ordem: str = "ASC") -> list:
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
        params["idLegislatura"] = [str(id) for id in idLegislatura]

    if ordenarPor is not reqMembros.__defaults__[3]:
        params["ordenarPor"] = ordenarPor
    
    params["ordem"] = ordem
    #print(params)
    query = urllib.parse.urlencode(params, doseq=True)
    if query != '':
        url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)

    url = url_id.format(id = idPartido)
    i = 0
    response = reqURL(s=s, url=url)
    resps.append(response)

    while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = reqURL(s=s, url=url)
        resps.append(response)
        i += 1
    lista_deputados = []

    for i in resps:
        lista_deputados.extend(list(map(new_auxiliar.Deputado, i.json()["dados"])))
    lista_discursos_deputados = []
    for deputado in lista_deputados:
        lista_discursos_deputados.append({deputado :reqDiscursos(deputado=deputado.Id, idLegislatura=idLegislatura, dataInicio=dataInicio, dataFim=dataFim, ordenarPor=ordenarPor, ordem=ordem)})
        time.sleep(5)
    return lista_discursos_deputados

def reqPartidos(siglas: list = [], dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordem: str = "ASC", ordenarPor: str = "sigla", ordenarPorDiscursos: str = ""):
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos"
    url_list.append(url_base)

    params = {}

    if siglas is not reqPartidos.__defaults__[0]:
        params["sigla"] = siglas

    if dataInicio is not reqPartidos.__defaults__[1]:
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

    while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = reqURL(s=s, url=url)
        resps.append(response)
        i += 1

    partidos = []
    for resp in resps:
        partidos.extend(list(map(new_auxiliar.Partido, resp.json()["dados"])))
    lista_discursos_deputados_partidos = {}
    for partido in partidos:
        lista_discursos_deputados_partidos[partido] = reqMembros(idPartido=partido.Id, dataInicio=dataInicio, dataFim=dataFim, idLegislatura=idLegislatura, ordenarPor=ordenarPorDiscursos, ordem=ordem)
    return lista_discursos_deputados_partidos

init_time = time.time()
requisicoes = reqPartidos(["PCdoB"],dataInicio="2019-06-01", dataFim="2019-06-15")
end_time = time.time()
print(requisicoes)