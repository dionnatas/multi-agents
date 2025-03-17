import os

def configurar_api_key(api_key=None):
    """
    Configura a chave da API da OpenAI.
    
    Args:
        api_key (str, optional): Chave da API da OpenAI. Se não for fornecida,
                                 tentará usar a variável de ambiente OPENAI_API_KEY.
    
    Returns:
        bool: True se a configuração foi bem-sucedida, False caso contrário.
    """
    # Se a chave for fornecida, configura a variável de ambiente
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        return True
    
    # Se a chave não for fornecida, verifica se já está configurada
    if "OPENAI_API_KEY" in os.environ and os.environ["OPENAI_API_KEY"]:
        return True
    
    # Se não estiver configurada, retorna False
    return False
