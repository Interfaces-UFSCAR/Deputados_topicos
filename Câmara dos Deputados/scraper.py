import scrap_discursos as sd
import pathlib
import time

"""Com a implementação atual, a pasta onde os arquivos serão armazenados seré criada na pasta onde o script estã sendo executado e consequentemente os discursos serão armazenados
Isto pode gerar sérios problemas dependendo do ambinte executado"""
def main():
    partidos = ["NOVO"]
    dataInicio = "2022-01-01"
    dataFim = "2022-12-31"

    path_root = pathlib.Path("./discursos/legis_56/p_novo/2022/")
    path_root.mkdir(parents=True, exist_ok=True)

    init_time = time.time()
    requisicoes = sd.reqPartidos(siglas=partidos, dataInicio=dataInicio, dataFim=dataFim)
    end_time = time.time()
    print(end_time - init_time)
    df = sd.partidoToDataFrame(requisicoes)
    siglas = df["sigla"].unique().tolist()

    for partido in siglas:
        mask_partido = df["sigla"] == partido
        df_partido = df[mask_partido]
        df_partido = df_partido.reset_index()
        df_partido.to_csv(pathlib.Path.joinpath(path_root, f"discursos_{partido}.csv"))

if __name__ == "__main__":
    main()