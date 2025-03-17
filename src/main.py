from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner, trace, RunConfig
from pydantic import BaseModel
import asyncio
import uuid
from openai import OpenAI
from src.config_manager import ConfigManager
from src.logger import Logger
from src.error_handler import catch_async_errors, APIKeyError, APIConnectionError, ValidationError

# Configurar logger específico para este módulo
logger = Logger.setup("main")

# Verificar se a chave de API da OpenAI está configurada
if not ConfigManager.validate_api_key():
    logger.error("API Key não configurada. O sistema não pode funcionar corretamente.")
    print("ERRO: OPENAI_API_KEY não está configurada. Execute o script run.sh para configurar a variável de ambiente.")
    exit(1)
else:
    api_key = ConfigManager.get_api_key()
    logger.info("API Key detectada e validada")
    print(f"API Key detectada: {api_key[:8]}...")

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="""Verifique se o usuário está fazendo uma pergunta educacional.
    Considere qualquer pergunta sobre conhecimentos gerais, conceitos, definições ou explicações como uma pergunta educacional válida.
    Apenas rejeite perguntas que sejam claramente não educacionais, como insultos, spam ou conteúdo inapropriado.""",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Especialista em Matemática",
    handoff_description="Agente especialista em perguntas sobre Matemática",
    instructions="""Você é um especialista em Matemática para estudantes do ensino médio.
        Responda perguntas sobre álgebra, geometria, trigonometria, funções, estatística e outros tópicos relacionados.
        Explique os conceitos de forma clara e didática, mostrando o passo a passo da resolução quando necessário.
        Use uma linguagem adequada para estudantes do ensino médio.
        Ao fim da resposta, forneça o nome do agente especialista que forneceu a resposta.""",
)

history_tutor_agent = Agent(
    name="Especialista em História",
    handoff_description="Agente especialista em perguntas sobre História",
    instructions="""Você é um especialista em História para estudantes do ensino médio.
        Responda perguntas sobre história do Brasil, história mundial, períodos históricos, revoluções, guerras e outros tópicos relacionados.
        Contextualize os eventos históricos e explique suas causas e consequências.
        Use uma linguagem clara e didática, adequada para estudantes do ensino médio.
        Ao final da sua resposta, inclua a seguinte assinatura: "[Resposta fornecida pelo Especialista em História]""",
)


@catch_async_errors
async def homework_guardrail(ctx, agent, input_data):
    """Verifica se a pergunta é educacional usando o guardrail agent.
    
    Args:
        ctx: Contexto da execução
        agent: Agente que está sendo executado
        input_data: Dados de entrada (pergunta do usuário)
        
    Returns:
        GuardrailFunctionOutput: Resultado da verificação
    """
    logger.debug(f"Verificando guardrail para input: '{input_data[:30]}{'...' if len(input_data) > 30 else ''}'") 
    
    try:
        result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
        final_output = result.final_output_as(HomeworkOutput)
        
        # Registrar resultado da verificação
        logger.info(f"Guardrail resultado: is_homework={final_output.is_homework}")
        
        # Modificado para sempre permitir a pergunta, independentemente do resultado
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=False,  # Sempre permite a pergunta
        )
    except Exception as e:
        logger.error(f"Erro no guardrail: {str(e)}")
        raise APIConnectionError(f"Falha na verificação da pergunta: {str(e)}")

triage_agent = Agent(
    name="Triage Agent",
    instructions="Você determina qual agente usar com base na pergunta de trabalho de casa do usuário",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

@catch_async_errors
async def processar_pergunta(pergunta):
    """
    Processa uma pergunta usando o agente de triagem e retorna a resposta.
    
    Args:
        pergunta (str): A pergunta a ser processada.
        
    Returns:
        tuple[str, str]: (resposta do agente especialista, ID do trace)
        
    Raises:
        ValidationError: Se a pergunta for inválida
        APIConnectionError: Se houver problemas de conexão com a API
        APIKeyError: Se a chave da API não estiver configurada
    """
    # Validar entrada
    if not pergunta or not isinstance(pergunta, str) or len(pergunta.strip()) == 0:
        logger.error("Tentativa de processar pergunta vazia")
        raise ValidationError("A pergunta não pode estar vazia")
    
    # Gerar ID único para o trace
    trace_id = f"trace_{uuid.uuid4().hex}"
    group_id = ConfigManager.get_config("nova", "trace_group_id")
    workflow_name = ConfigManager.get_config("nova", "trace_workflow_name")

    # Configurar o rastreamento
    run_config = RunConfig(
        trace_id=trace_id,
        workflow_name=workflow_name,
        group_id=group_id,
        trace_include_sensitive_data=True
    )
    
    logger.info(f"Processando pergunta: '{pergunta[:30]}{'...' if len(pergunta) > 30 else ''}'")
    logger.info(f"Trace ID: {trace_id}")
    print(f"[TRACE] ID: {trace_id}")
    
    try:
        # Executar a pergunta com trace
        with trace(run_config.workflow_name):
            result = await Runner.run(triage_agent, pergunta, run_config=run_config)
        
        logger.info("Resposta obtida com sucesso")
        # Retornar a resposta e o ID do trace
        return result.final_output, trace_id
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {str(e)}")
        raise APIConnectionError(f"Falha na comunicação com a API da OpenAI: {str(e)}")

async def main():
    """Função principal para testar o processamento de perguntas."""
    try:
        logger.info("Iniciando teste do sistema de processamento de perguntas")
        
        # Exemplo de uso para teste
        pergunta_teste = "O que é tempo verbal em português?"
        print(f"\nProcessando pergunta de teste: '{pergunta_teste}'\n")
        
        resposta, trace_id = await processar_pergunta(pergunta_teste)
        
        print("\nResposta obtida:")
        print(resposta)
        print(f"\n[TRACE] Você pode visualizar o trace completo no painel da OpenAI usando o ID: {trace_id}\n")
        logger.info(f"Teste concluído com sucesso. Trace ID: {trace_id}")
    except Exception as e:
        logger.error(f"Erro durante o teste: {str(e)}", exc_info=True)
        print(f"\nOcorreu um erro durante o teste: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Erro fatal na execução do programa: {str(e)}", exc_info=True)
        print(f"\nErro fatal: {str(e)}")
        print("O programa será encerrado.")