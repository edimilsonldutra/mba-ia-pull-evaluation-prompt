"""
Testes automatizados para validação de prompts.
"""
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
    @staticmethod
    def _get_prompt_data():
        data = load_prompts("prompts/bug_to_user_story_v2.yml")
        assert data is not None, "Arquivo prompts/bug_to_user_story_v2.yml não pôde ser carregado"
        assert "bug_to_user_story_v2" in data, "Chave bug_to_user_story_v2 não encontrada"
        return data["bug_to_user_story_v2"]

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = self._get_prompt_data()
        assert "system_prompt" in prompt_data
        assert isinstance(prompt_data["system_prompt"], str)
        assert prompt_data["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = self._get_prompt_data()
        system_prompt = prompt_data.get("system_prompt", "").lower()

        persona_indicators = [
            "você é",
            "product manager",
            "senior product manager",
            "assistente",
            "especializado",
        ]

        assert any(indicator in system_prompt for indicator in persona_indicators)

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = self._get_prompt_data()
        combined = (
            prompt_data.get("system_prompt", "") + "\n" + prompt_data.get("user_prompt", "")
        ).lower()

        expected_terms = [
            "markdown",
            "user story",
            "como um",
            "eu quero",
            "para que",
        ]
        assert any(term in combined for term in expected_terms)

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = self._get_prompt_data()
        combined = (
            prompt_data.get("system_prompt", "") + "\n" + prompt_data.get("user_prompt", "")
        ).lower()

        signals = [
            "few-shot",
            "exemplo",
            "entrada:",
            "saída esperada",
        ]
        assert sum(1 for signal in signals if signal in combined) >= 2

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_data = self._get_prompt_data()
        combined = (
            str(prompt_data.get("description", ""))
            + "\n"
            + str(prompt_data.get("system_prompt", ""))
            + "\n"
            + str(prompt_data.get("user_prompt", ""))
        ).lower()
        assert "[todo]" not in combined
        assert "todo" not in combined

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = self._get_prompt_data()
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert len(techniques) >= 2

        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, f"Estrutura inválida: {errors}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])