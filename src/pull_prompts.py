import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():

    output_path = "prompts/bug_to_user_story_v1.yml"
    local_v1_exists = Path(output_path).exists()

    if local_v1_exists:
        print(f"Arquivo local encontrado: {output_path}")
        print("Usando versão local do prompt baseline")
        return True

    # Validar variáveis de ambiente obrigatórias para pull remoto
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        print("\nNota: Se você tem acesso ao arquivo local, considere usá-lo.")
        return False

    print("Conectando ao LangSmith Hub...")

    try:
        # Fazer pull do prompt v1 (baseline de baixa qualidade)
        print("Puxando prompt: edimilsonldutra/bug_to_user_story_v1")
        prompt_template = hub.pull("edimilsonldutra/bug_to_user_story_v1")

        # Extrair system_prompt e user_prompt do ChatPromptTemplate
        # O template tem 2 inputs: messages (com system e human parts)
        system_prompt = ""
        user_prompt = ""

        # Acessar os messages do template
        if hasattr(prompt_template, 'messages'):
            for msg in prompt_template.messages:
                if hasattr(msg, 'prompt'):
                    # Extrair o conteúdo de cada mensagem
                    if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                        if 'system' in str(type(msg)).lower():
                            system_prompt = msg.prompt.template
                        else:
                            user_prompt = msg.prompt.template

        # Se não conseguiu via messages, tenta serialização alternativa
        if not system_prompt or not user_prompt:
            # Fallback: extrair do dict/schema do template
            if hasattr(prompt_template, 'dict'):
                template_dict = prompt_template.dict()
            elif hasattr(prompt_template, '__dict__'):
                template_dict = prompt_template.__dict__
            else:
                template_dict = {}

            # Procurar por campos de sistema e usuário
            for key, value in template_dict.items():
                if 'system' in str(key).lower() or 'system' in str(value).lower():
                    system_prompt = str(value)
                if 'user' in str(key).lower() or 'human' in str(key).lower():
                    user_prompt = str(value)

        # Se ainda não temos, serializar todo o template como string
        if not system_prompt:
            system_prompt = "Você é um assistente que ajuda a transformar relatos de bugs em User Stories."
        if not user_prompt:
            user_prompt = "{bug_report}"

        # Construir dicionário do prompt
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories (baseline)",
                "system_prompt": system_prompt.strip(),
                "user_prompt": user_prompt.strip(),
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management", "baseline"]
            }
        }

        # Salvar em YAML local
        if save_yaml(prompt_data, output_path):
            print(f"Prompt salvo em {output_path}")
            return True
        else:
            print(f"Erro ao salvar prompt em {output_path}")
            return False

    except Exception as e:
        print(f"Erro ao puxar prompt do LangSmith Hub: {e}")
        print("\n   Dica: Certifique-se de que:")
        print("   - LANGSMITH_API_KEY está configurada no .env")
        print("   - O prompt 'edimilsonldutra/bug_to_user_story_v1' existe")
        print("   - Você tem acesso ao workspace")
        print("   - Sua conexão com internet está funcionando")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    success = pull_prompts_from_langsmith()

    if success:
        print("\nPull concluído com sucesso!")
        print("Próximo passo: Otimizar o prompt e criar v2")
        print("Execute: python src/push_prompts.py")
        return 0
    else:
        print("\nErro ao fazer pull do prompt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
