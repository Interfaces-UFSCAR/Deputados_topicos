'''This module shows an example on how the extractors works'''
import pathlib
import time
import scrap_discursos as sd


def main():
    '''A example of the topic extraction made
    This implementation creates the speeches files on the running folder.
    This can be a problem depending on the ambient of execution.'''
    partidos = ["NOVO"]
    data_inicio = "2022-01-01"
    data_fim = "2022-12-31"

    path_root = pathlib.Path("./discursos/legis_56/p_novo/2022/")
    path_root.mkdir(parents=True, exist_ok=True)

    init_time = time.time()
    requisicoes = sd.req_partidos(siglas=partidos,
                                  data_inicio=data_inicio,
                                  data_fim=data_fim)
    end_time = time.time()
    print(end_time - init_time)
    df = sd.partido_to_dataframe(requisicoes)
    siglas = df["sigla"].unique().tolist()

    for partido in siglas:
        mask_partido = df["sigla"] == partido
        df_partido = df[mask_partido]
        df_partido = df_partido.reset_index()
        df_partido.to_csv(pathlib.Path.joinpath(path_root,
                                                f"discursos_{partido}.csv"))


if __name__ == "__main__":
    main()
