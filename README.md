# TECH CHALLENGE

O Tech Challenge desta fase será a criação de uma aplicação que utilize
análise de vídeo. O seu projeto deve incorporar as técnicas de reconhecimento
facial, análise de expressões emocionais em vídeos e detecção de atividades.

# A PROPOSTA DO DESAFIO

Você deverá criar uma aplicação a partir do vídeo que se encontra
disponível na plataforma do aluno, e que execute as seguintes tarefas:

1. **Reconhecimento facial**: Identifique e marque os rostos presentes no vídeo.
2. **Análise de expressões emocionais**: Analise as expressões emocionais dos rostos identificados.
3. **Detecção de atividades**: Detecte e categorize as atividades sendo realizadas no vídeo.
4. **Geração de resumo**: Crie um resumo automático das principais atividades e emoções detectadas no vídeo.

# O QUE ESPERAMOS COMO ENTREGÁVEL?

1. **Código Fonte**: todo o código fonte da aplicação deve ser entregue em
   um repositório Git, incluindo um arquivo README com instruções
   claras de como executar o projeto.
2. **Relatório**: o resumo obtido automaticamente com as principais
   atividades e emoções detectadas no vídeo. Nesse momento
   esperando que o relatório inclua:

- Total de frames analisados.
- Número de anomalias detectadas.
  Observação: movimento anômalo não segue o padrão geral de atividades
  (como gestos bruscos ou comportamentos atípicos) esses são classificados
  como anômalos.

3. **Demonstração em Vídeo**: um vídeo demonstrando a aplicação em
   funcionamento, evidenciando cada uma das funcionalidades
   implementadas.

## Como executar o projeto

A implementação foi realizada em ambiente docker para facilitar a execução e desenvolvimento do mesmo,
sabendo-se que podemos enfrentar alguns desafions quando trabalhamos com diferentes sistemas operacionais.

- Primeiramente coloque o docker para rodar
- Agora execute o seguinte comando: `docker-compose up -d --build`
- Aguarde o docker realizar a configuração de todas as imagens necessárias
- Agora execute o seguinte comando: `docker-compose run app python main.py`
- O script será iniciado, processando o arquivo de vídeo e criando um novo arquivo de saída chamado `output.mp4`

- O relatório será apresentado no final da execução do script.
- No vídeo de saída, você poderá ver todo processamento que foi realizado no vídeo, juntamente com os elementos necessários para realizar o reconhecimento fácil e emoções das pessoas no vídeo.
