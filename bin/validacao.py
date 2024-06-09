import json
import re

def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_json(path: str) -> str:
    produto_str = read_file(path)   
    return json.loads(produto_str)

# s = contar sucesso | n = contar sem estoque
def count_regex_matches(id: str, mode: str, content: str) -> int:
    
    test_rex = f"\[{id:02d}\].+\(\w+:.sucesso\)"
    if mode == "n":
        test_rex = f"\[{id:02d}\].+\(\w+:.erro_sem_estoque\)"
    
    matches = re.findall(test_rex, content)
    return len(matches)

if __name__ == "__main__":
    produtos_json = read_json("./database/produtos.json")
    extrato_str   = read_file("./database/extrato.txt")
    
    for prod in produtos_json:
        #produtos.json
        prod_id = int(prod["id"])
        estoque_count = int(prod["estoque"])
        #extrato.txt
        success_extrato_count = int(count_regex_matches(prod_id, "s", extrato_str))
        fail_extrato_count = 0 #int(count_regex_matches(prod_id, "n", extrato_str))
        total_extract = success_extrato_count + fail_extrato_count
        
        #print 
        print(f'ID: {prod["id"]} | ESTOQUE: {estoque_count} | EXTRATO: {total_extract} | TOTAL: {total_extract + estoque_count}')