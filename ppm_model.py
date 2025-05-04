import math

class PPMModel:
    def __init__(self, alphabet, order):
        self.order = order
        self.contexts = {k: {} for k in range(1, order + 1)}
        self.k0_frequencies = {}
        self.alphabet = set(alphabet)
        self.seen_symbols = set()
        self.k0_unique_symbols = 0
        self.excluded_symbols = set()
        self.total_bits = 0.0
        self.total_symbols = 0
        self.escape_counts = 0 

    def update(self, symbol, history):
        self.excluded_symbols = set()
        
        if symbol not in self.seen_symbols:
            self.seen_symbols.add(symbol)
            self.k0_unique_symbols += 1

        if symbol not in self.k0_frequencies:
            self.k0_frequencies[symbol] = 0
        self.k0_frequencies[symbol] += 1

        for k in range(1, self.order + 1):
            if len(history) >= k:
                context = "".join(history[-k:])
                if context not in self.contexts[k]:
                    self.contexts[k][context] = {'symbols': set(), 'frequencies': {}}

                if symbol not in self.contexts[k][context]['symbols']:
                    self.contexts[k][context]['symbols'].add(symbol)

                if symbol not in self.contexts[k][context]['frequencies']:
                    self.contexts[k][context]['frequencies'][symbol] = 0
                self.contexts[k][context]['frequencies'][symbol] += 1

    def _get_probability_with_details(self, symbol, history):
        self.excluded_symbols = set()
        steps = []
        prob = 1.0
        formula_parts = []
        
        # Tenta codificar com ordens de self.order até 1
        for k in range(self.order, 0, -1):
            if len(history) >= k:
                context = "".join(history[-k:])
                if context in self.contexts[k]:
                    frequencies = self.contexts[k][context]['frequencies']
                    unique_symbols = len(self.contexts[k][context]['symbols'])
                    total = sum(frequencies.values())
                    
                    if symbol in frequencies:
                        step_prob = frequencies[symbol] / (total + unique_symbols)
                        steps.append(f"Ordem {k}: símbolo encontrado no contexto '{context}' - prob = {step_prob:.4f}")
                        prob *= step_prob
                        formula_parts.append(f"{step_prob:.4f}")
                        self.excluded_symbols.update(frequencies.keys())
                        return {
                            'steps': steps,
                            'prob': prob,
                            'formula': " × ".join(formula_parts),
                            'order': k
                        }
                    else:
                        step_prob_esc = unique_symbols / (total + unique_symbols)
                        steps.append(f"Ordem {k}: escape no contexto '{context}' - prob = {step_prob_esc:.4f}")
                        prob *= step_prob_esc
                        formula_parts.append(f"{step_prob_esc:.4f}")
                        self.excluded_symbols.update(frequencies.keys())

         # Ordem 0 (considerando exclusão)
        available_symbols = {s: c for s, c in self.k0_frequencies.items() 
                           if s not in self.excluded_symbols}
        total_k0 = sum(available_symbols.values())
        
        # Modificação aqui: usar self.escape_counts em vez de self.k0_unique_symbols
        unique_k0 = len(available_symbols) + (self.escape_counts - len(self.excluded_symbols))
        
        if total_k0 + unique_k0 > 0:
            if symbol in available_symbols:
                step_prob_k0 = available_symbols[symbol] / (total_k0 + unique_k0)
                steps.append(f"Ordem 0: símbolo encontrado - prob = {step_prob_k0:.4f}")
                prob *= step_prob_k0
                formula_parts.append(f"{step_prob_k0:.4f}")
                return {
                    'steps': steps,
                    'prob': prob,
                    'formula': " × ".join(formula_parts),
                    'order': 0
                }
            else:
                # Incrementa o contador de escape apenas quando realmente ocorre um escape
                self.escape_counts += 1
                step_prob_esc_k0 = unique_k0 / (total_k0 + unique_k0)
                steps.append(f"Ordem 0: escape - prob = {step_prob_esc_k0:.4f}")
                prob *= step_prob_esc_k0
                formula_parts.append(f"{step_prob_esc_k0:.4f}")

        # Ordem -1 (considerando exclusão)
        unseen = self.alphabet - self.seen_symbols - self.excluded_symbols
        if symbol in unseen:
            step_prob_k_minus_1 = 1.0 / len(unseen) if unseen else 0.0
            steps.append(f"Ordem -1: símbolo não visto - prob = {step_prob_k_minus_1:.4f}")
            prob *= step_prob_k_minus_1
            formula_parts.append(f"{step_prob_k_minus_1:.4f}")
            return {
                'steps': steps,
                'prob': prob,
                'formula': " × ".join(formula_parts),
                'order': -1
            }
        else:
            return {
                'steps': steps + ["Erro: Símbolo não encontrado no alfabeto ou foi excluído"],
                'prob': 0.0,
                'formula': " × ".join(formula_parts) + " × 0",
                'order': None
            }

    def print_current_context(self, k, context):
        if k == 0:
            print("\n=== Frequências de Ordem 0 (k=0) ===")
            print("Simb.   Cont.   Prob.")
            available_symbols = {s: c for s, c in self.k0_frequencies.items() 
                              if s not in self.excluded_symbols}
            total = sum(available_symbols.values())
            unique = len(available_symbols) + (self.k0_unique_symbols - len(self.excluded_symbols))
            
            if total + unique > 0:
                for symbol, count in sorted(available_symbols.items()):
                    prob = count / (total + unique)
                    print(f"{symbol:<7} {count:<7} {prob:.4f}")
                
                remaining_unseen = self.alphabet - self.seen_symbols - self.excluded_symbols
                if remaining_unseen or (len(self.seen_symbols) < len(self.alphabet) and not self.excluded_symbols):
                    prob_esc = unique / (total + unique)
                    print(f"esc     {unique:<7} {prob_esc:.4f}")
            else:
                print(f"esc     {unique:<7} 0.0000")
        else:
            if context in self.contexts[k]:
                print(f"\n=== Contexto de Ordem {k} (k={k}): '{context}' ===")
                print("Simb.   Cont.   Prob.")
                frequencies = self.contexts[k][context]['frequencies']
                unique_symbols = len(self.contexts[k][context]['symbols'])
                total = sum(frequencies.values())

                for symbol, count in sorted(frequencies.items()):
                    prob = count / (total + unique_symbols)
                    print(f"{symbol:<7} {count:<7} {prob:.4f}")
                prob_esc = unique_symbols / (total + unique_symbols)
                print(f"esc     {unique_symbols:<7} {prob_esc:.4f}")

    def process_symbol(self, symbol, history):
        print(f"\n--- Processando símbolo: '{symbol}' ---")
        print(f"Histórico atual: '{''.join(history)}'")
        
        prob_info = self._get_probability_with_details(symbol, history)
        
        print("\nPassos de codificação:")
        for step in prob_info['steps']:
            print(f"  {step}")
            # Mostra a tabela relevante para cada passo
            if "Ordem" in step and "contexto" in step:
                parts = step.split("'")
                if len(parts) >= 2:
                    context = parts[1]
                    k = int(step.split()[1][:-1])
                    self.print_current_context(k, context)
            elif "Ordem 0" in step:
                self.print_current_context(0, None)
        
        print(f"\nProbabilidade final: {prob_info['formula']} = {prob_info['prob']:.4f}")
        
        if prob_info['prob'] > 0:
            bits = -math.log2(prob_info['prob'])
            self.total_bits += bits
            self.total_symbols += 1
            print(f"Contribuição para entropia: {bits:.4f} bits")
        
        self.update(symbol, history)
        return symbol

    def print_final_stats(self):
        if self.total_symbols > 0:
            print("\n=== ESTATÍSTICAS FINAIS ===")
            print(f"Total de bits: {self.total_bits:.4f}")
            print(f"Entropia média: {self.total_bits/self.total_symbols:.4f} bits/símbolo")


if __name__ == "__main__":
    texto = "abracadabra"
    ordem = 2
    alfabeto = sorted(set(texto))

    modelo = PPMModel(alfabeto, ordem)
    historico = []

    print(f"=== Codificando texto: '{texto}' ===")
    for simbolo in texto:
        historico.append(modelo.process_symbol(simbolo, historico))
    
    modelo.print_final_stats()
