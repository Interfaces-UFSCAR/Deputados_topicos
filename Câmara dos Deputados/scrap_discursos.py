'''
This module has the responsable functions for retrieving the data from the API.
'''


import urllib.parse
import time
import requests
from requests.structures import CaseInsensitiveDict
import urllib.parse
import time
import pandas as pd

#Este código está utilizando as novas classes, que utilizam todas as informações presentes nas requisições que foram feitas anteriormente
import new_auxiliar

def reqURL(s: requests.Session, url: str) -> requests.Response:
    """Resquests a certain URL using the given Session that is being used.
    The function does not return until the URL responses, what can make the function run forever. if there is any problem with the URL being requested"""
    _not_got = True
    while _not_got:
        response = s.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            _not_got = False
        elif response.status_code == 429:
            retry_after = int(response.headers["retry-after"])
            time.sleep(retry_after)
    return response

def reqDiscursos(deputado: int, s: requests.Session, idLegislatura: list = [], dataInicio: str = "", dataFim: str = "", ordenarPor: str = "dataHoraInicio", ordem: str = "ASC") -> list:
    """Faz a requisção dos discursos de um determinado Deputado baseado no ID do Deputado"""
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
    url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)

    url = url_id.format(id=deputado)
    i = 0
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

def reqMembros(idPartido: int, s: requests.Session, dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordenarPor: str = "", ordem: str = "ASC") -> list:
    """Faz as requisições dos discursos dos membros de um partido baseado no ID do partido"""
    url_list = []
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
    query = urllib.parse.urlencode(params, doseq=True)
    url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)
    url = url_id.format(id = idPartido)
    i = 0
    response = reqURL(s=s, url=url)

    # Não é necessário nesse momento a realização da checagem dos valores next, isto acontece pelo fato de que este endpoint não está utiliizando o valor 'itens'
    # Por isso não é necessário realizar toda esta lógica response já possui todas as respostas necessária

    """while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = reqURL(s=s, url=url)
        resps.append(response)
        i += 1"""
    lista_deputados = list(map(new_auxiliar.Deputado, response.json()["dados"]))

    lista_discursos_deputados = []
    for deputado in lista_deputados:
        lista_discursos_deputados.append({deputado :reqDiscursos(deputado=deputado.Id, s=s, idLegislatura=idLegislatura, dataInicio=dataInicio, dataFim=dataFim, ordenarPor=ordenarPor, ordem=ordem)})
        #time.sleep(5)
    return lista_discursos_deputados

def reqPartidos(siglas: list = [], dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordem: str = "ASC", ordenarPor: str = "sigla", ordenarPorDiscursos: str = ""):
    "Faz a requisição dos discursos dos membros de um ou mais partidos, baseando-se nas siglas dos Partidos"
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos"
    url_list.append(url_base)

    params = {}

    if siglas is not reqPartidos.__defaults__[0]:
        params["sigla"] = siglas

    if dataInicio is not reqPartidos.__defaults__[1]:
        params["dataInicio"] = dataInicio

    if dataFim is not reqPartidos.__defaults__[2]:
        params["dataFim"] = dataFim

    if idLegislatura is not reqPartidos.__defaults__[3]:
        params["idLegislatura"] = [str(id) for id in idLegislatura]

    params["ordenarPor"] = ordenarPor
    params["ordem"] = ordem
    query = urllib.parse.urlencode(params, doseq=True)
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
        lista_discursos_deputados_partidos[partido] = reqMembros(idPartido=partido.Id, s=s, dataInicio=dataInicio, dataFim=dataFim, idLegislatura=idLegislatura, ordenarPor=ordenarPorDiscursos, ordem=ordem)
    return lista_discursos_deputados_partidos

def partidoToDataFrame(estrutura: dict) -> pd.DataFrame:
    """Transforma a estrutura das requisições de partidos no formato de um CSV onde cada linha é um discurso"""
    list_df = []
    for partido in estrutura:
        for dict_deputado in estrutura[partido]:
            for deputado in dict_deputado:
                for discurso in dict_deputado[deputado]:
                    linha = partido.to_list() + deputado.to_list() + discurso.to_list()
                    list_df.append(linha)
    
    columns = new_auxiliar.Partido.get_variables() + new_auxiliar.Deputado.get_variables() + new_auxiliar.Discurso.get_variables()
    df = pd.DataFrame(data=list_df, columns=columns)
    df = df.drop_duplicates(subset=["dataHoraFim", "dataHoraInicio", "faseVento.dataHoraFim", "faseEvento.dataHoraInicio", "faseEvento.titulo", "keywords", "sumario", "tipoDiscurso", "transcricao", "uriEvento", "urlAudio", "urlTexto", "urlVideo"])
    # Necessário o drop_duplicates pelo fato de que eu não sei o por que existem alguns deputados que estão com versões iguais, a única coisa diferente é o nome, onde um é "DEPUTADO MAIÚSCULO" e o outro é "Deputado Maiúsculo"
    return df

def main():
    init_time = time.time()
    requisicoes = reqPartidos(siglas=["PL"], dataInicio="2019-06-02", dataFim="2019-07-02")
    end_time = time.time()
    #print(requisicoes)
    print(end_time - init_time)
    df = partidoToDataFrame(requisicoes)
    print(df.shape)
    df.to_csv("discursos_PL.csv")

if __name__ == "__main__":
    main()