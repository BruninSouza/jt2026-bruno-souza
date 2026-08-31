# Contexto
Análise de investimento imobiliário de temporada em Itapema (SC) para a Seazone.
Dados em `data/`. Scripts em `src/`. Resultados em `outputs/`.
Estou no Windows 10, usando PowerShell. Não sou desenvolvedor:
explique as decisões técnicas em português simples.
Entrega hoje às 19h30. Prioridade é decisão defensável, não completude.

# Regras
- NUNCA imprima o conteúdo bruto dos CSVs no chat. Escreva scripts Python que leem
  de `data/` e salvam resultados em `outputs/`.
- Uma tarefa por vez. Não tente resolver a análise inteira numa resposta só.
- Um script por etapa, numerado: src/01_perfil.py, src/02_receita.py, ...
- Todo script imprime no final: linhas de entrada, linhas após os filtros e quantas
  caíram por qual filtro.
- Premissas de negócio ficam num dicionário no topo do arquivo, com um comentário
  justificando cada valor.
- Nunca invente nome de coluna. Se não souber, escreva código que inspecione o
  arquivo e me mostre o resultado.
- Não use try/except genérico para esconder erro. Deixe o erro aparecer.
- Nenhum número em texto sem o arquivo de origem em `outputs/`.
- Antes de escrever código, me explique o plano em 5 linhas e espere eu aprovar.
- Quando eu pedir uma conclusão, apresente também a evidência contrária.
- Não elogie minhas perguntas. Discorde quando achar que estou errado.