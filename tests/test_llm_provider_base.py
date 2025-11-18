from svt_core.llm_provider.base import DummyProvider, LLMResponse


def test_dummy_provider_generate():
    provider = DummyProvider()
    resp = provider.generate("hello world")
    assert isinstance(resp, LLMResponse)
    assert resp.text.startswith("dummy-response:")


def test_dummy_provider_health_and_describe():
    provider = DummyProvider()
    assert provider.health_check()["status"] == "ok"
    assert provider.describe()["name"] == "dummy"
