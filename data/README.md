# Dados do projeto

## Origem

Portal oficial Filipeia/SEPLAN/PMJP: https://filipeia.joaopessoa.pb.gov.br/

Arquivos baixados para este projeto em 11/10/2026:

- Quadras: https://filipeia.joaopessoa.pb.gov.br/files/donwload/quadras_gerais.zip
- Logradouros: https://filipeia.joaopessoa.pb.gov.br/files/donwload/Logradouro_gerais.zip
- Bairros: https://filipeia.joaopessoa.pb.gov.br/files/donwload/bairros.zip

O portal também publica CSVs para as camadas. Os Shapefiles podem ser baixados localmente para data/source e o índice que o app usa é gerado em data/generated/quadras.json. Os arquivos brutos ficam fora do repositório público e do site; o app público distribui somente o índice necessário para consulta.

## Campos observados

- Quadras: setor, qd_atual, qd_antes, área e perímetro; a geometria é PolygonZ em SIRGAS 2000 / UTM 25S.
- Logradouros: nome_logr, tipo, código e geometria de linhas; o DBF inclui 23.450 registros.
- Bairros: N_BAIRRO e geometria de polígonos.

O identificador da busca usa bairro + setor + quadra. O registro Torre / Setor 10 / Quadra 119 existe uma única vez na camada de quadras e foi associado a quatro nomes de logradouro próximos no arquivo oficial.

## Preparação

Execute o script scripts/build_data.py depois de substituir os arquivos por uma versão atualizada. Ele usa apenas a biblioteca padrão do Python e gera data/generated/quadras.json.

A relação espacial considera ruas até 25 metros do limite da quadra. Essa distância é uma tolerância inicial; ela precisa ser conferida em campo/mapa, especialmente em vias largas ou quadras irregulares.

## Atribuição e uso

O Filipeia informa que os dados podem ser usados em análises, estudos e aplicativos, exige a menção da fonte como “Filipeia/SEPLAN/PMJP” e veda a venda onerosa dos arquivos ou informações. Verifique as condições atuais antes de distribuir ou comercializar o app.

## Cobertura da primeira geração

O índice gerado contém 8.986 quadras com bairro atribuído. Há 40 registros da camada de quadras que não entraram na primeira geração por não terem uma associação bairro/geometria resolvida pelas regras atuais. Se algum aparecer em uma rota, será necessário revisar esse caso específico antes de confiar no resultado.


## Divergência conhecida na busca

Na cópia local consultada, Setor 37 / Quadra 331 existe como Funcionários. A combinação Gramame / Setor 37 / Quadra 331 não consta no índice. A interface não troca o bairro automaticamente: mostra a associação encontrada e deixa o leiturista confirmar antes de adicioná-la à rota.
