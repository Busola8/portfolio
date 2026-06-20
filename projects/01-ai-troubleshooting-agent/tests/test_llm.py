from app.llm import OpenAILLMClient


class BrokenResponses:
    def create(self, **kwargs):
        raise RuntimeError("invalid api key")


class BrokenClient:
    responses = BrokenResponses()


def test_openai_llm_falls_back_when_api_call_fails() -> None:
    client = OpenAILLMClient.__new__(OpenAILLMClient)
    client.client = BrokenClient()
    client.model = "gpt-test"
    fallback = ("Local RCA", 0.8, ["Use fallback"])

    assert client.generate_rca("incident", {}, [], fallback) == fallback
