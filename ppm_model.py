import math

class PPMModel:
    def __init__(self, alphabet, order):
        self.order = order
        self.contexts = {k: {} for k in range(1, order + 1)}  # {k: {contexto: {símbolo: contagem}}}
        self.k0_frequencies = {}  # {símbolo: contagem}
        self.alphabet = set(alphabet)
        self.seen_symbols = set()
        self.k0_unique_symbols = 0  # Conta símbolos únicos para k=0

    def update(self, symbol, history):
        # Atualiza k=-1
        if symbol not in self.seen_symbols:
            self.seen_symbols.add(symbol)
            self.k0_unique_symbols += 1  # Incrementa contador de símbolos únicos

        # Atualiza k=0
        if symbol not in self.k0_frequencies:
            self.k0_frequencies[symbol] = 0
        self.k0_frequencies[symbol] += 1

        # Atualiza k=1, k=2, ..., k=order
        for k in range(1, self.order + 1):
            if len(history) >= k:
                context = "".join(history[-k:])  # Contexto de tamanho k
                if context not in self.contexts[k]:
                    self.contexts[k][context] = {'symbols': set(), 'frequencies': {}}

                if symbol not in self.contexts[k][context]['symbols']:
                    self.contexts[k][context]['symbols'].add(symbol)

                if symbol not in self.contexts[k][context]['frequencies']:
                    self.contexts[k][context]['frequencies'][symbol] = 0
                self.contexts[k][context]['frequencies'][symbol] += 1

    def get_context_data(self, history):
        context_data = {}
        for k in range(self.order, 0, -1):
            if len(history) >= k:
                context = "".join(history[-k:])
                if context in self.contexts[k]:
                    context_data['context'] = context
                    context_data['symbols'] = self.contexts[k][context]['frequencies']
                    return context_data
        return None  # Retorna None se não encontrar contexto

    def calculate_message_entropy(self, full_history):
        """Calcula entropia mostrando o cálculo passo a passo"""
        total_bits = 0.0
        history = []
        
        print("\n=== CÁLCULO DE ENTROPIA PASSO-A-PASSO ===")
        print(f"Alfabeto: {', '.join(sorted(self.alphabet))}\n")
        
        for i, symbol in enumerate(full_history):
            # Calcula ANTES de atualizar o modelo
            prob_detail = self._get_probability_with_details(symbol, history)
            prob = prob_detail['prob']
            bits = -math.log2(prob) if prob > 0 else 0
            
            # Atualiza modelo
            self.update(symbol, history)
            history.append(symbol)
            
            # Exibe o cálculo
            print(f"Passo {i+1}: '{symbol}'")
            print(f"Contexto atual: '{''.join(history[-self.order:])}'")
            
            for step in prob_detail['steps']:
                print(f"• {step}")
            
            print(f"= P('{symbol}') = {prob_detail['formula']} = {prob:.4f}")
            print(f"Contribuição: {bits:.4f} bits\n")
            
            total_bits += bits
        
        avg_entropy = total_bits / len(full_history) if full_history else 0
        print(f"ENTROPIA TOTAL: {total_bits:.4f} bits")
        print(f"MÉDIA: {avg_entropy:.4f} bits/símbolo")
        return avg_entropy

    def _get_probability_with_details(self, symbol, history):
        """Versão final corrigida com exclusão apropriada e reset de exclusões"""
        result = {
            'prob': 1.0,
            'steps': [],
            'formula_parts': []
        }
        
        current_unseen = self.alphabet - self.seen_symbols
        excluded_symbols = set()  # Reinicia a cada símbolo novo
        
        # Primeiro verifica se o símbolo já foi visto em algum contexto
        for k in range(min(self.order, len(history)), -1, -1):
            context = "".join(history[-k:]) if k > 0 else ""
            
            # Obtém os dados do contexto atual
            if k > 0:
                ctx_data = self.contexts[k].get(context, {'symbols': set(), 'frequencies': {}})
                current_symbols = ctx_data['symbols']
                freqs = ctx_data['frequencies'].copy()
            else:
                current_symbols = set(self.k0_frequencies.keys())
                freqs = self.k0_frequencies.copy()
            
            # Calcula unique symbols (não incluindo os excluídos)
            available_symbols = current_symbols - excluded_symbols
            unique = len(available_symbols)
            
            # Filtra frequências para remover símbolos excluídos
            freqs = {s: f for s, f in freqs.items() if s in available_symbols}
            total = sum(freqs.values())
            
            # Se encontrou o símbolo no contexto atual (após exclusão)
            if symbol in freqs:
                prob = freqs[symbol] / (total + unique)
                result['prob'] *= prob
                excl_msg = f" (excluídos: {', '.join(sorted(excluded_symbols))}" if excluded_symbols else ""
                result['steps'].append(f"Ordem {k} ('{context}'): P('{symbol}') = {freqs[symbol]}/({total}+{unique}){excl_msg}")
                result['formula_parts'].append(f"{freqs[symbol]}/{total+unique}")
                break
                
            # Se não encontrou, calcula escape e atualiza símbolos excluídos
            else:
                # Apenas adiciona os símbolos DESTE contexto aos excluídos
                excluded_symbols.update(current_symbols)
                
                # Se não há símbolos disponíveis, escape automático
                if unique == 0:
                    result['prob'] *= 1.0
                    result['steps'].append(f"Ordem {k} ('{context}'): Escape automático (nenhum símbolo disponível)")
                    result['formula_parts'].append("1")
                else:
                    esc_prob = unique / (total + unique)
                    result['prob'] *= esc_prob
                    excl_msg = f" (excluídos: {', '.join(sorted(excluded_symbols))}" if excluded_symbols else ""
                    result['steps'].append(f"Ordem {k} ('{context}'): P(escape) = {unique}/({total}+{unique}){excl_msg}")
                    result['formula_parts'].append(f"{unique}/{total+unique}")
        
        # Se não encontrou em nenhuma ordem, verifica ordem -1
        else:
            if symbol in current_unseen:
                available_symbols = current_unseen - excluded_symbols
                if available_symbols:
                    prob = 1.0 / len(available_symbols)
                    result['prob'] *= prob
                    excl_msg = f" (excluídos: {', '.join(sorted(excluded_symbols))}" if excluded_symbols else ""
                    result['steps'].append(f"Ordem -1: P('{symbol}') = 1/{len(available_symbols)}{excl_msg}")
                    result['formula_parts'].append(f"1/{len(available_symbols)}")
                else:
                    result['prob'] = 0.0
                    result['steps'].append("Erro: Nenhum símbolo disponível após exclusão")
            else:
                result['prob'] = 0.0
                result['steps'].append("Erro: Símbolo deveria ter sido encontrado em algum contexto")
        
        result['formula'] = " * ".join(result['formula_parts']) if result['formula_parts'] else "0"
        return result

    def print_tables(self, history):
        context_data = self.get_context_data(history)

        # Imprime tabelas k=order, k=order-1, ..., k=1
        for k in range(self.order, 0, -1):
            print(f"\n=== Contextos de Ordem {k} (k={k}) ===")
            print("Contexto   Simb.   Cont.   Prob.")
            for context in sorted(self.contexts[k].keys()):
                frequencies = self.contexts[k][context]['frequencies']
                unique_symbols = len(self.contexts[k][context]['symbols'])
                total = sum(frequencies.values())

                for symbol, count in sorted(frequencies.items()):
                    prob = count / (total + unique_symbols)
                    print(f"{context:<10} {symbol:<6} {count:<6} {prob:.4f}")
                print(f"{context:<10} esc    {unique_symbols:<6} {unique_symbols / (total + unique_symbols):.4f}")
                print("-" * 35)  # Linha de separação

        # Imprime tabela k=0
        print("\n=== Frequências de Ordem 0 (k=0) ===")
        print("Simb.   Cont.   Prob.")
        total = sum(self.k0_frequencies.values())
        if total + self.k0_unique_symbols > 0:
            for symbol, count in sorted(self.k0_frequencies.items()):
                prob = count / (total + self.k0_unique_symbols)
                print(f"{symbol:<6} {count:<6} {prob:.4f}")
            # Verifica se todos os símbolos foram vistos
            if len(self.seen_symbols) < len(self.alphabet):  # Apenas exibe 'esc' se nem todos os símbolos foram vistos
                print(f"esc    {self.k0_unique_symbols:<6} {self.k0_unique_symbols / (total + self.k0_unique_symbols):.4f}")
        else:
            print(f"esc    {self.k0_unique_symbols:<6} 0.0000")

        # Imprime tabela k=-1
        print("\n=== Símbolos Não Vistos (k=-1) ===")
        print("Simb.   Prob.")
        unseen = self.alphabet - self.seen_symbols
        if unseen:
            prob = 1.0 / len(unseen)
            for symbol in sorted(unseen):
                print(f"{symbol:<6} {prob:.4f}")
        else:
            print("(Todos os símbolos já foram vistos)")

        return context_data

    def save_model(self, filename):
        """Salva o modelo PPM em um arquivo"""
        with open(filename, 'w') as f:
            # Salva informações básicas
            f.write(f"ALPHABET: {','.join(sorted(self.alphabet))}\n")
            f.write(f"ORDER: {self.order}\n")
            f.write(f"SEEN_SYMBOLS: {','.join(sorted(self.seen_symbols))}\n")
            f.write(f"K0_UNIQUE_SYMBOLS: {self.k0_unique_symbols}\n")
            
            # Salva as frequências de ordem 0
            f.write("\n=== K0_FREQUENCIES ===\n")
            for symbol, count in sorted(self.k0_frequencies.items()):
                f.write(f"{symbol}:{count}\n")
            
            # Salva os contextos de ordens superiores
            for k in range(1, self.order + 1):
                f.write(f"\n=== K{k}_CONTEXTS ===\n")
                for context, data in sorted(self.contexts[k].items()):
                    f.write(f"CONTEXT:{context}\n")
                    for symbol, count in sorted(data['frequencies'].items()):
                        f.write(f"{symbol}:{count}\n")
                    f.write("END_CONTEXT\n")
        
        print(f"Modelo PPM salvo em {filename}")

    @classmethod
    def load_model(cls, filename):
        """Carrega um modelo PPM de um arquivo"""
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Processa informações básicas
        alphabet = set()
        order = 0
        seen_symbols = set()
        k0_unique_symbols = 0
        k0_frequencies = {}
        contexts = {}
        
        current_section = None
        current_context = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("ALPHABET:"):
                alphabet = set(line.split(':')[1].split(','))
            elif line.startswith("ORDER:"):
                order = int(line.split(':')[1])
                contexts = {k: {} for k in range(1, order + 1)}
            elif line.startswith("SEEN_SYMBOLS:"):
                seen_symbols = set(line.split(':')[1].split(',')) if line.split(':')[1] else set()
            elif line.startswith("K0_UNIQUE_SYMBOLS:"):
                k0_unique_symbols = int(line.split(':')[1])
            elif line.startswith("=== K0_FREQUENCIES ==="):
                current_section = 'k0_frequencies'
            elif line.startswith("=== K") and line.endswith("_CONTEXTS ==="):
                current_section = f"k{line.split('K')[1].split('_')[0]}_contexts"
            elif current_section == 'k0_frequencies':
                if ':' in line:
                    symbol, count = line.split(':')
                    k0_frequencies[symbol] = int(count)
            elif current_section and current_section.startswith('k') and current_section.endswith('_contexts'):
                k = int(current_section[1:].split('_')[0])
                if line.startswith("CONTEXT:"):
                    context = line.split(':')[1]
                    current_context = context
                    contexts[k][context] = {'symbols': set(), 'frequencies': {}}
                elif line == "END_CONTEXT":
                    current_context = None
                elif current_context and ':' in line:
                    symbol, count = line.split(':')
                    contexts[k][current_context]['frequencies'][symbol] = int(count)
                    contexts[k][current_context]['symbols'].add(symbol)
        
        # Cria a instância do modelo
        model = cls(alphabet, order)
        model.seen_symbols = seen_symbols
        model.k0_unique_symbols = k0_unique_symbols
        model.k0_frequencies = k0_frequencies
        model.contexts = contexts
        
        print(f"Modelo PPM carregado de {filename}")
        return model