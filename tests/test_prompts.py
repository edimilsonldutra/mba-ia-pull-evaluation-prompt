import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        assert "bug_to_user_story_v2" in prompts, "Prompt 'bug_to_user_story_v2' not found in YAML"
        assert "system_prompt" in prompts["bug_to_user_story_v2"], "Field 'system_prompt' is missing"
        assert prompts["bug_to_user_story_v2"]["system_prompt"].strip() != "", "system_prompt is empty"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        system_prompt = prompts["bug_to_user_story_v2"]["system_prompt"]
        assert "Você é" in system_prompt or "You are" in system_prompt, "No role/persona definition found in system_prompt"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        full_prompt = prompts["bug_to_user_story_v2"]["system_prompt"]
        assert "Markdown" in full_prompt or "User Story" in full_prompt or "Given-When-Then" in full_prompt, \
            "Prompt must mention Markdown, User Story, or Given-When-Then format"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        system_prompt = prompts["bug_to_user_story_v2"]["system_prompt"]
        # Count examples by looking for BUG markers (supports multiple formats)
        example_count = (
            system_prompt.count("BUG REPORT INPUT:") +
            system_prompt.count("**BUG REPORT INPUT:**") +
            system_prompt.count("BUG REPORT:") +
            system_prompt.count("**BUG REPORT:**") +
            system_prompt.count("**BUG:**") +
            system_prompt.count("BUG:")
        )
        assert example_count >= 2, f"Expected at least 2 few-shot examples, found {example_count}"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        system_prompt = prompts["bug_to_user_story_v2"]["system_prompt"]
        user_prompt = prompts["bug_to_user_story_v2"]["user_prompt"]

        # Check system and user prompts (not constraints section)
        for prompt_part in [system_prompt, user_prompt]:
            # Don't match [TODO] if it's in the context of constraint instructions
            lines = prompt_part.split('\n')
            for line in lines:
                if "RESTRIÇÕES" not in line and "Não faça" not in line:
                    assert "[TODO]" not in line, f"Found incomplete TODO marker: {line}"
                    assert line.strip().startswith("TODO:") == False or "TODO:" not in line, f"Found TODO text: {line}"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        techniques = prompts["bug_to_user_story_v2"].get("techniques_applied", [])
        assert isinstance(techniques, list), "techniques_applied must be a list"
        assert len(techniques) >= 2, f"Minimum 2 techniques required, found {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])