from openai import OpenAI
import json
import time

client = OpenAI()

# Função para extrair e exibir informações do RequiredActionFunctionToolCall
def extrair_tool_call_info(run):
    if run.status == "requires_action" and run.required_action:
        if run.required_action.type == "submit_tool_outputs":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            for i, tool_call in enumerate(tool_calls):
                if tool_call.type == "function":
                    print(f"\n--- Tool Call {i+1} ---")
                    print(f"RequiredActionFunctionToolCall id: {tool_call.id}")
                    print(f"Function name: {tool_call.function.name}")
                    print(f"Arguments: {tool_call.function.arguments}")
                    
                    # Converter os argumentos de string JSON para dicionário Python
                    try:
                        args = json.loads(tool_call.function.arguments)
                        print(f"\nArgumentos processados:")
                        for key, value in args.items():
                            print(f"{key}: {value}")
                    except json.JSONDecodeError as e:
                        print(f"Erro ao decodificar argumentos JSON: {e}")
                    
                    return tool_call.id
    return None

thread_id = "thread_wEkdsrsY2xnWt1SeIodTikUF"

# Primeiro, vamos verificar o run específico mencionado pelo usuário
run_id_especifico = "run_t9qlgqEbSquidprnPyJIento"
print(f"\n=== Verificando o run específico {run_id_especifico} ===\n")

try:
    # Recuperar o run específico
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id_especifico
    )
    
    print(f"Status do run: {run.status}")
    
    if run.status == "requires_action":
        print("\nEste run requer ação!")
        print(f"Tipo de ação requerida: {run.required_action.type}")
        
        # Extrair e exibir informações do RequiredActionFunctionToolCall
        tool_call_id = extrair_tool_call_info(run)
        
        if tool_call_id:
            print(f"\nRequiredActionFunctionToolCall id para usar na resposta: {tool_call_id}")
        else:
            print("\nNenhum RequiredActionFunctionToolCall encontrado.")
    else:
        print(f"O run não requer ação. Status atual: {run.status}")
        
except Exception as e:
    print(f"Erro ao buscar o run específico: {e}")

# Agora, vamos verificar todos os runs ativos no thread
print("\n=== Verificando todos os runs ativos no thread ===\n")

try:
    # Listar todos os runs no thread
    runs = client.beta.threads.runs.list(
        thread_id=thread_id
    )
    
    # Verificar se há runs ativos que requerem ação
    requires_action_runs = [run for run in runs.data if run.status == "requires_action"]
    
    if requires_action_runs:
        print(f"Encontrados {len(requires_action_runs)} runs que requerem ação.")
        
        # Processar cada run que requer ação
        for i, run in enumerate(requires_action_runs):
            print(f"\n--- Run {i+1} ---")
            print(f"Run ID: {run.id}")
            print(f"Status: {run.status}")
            print(f"Criado em: {run.created_at}")
            
            # Recuperar detalhes completos do run
            run_details = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            # Extrair o tool_call_id
            tool_call_id = extrair_tool_call_info(run_details)
            
            if tool_call_id:
                print(f"\nRequiredActionFunctionToolCall id para usar na resposta: {tool_call_id}")
            else:
                print("\nNenhum RequiredActionFunctionToolCall encontrado.")
    else:
        print("Não foram encontrados runs que requerem ação.")
        
        # Vamos criar um novo run para demonstração
        print("\n=== Criando um novo run para demonstração ===\n")
        
        # Verificar se há algum run ativo
        active_runs = [run for run in runs.data if run.status in ["queued", "in_progress"]]        
        if active_runs:
            print(f"Existem {len(active_runs)} runs ativos no thread. Aguardando conclusão...")
            
            for active_run in active_runs:
                print(f"Aguardando conclusão do run {active_run.id}...")
                
                # Aguardar até que o run seja concluído
                while True:
                    run_status = client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=active_run.id
                    )
                    
                    print(f"Status: {run_status.status}")
                    
                    if run_status.status not in ["queued", "in_progress"]:
                        print(f"Run {active_run.id} concluído com status: {run_status.status}")
                        break
                    
                    # Aguardar 2 segundos antes de verificar novamente
                    time.sleep(2)
        
        try:
            # Criar nova mensagem
            thread_message = client.beta.threads.messages.create(
                thread_id,
                role="user",
                content="Quanto é 10 * 10?",
            )
            print("Nova mensagem criada.")
            
            # Criar novo run
            new_run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id="asst_WhiiRlPHO2Y8itK1S5PK2ySw"
            )
            print(f"Novo run criado com ID: {new_run.id}")
            
            # Aguardar até que o run requeira ação ou seja concluído
            print("\nAguardando o run...")
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=new_run.id
                )
                
                print(f"Status: {run_status.status}")
                
                if run_status.status == "requires_action":
                    print("\nO run requer ação!")
                    
                    # Extrair o tool_call_id
                    tool_call_id = extrair_tool_call_info(run_status)
                    
                    if tool_call_id:
                        print(f"\nRequiredActionFunctionToolCall id para usar na resposta: {tool_call_id}")
                    else:
                        print("\nNenhum RequiredActionFunctionToolCall encontrado.")
                    
                    break
                elif run_status.status in ["completed", "failed", "cancelled", "expired"]:
                    print(f"Run concluído com status: {run_status.status}")
                    break
                
                # Aguardar 2 segundos antes de verificar novamente
                time.sleep(2)
        except Exception as e:
            print(f"Erro ao criar novo run: {e}")
        
except Exception as e:
    print(f"Erro ao listar runs: {e}")
