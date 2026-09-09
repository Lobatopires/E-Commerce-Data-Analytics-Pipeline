# 🛒 E-Commerce Data Analytics Pipeline (End-to-End)

## Sobre o Projeto
Este repositório documenta a construção de uma pipeline de dados completa, criada para simular os desafios reais de um ambiente de negócio. Mais do que ligar tabelas num dashboard, o meu foco foi garantir a **qualidade, integração e integridade da informação** desde a extração até à visualização final. 

O objetivo analítico foi mapear o perfil demográfico dos clientes de uma loja fictícia de e-commerce e quantificar o impacto de eventos sazonais (como Feriados Nacionais) nos picos de faturação.

## Stack Tecnológica
* **Python (Pandas, Requests):** Consumo de APIs, automação do processo de ETL, tratamento de dados inconsistentes e injeção programática.
* **SQL (Demonstração Adicional):** Embora a fonte de dados principal sejam ficheiros planos (CSV), incluí na pasta `/sql` scripts de análise exploratória simulada e validação de regras de negócio (incluindo *Window Functions*) a titulo de demostração de proficiência em ambiente de base de dados relacional.
* **Power BI & DAX:** Modelagem dimensional (*Star Schema*), criação de métricas dinâmicas e *storytelling* visual.

## Desafios Técnicos e Soluções
Durante o desenvolvimento, deparei-me com problemas típicos de dados reais e implementei as seguintes soluções:

1. **Extração Dinâmica via API:** Para analisar a sazonalidade, em vez de depender de ficheiros estáticos, desenvolvi um script que consome uma API para extrair dinamicamente os Feriados Nacionais e armazená-los para cruzamento com os dados de vendas.
2. **Automação da Limpeza (Python):** Criei um motor de regras automatizado que padroniza formatos de texto (como nomes de cidades) e trata idades vazias antes de os dados chegarem ao modelo final.
3. **Resolução de Integridade Referencial (O "Cliente Fantasma"):** Identifiquei registos de encomendas órfãs sem correspondência na base de clientes. Para garantir que nenhuma receita financeira era perdida, programei o Python para injetar um "Ghost Record" (ID -1), preservando a exatidão financeira no Power BI.
4. **Modelagem Star Schema:** Estruturei os dados dividindo-os em tabelas de Factos (`Orders`, `Payments`) e Dimensões (`Customers`, `Products`), otimizando a performance e escalabilidade.
5. **Resolução de Relacionamentos Complexos (DAX):** O cruzamento das vendas diárias com a tabela de Feriados gerou um desafio de cardinalidade Muitos-para-Muitos. Resolvi este bloqueio criando uma tabela `dCalendario` dedicada e usando `CALCULATE` e `FILTER` para isolar a faturação sazonal.

## Principais Insights
*(Estes são exemplos baseados nos dados processados)*
* O grupo demográfico "36-50 anos" representa a maior fatia de receita sustentável ao longo do ano.
* O feriado "Dia da Liberdade" regista consistentemente o maior pico isolado de vendas, sugerindo oportunidades para campanhas de marketing direcionadas.

## Aprendizagens Pessoais
Além da componente analítica, este projeto permitiu-me consolidar boas práticas de engenharia de software aplicadas a dados, incluindo a integração de fontes externas (APIs), controlo de versões com Git e gestão do ambiente de desenvolvimento.

## Dashboard Interativo
![Demonstração do Dashboard](link_para_uma_imagem_ou_gif_do_dashboard_aqui)

---
*Para explorar a lógica de extração e consumo da API, consulte a pasta `/scripts`. Para as validações na base de dados, veja a pasta `/sql`.*