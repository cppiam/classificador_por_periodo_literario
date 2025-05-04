import json
from ppm_model import PPMModel
from train_models import build_alphabet_from_txts

def classify_text_by_entropy(text, model_paths, alphabet, order=5):
    models_entropy = {}

    for period, path in model_paths.items():
        print(f"\nCarregando modelo para '{period}'...")
        model = PPMModel(alphabet, order)
        model.load_model(path)
        model.total_bits = 0.0
        model.total_symbols = 0

        print(f"Calculando entropia para '{period}'...")
        history = []
        for symbol in text:
            model.process_symbol(symbol, history)
            history.append(symbol)
            if len(history) > model.order:
                history.pop(0)

        models_entropy[period] = model.total_bits/model.total_symbols
        #print(f"Entropia média para '{period}': {models_entropy[period]:.4f} bits")

    best_period = min(models_entropy, key=models_entropy.get)
    return best_period, models_entropy

if __name__ == "__main__":
    model_paths = {
        "barroco": "ppm_tabela_barroco.json",
        "romantismo": "ppm_tabela_romantismo.json",
        "realismo": "ppm_tabela_realismo.json",
        "modernismo": "ppm_tabela_modernismo.json"
    }

    alphabet = build_alphabet_from_txts("books")

    with open("O curtiço.txt", 'rb') as f:
        text = f.read().decode('utf-8')

    text = text.lower()
    text = text.split()
    texto_limpo = " ".join(text)

    predicted_period, entropies = classify_text_by_entropy(texto_limpo, model_paths, alphabet, order=5)

    print(f"\n--- Resultados da Classificação ---")
    for period, entropy in entropies.items():
        print(f"Entropia média para '{period}': {entropy:.4f} bits")
    print(f"\nO texto foi classificado como pertencente ao período: {predicted_period}")