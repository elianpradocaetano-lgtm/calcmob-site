import streamlit as st

# 1. Configuração da Página
st.set_page_config(page_title="Calculadora Privada - Reviale", page_icon="📊")

# 2. Definição da Senha (Altere aqui para a senha que desejar)
CODIGO_ACESSO = "REVIALE2025"


# 3. Função para verificar o acesso
def verificar_acesso():
    # Inicializa o estado de acesso se não existir
    if "acesso_liberado" not in st.session_state:
        st.session_state["acesso_liberado"] = False

    if not st.session_state["acesso_liberado"]:
        st.markdown("## 🔐 Área Restrita")
        st.info("Esta calculadora é de uso exclusivo. Por favor, insira o código de acesso.")

        senha_digitada = st.text_input("Código de Acesso:", type="password")

        if st.button("LIBERAR CALCULADORA"):
            if senha_digitada == CODIGO_ACESSO:
                st.session_state["acesso_liberado"] = True
                st.rerun()  # Atualiza a página para mostrar a calculadora
            else:
                st.error("Código incorreto. Tente novamente.")
        return False
    return True


# 4. Lógica de exibição
if verificar_acesso():
    # --- TUDO O QUE ESTIVER AQUI DENTRO SÓ APARECE COM A SENHA ---
    st.title("📊 Calculadora Imobiliária")
    st.success("Acesso Autorizado")

    # Exemplo de conteúdo da sua calculadora:
    valor_imovel = st.number_input("Valor do Imóvel (R$):", min_value=0.0, format="%.2f")
    taxa = st.slider("Taxa de Juros (%)", 0.0, 20.0, 9.5)

    # Botão para sair e bloquear novamente
    if st.button("Sair / Bloquear"):
        st.session_state["acesso_liberado"] = False
        st.rerun()

    # Cole o restante do código da sua calculadora original aqui abaixo...