import sqlite3
from sqlite3 import Error

# Função para criar a conexão com o banco de dados


def create_connection():
    conn = None
    try:
        # Cria ou abre o arquivo do banco de dados
        conn = sqlite3.connect('users.db')
        return conn
    except Error as e:
        print(e)
    return conn

# Função para criar a tabela de usuários


def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
    except Error as e:
        print(e)

# Função para inserir um novo usuário


def insert_user(conn, username, password):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password) VALUES (?, ?)
        ''', (username, password))
        conn.commit()
    except Error as e:
        print(e)

# Função para verificar as credenciais do usuário


def check_user(conn, username, password):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        user = cursor.fetchone()
        return user is not None
    except Error as e:
        print(e)
    return False

# Inicialização do banco de dados e criação da tabela


def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        # Inserir um usuário padrão (opcional)
        insert_user(conn, 'admin', 'renova2025')
        insert_user(conn, 'Edword', 'renova2025')
    else:
        print("Erro ao conectar ao banco de dados.")
    conn.close()
