# Design

## Direção
Caderno de rota de campo, atualizado para consulta rápida durante o trabalho. A folha diária reúne a busca, as paradas em ordem e a abertura dos logradouros no Google Maps.

## Linguagem visual
- Fundo cinza-papel claro e folhas quase brancas com sombra suave.
- Índigo escuro para estrutura e ações; laranja queimado para sequência e sinalização.
- Tipografia sans-serif robusta em toda a interface, com números tabulares para setor, quadra e ordem da rota.
- Controles com bom contraste, cantos suaves e áreas de toque confortáveis; evitar aparência de formulário antigo.

## Composição e componentes
- Cabeçalho índigo com marca vetorial de quadras.
- No desktop, consulta e lista diária lado a lado; em telas estreitas, busca primeiro e rota abaixo.
- Bairro em uma linha, setor e quadra juntos, botão de adicionar evidente.
- Cada parada mostra seu número em destaque, bairro, setor, ruas próximas e acesso ao Maps.
- A rota pode ter qualquer quantidade de quadras; a contagem exibida é informativa.
- O estado vazio explica como começar e usa um esquema cartográfico decorativo, sem simular mapa real.

## Interação e acessibilidade
- Foco visível, labels associados, mensagens anunciadas por aria-live, áreas de toque ampliadas e suporte a movimento reduzido.
- Divergências bairro/setor/quadra são explicadas; a troca de bairro exige confirmação do usuário.
- A rota continua salva localmente por data; nenhuma sincronização ou geolocalização é indicada pela interface.
