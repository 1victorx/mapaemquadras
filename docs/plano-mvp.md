# Plano inicial do MVP

## Skills aplicadas

| Skill | Uso neste projeto |
|---|---|
| descoberta-produto | Definir usuário, necessidade, jornada, MVP e perguntas em aberto. |
| orquestracao-projeto | Ordenar disciplinas e carregar somente especialidades relevantes. |
| planejamento-projeto | Quebrar o trabalho em marcos com dependências e critérios de aceite. |
| ux-ui-design | Priorizar consulta rápida e uso em celular. |
| arquitetura-frontend | Separar entrada da rota, resultados, estados e acesso a dados. |
| acessibilidade-web | Garantir formulários, foco, contraste e controles acessíveis. |
| aplicacao-web-profissional | Guiar a implementação ponta a ponta e futuras fatias do MVP. |

Skills condicionais: design-api, banco-dados e arquitetura-backend só serão necessárias se a origem exigir um serviço próprio. Revisar segurança antes de publicar ou adicionar coleta/sincronização.

## Escopo confirmado

- Usuário primário: leiturista de água em rota diária.
- Rota do dia: lista ordenada, sem quantidade máxima de quadras.
- Identificador informado: bairro + setor + número da quadra.
- Resultado: ruas próximas à quadra, cada uma com seu próprio botão do Google Maps.
- O usuário escolhe qual rua abrir.
- Armazenamento local no navegador, separado por data.
- Sem cadastro de clientes, leituras ou localização contínua.

## Dados e evidência

O Filipeia publica Shapefiles de Quadras, Bairros e Logradouros. Os três conjuntos foram baixados para data/source localmente; os arquivos brutos ficam excluídos do repositório público. O script scripts/build_data.py relaciona as geometrias e gera data/generated/quadras.json.

Campos observados:
- Quadras: setor, qd_atual, qd_antes, área e perímetro; geometria PolygonZ em SIRGAS 2000 / UTM 25S.
- Logradouros: nome_logr, tipo, código e linhas geográficas; 23.450 registros no DBF.
- Bairros: N_BAIRRO e polígonos.

A associação de rua usa distância inicial de até 25 metros do limite da quadra. Isso funciona para o caso Torre / Setor 10 / Quadra 119, que encontrou quatro vias. Ainda é necessário validar outras quadras e casos de vias largas, ruas sem nome e divisões entre bairros.

## Fases

### 0. Fonte e dados — iniciado
- Confirmar dados oficiais e arquivos disponíveis.
- Preparar as geometrias para consulta.
- Validar três ou mais quadras em áreas diferentes.

Critério de passagem: nome(s) de rua e ponto do Maps conferem com o portal em exemplos reais.

### 1. Fluxo e protótipo — iniciado
- Montar a lista na ordem da rota.
- Mostrar bairro, setor, quadra e ruas.
- Exibir estados carregando, erro, vazio e quadra não encontrada.
- Revisar a tela em celular e acessibilidade básica.

### 2. Fatia funcional
- Regenerar o índice a partir dos arquivos oficiais.
- Consultar quadras e exibir ruas relacionadas.
- Abrir o ponto da rua escolhida no Google Maps.
- Preservar a lista do dia no navegador.

Critério de passagem: os exemplos de validação funcionam ponta a ponta.

### 3. Validação de campo
- Conferir resultados com várias rotas reais, sem incluir dados de clientes.
- Corrigir associações ambíguas e verificar se a coordenada do Maps é útil.
- Avaliar modo sem internet somente se necessário.

## Decisões técnicas

- Aplicação web estática em HTML, CSS e JavaScript, sem servidor de aplicação no MVP.
- Preparação dos dados com Python padrão.
- O destino usa coordenadas extraídas da linha do logradouro perto da quadra.
- Hospedagem temporária pública no GitHub Pages, com publicação automática a partir da branch main. O workflow disponibiliza somente os arquivos necessários para o app.

## Riscos e limitações

- O raio de 25 metros é uma heurística de associação; não representa cadastro oficial de frente ou lado da quadra.
- Quadras podem tocar várias ruas, então o usuário escolhe uma opção.
- Alguns centróides ficam perto da divisa entre bairros; esses casos aparecem com aviso.
- Dados de mapa podem ficar desatualizados; regenerar o índice com arquivos oficiais atualizados.
- O portal exige atribuição como “Filipeia/SEPLAN/PMJP” e informa restrições à venda onerosa dos arquivos ou informações. Rever as condições antes de distribuir ou comercializar o app.

## Próximo passo

Abrir o protótipo em navegador, validar mais quadras de uma rota e ajustar a associação espacial com base nos resultados.
