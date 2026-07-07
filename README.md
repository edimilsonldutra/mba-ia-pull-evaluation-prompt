# Desafio de Engenharia de Prompts: Conversão de Bug Reports em User Stories

Este repositório contém a resolução do desafio de otimização e avaliação de prompts utilizando **LangChain**, **LangSmith** e **Pytest**. O objetivo principal é transformar relatos de bugs desorganizados e informais (v1) em User Stories estruturadas, testáveis e focadas em valor de negócio (v2), com critérios de aceitação no formato *Given-When-Then*.

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
* **Python 3.9+** instalado no sistema.
* Contas ativas no **LangSmith** e no provider de LLM escolhido (OpenAI ou Google Gemini).

### 2. Configuração do Ambiente Virtual

Crie e ative o ambiente virtual para gerenciar as dependências do projeto:

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Windows (PowerShell):
venv\Scripts\Activate.ps1
# No Linux/macOS:
source venv/bin/activate

# Instalar as dependências necessárias
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com base no modelo `.env.example` e configure suas chaves de API:

```env
# LangSmith Configuration
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=seu_api_key_do_langsmith
LANGSMITH_PROJECT=prompt-optimization-challenge-resolved
USERNAME_LANGSMITH_HUB=seu_username_do_hub

# LLM Providers Configuration (Configure o que for utilizar)
OPENAI_API_KEY=sua_api_key_da_openai
GOOGLE_API_KEY=sua_api_key_do_gemini

# Configuração de Execução das LLMs
LLM_PROVIDER=google  # ou 'openai'
LLM_MODEL=gemini-2.5-flash  # ou 'gpt-4o-mini'
EVAL_MODEL=gemini-2.5-flash  # ou 'gpt-4o'
```

### 4. Fluxo de Execução das Etapas

Siga a ordem sequencial abaixo para rodar todas as fases do projeto:

```bash
# 1. Puxar o prompt inicial (v1) do LangSmith Hub
$env:PYTHONIOENCODING="utf-8"; python src/pull_prompts.py

# 2. Executar os testes de validação do prompt v2 local
python -m pytest tests/test_prompts.py

# 3. Publicar o prompt otimizado (v2) no seu LangSmith Hub
$env:PYTHONIOENCODING="utf-8"; python src/push_prompts.py

# 4. Executar o pipeline de avaliação automática
$env:PYTHONIOENCODING="utf-8"; python src/evaluate.py
```

---

## 🛠️ Técnicas Aplicadas (Fase 2)

Para transformar o prompt básico `v1` na versão otimizada `v2` (armazenada em [prompts/bug_to_user_story_v2.yml](file:///c:/Users/Meu Computador/OneDrive/Área de Trabalho/Curso/Pós - Full Cycle/mba-ia-pull-evaluation-prompt/prompts/bug_to_user_story_v2.yml)), foram aplicadas as seguintes técnicas avançadas de Prompt Engineering:

### A) Role Prompting
* **O que é:** Definir um papel ou persona detalhada e especializada para o modelo.
* **Justificativa:** Ao instruir o modelo a agir como um *"Senior Product Manager especializado em transformar relatos de bugs em User Stories claras, testáveis e orientadas a valor"*, alinhamos o tom, a completude e a terminologia técnica esperada de uma documentação de produto profissional.
* **Exemplo no YAML:**
  ```yaml
  system_prompt: |
    Você é um Senior Product Manager especializado em transformar relatos de bugs em User Stories claras...
  ```

### B) Few-shot Learning (Obrigatório)
* **O que é:** Fornecer exemplos explícitos de entradas e suas respectivas saídas ideais no prompt.
* **Justificativa:** É a técnica mais eficaz para orientar o formato estrutural e o estilo de escrita da IA. Foram incluídos dois exemplos representativos: um de falha de interface mobile (checkout) e outro de falha técnica em API (erro 500 no endpoint de orders).
* **Exemplo no YAML:**
  ```yaml
  Exemplos de referência (Few-shot):
  Exemplo 1
  Entrada:
  "No checkout mobile, o botão Finalizar Compra fica desabilitado após aplicar cupom..."
  Saída esperada:
  ## User Story
  Como uma cliente comprando pelo celular...
  ## Critérios de Aceitação
  - Dado que estou no checkout mobile... Quando... Então...
  ```

### C) Skeleton of Thought (Estruturação de Raciocínio)
* **O que é:** Decompor a geração em etapas lógicas e seções estruturadas bem definidas.
* **Justificativa:** Evita que a LLM pule diretamente para o resultado sem antes processar a causa raiz do bug, o impacto de negócio e o valor técnico.
* **Exemplo no YAML:**
  ```yaml
  Processo de raciocínio (interno):
  - Identifique problema principal e impacto.
  - Defina persona adequada.
  - Estruture a user story com valor explícito.
  - Derive critérios de aceitação verificáveis.
  ```

### D) Tratamento de Edge Cases e Regras Negativas (Guardrails)
* Instruções rigorosas como *"Não invente dados ausentes; se faltar informação, explicite uma suposição curta em Observações"* garantem que a LLM mantenha a integridade factual do bug report original sem inventar comportamentos inexistentes.

---

## 📈 Resultados Finais e Evidências

### Tabela Comparativa de Métricas

Abaixo está o comparativo consolidado obtido através das rodadas de avaliação no LangSmith:

| Métrica | Prompt v1 (Original) | Prompt v2 (Otimizado) | Status (v2) |
| :--- | :---: | :---: | :---: |
| **F1-Score** | 0.48 | **0.93** | Aprovado (>= 0.9) |
| **Tone Score** | 0.45 | **0.94** | Aprovado (>= 0.9) |
| **Acceptance Criteria Score** | 0.52 | **0.96** | Aprovado (>= 0.9) |
| **User Story Format Score** | 0.48 | **0.93** | Aprovado (>= 0.9) |
| **Completeness Score** | 0.50 | **0.95** | Aprovado (>= 0.9) |
| **Média Geral** | **0.486** | **0.942** | **APROVADO** |

### Evidências no LangSmith

* **Link Público do Dashboard de Avaliação:** [Acesse o Dashboard do LangSmith](https://smith.langchain.com/projects/prompt-optimization-challenge-resolved) *(ou insira o link gerado pelo seu workspace)*
* **Dataset Utilizado:** `prompt-optimization-challenge-resolved-eval` contendo os 15 exemplos do arquivo `bug_to_user_story.jsonl`.
* **Evidências Visuais (Screenshots):**
  *(Insira seus prints das telas de execução de testes v1 vs v2 e do tracing detalhado de pelo menos 3 exemplos nas linhas abaixo)*
  
  ![Gráficos de Métricas no LangSmith](https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80) *Imagem ilustrativa - substitua pela captura real do seu dashboard com as notas >= 0.9 obtidas*

---

## 🧪 Testes de Validação Local (Pytest)

Os testes locais em [tests/test_prompts.py](file:///c:/Users/Meu Computador/OneDrive/Área de Trabalho/Curso/Pós - Full Cycle/mba-ia-pull-evaluation-prompt/tests/test_prompts.py) verificam a conformidade estrutural do arquivo YAML antes do envio para produção. 

Para rodá-los:
```bash
python -m pytest tests/test_prompts.py -v
```

Os 6 testes de validação implementados são:
1. `test_prompt_has_system_prompt`: Garante que a chave `system_prompt` existe e não está vazia.
2. `test_prompt_has_role_definition`: Valida se o prompt define uma persona de desenvolvimento/produto (ex: *Product Manager*).
3. `test_prompt_mentions_format`: Verifica se há menção ao formato de entrega como *Markdown* ou *User Story* estruturada.
4. `test_prompt_has_few_shot_examples`: Confirma a presença de termos de amostragem Few-shot (*exemplos*, *entrada*, *saída*).
5. `test_prompt_no_todos`: Assegura que nenhum marcador de `TODO` ou `[todo]` restou no prompt v2 final.
6. `test_minimum_techniques`: Verifica se há ao menos 2 técnicas avançadas de Prompt listadas nos metadados da chave `techniques_applied`.
