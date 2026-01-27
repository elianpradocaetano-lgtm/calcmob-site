import os
import sys
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

# Configuração de diretórios para o executável
if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

# CONFIGURAÇÕES DE SEGURANÇA
app.secret_key = 'elian_secret_key_2024'  # Chave para criptografar a sessão
SENHA_MESTRE = "123456"  # <--- ALTERE AQUI A SUA SENHA


def converter_para_float(valor):
    if not valor: return 0.0
    valor_str = str(valor).replace('.', '').replace(',', '.')
    try:
        return float(valor_str)
    except:
        return 0.0


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        if request.form.get('senha') == SENHA_MESTRE:
            session['logado'] = True
            return redirect(url_for('index'))
        else:
            erro = "Senha incorreta!"

    # HTML da tela de login direto no Python para facilitar
    return f'''
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; background:#f1f5f9;">
        <div style="background:white; padding:40px; border-radius:15px; shadow: 0 10px 15px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; text-align:center;">
            <h2 style="color:#1e293b; margin-bottom:10px;">Financiador Pro</h2>
            <p style="font-size:12px; color:#64748b; margin-bottom:20px; text-transform:uppercase; font-weight:bold;">Acesso Restrito</p>
            <form method="post">
                <input type="password" name="senha" placeholder="Senha de Acesso" autofocus
                       style="padding:12px; width:200px; border-radius:8px; border:1.5px solid #cbd5e1; margin-bottom:15px; outline:none;">
                <br>
                <button type="submit" style="background:#10b981; color:white; border:none; padding:12px 30px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">ENTRAR</button>
            </form>
            {f'<p style="color:red; font-size:12px; margin-top:15px;">{erro}</p>' if erro else ''}
        </div>
    </div>
    '''


@app.route('/')
def index():
    if not session.get('logado'):
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    if not session.get('logado'):
        return jsonify({'erro': 'Acesso negado'}), 401

    try:
        dados = request.get_json()
        valor_imovel = converter_para_float(dados.get('valor_imovel'))
        perc_obra = converter_para_float(dados.get('percentual_obra', 20))
        qtd_meses_obra = int(dados.get('numero_parcelas', 24))
        taxa_anual = converter_para_float(dados.get('taxa_juros', 9.5)) / 100

        # Fluxo de Obra
        valor_total_obra = valor_imovel * (perc_obra / 100)
        valor_sinal = valor_imovel * (converter_para_float(dados.get('percentual_sinal', 5)) / 100)
        valor_total_baloes = valor_imovel * (converter_para_float(dados.get('percentual_baloes', 5)) / 100)
        valor_total_mensais = valor_total_obra - valor_sinal - valor_total_baloes

        val_mensal_obra = valor_total_mensais / qtd_meses_obra if qtd_meses_obra > 0 else 0
        val_balao_obra = valor_total_baloes / int(dados.get('numero_baloes', 3))

        # Financiamento e Regra de Renda
        valor_financiado = valor_imovel - valor_total_obra
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1

        renda_teste = valor_financiado / 33.333333
        renda_final = valor_financiado / 25.1182 if renda_teste > 12000.01 else renda_teste

        primeira_sac = (valor_financiado / 420) + (valor_financiado * taxa_mensal)
        parcela_price = valor_financiado * (taxa_mensal * (1 + taxa_mensal) ** 360) / ((1 + taxa_mensal) ** 360 - 1)

        return jsonify({
            'valor_imovel': valor_imovel,
            'valor_sinal': valor_sinal,
            'val_mensal_obra': val_mensal_obra,
            'val_balao_obra': val_balao_obra,
            'total_obra': valor_total_obra,
            'valor_financiado': valor_financiado,
            'renda_final': renda_final,
            'parcela_sac': primeira_sac,
            'parcela_price': parcela_price,
            'qtd_m': qtd_meses_obra,
            'qtd_b': int(dados.get('numero_baloes', 3))
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 400


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()
    app.run(port=5000)