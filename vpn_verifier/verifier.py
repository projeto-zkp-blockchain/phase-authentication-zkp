from flask import Flask, request, jsonify
import hashlib
import ecdsa
import json
from datetime import datetime
import os
import database
import time

app = Flask(__name__)

#-----------Funções para o procolo ZKP trabalhar com Curvas Elípticas------------------------------

# Definindo a curva secp256k1
curva = ecdsa.SECP256k1
G = curva.generator  # Ponto gerador da curva
p = curva.order  # Ordem da curva

# Calcula o hash SHA256 de strings concatenadas e retorna em inteiro
def H(*args):
    concatenated = "".join(args)
    hash_hex = hashlib.sha256(concatenated.encode('utf-8')).hexdigest()
    return int(hash_hex, 16)

# Função para calcular o IDuser
def calcula_IDuser(Quser):
    Quser_point = Quser.pubkey.point
    Quser_x = hex(Quser_point.x())
    Quser_y = hex(Quser_point.y())
    return H(str(Quser_x), str(Quser_y))

# Busca a chave pública do usuário no banco de dados pelo IDuser    
def carregar_chave_publica_DB(IDuser):
    Quser_x, Quser_y = database.dadosUser(IDuser)
    Quser_x_int = int(Quser_x)
    Quser_y_int = int(Quser_y)
    return Quser_x_int, Quser_y_int

# Calcula o desafio, σ1 = H(G||Quser||A1||IDuser)
def verificador_calcula_sigma(G, Quser_x, Quser_y, A1_x, A1_y, IDuser):

    A1_x_hex = hex(A1_x)
    A1_y_hex = hex(A1_y)
    G_x_hex = hex(G.x())
    G_y_hex = hex(G.y())
    Quser_x_hex = hex(Quser_x)
    Quser_y_hex = hex(Quser_y)
    IDuser_hex = hex(IDuser)

    """
    print("\nEntrada para calcular o Sigma:")
    print("A1_x:", A1_x_hex)
    print("A1_y:", A1_y_hex)
    print("G_x:", G_x_hex)
    print("G_y:", G_y_hex)
    print("Quser_x:", Quser_x_hex)
    print("Quser_y:", Quser_y_hex)
    print("IDuser:", IDuser_hex)
    """

    desafio_sigma = H(str(G_x_hex), str(G_y_hex), str(Quser_x_hex), str(Quser_y_hex), str(A1_x_hex), str(A1_y_hex), str(IDuser_hex))
    return desafio_sigma

# Calcula a resposta pi(π) pro desafio sigma(σ), tal que 
def verificador_verifica_resposta(resposta_pi, sigma, Quser, A1):
    Quser_point = Quser.pubkey.point
    operacao_1 = resposta_pi * G
    operacao_2 = sigma * Quser_point
    operacao_2_inverso = -operacao_2
    P1 = operacao_1 + operacao_2_inverso
    return 1 if P1 == A1 else 0


#-----------------Código Gerenciamento Arquivos Json Interações ------------------


# Diretório para salvar os arquivos
PASTA_INTERACOES = "interacoes"

# Certifique-se de que a pasta existe
if not os.path.exists(PASTA_INTERACOES):
    os.makedirs(PASTA_INTERACOES)

def iniciar_interacao(id_user, quser_x, quser_y, a_x, a_y, desafio_sigma):
    """
    Cria o arquivo JSON com as informações iniciais da autenticação.
    """
    # Substitui caracteres inválidos no nome do arquivo
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    id_user_resumido = str(id_user)[:10] # Reduz o hash a 10 caracteres
    nome_arquivo = f"{PASTA_INTERACOES}/autenticacao_{id_user_resumido}_{timestamp}.json"
    dados = {
        "IDuser": id_user,
        "Quser_x": quser_x,
        "Quser_y": quser_y,
        "rodadaAtual": {
            "numero": 1,
            "Ponto_A_x": a_x,
            "Ponto_A_y": a_y,
            "desafioSigma": desafio_sigma
        }
    }
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)
    return nome_arquivo

def obter_informacoes(nome_arquivo):
    """
    Retorna as informações do arquivo JSON.
    """
    with open(nome_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    return dados

def atualizar_rodada(nome_arquivo):
    """
    Atualiza os dados da rodada atual: incrementa o número da rodada e define os valores como None.
    """
    with open(nome_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    
    dados["rodadaAtual"]["numero"] += 1
    dados["rodadaAtual"]["Ponto_A_x"] = None
    dados["rodadaAtual"]["Ponto_A_y"] = None
    dados["rodadaAtual"]["desafioSigma"] = None
    
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)
    
    return True

def preencher_rodada(nome_arquivo, a_x, a_y, desafio_sigma):
    """
    Preenche os dados da rodada atual com os valores fornecidos.
    """
    with open(nome_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    
    dados["rodadaAtual"]["Ponto_A_x"] = a_x
    dados["rodadaAtual"]["Ponto_A_y"] = a_y
    dados["rodadaAtual"]["desafioSigma"] = desafio_sigma
    
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)
    
    return True

def apagar_arquivo(nome_arquivo):
    """
    Apaga o arquivo JSON especificado.
    """
    try:
        os.remove(nome_arquivo)
        print(f"Arquivo {nome_arquivo} removido com sucesso.")
        return True
    except FileNotFoundError:
        print(f"Arquivo {nome_arquivo} não encontrado.")
        return False
    except Exception as e:
        print(f"Erro ao tentar remover o arquivo {nome_arquivo}: {e}")
        return False


#------------- Rotas para Autenticações dos Usuários ------------------------------

def log_tempo(acao, inicio, fim):
    tempo_decorrido = fim - inicio
    print(f"Tempo de execução ({acao}): {tempo_decorrido:.4f} segundos")

@app.route('/')
def home():
    return jsonify(message="Bem-vindo a aplicacao!")

@app.route('/iniciar_interacao_rodadas', methods=['POST'])
def iniciarInteracao():
    inicioGeral = time.time()
    
    data = request.get_json()
    A1_x = data['A1_x']
    A1_y = data['A1_y']
    IDuser = data['IDuser']

    # Marcar tempo para carregar chave pública
    inicioDB = time.time()
    Quser_x, Quser_y = carregar_chave_publica_DB(IDuser)
    fimDB = time.time()
    log_tempo("Carregar chave pública DB", inicioDB, fimDB)

    # Marcar tempo para cálculo do sigma
    inicioSigma = time.time()
    sigma = verificador_calcula_sigma(G, Quser_x, Quser_y, A1_x, A1_y, IDuser)
    fimSigma = time.time()
    log_tempo("Calcular sigma", inicioSigma, fimSigma)

    # Salvar interação
    interacao = iniciar_interacao(IDuser, Quser_x, Quser_y, A1_x, A1_y, sigma)

    fimGeral = time.time()
    log_tempo("Iniciar interação geral", inicioGeral, fimGeral)

    sigma_str = str(sigma)
    return jsonify({'sigma': sigma_str, 'interacao': interacao})

@app.route('/multiplas_interacoes', methods=['POST'])
def verificar():

    inicioGeralM = time.time()

    # Recebe os dados da requisição
    inicioRecebimento = time.time()
    data = request.get_json()
    A_x = int(data['A_x'])
    A_y = int(data['A_y'])
    interacao = data['interacao']
    fimRecebimento = time.time()
    tempoRecebimento = fimRecebimento - inicioRecebimento
    print(f"Tempo para receber os dados: {tempoRecebimento:.2f} segundos")

    # Obtém informações do arquivo JSON
    inicioLeitura = time.time()
    infos = obter_informacoes(interacao)
    id_user = infos["IDuser"]
    Quser_x = infos["Quser_x"]
    Quser_y = infos["Quser_y"]
    fimLeitura = time.time()
    tempoLeitura = fimLeitura - inicioLeitura
    print(f"Tempo para leitura do arquivo JSON: {tempoLeitura:.2f} segundos")

    # Calcula o desafio sigma
    inicioSigma = time.time()
    sigma = verificador_calcula_sigma(G, Quser_x, Quser_y, A_x, A_y, id_user)
    fimSigma = time.time()
    tempoSigma = fimSigma - inicioSigma
    print(f"Tempo para calcular sigma: {tempoSigma:.2f} segundos")

    # Atualiza a rodada com os novos dados
    inicioAtualizacao = time.time()
    preencher_rodada(interacao, A_x, A_y, sigma)
    fimAtualizacao = time.time()
    tempoAtualizacao = fimAtualizacao - inicioAtualizacao
    print(f"Tempo para atualizar a rodada: {tempoAtualizacao:.2f} segundos")

    # Tempo total da execução
    fimGeralM = time.time()
    tempoGeralM = fimGeralM - inicioGeralM
    print(f"Tempo total da execução da rota /multiplas_interacoes: {tempoGeralM:.2f} segundos")
    
    return jsonify({'sigma': sigma})


@app.route('/verificar_resposta', methods=['POST'])
def verificar_resposta():
    inicioVerificar = time.time()

    data = request.get_json()
    resposta_pi = int(data['resposta_pi'])
    interacao = data['interacao']

    # Obter informações da interação
    inicioInfos = time.time()
    infos = obter_informacoes(interacao)
    fimInfos = time.time()
    log_tempo("Obter informações da interação", inicioInfos, fimInfos)

    # Reconstruir os objetos necessários
    ponto_A = ecdsa.ellipticcurve.Point(curva.curve, infos["rodadaAtual"]["Ponto_A_x"], infos["rodadaAtual"]["Ponto_A_y"])
    Quser_point = ecdsa.ellipticcurve.Point(curva.curve, infos["Quser_x"], infos["Quser_y"])
    Quser = ecdsa.VerifyingKey.from_public_point(Quser_point, curve=curva)

    # Verificar resposta
    inicioVerificacao = time.time()
    status = verificador_verifica_resposta(resposta_pi, infos["rodadaAtual"]["desafioSigma"], Quser, ponto_A)
    fimVerificacao = time.time()
    log_tempo("Verificar resposta", inicioVerificacao, fimVerificacao)

    # Atualizar rodada ou finalizar
    if status == 1:
        if infos["rodadaAtual"]["numero"] == 3:
            apagar_arquivo(interacao)
        else:
            atualizar_rodada(interacao)
    else:
        print("Falha na autenticação:", interacao)

    fimVerificar = time.time()
    log_tempo("Verificar resposta geral", inicioVerificar, fimVerificar)

    return jsonify({'status': status})


if __name__ == "__main__":
    #app.run(port=5000)
    app.run(host='0.0.0.0', port=5000)  # Modificado para rodar no Google Cloud ou Replit
