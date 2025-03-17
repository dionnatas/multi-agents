# Sistema de Classificação de Perguntas por Matéria

Este projeto utiliza o SDK de agentes da OpenAI para criar um sistema que classifica perguntas por matérias do ensino médio e as encaminha para agentes especialistas que fornecerão respostas adequadas.

## Estrutura do Projeto

O projeto é composto por:

- Um agente orquestrador que recebe a pergunta inicial
- Agentes especialistas em diferentes matérias (português, matemática, história, etc.)
- Sistema de classificação que determina a matéria da pergunta

## Requisitos

- Python 3.9+
- OpenAI API Key
- Biblioteca `openai-agents`

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Uso

Execute o script principal:

```
python src/main.py
```

## Configuração

Defina sua chave de API da OpenAI como uma variável de ambiente:

```
export OPENAI_API_KEY='sua-chave-api'
```
