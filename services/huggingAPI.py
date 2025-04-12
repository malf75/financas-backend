import requests
import re
from setup.settings import HUGGING_TOKEN

def limpar_texto(texto):
    texto = re.sub(r'[\n\\]', '', texto)
    texto = texto.strip('"')
    return texto

def hugging_api_request(dados):
    try:
        prompt = (
            f"Based in this financial data: {dados}"
            "Give me a Feedback based on the expenses and earnings, and a financial hint with a max of 50 words"
            "Don't return the promt in the response, and consider using portuguese"
        )

        headers = {"Authorization": f"Bearer {HUGGING_TOKEN}"}
        url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 50, "return_full_text": False}
        }

        response = requests.post(url, headers=headers, json=payload)
        resultado = response.json()

        if isinstance(resultado, list) and "generated_text" in resultado[0]:
            dica = resultado[0]["generated_text"]
            dica_limpa = limpar_texto(dica)
            return {"Dicas": dica_limpa}
        else:
            texto_raw = str(resultado)
            texto_limpo = limpar_texto(texto_raw)
            return {"Dicas": texto_limpo}

    except Exception as e:
        raise Exception(f"Erro ao fazer requisição para a API Hugging Face: {e}")