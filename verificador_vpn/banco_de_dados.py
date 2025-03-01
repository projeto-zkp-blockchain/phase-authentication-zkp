import mysql.connector

# Conectar ao banco de dados
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        #password="1234",
        database="tcc_zkp"
    )


# Função para criar o banco de dados, a tabela e inserir os dados iniciais
def inicializar_bd():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
        # password="1234"
    )
    try:
        with conexao.cursor() as cursor:
            # Criar banco de dados se não existir
            cursor.execute("CREATE DATABASE IF NOT EXISTS tcc_zkp")
            # Selecionar o banco de dados
            cursor.execute("USE tcc_zkp")
            
            # Verificar se a tabela usuario já existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'tcc_zkp' AND table_name = 'usuario'
            """)
            tabela_existe = cursor.fetchone()[0] > 0
            
            if not tabela_existe:
                # Criar tabela usuario
                sql_create_table = """
                CREATE TABLE usuario (
                    IDuser VARCHAR(300) PRIMARY KEY,
                    Quser_x VARCHAR(300),
                    Quser_y VARCHAR(300)
                )
                """
                cursor.execute(sql_create_table)
                print("Tabela 'usuario' criada com sucesso.")
                
                # Inserir dados iniciais
                sql_insert_usuarios = """
                INSERT INTO usuario (IDuser, Quser_x, Quser_y)
                VALUES (%s, %s, %s)
                """
                usuarios = [
                    ("41207561216977194318516402913523669168381596964654559210880595085498182487570", 
                     "72090262219443511039303502547527453758231356982829788985599462950765292300461", 
                     "38848789281679815859836621466958307971972939122034974023543399921937058804999"),
                    ("73462656479853684390593746330140932196836891974511709838144442585046840337136", 
                     "84304294948624029307622458425446942818794024746581059426490539640723920276685", 
                     "70259967970354414344264218957493196938939334440830887933707474755141229588440"),
                    ("77247943931852287773845246847057509871902814453172821881486024590990618618273", 
                     "107006254904108049494009817940083447348237170221735480961553733841068625362829", 
                     "62010255730677416943327643106320864859509547671615529985845651962083356106395"),
                    ("82060290871239600173345710650584367045742991382377050294254664527272852190899", 
                     "45614009712185681651678826924177396674781769231310356954025719047664580835571", 
                     "122055562683286077939143021247209161438263714638758026704364385122398086975")
                ]
                cursor.executemany(sql_insert_usuarios, usuarios)
                conexao.commit()
                print("Usuários iniciais inseridos com sucesso.")
            else:
                print("A tabela 'usuario' já existe. Nenhum dado foi inserido.")
                
    except mysql.connector.Error as erro:
        print(f"Erro ao inicializar o banco de dados ou tabela: {erro}")
    finally:
        conexao.close()

# Função para selecionar chave pública do usuário
def dadosUser(IDuser):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Comando SQL para selecionar Quser_x e Quser_y da tabela usuario
            sql_select = """
            SELECT Quser_x, Quser_y FROM usuario 
            WHERE IDuser = %s
            """
            cursor.execute(sql_select, (IDuser,))  # Passando IDuser como tupla
            resultado = cursor.fetchone()  # Obtendo o resultado da consulta
            if resultado:
                Quser_x, Quser_y = resultado
                print(f"Chave Pública do usuário {IDuser}: Quser_x = {Quser_x}, Quser_y = {Quser_y}.")
                return Quser_x, Quser_y  # Retornando os valores da chave pública
            else:
                print(f"Nenhum usuário encontrado com ID {IDuser}.")
                return None
    except mysql.connector.Error as erro:
        print(f"Erro ao obter dados do usuário: {erro}")
        return None
    finally:
        conexao.close()


# Inicializar o banco de dados e tabela
inicializar_bd()

#chave_publica = dadosUser(41207561216977194318516402913523669168381596964654559210880595085498182487570)

