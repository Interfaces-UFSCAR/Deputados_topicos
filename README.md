# Projeto de Iniciação Científica Matteus Guilherme de Souza

Este projeto é o repositório para o projeto de Iniciação Científica de Matteus Guilherme de Souza.

O projeto tem como objetivo a utilização do algoritmo PBG para a extração de tópicos de discursos transcritos da Câmara dos Deputados.

# Necessidades

É necessário a utilização do código do algoritmo PBG feito por Thiago Faleiros em https://github.com/thiagodepaulo/PyPBG .

O código deve ser baixado e então transformado para uma biblioteca Python existente na versão a ser utilizada do Python.

É necessário o uso do *Python 3.6* ou superior.

## Instalação do pacote pyPBG

### Instalação no Python principal da máquina

Para a realização da instalação diretamente no Python da máquina deve-se utilizar o comando

```
sudo python3 setup.py install
```

na pasta onde o projeto pyPBG está instalado.

### Instalação com a utilização de venv

Para este psso é necessário primeiramente configurar o virtual enviroment do python para que ele execute os comandos do Python e instale as bibliotecas no local especificado e não na pasta principal do Python na máquina.

Passando então para o comando a ser utilizado caso esteja-se com um virtual enviroment configurado, tem-se que o comando deve ser

```
sudo {virtualenviroment}/{folder}/{path}/bin/python setup.py install
```

Para as duas aplicações, tem-se que o pacote deve estar instalado no Python a ser utilizado.

# Instalação dos demais pacotes necessários

Os demais pacotes a serem instalados podem ser obtidos com ajuda da pip, gerente de pacotes padrçao do Python.

Para tal, na pasta principal deste projeto, tem-se um arquivo nomeado requirements.txt, que será utilizado para a realização da instalação dos pacotes.

Estando na mesma pasta que este arquivo, no terminal de comando, deve-se digitar o seguinte comando

```
python3 -m pip install -r requirements.txt
```

Ao final, todos os pacotes necessários para a execução do pacote devem estar inclusos

# Explicação das diversas partes

Existem alguns algoritmos de bibliotecas espalhados

## Coleta dos discursos

Primeiro e o principal para a coleta dos discursos é o algoritmo *scrap_discursos.py*.

A função principal deste algoritmo é a função reqPartidos, que fará a requisição dos discursos de todos os deputados de um ou mais partidos. Há diversos outros parâmetros que podem ser configurados, como as datas de início e fim da coleta, o identificador de uma legislatura específica, ordem ascendete ou decrescente e o que deve ser utilizado para realizar a ordenação.

Caso queira utilizar as funções para coleta dos discursos de um determinado deputado por exemplo, deve-se saber o identificador de tal parlamentar. Tal informação além de outras pode ser obtida na página da API, no caso: https://dadosabertos.camara.leg.br/swagger/api.html .

## Estruturas internas do código

O código utiliza algumas classes para realizar o armazenamento e manejamento dos discursos. As 3 principais classes são Partido, Deputado e Discurso. As classes são mapeamentos dos dados vindos da API para cada um dos tipos de dados utilizados.

# Código *Scraper.py*

Este código possui como objetivo a coleta de dados da API para diversos partidos, salvando cada um dos partidos em um arquivo separado.

Para a seleção dos diversos partidos deve-se criar um arquivo *partidos.txt*.