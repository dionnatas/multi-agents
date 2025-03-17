#!/bin/bash

# Carregar variáveis de ambiente do arquivo .env se ele existir
if [ -f ".env" ]; then
    echo "Carregando variáveis de ambiente do arquivo .env..."
    # Carregar variáveis do arquivo .env
    export $(grep -v '^#' .env | xargs)
    echo "Variáveis de ambiente carregadas com sucesso."
else
    echo "Arquivo .env não encontrado. Usando o arquivo .env.example como modelo."
    echo "Para configurar permanentemente, copie o arquivo .env.example para .env e edite-o."
    echo "cp .env.example .env"
    echo "nano .env  # ou use seu editor preferido"
    echo
    
    # Verificar se a chave de API da OpenAI está configurada
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "ATENÇÃO: A variável de ambiente OPENAI_API_KEY não está configurada."
        
        # Solicitar a chave de API do usuário
        read -p "Deseja informar sua chave de API agora? (s/n): " resposta
        if [ "$resposta" = "s" ]; then
            read -p "Digite sua chave de API da OpenAI: " api_key
            export OPENAI_API_KEY="$api_key"
            echo "Chave de API configurada temporariamente para esta sessão."
            
            # Perguntar se deseja salvar no arquivo .env
            read -p "Deseja salvar esta chave no arquivo .env para uso futuro? (s/n): " salvar
            if [ "$salvar" = "s" ]; then
                echo "Criando arquivo .env..."
                echo "OPENAI_API_KEY=$api_key" > .env
                echo "Chave de API salva no arquivo .env."
            fi
        else
            echo "O programa não pode continuar sem uma chave de API válida."
            exit 1
        fi
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
