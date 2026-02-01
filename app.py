import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'elian_caetano_v3_final')
SENHA_MESTRE = "123456"


def limpar_valor(v):
    if not v: return 0.0
    s = str(v).replace('.', '').replace(',', '.').strip()
    try:
        return float(s)
    except:
        return 0.0


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('senha') == SENHA_MESTRE:
            session['logado'] = True
            return redirect(url_for('index'))
    return '''
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;background:#f1f5f9;">
        <form method="post" style="background:white;padding:40px;border-radius:15px;box-shadow:0 10px 15px rgba(0,0,0,0.1);text-align:center;">
            <h2 style="color:#1e293b;margin-bottom:20px;">Financiador Pro</h2>
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
    if not session.get('logado'): return jsonify({'erro': 'Acesso negado'}), 401
    try:
        dados = request.get_json()
        v_imovel = limpar_valor(dados.get('valor_imovel'))
        p_obra = limpar_valor(dados.get('percentual_obra', 20)) / 100
        p_sinal = limpar_valor(dados.get('percentual_sinal', 5)) / 100
        p_baloes = limpar_valor(dados.get('percentual_baloes', 5)) / 100
        meses_obra = int(limpar_valor(dados.get('numero_parcelas', 24)))
        num_baloes = int(dados.get('numero_baloes', 3))
        taxa_anual = limpar_valor(dados.get('taxa_juros', 9.5)) / 100

        total_obra = v_imovel * p_obra
        v_sinal = v_imovel * p_sinal
        v_baloes_total = v_imovel * p_baloes
        v_mensais_total = total_obra - v_sinal - v_baloes_total
        v_mensal = v_mensais_total / meses_obra if meses_obra > 0 else 0
        v_balao = v_baloes_total / num_baloes if num_baloes > 0 else 0

        # --- LÓGICA DE FINANCIAMENTO ---
        v_financiado = v_imovel - total_obra
        taxa_mensal = (1 + taxa_anual) ** (1 / 12) - 1
        sac = (v_financiado / 420) + (v_financiado * taxa_mensal)

        n = 360
        denominador = ((1 + taxa_mensal) ** n) - 1
        price = v_financiado * (taxa_mensal * (1 + taxa_mensal) ** n) / denominador if denominador > 0 else 0

        # --- A REGRA DE OURO SOLICITADA ---
        # Crédito até 400.000,00 -> Fator 33.333333 (Resulta em 12k de renda)
        # Crédito acima de 400.000,00 -> Fator 25.1182 (Regra de Mercado/SBPE)
        if v_financiado <= 400000.01:
            renda_final = v_financiado / 33.333333
        else:
            renda_final = v_financiado / 25.1182

        return jsonify({
            'renda_final': renda_final,
            'valor_sinal': v_sinal,
            'val_mensal_obra': v_mensal,
            'val_balao_obra': v_balao,
            'total_obra': total_obra,
            'valor_financiado': v_financiado,
            'parcela_sac': sac,
            'parcela_price': price,
            'qtd_m': meses_obra,
            'qtd_b': num_baloes
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 400


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)