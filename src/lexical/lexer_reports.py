# ====== Exibir os tokens processados ====== 
def show_tokens(processed_tokens, error_tokens):
    print("\n===================== TOKENS PROCESSADOS =======================")
    header = f"{'Token':<20} {'Valor':<28} {'Linha':<6} {'Posição':<5}"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for token in processed_tokens:
        print(f"{token.type:<20} {str(token.value):<30} {token.lineno:<6} {token.lexpos:<6}")

    if error_tokens:
        header = f"{'Token':<20} {'Valor':<28} {'Linha':<6} {'Posição':<5}"
        print("\n======================= ERROS LÉXICOS ==========================")
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        for error in error_tokens:
            print(f"{error['Token']:<20} {error['Valor']:<30} {error['Linha']:<6} {error['Posição']:<5}")

# ====== Exibir a tabela de símbolos ====== 
def show_symbol_table(symbol_table):
    print("\n================== TABELA DE SÍMBOLOS ==================")
    print("-" * 55)
    print(f"{'Token':<20} {'Valor':<30}")
    print("-" * 55)
    for entry in symbol_table:
        print(f"{entry['Token']:<20} {entry['Valor']:<30}")

# ====== Exibir a contagem de tokens ====== 
def show_token_count(processed_tokens):
    counts = {}
    for token in processed_tokens:
        counts[token.type] = counts.get(token.type, 0) + 1
    
    print("\n======== CONTAGEM DE TOKENS =======")
    print("-" * 35)
    print(f"{'Token':<20} {'Quantidade':<10}")
    print("-" * 35)

    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    
    for token, count in sorted_counts:
        if count > 0:
            print(f"{token:<20} {count:<10}")