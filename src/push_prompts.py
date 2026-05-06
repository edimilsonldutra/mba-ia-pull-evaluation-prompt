"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "").strip()
        user_prompt = prompt_data.get("user_prompt", "{bug_report}").strip()

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        techniques = prompt_data.get("techniques_applied", [])
        tags = prompt_data.get("tags", [])
        metadata = {
            "description": prompt_data.get("description", "Prompt otimizado de bug to user story"),
            "techniques_applied": techniques,
            "version": prompt_data.get("version", "v2"),
            "tags": tags,
        }

        try:
            hub.push(
                prompt_name,
                object=prompt_template,
                new_repo_is_public=True,
                description=metadata["description"],
                readme=(
                    "Prompt otimizado para converter bug reports em user stories. "
                    f"Técnicas: {', '.join(techniques) if techniques else 'não informado'}."
                ),
                tags=tags,
            )
        except TypeError:
            # Compatibilidade com versões de LangChain/LangSmith que aceitam apenas argumentos básicos.
            hub.push(
                prompt_name,
                object=prompt_template,
                new_repo_is_public=True,
            )

        print(f"✓ Prompt publicado: {prompt_name}")
        return True
    except Exception as exc:
        print(f"❌ Falha no push de {prompt_name}: {exc}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    required_fields = ["description", "system_prompt", "user_prompt", "version", "techniques_applied"]

    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    if not str(prompt_data.get("system_prompt", "")).strip():
        errors.append("system_prompt está vazio")

    if not str(prompt_data.get("user_prompt", "")).strip():
        errors.append("user_prompt está vazio")

    techniques = prompt_data.get("techniques_applied", [])
    if not isinstance(techniques, list) or len(techniques) < 2:
        errors.append("techniques_applied deve conter ao menos 2 técnicas")

    combined_text = "\n".join([
        str(prompt_data.get("description", "")),
        str(prompt_data.get("system_prompt", "")),
        str(prompt_data.get("user_prompt", "")),
    ]).lower()
    if "[todo]" in combined_text or "todo" in combined_text:
        errors.append("Prompt contém marcador TODO")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPT OTIMIZADO")

    username = (
        os.getenv("LANGSMITH_USERNAME", "").strip()
        or os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    )
    required_vars = ["LANGSMITH_API_KEY"]

    if not check_env_vars(required_vars):
        return 1

    yaml_data = load_yaml("prompts/bug_to_user_story_v2.yml")
    if not yaml_data:
        print("❌ Não foi possível carregar prompts/bug_to_user_story_v2.yml")
        return 1

    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in yaml_data:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        return 1

    prompt_data = yaml_data[prompt_key]
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"  - {error}")
        return 1

    full_prompt_name = f"{username}/bug_to_user_story_v2" if username else "bug_to_user_story_v2"
    if not username:
        print("⚠️  Username do Hub não informado. Usando nome padrão: bug_to_user_story_v2")

    if push_prompt_to_langsmith(full_prompt_name, prompt_data):
        print("\n✅ Push concluído com sucesso.")
        print("Confira em: https://smith.langchain.com/prompts")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
