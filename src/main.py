import os
from lexer import process_file, show_tokens, show_symbol_table, show_token_count

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
        print("\n===== SELEÇÃO DO ARQUIVO =====")
        print("1. Digitar o caminho completo do arquivo .tonto")
        print("2. Listar e escolher um arquivo .tonto da pasta examples")
        choice = input("Escolha uma opção (1/2): ").strip()

        if choice == '1':
            path = input("Digite o caminho do arquivo .tonto: ").strip().strip('"')
            if not os.path.isfile(path):
                print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
                continue
            return path
        elif choice == '2':
            files = list_example_tonto_files()
            if not files:
                print("Nenhum arquivo .tonto encontrado em 'examples'.")
                continue
            print("\nArquivos encontrados:")
            for idx, f in enumerate(files, start=1):
                rel = os.path.relpath(f, os.path.dirname(__file__))
                print(f"{idx}. {rel}")
            while True:
                sel = input("Digite o número do arquivo desejado: ").strip()
                if sel.isdigit():
                    i = int(sel)
                    if 1 <= i <= len(files):
                        return files[i-1]
                print("Seleção inválida. Tente novamente.")
        else:
            print("Opção inválida. Tente novamente.")

def menu_loop():
    while True:
        print("\n====== MENU DE OPÇÕES ======")
        print("1. Exibir Tokens Processados")
        print("2. Exibir Tabela de Símbolos")
        print("3. Exibir Contagem de Tokens")
        print("4. Analisar outro arquivo (.tonto)")
        print("5. Sair")
        choice = input("Escolha uma opção: ").strip()
        if choice == '1':
            show_tokens()
        elif choice == '2':
            show_symbol_table()
        elif choice == '3':
            show_token_count()
        elif choice == '4':
            new_path = choose_input_file()
            if process_file(new_path):
                print("Arquivo processado com sucesso. Você pode visualizar os dados com as opções 1-3.")
            else:
                print("Falha ao processar o arquivo selecionado.")
        elif choice == '5':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def main():
    file_path = choose_input_file()
    if process_file(file_path):
        menu_loop()
    else:
        print("Falha ao processar o arquivo. Encerrando.")

if __name__ == "__main__":
    main()
