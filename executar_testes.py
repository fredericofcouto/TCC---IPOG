"""Confere os dados publicados do TCC com a biblioteca padrão do Python."""

import csv
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def rodar(pasta, *argumentos):
    subprocess.run(
        [sys.executable, *argumentos],
        cwd=pasta,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def conferir_pos_fechamento(pasta):
    for serie in ("serie_ff", "serie_chr"):
        rodar(pasta, "classificar.py", f"{serie}/casos", "figura.png", f"{serie}/previsoes.csv")
    rodar(pasta, "conferir.py", ".")

    resultado = pasta / "resultados.csv"
    with resultado.open(encoding="utf-8-sig", newline="") as arquivo:
        sessoes = list(csv.DictReader(arquivo))
    acertos = sum(linha["previsao"] == linha["condicao"] for linha in sessoes)
    inconclusivos = sum(linha["previsao"] == "?" for linha in sessoes)
    print(f"{len(sessoes)} sessões: {acertos} acertos e {inconclusivos} inconclusivos.", flush=True)
    if (len(sessoes), acertos, inconclusivos) != (32, 12, 20):
        raise ValueError("A classificação divergiu dos resultados publicados.")
    return resultado


def conferir_interrupcao(pasta):
    resultado = pasta / "resultados_recalculados.csv"
    rodar(pasta, "medir.py", ".", resultado.name)

    hash_original = hashlib.sha256((pasta / "resultados.csv").read_bytes()).hexdigest()
    hash_recalculado = hashlib.sha256(resultado.read_bytes()).hexdigest()
    print(f"SHA-256 original:    {hash_original}", flush=True)
    print(f"SHA-256 recalculado: {hash_recalculado}", flush=True)
    if hash_original != hash_recalculado:
        raise ValueError("O CSV recalculado divergiu do original.")
    return resultado


def main():
    pasta = Path(__file__).resolve().parent
    pacote = pasta / "Dados_do_ensaio_TCC.zip"
    if not pacote.is_file():
        raise FileNotFoundError(f"Coloque {pacote.name} na mesma pasta que este script.")

    with tempfile.TemporaryDirectory(prefix="tcc_ensaio_") as temporaria:
        dados = Path(temporaria)
        with zipfile.ZipFile(pacote) as zip_dados:
            zip_dados.extractall(dados)

        print("1/2 - Conferindo a classificação pós-fechamento...", flush=True)
        pos_fechamento = conferir_pos_fechamento(dados / "pos_fechamento")
        print("2/2 - Conferindo os testes de interrupção...", flush=True)
        interrupcao = conferir_interrupcao(dados / "interrupcao")

        saida = Path(tempfile.mkdtemp(prefix="Resultados_TCC_", dir=pasta))
        shutil.copyfile(pos_fechamento, saida / "pos_fechamento_recalculado.csv")
        shutil.copyfile(interrupcao, saida / "interrupcao_recalculada.csv")

    print("\nConferência concluída com sucesso.")
    print(f"CSVs recalculados: {saida}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as erro:
        print(f"Erro ao rodar {erro.cmd[1]} (código {erro.returncode}).", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, zipfile.BadZipFile) as erro:
        print(f"Erro na conferência: {erro}", file=sys.stderr)
        sys.exit(1)
