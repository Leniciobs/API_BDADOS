from flask import Flask, jsonify, request, abort
import sqlite3

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('bauru_participa.db')
    return conn

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enquetes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opcoes_enquete (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquete_id INTEGER,
            opcao TEXT NOT NULL,
            votos INTEGER DEFAULT 0,
            FOREIGN KEY (enquete_id) REFERENCES enquetes(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/enquetes', methods=['POST'])
def criar_enquete():
    data = request.get_json()
    titulo = data.get('titulo')
    descricao = data.get('descricao')
    if not titulo or not descricao:
        abort(400, 'Titulo e descricao sao obrigatórios')
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO enquetes (titulo, descricao) VALUES (?, ?)', (titulo, descricao))
    enquete_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': 'Enquete criada com sucesso', 'enquete_id': enquete_id}), 201

@app.route('/api/enquetes', methods=['GET'])
def listar_enquetes():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo, descricao FROM enquetes')
    enquetes = cursor.fetchall()
    conn.close()
    return jsonify({'enquetes': enquetes})

@app.route('/api/enquetes/<int:id>', methods=['GET'])
def detalhes_enquete(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo, descricao FROM enquetes WHERE id=?', (id,))
    enquete = cursor.fetchone()
    if not enquete:
        abort(404, 'Enquete nao encontrada')
    
    cursor.execute('SELECT id, opcao, votos FROM opcoes_enquete WHERE enquete_id=?', (id,))
    opcoes = cursor.fetchall()
    conn.close()
    return jsonify({'enquete': enquete, 'opcoes': opcoes})

if __name__ == '__main__':
    app.run(debug=True)
