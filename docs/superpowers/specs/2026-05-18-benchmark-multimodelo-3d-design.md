# Benchmark Multi-Modelo e Superfícies 3D

## Objetivo

Expandir o pipeline atual para responder à pergunta central do README com foco em performance preditiva: comparar múltiplos modelos locais fortes no mesmo split temporal, manter TabPFN como benchmark opcional de referência e gerar resultados 3D que ajudem a visualizar superfícies de resposta do modelo campeão local.

## Escopo

- Generalizar o benchmark local além de Ridge e Random Forest.
- Manter o split temporal `train < 2015` / `test >= 2015`.
- Adotar tuning temporal pesado para modelos locais treináveis.
- Preservar compatibilidade com o pipeline atual e com o comparativo opcional de TabPFN.
- Produzir figuras 3D estáticas como artefatos analíticos de resultado.
- Exportar assets compactos para a camada web consumindo o novo esquema de comparação.

## Arquitetura

Criar uma camada compartilhada em `src/models/` para centralizar preparação de dados, geração de folds temporais, registro de modelos locais, tuning, métricas, predições e dados de superfície. `scripts/08_train_baseline_models.py` passa a funcionar como benchmark local pesado; `scripts/09_train_tabpfn_priorlabs.py` continua opcional, mas reusa o mesmo preparo de features e acrescenta o benchmark externo ao comparativo global; `scripts/10` e `11` deixam de assumir um único campeão fixo.

## Modelos locais alvo

Base sempre presente:
- Ridge
- ElasticNet
- RandomForestRegressor
- ExtraTreesRegressor
- HistGradientBoostingRegressor
- GradientBoostingRegressor

Modelos opcionais por biblioteca disponível:
- XGBoost
- LightGBM
- CatBoost

## Saídas esperadas

Tabelas:
- métricas locais detalhadas
- predições locais por modelo
- resultados de busca de hiperparâmetros
- importância de features por modelo quando aplicável
- comparativo global entre modelos locais e TabPFN opcional
- resumo de resíduos por modelo e resíduos do campeão final

Figuras:
- comparativo local de modelos
- erro temporal multi-modelo
- importância de features do melhor modelo local compatível
- superfícies 3D estáticas para os melhores modelos locais

Assets web:
- ranking expandido de modelos
- séries temporais e comparativos atualizados
- payload opcional para futuras superfícies 3D no frontend

## Restrições e decisões

- O pipeline principal precisa continuar útil sem credenciais de TabPFN.
- Os modelos locais devem ser reproduzíveis e não depender de API externa.
- A interpretação do relatório continua preditiva/associativa, não causal.
- As superfícies 3D devem representar relações reais do modelo com duas features relevantes, mantendo as demais fixadas em valores de referência.
