import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'elian_v6_comparativo')
SENHA_MESTRE = "123456"

def limpar_valor(v):
    if not v: return 0.0
    s = str(v).replace('.', '').replace(',', '.').strip()
    try: return float(s)
    except: return 0.0

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('senha') == SENHA_MESTRE:
            session['logado'] = True
            return redirect(url_for('index'))
    return '''
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;background:#f1f5f9;">
        <form method="post" style="background:white;padding:40px;border-radius:15px;box-shadow:0 10px 15px rgba(0,0,0,0.1);text-align:center;">
            <h2 style="color:#1e293b;margin-bottom:20px;">Calculadora Estratégica</h2>
            <input type="password" name="senha" placeholder="Senha" autofocus style="padding:12px;border-radius:8px;border:1.5px solid #cbd5e1;margin-bottom:15px;outline:none;"><br>
            <button type="submit" style="background:#10b981;color:white;border:none;padding:12px 30px;border-radius:8px;cursor:pointer;font-weight:bold;width:100%;">ENTRAR</button>
        </form>
    </div>
    '''

@app.route('/')
def index():
    if not session.get('logado'): return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    if not session.get('logado'): return jsonify({'erro': 'Não autorizado'}), 401
    try:
        dados = request.get_json()
        v_imovel = limpar_valor(dados.get('valor_imovel'))
        p_obra = limpar_valor(dados.get('percentual_obra')) / 100
        p_sinal = limpar_valor(dados.get('percentual_sinal')) / 100
        p_baloes = limpar_valor(dados.get('percentual_baloes')) / 100
        meses_obra = int(limpar_valor(dados.get('numero_parcelas')))
        incc_mensal = limpar_valor(dados.get('taxa_incc')) / 100
        taxa_anual_banco = limpar_valor(dados.get('taxa_juros')) / 100

        # --- CENÁRIO 1: HOJE (ESTÁTICO) ---
        total_obra_hoje = v_imovel * p_obra
        v_sinal_hoje = v_imovel * p_sinal
        v_balao_hoje = (v_imovel * p_baloes) / 3
        v_mensal_hoje = (total_obra_hoje - v_sinal_hoje - (v_imovel * p_baloes)) / meses_obra
        v_fin_hoje = v_imovel - total_obra_hoje
        renda_hoje = v_fin_hoje / 33.333333 if v_fin_hoje <= 400000.01 else v_fin_hoje / 25.1182

        # --- CENÁRIO 2: PROJETADO (INCC) ---
        # Correção aplicada mês a mês (Sinal não corrige pois é pago hoje)
        v_mensal_fim = v_mensal_hoje * ((1 + incc_mensal) ** meses_obra)
        v_balao_fim = v_balao_hoje * ((1 + incc_mensal) ** meses_obra)
        v_fin_final = v_fin_hoje * ((1 + incc_mensal) ** meses_obra)
        renda_final = v_fin_final / 33.333333 if v_fin_final <= 400000.01 else v_fin_final / 25.1182

        # Datas
        hoje = datetime.now()
        datas = {
            'sinal': hoje.strftime('%m/%Y'),
            'p1': (hoje + timedelta(days=32)).strftime('%m/%Y'),
            'pf': (hoje + timedelta(days=30 * meses_obra)).strftime('%m/%Y')
        }

        return jsonify({
            'hoje': {
                'v_fin': v_fin_hoje,
                'v_mensal': v_mensal_hoje,
                'v_balao': v_balao_hoje,
                'renda': renda_hoje
            },
            'futuro': {
                'v_fin': v_fin_final,
                'v_mensal': v_mensal_fim,
                'v_balao': v_balao_fim,
                'renda': renda_final
            },
            'v_sinal': v_sinal_hoje,
            'datas': datas
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)