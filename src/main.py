import os
from lexer import process_file, show_tokens, show_symbol_table, show_token_count
from parser import parse_file, show_syntax_summary, show_syntax_errors

# Guardar último resultado de análise sintática
current_file = None
current_ast = None
current_summary = None
current_syntax_errors = None

def list_example_tonto_files():
    base_dir = os.path.join(os.path.dirname(__file__), 'examples')
    found = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if fname.lower().endswith('.tonto'):
                found.append(os.path.join(root, fname))
    return sorted(found)

def choose_input_file():
    while True:
        print("\n================= SELEÇÃO DO ARQUIVO =================")
        print("1. Digitar o caminho completo do arquivo .tonto")
        print("2. Listar e escolher um arquivo .tonto da pasta examples")
        choice = input("Escolha uma opção (1/2): ").strip()

        if choice == '1':
            path = input("\nDigite o caminho do arquivo .tonto: ").strip().strip('"')
            if not os.path.isfile(path):
                print("❌ Arquivo não encontrado. Verifique o caminho e tente novamente.")
                continue
            return path
        elif choice == '2':
            files = list_example_tonto_files()
            if not files:
                print("❌ Nenhum arquivo .tonto encontrado em 'examples'.")
                continue

            print("\nArquivos disponíveis:")
            for idx, f in enumerate(files, start=1):
                rel = os.path.relpath(f, os.path.dirname(__file__))
                print(f"{idx}. {rel}")
            try:
                opt = int(input("Escolha um arquivo pelo número: ").strip())
                if 1 <= opt <= len(files):
                    return files[opt - 1]
            except ValueError:
                pass
            print("❌ Opção inválida, tente novamente.")
        else:
            print("❌ Opção inválida. Tente novamente.")

def run_all_analyses(file_path):
    """Roda análise léxica e sintática para o arquivo."""
    global current_file, current_ast, current_summary, current_syntax_errors

    # análise léxica
    if not process_file(file_path):
        print("❌ Falha na análise léxica. Verifique o arquivo.")
        return False

    # análise sintática
    ast, summary, errors = parse_file(file_path)
    current_file = file_path
    current_ast = ast
    current_summary = summary
    current_syntax_errors = errors
    print("\n✅ Arquivo analisado com sucesso (léxico + sintático)!")
    return True

def menu_loop():
    while True:
        print("\n=========== MENU DE OPÇÕES ===========")
        print("1. Exibir Tokens Processados (léxico)")
        print("2. Exibir Tabela de Símbolos (léxico)")
        print("3. Exibir Contagem de Tokens (léxico)")
        print("4. Exibir Resumo Sintático")
        print("5. Exibir Erros Sintáticos")
        print("6. Analisar outro arquivo (.tonto)")
        print("7. Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == '1':
            show_tokens()
        elif choice == '2':
            show_symbol_table()
        elif choice == '3':
            show_token_count()
        elif choice == '4':
            if current_summary is None:
                print("❌ Nenhuma análise sintática realizada ainda.")
            else:
                show_syntax_summary(current_summary)
        elif choice == '5':
            if current_syntax_errors is None:
                print("❌Nenhuma análise sintática realizada ainda.")
            else:
                show_syntax_errors(current_syntax_errors)
        elif choice == '6':
            new_path = choose_input_file()
            if run_all_analyses(new_path):
                print("Novo arquivo analisado. Use as opções 1-5 para visualizar.")
        elif choice == '7':
            print("Saindo...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

def main():
    file_path = choose_input_file()
    if run_all_analyses(file_path):
        menu_loop()

if __name__ == "__main__":
    main()
