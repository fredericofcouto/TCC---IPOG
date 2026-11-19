# Material suplementar do TCC sobre vestígios de navegador

O arquivo [Dados_do_ensaio_TCC.zip](./Dados_do_ensaio_TCC.zip) reúne scripts, registros por sessão, perfis de laboratório, imagens sintéticas de referência e resultados em CSV. As coletas foram feitas em um servidor local com imagens sintéticas.

## Conferência rápida no Windows

1. No topo do repositório, clique em **Code → Download ZIP** e escolha **Extrair Tudo** no Windows.
2. Abra a pasta extraída que contém `executar_testes.py` e `Dados_do_ensaio_TCC.zip`. Clique na barra de endereço do Explorador, digite `powershell` e pressione **Enter**.
3. Na janela aberta, cole este comando e pressione **Enter**.

```powershell
python .\executar_testes.py
```

O script usa o Python 3 já instalado, extrai o ZIP de dados para uma pasta temporária e roda as duas conferências. O resultado esperado é **12 acertos e 20 casos inconclusivos em 32 sessões**, seguido de **dois hashes SHA-256 iguais**. Os CSVs recalculados ficam em uma nova pasta `Resultados_TCC_...`, ao lado do script.

Se o Windows reconhecer o Python pelo iniciador `py`, o mesmo comando pode ser executado como `py -3 .\executar_testes.py`. Se ambos os comandos estiverem indisponíveis, instale o [Python para Windows](https://www.python.org/downloads/windows/) e reabra o PowerShell.

| Se você quer… | Comece por |
| --- | --- |
| Ler as medições originais | Abra os arquivos CSV descritos na seção 1 |
| Conferir os resultados sem instalar navegadores | Use o comando da conferência rápida acima |
| Gerar novas sessões no ambiente do estudo | Execute a seção 3 em Linux x86-64 ou WSL em um computador x86-64 |

## 1. Baixar e localizar os resultados

Abra o [arquivo ZIP no GitHub](./Dados_do_ensaio_TCC.zip), clique no botão de download e extraia o conteúdo para uma pasta nova. Use como raiz a pasta que contém `LEIA-ME.txt`, `ensaio.py` e as subpastas `pos_fechamento` e `interrupcao`.

| Caminho dentro do ZIP | O que contém |
| --- | --- |
| `serie_1/resultados.csv` e `serie_2/resultados.csv` | Duas séries iniciais no Firefox com 16 sessões cada |
| `pos_fechamento/resultados.csv` | Classificação após o fechamento em 32 sessões |
| `interrupcao/resultados.csv` | Resultado de 16 sessões com transferências integrais ou interrompidas |
| `SHA256.txt` | Soma SHA-256 dos arquivos listados no manifesto |

Os CSVs podem ser abertos em uma planilha. No Linux, execute `sha256sum -c SHA256.txt` na raiz da pasta extraída para verificar o manifesto antes de reprocessar os dados.

## 2. Comandos individuais para conferência manual

Esta etapa usa somente a biblioteca padrão do Python. Trabalhe em uma nova extração do ZIP, pois o programa regrava `previsoes.csv` e `pos_fechamento/resultados.csv` na pasta de trabalho.

Para acompanhar cada comando separadamente, abra o PowerShell na raiz **do ZIP de dados extraído**, onde estão as pastas `pos_fechamento` e `interrupcao`. Confirme que `python --version` mostra uma versão do Python 3. No Linux ou WSL, use `python3` no lugar de `python` e mantenha a mesma sequência.

```powershell
cd pos_fechamento
python classificar.py serie_ff/casos figura.png serie_ff/previsoes.csv
python classificar.py serie_chr/casos figura.png serie_chr/previsoes.csv
python conferir.py .

cd ../interrupcao
python medir.py . resultados_recalculados.csv
Get-FileHash -Algorithm SHA256 resultados.csv,resultados_recalculados.csv
cd ..
```

- Os dois comandos `classificar.py` leem os casos e a imagem de referência e gravam as previsões do Firefox e do Chrome Headless Shell, respectivamente. Cada linha recebe `D` para download, `I` para imagem incorporada ou `?` para resultado inconclusivo.
- `conferir.py .` cruza as previsões com o gabarito e gera `pos_fechamento/resultados.csv`. Nos dados fornecidos, espera-se **12 acertos e 20 inconclusivos em 32 sessões**.
- `medir.py . resultados_recalculados.csv` relê os arquivos preservados nas sessões de interrupção. O SHA-256 dos dois CSVs deve ser igual. Em Linux ou WSL, substitua `Get-FileHash ...` por `sha256sum resultados.csv resultados_recalculados.csv`.

## 3. Repetir a coleta no ambiente do estudo

Execute os blocos a seguir na ordem apresentada, na mesma sessão do terminal. Para reproduzir as condições registradas no estudo, use Linux x86-64 ou WSL em x86-64, Python 3.12 e as versões de navegador e bibliotecas especificadas abaixo. Portas e identificadores de sessão são gerados em cada execução. Use caminhos de saída novos ao repetir os comandos de coleta.

### 3.1. Preparar o Python e o Firefox

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

### 3.2. Rodar as duas séries iniciais no Firefox

```bash
python ensaio.py resultado_serie_1
python ensaio_temporal.py resultado_serie_2
```

`ensaio.py` recria a primeira série. `ensaio_temporal.py` recria a segunda série e também registra a observação do cache antes do fechamento. Cada comando cria sua própria pasta com `resultados.csv` e artefatos de teste.

### 3.3. Preparar o geckodriver e o Chrome Headless Shell

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

### 3.4. Coletar e classificar novas sessões após o fechamento

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

### 3.5. Coletar novas sessões de transferência interrompida

```bash
cd interrupcao
python interromper.py firefox nova_coleta/firefox
python interromper.py chromium nova_coleta/chromium
python medir.py nova_coleta nova_coleta/resultados.csv
cd ..
```

`interromper.py` prepara respostas integrais e interrompidas no servidor local. `medir.py` classifica os arquivos preservados e grava `interrupcao/nova_coleta/resultados.csv`.

Os três arquivos `LEIA-ME.txt` internos documentam as colunas, as condições do experimento e a interpretação dos resultados.
