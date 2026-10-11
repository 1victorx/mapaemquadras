# MapaEmQuadras

Aplicação web mobile-first para organizar a rota diária de leitura e abrir no Google Maps as ruas próximas a cada quadra.

## Usar o app

1. Escolha o bairro e informe setor e quadra como aparecem na rota.
2. Adicione as quadras na ordem de trabalho. A rota não tem quantidade máxima.
3. Abra no Maps a rua que deseja consultar.

A lista fica salva neste navegador e aparelho, separada por data. O app não coleta leituras, dados de clientes nem localização contínua.

## Dados

O app usa o arquivo data/generated/quadras.json, um índice derivado dos dados cartográficos do Filipeia/SEPLAN/PMJP. Atribuição da fonte: Filipeia / SEPLAN / PMJP (https://filipeia.joaopessoa.pb.gov.br/sigweb/).

As camadas brutas de GIS não fazem parte do repositório nem do site público. Elas contêm metadados desnecessários para executar o app. Para reconstruir o índice, consulte as fontes e instruções em data/README.md, obtenha os dados no portal oficial e execute python scripts/build_data.py.

O portal exige atribuição e informa que os dados e informações não podem ser vendidos. Verifique as condições atuais antes de redistribuir ou comercializar o app.

## Desenvolvimento local

Na pasta do projeto, inicie um servidor HTTP local, por exemplo:

python -m http.server 8000 --bind 127.0.0.1

Depois abra http://localhost:8000.

## Publicação temporária

O workflow em .github/workflows/deploy-pages.yml publica no GitHub Pages quando há uma atualização na branch main. O site publica apenas os arquivos necessários para o app e o índice de quadras; arquivos de planejamento, ferramentas locais e camadas brutas não entram no site.
