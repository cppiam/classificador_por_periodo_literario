from ppm_model import PPMModel
import math
import os

def build_alphabet_from_txts(directory="books"):
    charset = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, encoding="utf-8") as f:
                    text = f.read()
                    charset.update(text)
    return sorted(charset)

def main():
    alphabet = build_alphabet_from_txts()
    model = PPMModel(alphabet, order=2)
    message = "abracadabra"
    history = []
    
    print("=== CÁLCULO PPM COM TABELAS ===")
    
    for i, symbol in enumerate(message):
        print(f"\n--- Passo {i+1}: '{symbol}' ---")
        
        # Mostra tabelas ANTES da atualização
        if history:
            print("\nTabelas do modelo ANTES deste símbolo:")
            model.print_tables(history)
        
        # Calcula probabilidade
        prob_info = model._get_probability_with_details(symbol, history)
        
        # Mostra cálculo
        print("\nCálculo de probabilidade:")
        for step in prob_info['steps']:
            print(f"  {step}")
        print(f"  = {prob_info['formula']} = {prob_info['prob']:.4f}")
        
        if prob_info['prob'] > 0:
            bits = -math.log2(prob_info['prob'])
            print(f"\nContribuição para entropia: -log2({prob_info['prob']:.4f}) = {bits:.4f} bits")
        
        # Atualiza modelo
        model.update(symbol, history)
        history.append(symbol)
        
        input("\nPressione Enter para continuar...")
    
    # Resultado final
    total_symbols = len(message)
    total_bits = sum(-math.log2(model._get_probability_with_details(symbol, message[:i])['prob']) 
                    for i, symbol in enumerate(message))
    
    print("\n=== RESULTADO FINAL ===")
    print(f"Total de bits: {total_bits:.4f}")
    print(f"Entropia média: {total_bits/total_symbols:.4f} bits/símbolo")

if __name__ == "__main__":
    main()