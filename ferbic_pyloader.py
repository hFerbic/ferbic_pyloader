from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import subprocess
import threading
import os
import json
import psutil  # Certifique-se de que o psutil está instalado

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Defina uma chave secreta para a sessão

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Diretório onde os arquivos .py e ícones serão salvos
UPLOAD_FOLDER = './uploaded_scripts/'
ICON_FOLDER = './icons/'
USER_DATA_FILE = 'users.json'  # Armazenar dados de usuário
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ICON_FOLDER'] = ICON_FOLDER

# Certifique-se de que os diretórios de upload existem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(ICON_FOLDER):
    os.makedirs(ICON_FOLDER)

# Função para garantir que o arquivo users.json exista e seja válido
def load_users():
    # Verifica se o arquivo é um diretório por acidente e o remove
    if os.path.isdir(USER_DATA_FILE):
        os.rmdir(USER_DATA_FILE)
        
    # Se o arquivo não existir, cria um arquivo JSON vazio
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w') as f:
            json.dump({}, f)

    # Carrega os usuários do arquivo, se não estiver vazio
    with open(USER_DATA_FILE, 'r') as f:
        try:
            return json.load(f) or {}
        except json.JSONDecodeError:
            # Retorna um dicionário vazio se o arquivo estiver vazio ou corrompido
            return {}

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

users = load_users()

scripts = {}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

# Verificação se não há usuários, redirecionar para a criação do primeiro
@app.before_request
def check_first_user():
    if len(users) == 0 and request.endpoint not in ['setup', 'static']:
        return redirect(url_for('setup'))

# Página de configuração do primeiro administrador
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if users:  # Se já houver usuários, redireciona para o login
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users[username] = {'password': password}
        save_users(users)
        return redirect(url_for('login'))
    
    return render_template('setup.html')

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if not users:  # Se não há usuários, redireciona para a configuração
        return redirect(url_for('setup'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return 'Credenciais inválidas!'
    
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rota principal protegida
@app.route('/')
@login_required
def index():
    return render_template('index.html', scripts=scripts)

# Servir ícones da pasta de ícones
@app.route('/icons/<filename>')
def get_icon(filename):
    return send_from_directory(app.config['ICON_FOLDER'], filename)

@app.route('/upload', methods=['POST'])
@login_required
def upload_script():
    # Verifica se o arquivo foi enviado
    if 'script_file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado."}), 400

    file = request.files['script_file']
    script_name = request.form['script_name']  # Nome fantasia
    real_filename = file.filename  # Nome real do arquivo
    icon = request.files.get('script_icon')

    # Verifica se o arquivo tem a extensão .py
    if real_filename == '' or not real_filename.endswith('.py'):
        return jsonify({"error": "Arquivo inválido. Apenas arquivos .py são permitidos."}), 400

    # Salva o arquivo .py
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], real_filename)
    file.save(filepath)

    # Se o ícone for enviado, salve-o
    icon_path = None
    if icon and icon.filename != '':
        icon_path = icon.filename  # Salva apenas o nome do arquivo
        icon.save(os.path.join(app.config['ICON_FOLDER'], icon_path))

    # Armazena tanto o nome fantasia quanto o nome real do arquivo
    scripts[script_name] = {'path': filepath, 'real_name': real_filename, 'process': None, 'icon': icon_path, 'pid': None}
    save_scripts()

    return jsonify({"message": f"Script {script_name} carregado com sucesso!"})

@app.route('/start', methods=['POST'])
@login_required
def start_script():
    script_name = request.form['script_name']
    script_data = scripts.get(script_name)
    if script_data and not script_data['process']:
        script_thread = threading.Thread(target=run_script, args=(script_data['path'], script_name))
        script_thread.start()
        return jsonify({"message": f"Script {script_name} iniciado com sucesso!"})
    else:
        return jsonify({"error": "Script já está em execução ou não foi encontrado."}), 400

@app.route('/stop', methods=['POST'])
@login_required
def stop_script():
    script_name = request.form['script_name']
    script_data = scripts.get(script_name)
    if script_data and script_data['process']:
        process = psutil.Process(script_data['pid'])
        process.terminate()  # Termina o processo
        script_data['process'] = None
        script_data['pid'] = None
        save_scripts()
        return jsonify({"message": f"Script {script_name} parado com sucesso!"})
    else:
        return jsonify({"error": "Script não está em execução."}), 400

@app.route('/status', methods=['GET'])
@login_required
def get_status():
    for script_name, script_data in scripts.items():
        # Verifique se o script tem um processo em execução
        if 'pid' in script_data and script_data['pid']:
            try:
                # Verifica se o processo ainda está ativo
                os.kill(script_data['pid'], 0)
                script_data['process'] = True
            except OSError:
                script_data['process'] = None
        else:
            script_data['process'] = None

    return jsonify(scripts)

@app.route('/delete', methods=['POST'])
@login_required
def delete_script():
    script_name = request.form['script_name']
    script_data = scripts.get(script_name)

    if script_data:
        # Tentar parar o script se estiver em execução
        if script_data['process']:
            process = psutil.Process(script_data['pid'])
            process.terminate()
            script_data['process'] = None
            script_data['pid'] = None

        # Remover o arquivo físico
        script_path = script_data.get('path')
        if script_path and os.path.exists(script_path):
            try:
                os.remove(script_path)
            except Exception as e:
                return jsonify({"error": f"Erro ao remover o arquivo: {str(e)}"}), 500

        # Remover o ícone, se houver
        icon_path = script_data.get('icon')
        if icon_path and os.path.exists(os.path.join(app.config['ICON_FOLDER'], icon_path)):
            try:
                os.remove(os.path.join(app.config['ICON_FOLDER'], icon_path))
            except Exception as e:
                return jsonify({"error": f"Erro ao remover o ícone: {str(e)}"}), 500

        # Remover o script do dicionário
        del scripts[script_name]
        save_scripts()
        return jsonify({"message": f"Script {script_name} excluído com sucesso!"})
    else:
        return jsonify({"error": "Script não encontrado."}), 404

def run_script(script_path, script_name):
    try:
        process = subprocess.Popen(
            ["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        scripts[script_name]['process'] = True
        scripts[script_name]['pid'] = process.pid  # Salva o PID do processo
        save_scripts()

        for line in process.stdout:
            print(f"Saída [{script_name}]: {line.strip()}")
        for line in process.stderr:
            print(f"Erro [{script_name}]: {line.strip()}")

        process.wait()
    except Exception as e:
        print(f"Erro ao executar {script_name}: {str(e)}")
    finally:
        scripts[script_name]['process'] = None
        scripts[script_name]['pid'] = None
        save_scripts()

def save_scripts():
    with open('scripts.json', 'w') as file:
        json.dump(scripts, file, indent=4)

def load_scripts():
    global scripts
    if os.path.exists('scripts.json'):
        with open('scripts.json', 'r') as file:
            scripts = json.load(file)

if __name__ == "__main__":
    load_scripts()
    app.run(host='0.0.0.0', port=1007)
