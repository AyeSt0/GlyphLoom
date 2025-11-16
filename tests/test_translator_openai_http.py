from glyphloom_core.core.models import TranslatorConfig
from glyphloom_core.translators.openai_http import OpenAIHttpTranslator


def test_openai_http_translator_echo():
    config = TranslatorConfig(
        provider="openai",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        api_key_env="DUMMY_KEY",
    )
    translator = OpenAIHttpTranslator(config)
    inputs = ["你好", "世界"]
    outputs = translator.translate_batch(inputs)

    assert len(outputs) == len(inputs)
    assert outputs[0].startswith("[openai:gpt-4o-mini]")
    assert outputs[1].endswith("世界")
