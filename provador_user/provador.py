import threading
import requests
import ecdsa
import random
import os
import json
import time

# Definindo a curva secp256k1
curva = ecdsa.SECP256k1
G = curva.generator  # Ponto gerador da curva
p = curva.order  # Ordem da curva

# Lock para evitar condições de corrida ao salvar no arquivo JSON
lock = threading.Lock()

# Função para salvar tempos detalhados no final do arquivo JSON
def salvar_tempo_em_json(tempos_execucao, arquivo_json="tempo_autenticacao.json"):

    with lock:
        # Verifica se o arquivo já existe
        if os.path.exists(arquivo_json):
            # Carrega os dados existentes
            with open(arquivo_json, "r") as arquivo:
                dados = json.load(arquivo)
        else:
            # Cria uma nova lista caso o arquivo não exista
            dados = []

        # Adiciona o novo registro de tempos à lista
        dados.append({"tempo_execucao_segundos": tempos_execucao})

        # Salva a lista atualizada no arquivo
        with open(arquivo_json, "w") as arquivo:
            json.dump(dados, arquivo, indent=4)
        print(f"Novo registro de tempos de execução adicionado a '{arquivo_json}'.")

# Função para carregar as chaves e o IDuser de um arquivo JSON
def carregar_chaves(arquivo):
    if not os.path.exists(arquivo):
        raise FileNotFoundError(f"O arquivo {arquivo} não foi encontrado.")

    with open(arquivo, 'r') as f:
        dados = json.load(f)
        
        # Carregar os dados do JSON
        IDuser = dados["IDuser"]
        Kuser_hex = dados["Kuser"]
        Quser_x = dados["Quser"]["x"]
        Quser_y = dados["Quser"]["y"]

        # Converter a chave privada de hexadecimal para o formato necessário
        Kuser = ecdsa.SigningKey.from_string(bytes.fromhex(Kuser_hex), curve=curva)
        Quser = Kuser.get_verifying_key()  # Obtenha a chave pública a partir da chave privada

        # Para debug, caso necessário
        print("IDuser:", Kuser_hex)
        print("Chaves carregadas:")
        print("Kuser (Chave Privada):", Kuser_hex)
        print("Quser_x (Chave Pública x):", Quser_x)
        print("Quser_y (Chave Pública y):", Quser_y, "\n")
        
    return IDuser, Kuser, Quser

# Função para o provador calcular o ponto compartilhado A
def provador_calcula_ponto_A(G, p):
    v = random.randint(1, p-1)
    A = v * G
    return A, v

# --- Provador responde ao desafio ---
def provador_responde(v, desafio_sigma, Kuser):
    kuser_int = int.from_bytes(Kuser.to_string(), byteorder='big')
    resposta_pi = (v + desafio_sigma * kuser_int) % p  # π1 = v1 + σ1 * Kuser (mod p)
    print("\nResposta (π):", resposta_pi, "\n")
    return resposta_pi

def provador():
    try:
        # Carrega as chaves e IDuser do provador
        IDuser, Kuser, Quser = carregar_chaves('chaves.json')

        tempos_por_etapa = {}  # Dicionário para armazenar os tempos de cada etapa e o tempo total
        
        # URL de onde vai estar o servidor VPN. Se estiver na Google Cloud, trocar "127.0.0.1:5000" pelo endereço público da VM.
        ip_server_vpn = "https://34.123.77.94:5000"

        #URL do inicio das interações com o verificador
        inicio_interacao_url = f"{ip_server_vpn}/iniciar_interacao_rodadas"

        inicio_tempo_total = time.time() #Marca o inicio do tempo que total para as três rodadas
        
        # Provador calcula A1 e envia para o verificador
        inicio_etapa = time.time()
        A1, v1 = provador_calcula_ponto_A(G, p)
        tempos_por_etapa['calculo_A1'] = time.time() - inicio_etapa  # Verificação do tempo por etapa, essa é de calcular A1.

        data = {
            'A1_x': A1.x(),
            'A1_y': A1.y(),
            'IDuser': IDuser,
        }

        # Faz a requisição POST para o verificador
        inicio_etapa = time.time()
        response = requests.post(inicio_interacao_url, json=data, verify=False)
        tempos_por_etapa['envio_A1_resposta_sigma1'] = time.time() - inicio_etapa # Tempo para enviar A1 e receber o desafio.
        if response.status_code == 200:
            inicio_etapa = time.time()
            sigma = int(response.json()['sigma'])
            interacao = response.json()['interacao']
            print("Sigma recebido do verificador:", sigma)
            print("Codigo interacao recebido do verificador:", interacao)
            tempos_por_etapa['pegando_sigma1_json'] = time.time() - inicio_etapa # Tempo para retirar do json sigma (desafio) e o código da interação

            # Provador responde ao desafio sigma
            inicio_etapa = time.time()
            resposta_pi = provador_responde(v1, sigma, Kuser)
            tempos_por_etapa['calculo_resposta_rodada_1'] = time.time() - inicio_etapa # Tempo para calcular a resposta
            
            # Enviar resposta ao verificador
            inicio_etapa = time.time()
            verify_url = f"{ip_server_vpn}/verificar_resposta"
            response = requests.post(verify_url, json={'resposta_pi': resposta_pi, 'interacao': interacao}, verify=False)
            
            tempos_por_etapa['envio_resposta_rodada_1'] = time.time() - inicio_etapa # Tempo para enviar a reposta e ter o retorno se está certa ou não

            if response.json().get('status') == 1:
                print("Autenticação bem-sucedida na Primeira Rodada!")
                multiplas_rodadas_url = f"{ip_server_vpn}/multiplas_interacoes"

                for i in range(2):
                    inicio_etapa = time.time()
                    A, v = provador_calcula_ponto_A(G, p)
                    tempos_por_etapa[f'calculo_A{i+2}'] = time.time() - inicio_etapa

                    data = {
                        'A_x': A.x(),
                        'A_y': A.y(),
                        'interacao': interacao,
                    }

                    inicio_etapa = time.time()
                    response = requests.post(multiplas_rodadas_url, json=data, verify=False)
                    tempos_por_etapa[f'envio_A{i+2}_resposta_sigma{i+2}'] = time.time() - inicio_etapa

                    inicio_etapa = time.time()
                    sigma = response.json()['sigma']
                    resposta_pi = provador_responde(v, sigma, Kuser)
                    tempos_por_etapa[f'calculo_resposta_rodada_{i+2}'] = time.time() - inicio_etapa

                    inicio_etapa = time.time()
                    response = requests.post(verify_url, json={'resposta_pi': resposta_pi, 'interacao': interacao}, verify=False)
                    tempos_por_etapa[f'envio_resposta_rodada_{i+2}'] = time.time() - inicio_etapa

                    if response.json().get('status') == 1:
                        print("Autenticação bem-sucedida na Rodada ", i + 2)
                    elif response.json().get('status') == 0:
                        print("Falha na Autenticação:", response.json().get('status'))
                        break
                    else:
                        print("Falha na autenticação!")

                if response.json().get('status') == 1:
                    print("Usuário autenticado com sucesso, passou pelas três rodadas!")
                else:
                    print("Falha na autenticação!")
        
        tempos_por_etapa['tempo_total'] = time.time() - inicio_tempo_total
        # Salva os tempos no JSON
        salvar_tempo_em_json(tempos_por_etapa)

    except Exception as e:
        print("Erro no provador:", e)


# Simula um execução com múltiplos usuários usando threads
def executar_provador_multiplos_usuarios(quantidade_usuarios):
    threads = []
    for i in range(quantidade_usuarios):
        thread = threading.Thread(target=provador)
        threads.append(thread)
        thread.start()
    # Aguarda todas as threads concluírem
    for thread in threads:
        thread.join()

# Calcula a média do tempo de um arquivo json com os tempos
def calcular_media_tempo_total_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    
    tempos_totais = [
        item["tempo_execucao_segundos"]["tempo_total"] for item in dados
    ]
    return sum(tempos_totais) / len(tempos_totais)


# -------------Exemplo de Uso------------
if __name__ == "__main__":

    # Chamada da função provador
    provador()

    # Algumas Observações
    """
    OBS 1:
    Sempre que a função "provador()" é executada, o tempo de cada operação e o total do ZKP são registrados
    pela função "salvar_tempo_em_json". Isso gera um arquivo chamado "tempo_autenticacao.json".
    Caso queira um nome diferente, basta trocar.

    OBS 2:
    Caso queira simular múltiplos usuários, use a função "executar_provador_multiplos_usuarios(10)".
    O número "10" pode ser alterado conforme necessário.
    Lembre-se de que o tempo também será registrado pela função "salvar_tempo_em_json".
    Nesse caso, pode ser interessante trocar o nome do arquivo, por exemplo para "theds_10.json",
    para analisar o desempenho com múltiplos usuários.

    OBS 3:
    Com o arquivo de tempo gerado, você pode usar a função:
    calcular_media_tempo_total_arquivo("theds_10.json")
    para calcular a média total do tempo registrado.
    """
