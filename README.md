# Material suplementar do TCC sobre vestígios de navegador

O [ZIP do ensaio](./Dados_do_ensaio_TCC.zip) reúne os roteiros, as imagens sintéticas de referência, os registros por sessão e os recortes dos perfis de laboratório. O [script de conferência](./executar_testes.py) recalcula os resultados a partir dos dados publicados e usa apenas a biblioteca padrão do Python 3.

## Conferência rápida no Windows

1. Baixe [Dados_do_ensaio_TCC.zip](./Dados_do_ensaio_TCC.zip?raw=true) e escolha **Extrair Tudo** no Windows.
2. Abra a pasta extraída que contém `executar_testes.py`, `pos_fechamento` e `interrupcao`. Na barra de endereço do Explorador, digite `powershell` e pressione **Enter**.
3. Execute o comando abaixo. O script que acompanha o ZIP usa uma cópia temporária dos dados extraídos.

```powershell
python .\executar_testes.py
```

<details>
<summary>Já tem uma extração antiga sem o script?</summary>

Na pasta que contém `pos_fechamento` e `interrupcao`, abra o PowerShell e execute estas linhas para baixar o script e rodar a conferência com os dados que você já extraiu.

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/fredericofcouto/TCC---IPOG/main/executar_testes.py' -OutFile '.\executar_testes.py' -ErrorAction Stop
python .\executar_testes.py
```

</details>

Em sistemas que disponibilizam o Python pelo iniciador `py`, use `py -3 .\executar_testes.py`. Em Linux ou WSL, use `python3 ./executar_testes.py`. [Instalador do Python para Windows](https://www.python.org/downloads/windows/)

| Conferência | Resultado esperado | Arquivo gerado |
| --- | --- | --- |
| Classificação após o fechamento | 12 acertos e 20 casos inconclusivos em 32 sessões | `pos_fechamento_recalculado.csv` |
| Ensaio de interrupção | Mesmo SHA-256 para o CSV recalculado e o original das 16 sessões | `interrupcao_recalculada.csv` |

Os dois CSVs ficam em uma pasta nova `Resultados_TCC_...`, ao lado do script. A conferência processa os registros publicados. Para gerar novas sessões com os navegadores, siga a seção de coleta.

## Dados publicados e integridade

| Caminho dentro do ZIP | Conteúdo |
| --- | --- |
| `serie_1/resultados.csv` e `serie_2/resultados.csv` | Séries iniciais no Firefox, com 16 sessões cada |
| `pos_fechamento/resultados.csv` | Classificação das 32 sessões após o fechamento |
| `interrupcao/resultados.csv` | Resultado das 16 sessões com respostas integrais ou interrompidas |

Abra os CSVs em uma planilha para consultar as medições originais. As instruções de conferência manual estão nos arquivos `LEIA-ME.txt` da raiz e das pastas `pos_fechamento` e `interrupcao`.

O SHA-256 de `Dados_do_ensaio_TCC.zip` é `6f808820682c9b2866cffcce9c443fce2df91cd1d99e6f91dff0896c3cd81444`. Para verificar os arquivos internos em Linux ou WSL, execute os dois comandos abaixo a partir da raiz do ZIP de dados extraído.

```bash
sha256sum -c SHA256.txt
(cd interrupcao && sha256sum -c SHA256SUMS.txt)
```

## Repetir a coleta no ambiente do estudo

Em Linux x86-64 ou WSL em x86-64, extraia `Dados_do_ensaio_TCC.zip` e abra o terminal na pasta que contém `ensaio.py`. Use Python 3.12, as versões indicadas abaixo e caminhos de saída novos a cada repetição. Execute os blocos em ordem, na mesma sessão do terminal. As portas e os identificadores de sessão variam a cada coleta.

### Preparar o Python e o Firefox

A partir da raiz da extração:

```bash
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install "playwright==1.62.0" "Pillow==13.0.0"

export PLAYWRIGHT_BROWSERS_PATH="$PWD/.navegadores/playwright"
python -m playwright install --with-deps firefox
export FIREFOX="$PLAYWRIGHT_BROWSERS_PATH/firefox-1538/firefox/firefox"
"$FIREFOX" --version
```

O ambiente virtual separa as dependências do projeto. O Playwright instala o Firefox distribuído para a versão registrada. O último comando permite verificar a versão do executável, **153.0** no estudo. Em distribuições compatíveis, a instalação das dependências do sistema pode solicitar autorização de administrador.

### Rodar as duas séries iniciais no Firefox

```bash
python ensaio.py resultado_serie_1
python ensaio_temporal.py resultado_serie_2
```

`ensaio.py` recria a primeira série. `ensaio_temporal.py` recria a segunda série e também registra a observação do cache antes do fechamento. Cada comando cria sua própria pasta com `resultados.csv` e artefatos de teste.

### Preparar o geckodriver e o Chrome Headless Shell

Para as duas etapas seguintes, instale também as dependências do Chromium e baixe os binários Linux x86-64 das versões registradas. Os comandos usam `curl`, `tar` e `unzip`.

```bash
python -m playwright install-deps chromium
mkdir -p .navegadores/geckodriver .navegadores/chrome

curl -fL "https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz" -o .navegadores/geckodriver.tar.gz
tar -xzf .navegadores/geckodriver.tar.gz -C .navegadores/geckodriver

curl -fL "https://storage.googleapis.com/chrome-for-testing-public/151.0.7922.34/linux64/chrome-headless-shell-linux64.zip" -o .navegadores/chrome-headless-shell.zip
unzip -q .navegadores/chrome-headless-shell.zip -d .navegadores/chrome

export GECKODRIVER="$PWD/.navegadores/geckodriver/geckodriver"
export CHROMIUM="$PWD/.navegadores/chrome/chrome-headless-shell-linux64/chrome-headless-shell"
"$GECKODRIVER" --version
"$CHROMIUM" --version
```

Os comandos exportam os caminhos absolutos dos executáveis para os scripts. Confira **geckodriver 0.36.0** e **Chrome Headless Shell 151.0.7922.34**. Se usar outro binário, registre a versão como uma condição diferente de execução. [Documentação do Playwright](https://playwright.dev/python/docs/browsers) · [geckodriver](https://github.com/mozilla/geckodriver/releases/tag/v0.36.0) · [Chrome for Testing](https://github.com/GoogleChromeLabs/chrome-for-testing#json-api-endpoints)

### Coletar e classificar novas sessões após o fechamento

```bash
cd pos_fechamento
python coletar.py firefox nova_coleta/serie_ff
python coletar.py chromium nova_coleta/serie_chr
python classificar.py nova_coleta/serie_ff/casos figura.png nova_coleta/serie_ff/previsoes.csv
python classificar.py nova_coleta/serie_chr/casos figura.png nova_coleta/serie_chr/previsoes.csv
python conferir.py nova_coleta
cd ..
```

Os dois primeiros comandos criam 16 sessões por navegador. Os classificadores geram as previsões, e `conferir.py` grava o cruzamento com o gabarito em `pos_fechamento/nova_coleta/resultados.csv`. Os nomes `serie_ff` e `serie_chr` são esperados pelo script de conferência.

### Coletar novas sessões de transferência interrompida

```bash
cd interrupcao
python interromper.py firefox nova_coleta/firefox
python interromper.py chromium nova_coleta/chromium
python medir.py nova_coleta nova_coleta/resultados.csv
cd ..
```

`interromper.py` prepara respostas integrais e interrompidas no servidor local. `medir.py` classifica os arquivos preservados e grava `interrupcao/nova_coleta/resultados.csv`.

Os três arquivos `LEIA-ME.txt` internos documentam as colunas, as condições do experimento e a interpretação dos resultados.
