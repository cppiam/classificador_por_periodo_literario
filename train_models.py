import os
from ppm_model import PPMModel

def build_alphabet_from_txts(directory="books"):
    charset = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    charset.update(f.read())
    return sorted(charset)

def load_text(file_path):
    with open(file_path, encoding="utf-8") as f:
        return f.read()

def train_and_save_model(period_name, file_path, alphabet, order=5):
    print(f"\nTreinando modelo para o período: {period_name}")
    text = load_text(file_path)

    model = PPMModel(alphabet, order)
    history = []

    for symbol in text:
        model.update(symbol, history)
        history.append(symbol)

    output_file = f"ppm_tabela_{period_name.lower()}.txt"
    model.save_model(output_file)

periodos = {
    "barroco": "books/barroco/textos_do_barroco.txt",
    "romantismo": "books/romantismo/textos_do_romantismo.txt",
    "realismo": "books/realismo/textos_do_realismo.txt",
    "modernismo": "books/modernismo/textos_do_modernismo.txt"
}

if __name__ == "__main__":
    alphabet = build_alphabet_from_txts("books")
    for periodo, caminho in periodos.items():
        train_and_save_model(periodo, caminho, alphabet)
