from unittest.mock import MagicMock

from svt_core.llm_provider.manager import ProviderManager
from svt_core.llm_provider.base import LLMResponse, LLMProvider


class FakeProvider(LLMProvider):
    def __init__(self, name: str, response: str, fail: bool = False):
        super().__init__(name)
        self.response = response
        self.fail = fail

    def generate(self, prompt: str, **kwargs):
        if self.fail:
            raise RuntimeError("fail")
        return LLMResponse(text=self.response)

    def health_check(self):
        return {"status": "ok"}

    def describe(self):
        return {"name": self.name}


def test_manager_switch_and_fallback():
    mgr = ProviderManager()
    mgr.register("cloud", FakeProvider("cloud", "cloud"))
    mgr.set_active("cloud")

    resp = mgr.generate("ping")
    assert resp.text == "cloud"

    mgr.register("bad", FakeProvider("bad", "", fail=True))
    mgr.set_active("bad")
    resp = mgr.generate("ping")
    assert resp.text != ""
    assert mgr.describe_active()["name"] == "local-ollama"
