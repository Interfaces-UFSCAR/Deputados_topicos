import requests
from requests.structures import CaseInsensitiveDict
import urllib.parse
import time

def reqPartidos(sigla:list = [], dataInicio: str = "", dataFim:str = "", idLegislatura:list = [], ordem:str = "ASC", ordenarPor:str = "sigla") -> list:
    if sigla is reqPartidos.__defaults__[0] and dataInicio is reqPartidos.__defaults__[1] \
    and dataFim is reqPartidos.__defaults__[2] and idLegislatura is reqPartidos.__defaults__[3] \
    and ordem is reqPartidos.__defaults__[4] and ordenarPor is reqPartidos.__defaults__[5]:
        # Se os parâmetros estiverem default, utiliza a URL gerada automaticamente pela API da Câmara dos deputados
        url_list = []
        url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos?ordem=ASC&ordenarPor=sigla"
        url_list.append(url_base)

    else:
        url_list = []
        url_base = "https://dadosabertos.camara.leg.br/api/v2/partidos?"
        url_list.append(url_base)

        # Geração dos parâmetros necessários
        params = {}

        if sigla is not reqPartidos.__defaults__[0]:
            params["sigla"] = sigla

        if dataInicio is not reqPartidos.__defaults__[1]:
            params["dataInicio"] = dataInicio

        if dataFim is not reqPartidos.__defaults__[2]:
            params["dataFim"] = dataFim
        
        if idLegislatura is not reqPartidos.__defaults__[3]:
            params["idLegislatura"] = [str(id) for id in idLegislatura]

        params["ordem"] = ordem
        params["ordenarPor"] = ordenarPor
        query = urllib.parse.urlencode(params, doseq=True)
        url_list.append(query)
    url = ''.join(url_list)
    # Neste ponto temos a URL pronta para a criação do primeiro get

    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    resps = []
    s = requests.Session()
    s.headers.update(headers)
    _not_got = False
    while not _not_got:
        response = s.get(url)
        if response.status_code >= 200 and response.status_code < 300:
            _not_got = True
        elif response.status_code == 429:
            retry_after = int(response.headers["retry-after"])
            time.sleep(retry_after)
    resps.append(response)
    i = 0
    # Primeira resposta da API obtida

    # O sistema sabe quando parar baseado na existência, ou não, de um campo 'next'
    #   dentro de cada um dos links dos headers das páginas
    # PROCURAR SE NÃO HÁ UM MEIO MAIS OTIMIZADO PARA FAZER TAIS REQUISIÇÕES
    while "next" in resps[i].links:
        next_request = resps[i].links["next"]["url"]
        _not_got = False
        while not _not_got:
            response = s.get(next_request)
            if response.status_code >= 200 and response.status_code < 300:
                _not_got = True
            elif response.status_code == 429:
                retry_after = int(response.headers["retry-after"])
                time.sleep(retry_after)
        resps.append(response)
        i += 1
    # Neste ponto temos todas as respostas de requisições possíveis para a página requisitada

    # Parte para extração dos IDs das respostas armazenadas
    ids = []
    for resp in resps: # Para cada resposta
        if resp.status_code >= 200 and resp.status_code < 300:
            for id in resp.json()["dados"]: # Para cada conjunto de dados dentro de uma resposta
                ids.append(id["id"]) # Adiciona o valor do ID a lista criada,
            #   que será o valor retornado por este algoritmo
    return ids
    # Retorna uma lista com os valores em formato de inteiros,
    #   é preciso nesse caso realizar a conversão mais tarde

def reqMembros(idsPartidos:list, dataInicio: str = "", dataFim: str = "", idLegislatura: list = [], ordenarPor: str = "", ordem:str = "ASC") -> list:
    if idsPartidos == []:
        raise Exception("A lista de IDs de partidos não pode ser vazia")
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
    # Para cada partido
    for idPartido in idsPartidos:
        url = url_id.format(id = idPartido)
        i = 0

        _not_got = True
        while _not_got:
            response = s.get(url)
            if response.status_code >= 200 and response.status_code < 300:
                _not_got = False
            elif response.status_code == 429:
                retry_after = int(response.headers["retry-after"])
                time.sleep(retry_after)
        resps.append(response)
        #print(url)
        #print(resps[i].json())
        
        # Para cada página de requisição existente para aquele partido
        while "next" in resps[i].links:
            next_request = resps[i].links["next"]["url"]
        _not_got = False
        while not _not_got:
            response = s.get(next_request)
            if response.status_code >= 200 and response.status_code < 300:
                _not_got = True
            elif response.status_code == 429:
                retry_after = int(response.headers["retry-after"])
                time.sleep(retry_after)
        resps.append(response)
        i += 1
    # Necessidade de tratar pois a API pode retornar partidos que não tenham ninguém \
    #   eleito na Câmara dos Deputados, mesmo que se tenha pedido para retornar somente \
    #   Partidos que contenham pessoas na Câmara dos deputados no momento da requisição
    # Verificação pode ser feita pela ideia de listas vazias na chave "dados" do json \
    #   da resposta
    lista_deputados = []
    #print(resps)
    for i in resps:
        if i.status_code  >= 200 and i.status_code <300:
            for j in i.json()["dados"]:
                lista_deputados.append(j["id"])
    return lista_deputados

def reqDiscursos(deputados: list, idLegislatura: list = [], dataInicio: str = "", dataFim: str = "", ordenarPor: str = "dataHoraInicio", ordem: str = "ASC")->list:
    if deputados is []:
        raise Exception("A lista de deputados a pegar o discurso não pode ser vazia")
    # Criação da URL a ser requisitada
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

    for deputado in deputados:
        url = url_id.format(id = deputado)
        i = 0
        headers = CaseInsensitiveDict()
        headers["accept"] = "application/json"
        _not_got = True
        while _not_got:
            resp = requests.get(url=url, headers=headers)
            if resp.status_code <= 200 and resp.status_code < 300:
                _not_got = False
            elif resp.status_code == 429:
                retry_after = int(resp.headers["retry-after"])
                time.sleep(retry_after)

        resps.append(resp)

        while "next" in resps[i].links:
            next_request = resps[i].links["next"]["url"]
            _not_got = True
            while _not_got:
                resp = requests.get(url=next_request, headers=headers)
                if resp.status_code <= 200 and resp.status_code < 300:
                    _not_got = False
                elif resp.status_code == 429:
                    retry_after = int(resp.headers["retry-after"])
                    time.sleep(retry_after)

            resps.append(requests.get(next_request, headers=headers))
            i += 1
    lista_discursos = []
    for i in resps:
        print(i.json())

idLegislatura = [52]
partidos = ["PT"]

inicio = time.time()
partidos = reqPartidos(sigla = partidos, dataInicio = "2022-01-01")
fim = time.time()
print("O tempo para conseguir os partidos a partir das siglas foi de: " + str(fim-inicio))
print(partidos)

inicio  = time.time()
membros = reqMembros(partidos, dataInicio="2022-01-01")
fim = time.time()
print("O tempo para conseguir os membros dos partidos a partir dos ids dos partidos foi de: " + str(fim-inicio))
print(membros)

inicio = time.time()
reqDiscursos(deputados=membros, dataInicio="2022-01-01")
fim = time.time()
print("O tempo para conseguir os discursos a partir dos deputados foi de: " + str(fim-inicio))