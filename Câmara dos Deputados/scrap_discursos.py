'''
This module has the responsable functions for retrieving the data from the API.
'''


import urllib.parse
import time
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd

import new_auxiliar


def create_params(id_legislatura,
                  data_inicio,
                  data_fim,
                  ordenar_por, ordem) -> dict[str, str | list[str]]:
    """Creates the dictionary of parameters for the request.

    Makes it passable between calls."""
    params: dict[str, str | list[str]] = {}
    if id_legislatura != []:
        params['idLegislatura'] = [str(legislatura)
                                   for legislatura in id_legislatura]
    if data_inicio != "":
        params["dataInicio"] = data_inicio
    if data_fim != "":
        params["dataFim"] = data_fim
    if ordenar_por != "":
        params["ordenarPor"] = ordenar_por
    params["ordem"] = ordem
    return params


def req_url(s: requests.Session, url: str) -> requests.Response:
    """Resquests a certain URL using the given Session that is being used.
    Does not return until the URL responses, can make the function run forever.
    If there is any problem with the URL being requested"""
    _not_got = True
    while _not_got:
        response = s.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            _not_got = False
        elif response.status_code == 429:
            retry_after = int(response.headers["retry-after"])
            time.sleep(retry_after)
    return response


def req_discursos(deputado: int,
                  s: requests.Session,
                  params: dict[str, str | list[str]],
                  ordenar_por: str = "dataHoraInicio") -> list:
    """Requisita os discursos de um Deputado baseado no ID do Deputado"""
    url_list = []
    resps: list[requests.Response] = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/deputados/{id}/discursos"
    url_list.append(url_base)

    params["ordenarPor"] = ordenar_por

    query = urllib.parse.urlencode(params, doseq=True)
    url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)

    url = url_id.format(id=deputado)
    i = 0
    response = req_url(s=s, url=url)
    resps.append(response)

    while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = req_url(s=s, url=url)
        resps.append(response)
        i += 1
    lista_discursos = []
    for resp in resps:
        try:
            lista_discursos.extend(list(map(new_auxiliar.Discurso,
                                            resp.json()["dados"])))
        except IndexError:  # Pode ser que esse não seja o erro correto
            pass
    return lista_discursos


def req_membros(id_partido: int,
                s: requests.Session,
                params: dict[str, str | list[str]],
                ordenar_por: str = "",) -> list:
    """Requisita os discursos dos membros de um partido com ID do partido"""
    url_list = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos/{id}/membros"
    url_list.append(url_base)

    params["ordenarPor"] = ordenar_por  # Troca pois não existe "sigla"
    # Troca na cópia e não na versão original
    # Necessário até pelo fato de que as chamadas são feitas em profundidade.

    query = urllib.parse.urlencode(params, doseq=True)
    url_list.append("?")
    url_list.append(query)
    url_id = ''.join(url_list)
    url = url_id.format(id=id_partido)
    # i = 0
    response = req_url(s=s, url=url)

    # Não é necessário nesse momento a realização da checagem dos valores next
    # acontece pelo fato de que este endpoint não está utiliizando 'itens'
    # Por isso não é necessário realizar toda esta lógica,
    # response já possui todas as respostas necessária

    # while "next" in resps[i].links:
    #     url = resps[i].links["next"]["url"]
    #     response = reqURL(s=s, url=url)
    #     resps.append(response)
    #     i += 1"""
    lista_deputados = list(map(new_auxiliar.Deputado,
                               response.json()["dados"]))

    lista_discursos_deputados = []
    for deputado in lista_deputados:
        lista_discursos_deputados.append({
            deputado:
            req_discursos(deputado=deputado.Id,
                          s=s,
                          params=params.copy(),
                          ordenar_por=ordenar_por)})
    return lista_discursos_deputados


def req_partidos(siglas: list[str] | None = None,
                 data_inicio: str = "",
                 data_fim: str = "",
                 id_legislatura: list[str] | None = None,
                 ordem: str = "ASC",
                 ordenar_por: str = "sigla",
                 ordenar_por_discursos: str = ""):
    '''Faz a requisição dos discursos dos membros de um ou mais partidos
    baseando-se nas siglas dos Partidos'''

    if siglas is None:
        siglas = []
    if id_legislatura is None:
        id_legislatura = []
    url_list = []
    resps = []
    url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos"
    url_list.append(url_base)

    params: dict[str, str | list[str]] = create_params(
        id_legislatura=id_legislatura,
        data_inicio=data_inicio,
        data_fim=data_fim,
        ordenar_por=ordenar_por,
        ordem=ordem)

    query = urllib.parse.urlencode(params, doseq=True)
    url_list.append("?")
    url_list.append(query)
    url = ''.join(url_list)

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    s = requests.Session()
    s.headers.update(headers)

    # Criação do primeiro request de partido
    response = req_url(s=s, url=url)
    resps.append(response)
    i = 0

    while "next" in resps[i].links:
        url = resps[i].links["next"]["url"]
        response = req_url(s=s, url=url)
        resps.append(response)
        i += 1

    partidos = []
    for resp in resps:
        partidos.extend(list(map(new_auxiliar.Partido, resp.json()["dados"])))
    lista_discursos_deputados_partidos = {}
    for partido in partidos:
        lista_discursos_deputados_partidos[partido] = req_membros(
            id_partido=partido.Id,
            s=s,
            params=params.copy(),  # Evitates that that calls change the dict
            ordenar_por=ordenar_por_discursos)
    return lista_discursos_deputados_partidos


def partido_to_dataframe(estrutura: dict) -> pd.DataFrame:
    """Transforma a estrutura das requisições de partidos para um CSV,
    onde cada linha é um discurso"""
    list_df = []
    for partido in estrutura:
        for dict_deputado in estrutura[partido]:
            for deputado in dict_deputado:
                for discurso in dict_deputado[deputado]:
                    partido_list = partido.to_list()
                    deputado_list = deputado.to_list()
                    discurso_list = discurso.to_list()
                    linha = partido_list + deputado_list + discurso_list
                    list_df.append(linha)

    columns = new_auxiliar.Partido.get_variables() + \
        new_auxiliar.Deputado.get_variables() + \
        new_auxiliar.Discurso.get_variables()
    df = pd.DataFrame(data=list_df, columns=columns)
    df = df.drop_duplicates(subset=["dataHoraFim",
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
                                    "urlVideo"])
    # drop_duplicates deve ser feito, existem deputados repetidos,
    # a única diferença entre eles é o nome,
    # onde um é maiúsculo e o outro minúsculo
    return df


def main():
    '''Testing function of the module'''
    init_time = time.time()
    requisicoes = req_partidos(siglas=["PL"],
                               data_inicio="2019-06-02",
                               data_fim="2019-07-02")
    end_time = time.time()
    # print(requisicoes)
    print(end_time - init_time)
    df = partido_to_dataframe(requisicoes)
    print(df.shape)
    df.to_csv("discursos_PL.csv")


if __name__ == "__main__":
    main()
