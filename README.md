# ufrj-hydrosense-data

## Pipeline de Processamento e Integração de Dados

Este repositório contém um pipeline completo para preparação de dados meteorológicos e de vazão para treinamento de modelos de Machine Learning para previsão mensal de vazão. As principais etapas e regras de negócio implementadas são:

### 1. Join Espacial (Estação Meteorológica x Subbacia)
- Cada estação meteorológica é associada a uma subbacia do reservatório de Funil via join espacial entre as coordenadas (latitude, longitude) e os polígonos do shapefile das subbacias.
- O resultado é um arquivo JSON contendo todos os atributos meteorológicos acrescidos do campo `Subbasin` (ID da subbacia).

### 2. Agregação Mensal dos Dados de Vazão
- Os dados diários de vazão são agregados para escala mensal utilizando a média dos valores diários.
- O resultado é um arquivo JSON com a média mensal de vazão para cada estação.

### 3. Junção dos Dados Meteorológicos e de Vazão
- Os dados meteorológicos e de vazão são unidos pelas chaves: ano, mês e ID da subbacia.
- O mapeamento entre estação fluviométrica e subbacia é feito via arquivo JSON de mapeamento.
- O resultado é um arquivo JSON combinando as variáveis meteorológicas e a vazão mensal para cada subbacia.

### 4. Deslocamento Temporal
- É criado um novo dataset em que as variáveis meteorológicas do mês X são associadas à vazão do mês X+1 (deslocamento temporal).
- Apenas registros com vazão diferente de null e maior que zero são mantidos.
- O objetivo é garantir que os dados meteorológicos representem as variáveis preditoras e a vazão seja a variável objetivo para previsão do mês seguinte.

### 5. Consistência Temporal
- O pipeline garante que a vazão sempre representa o mês imediatamente posterior ao registro meteorológico.
- São realizados testes automatizados para garantir a integridade e consistência dos dados.

### 6. Testes Automatizados
- Um notebook de testes automatizados está disponível em `tests/test_pipeline_dados.ipynb`.
- O notebook valida todas as regras de negócio, exemplos de registros e possíveis inconsistências.

### 7. Observações
- O arquivo meteorológico bruto (`data/glob_1993a2023_mo.csv`) está no `.gitignore` devido ao seu tamanho.
- Todos os scripts do pipeline estão na pasta `scripts/`.

---

Para mais detalhes sobre cada etapa, consulte os scripts e o notebook de testes.