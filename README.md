# 1. Implementação do Protocolo *Zero Knowledge Protocol* (ZKP)

O código neste repositório refere-se à simulação do processo de autenticação utilizando o protocolo ZKP. No contexto apresentado, o Usuário (Cliente VPN) atua como *provador*, enquanto a VPN (Servidor VPN) desempenha o papel de *verificador*. O código implementa todas as funções e operações necessárias para a análise de desempenho e futuras implementações do protocolo em cenários do mundo real. 

O protocolo ZKP implementado utiliza o problema matemático de curvas elípticas. Nesse contexto, algumas notações matemáticas vêm dessa área, como operações com pontos de uma curva elíptica, além de operações como *hash*, módulo e multiplicações. Na imagem a seguir, é apresentada a execução do protocolo em três rodadas, que foi implementada no código.

<img src="https://github.com/user-attachments/assets/d74ed3c3-3319-4b84-9719-b3bed44b20c3" alt="Processo de autenticação do ZKP" width="90%">


# 2. Sobre a Implementação

A curva elíptica escolhida foi a **secp256k1**, amplamente conhecida por ser utilizada na criptomoeda Bitcoin, e é considerada segura. Outro motivo para sua escolha é o fato de ser amplamente reconhecida, com inúmeras bibliotecas disponíveis em praticamente todas as linguagens de programação, o que pode ser interessante para implementações em outros cenários e linguagens.

## 2.1 Instalação Pacotes

- Primeiramente, deve-se ter o Python instalado.
- As bibliotecas necessárias para a instalação do provador (Pasta **provador_user**) são: `threading`, `requests`, `ecdsa`, `random`, `os`, `json` e `time`. Para isso, basta executar:

`pip install threading requests ecdsa random os json time`

- As bibliotecas necessárias para a instalação do verificador (Pasta **verificador_vpn**) são: `Flask`, `hashlib`, `ecdsa`, `json`, `datetime` e `os`. Para isso, basta executar:

`pip install Flask hashlib ecdsa json datetime os`

- A versão anterior instala todas as bibliotecas de uma vez. Entretanto, vale destacar que algumas bibliotecas fazem parte dos pacotes padrões do Python. Logo, recomendo que seja instalado apenas as bibliotecas que o compilador indicar, ou seja, apenas execute o comando `pip install nome_biblioteca` para as bibliotecas faltantes indicadas pelo compilador.

## 2.2 Instalação Banco de Dados

- Deve-se ter o banco de dados MySQL instalado. Recomendo o uso do [phpMyAdmin](https://www.phpmyadmin.net/), que foi o utilizado no projeto.
- O código deste repositório foi configurado para gerar o banco, tabelas e inserir alguns usuários automaticamente no banco de dados. O usuário configurado no código é `root` e a senha também é `root`. Caso o seu banco de dados utilize credenciais diferentes, basta alterar as informações de login no arquivo Python: `verificador_vpn/banco_de_dados.py`.

### Sobre o phpMyAdmin

- Foram realizados testes tanto de forma local quanto em uma máquina virtual com Ubuntu 20.04 LTS na Google Cloud. Caso deseje realizar algo semelhante, consulte o [Tutorial de Instalação do phpMyAdmin no Ubuntu 20.04 LTS](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-20-04-pt).

## 2.3 Sobre a Máquina Virtual na Google Cloud

- A máquina virtual utilizada no projeto é a Ubuntu 20.04 LTS. Para aprender como configurá-la, veja este [Tutorial de Instalação](https://youtu.be/MiiexH6Ik4w?si=FD8r5FHKlO09JGiZ).
- É importante habilitar o *firewall* para permitir o acesso externo à VM. Nesse caso, deve-se habilitar a porta 5000, que é utilizada pelo Flask por padrão. Veja como fazer isso neste [Tutorial sobre como Habilitar a Porta](https://www.youtube.com/watch?v=8NR2q9y9uBo).


## 2.4 Como Executar o código

### Verificador

- Na pasta `verificador_vpn` execute `python verificador.py` para Windows ou `python3 verificador.py` para linux, com isso o servidor já vai estar rodando na porta 5000.

### Provador
- Na pasta `provador_user` execute `python provador.py` para Windows ou `python3 provador.py` para linux, será iniciado o processo de autenticação.

# 3. Considerações Finais

- O protocolo implementado está funcionando conforme especificado. Em uma análise inicial, executando na Google Cloud nos Estados Unidos, o tempo médio para autenticar o usuário é de aproximadamente 2,26 segundos. Quando executado localmente, esse tempo reduz para cerca de 0,075 segundos, demonstrando que o protocolo é bastante eficiente. A maior parte da demora na autenticação ocorre devido à latência de rede.

- O código também inclui funções para testar múltiplos usuários simultaneamente utilizando *threads* do Python, gerar arquivos com os tempos de execução, além de calcular médias das execuções. Essas funcionalidades facilitam análises de desempenho e escalabilidade do protocolo.
