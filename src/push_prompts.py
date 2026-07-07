import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:

    try:
        print(f"Fazendo push do prompt para: {prompt_name}")

        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")

        # Criar ChatPromptTemplate a partir dos prompts
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Fazer push para o LangSmith Hub
        print(f"Conectando ao LangSmith Hub...")
        url = hub.push(
            repo_full_name=prompt_name,
            object=prompt_template,
            new_repo_is_public=True,  # PÚBLICO
            new_repo_description=prompt_data.get("description", ""),
            tags=prompt_data.get("tags", [])
        )

        print(f"Prompt publicado com sucesso!")
        print(f"URL: {url}")
        return True

    except Exception as e:
        error_msg = str(e).lower()
        print(f"Erro ao fazer push do prompt: {e}")

        if "ssl" in error_msg or "certificate" in error_msg:
            print("\nErro de conexão SSL/TLS detectado")
            print("Dica: Verifique sua conexão de internet e firewall")
            print("O código está pronto para push quando a conexão for restaurada")
        else:
            print("\n   Dica: Certifique-se de que:")
            print("   - LANGSMITH_API_KEY está configurada no .env")
            print("   - USERNAME_LANGSMITH_HUB está configurada no .env")
            print("   - O prompt YAML v2 está bem formado")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    
    errors = []

    # Campos obrigatórios
    required_fields = ['description', 'system_prompt', 'user_prompt', 'version']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    # Validar system_prompt não vazio
    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    # Validar user_prompt não vazio
    user_prompt = prompt_data.get('user_prompt', '').strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    # Validar ausência de TODOs
    if 'TODO' in system_prompt or '[TODO]' in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    if 'TODO' in user_prompt or '[TODO]' in user_prompt:
        errors.append("user_prompt ainda contém TODOs")

    # Validar técnicas aplicadas (mínimo 2)
    techniques = prompt_data.get('techniques_applied', [])
    if not isinstance(techniques, list) or len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques) if isinstance(techniques, list) else 0}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH HUB")

    # Validar variáveis de ambiente
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    # Carregar prompt v2 otimizado
    print("Carregando prompt otimizado (v2)...")
    prompt_data = load_yaml("prompts/bug_to_user_story_v2.yml")

    if not prompt_data:
        print("Erro ao carregar prompts/bug_to_user_story_v2.yml")
        return 1

    # Extrair dados do wrapper YAML
    if "bug_to_user_story_v2" in prompt_data:
        prompt_content = prompt_data["bug_to_user_story_v2"]
    else:
        prompt_content = prompt_data

    # Validar estrutura do prompt
    print("Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_content)

    if not is_valid:
        print("Prompt inválido! Erros encontrados:")
        for error in errors:
            print(f"      - {error}")
        return 1

    print("Prompt válido")

    # Fazer push para o LangSmith Hub
    prompt_name = f"{username}/bug_to_user_story_v2"
    if push_prompt_to_langsmith(prompt_name, prompt_content):
        print(f"\nPush concluído com sucesso!")
        print(f"   Prompt publicado: {prompt_name}")
        print(f"   Próximo passo: Avaliar prompt")
        print(f"   Execute: python src/evaluate.py")
        return 0
    else:
        print("\nErro ao fazer push do prompt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
