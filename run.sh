#!/bin/bash

# Verificar se a chave de API da OpenAI está configurada
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ATENÇÃO: A variável de ambiente OPENAI_API_KEY não está configurada."
    echo "Por favor, configure sua chave de API usando o comando:"
    echo "export OPENAI_API_KEY='sua-chave-api-aqui'"
    echo "Ou adicione-a ao seu arquivo ~/.bashrc ou ~/.zshrc"
    
    # Solicitar a chave de API do usuário
    read -p "Deseja informar sua chave de API agora? (s/n): " resposta
    if [ "$resposta" = "s" ]; then
        read -p "Digite sua chave de API da OpenAI: " api_key
        export OPENAI_API_KEY="$api_key"
        echo "Chave de API configurada temporariamente para esta sessão."
    else
        echo "O programa não pode continuar sem uma chave de API válida."
        exit 1
    fi
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    # Ativar o ambiente virtual
    source venv/bin/activate
fi

# Mensagem de boas-vindas
echo "=================================================="
echo "      Sistema Educacional Multi-Agentes"        
echo "=================================================="
echo "Iniciando o sistema..."

# Exibir menu de escolha da API
echo
echo "=== Sistema Educacional de Perguntas e Respostas ==="
echo "Este sistema utiliza agentes especializados para responder suas perguntas."
echo "Cada pergunta é classificada e encaminhada para o especialista adequado."
echo

echo "Escolha qual API da OpenAI deseja utilizar:"
echo "1. API Nova (Agents SDK - recomendada)"
echo "2. API Antiga (Assistants API - será descontinuada em 2026)"
echo

read -p "Digite o número da sua escolha (1 ou 2): " escolha

if [ "$escolha" = "1" ]; then
    echo
    echo "Escolha qual versão da API Nova deseja executar:"
    echo "1. Padrão (sem persistência de contexto)"
    echo "2. Com persistência de contexto (experimental)"
    echo
    
    read -p "Digite o número da sua escolha (1 ou 2): " versao
    
    if [ "$versao" = "1" ]; then
        echo "Executando API Nova padrão..."
        python -m src.interativo
    else
        echo "Executando API Nova com persistência de contexto..."
        python -m src.interativo_com_contexto
    fi
else
    echo "Executando API Antiga..."
    python -m src.old_api.interativo
fi
