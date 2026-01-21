from g4f import ChatCompletion
from g4f.Provider import You, OpenAI, Bard
from g4f.errors import ModelNotFoundError

providers = [You, OpenAI, Bard]  # mavjud providerlar
models = ["gpt-4o-mini", "gpt-4", "claude-3-haiku", "mixtral"]

def auto_chat(question):
    for provider in providers:
        for model in models:
            try:
                response = ChatCompletion.create(
                    model=model,
                    provider=provider,
                    messages=[{"role": "user", "content": question}],
                    stream=False
                )
                print(f"✅ Ishladi: {model} ({provider.__name__})")
                return response
            except ModelNotFoundError:
                continue
            except Exception as e:
                continue
    return "⚠️ Hech qanday model ishlamadi"

print(auto_chat("Python nima?"))
