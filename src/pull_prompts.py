"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do Hub e salva localmente em YAML."""
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = Path("prompts/bug_to_user_story_v1.yml")

    print(f"Puxando prompt: {prompt_name}")
    prompt = hub.pull(prompt_name)

    messages = getattr(prompt, "messages", [])
    system_prompt = ""
    user_prompt = "{bug_report}"

    for message in messages:
        message_type = getattr(message, "prompt", None)
        template = getattr(message_type, "template", "")

        if getattr(message, "__class__", type("", (), {})).__name__.lower().startswith("system"):
            system_prompt = template or system_prompt
        elif getattr(message, "__class__", type("", (), {})).__name__.lower().startswith("human"):
            user_prompt = template or user_prompt

    if not system_prompt:
        system_prompt = (
            "Você é um assistente especializado em transformar relatos de bugs em user stories. "
            "Converta o bug report em uma user story estruturada."
        )

    payload = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source_hub_prompt": prompt_name,
            "tags": ["bug-analysis", "user-story", "product-management"]
        }
    }

    if not save_yaml(payload, str(output_path)):
        raise RuntimeError(f"Falha ao salvar YAML em {output_path}")

    print(f"✓ Prompt salvo em: {output_path}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPT DO LANGSMITH")

    if not os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    try:
        pull_prompts_from_langsmith()
        print("\n✅ Pull concluído com sucesso.")
        return 0
    except Exception as exc:
        print(f"\n❌ Erro no pull: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
