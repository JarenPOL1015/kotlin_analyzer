import streamlit as st
from streamlit_ace import st_ace
from controller import analyze_code

st.set_page_config(layout="wide")

# Inicializar session_state
if 'all_tokens' not in st.session_state:
    st.session_state['all_tokens'] = "Ejecuta el análisis para ver los tokens"
if 'lex_errors' not in st.session_state:
    st.session_state['lex_errors'] = "Ejecuta el análisis para ver errores léxicos"
if 'sintactic_errors' not in st.session_state:
    st.session_state['sintactic_errors'] = "Ejecuta el análisis para ver errores sintácticos"
if 'parse_tree' not in st.session_state:
    st.session_state['parse_tree'] = "Ejecuta el análisis para ver el árbol sintáctico"
if 'semantic_errors' not in st.session_state:
    st.session_state['semantic_errors'] = "Ejecuta el análisis para ver errores semánticos"
if 'lex_ok' not in st.session_state:
    st.session_state['lex_ok'] = None
if 'sintactic_ok' not in st.session_state:
    st.session_state['sintactic_ok'] = None
if 'semantic_ok' not in st.session_state:
    st.session_state['semantic_ok'] = None
if 'uploaded_file_content' not in st.session_state:
    st.session_state['uploaded_file_content'] = None
if 'editor_key' not in st.session_state:
    st.session_state['editor_key'] = 0

def run_analysis():
    # Obtener el código del editor actual usando el key dinámico
    editor_key = f'ace_editor_{st.session_state["editor_key"]}'
    code = st.session_state.get(editor_key, '')
    
    # Limpiar estados previos al inicio
    st.session_state['all_tokens'] = ''
    st.session_state['lex_errors'] = ''
    st.session_state['sintactic_errors'] = ''
    st.session_state['parse_tree'] = ''
    st.session_state['semantic_errors'] = ''
    st.session_state['lex_ok'] = None
    st.session_state['sintactic_ok'] = None
    st.session_state['semantic_ok'] = None
    
    if code and code.strip():
        result = analyze_code(code)
        
        # Léxico
        st.session_state['all_tokens'] = '\n'.join(result['tokens']) if result['tokens'] else ''
        st.session_state['lex_errors'] = '\n'.join(result['lex_errors']) if result['lex_errors'] else ''
        st.session_state['lex_ok'] = not bool(result['lex_errors'])
        
        # Sintáctico
        if result['lex_errors']:
            st.session_state['sintactic_ok'] = False  # Indicar que no se ejecutó por errores léxicos
            st.session_state['parse_tree'] = ''
            st.session_state['sintactic_errors'] = ''
        else:
            st.session_state['sintactic_errors'] = '\n'.join(result['sintactic_errors']) if result['sintactic_errors'] else ''
            st.session_state['sintactic_ok'] = not bool(result['sintactic_errors'])
            if result['parse_tree'] and not result['sintactic_errors']:
                import pprint
                st.session_state['parse_tree'] = pprint.pformat(result['parse_tree'], indent=2, width=80)
            else:
                st.session_state['parse_tree'] = ''
        
        # Semántico
        if result['lex_errors'] or result['sintactic_errors']:
            st.session_state['semantic_ok'] = False  # Indicar que no se ejecutó por errores previos
            st.session_state['semantic_errors'] = ''
        elif result['semantic_errors']:
            st.session_state['semantic_errors'] = '\n'.join(str(e) for e in result['semantic_errors'])
            st.session_state['semantic_ok'] = False
        else:
            st.session_state['semantic_errors'] = ''
            st.session_state['semantic_ok'] = True

def reset_editor():
    """Resetea el contenido del editor y todos los estados de análisis."""
    st.session_state['all_tokens'] = "Ejecuta el análisis para ver los tokens"
    st.session_state['lex_errors'] = "Ejecuta el análisis para ver errores léxicos"
    st.session_state['sintactic_errors'] = "Ejecuta el análisis para ver errores sintácticos"
    st.session_state['parse_tree'] = "Ejecuta el análisis para ver el árbol sintáctico"
    st.session_state['semantic_errors'] = "Ejecuta el análisis para ver errores semánticos"
    st.session_state['lex_ok'] = None
    st.session_state['sintactic_ok'] = None
    st.session_state['semantic_ok'] = None
    st.session_state['uploaded_file_content'] = None
    # Incrementar key para forzar recreación del editor
    st.session_state['editor_key'] += 1

with st.container():
    title, options = st.columns([2, 2])
    
    with title:
        st.title("KotlinAnalyzer")

    with options:
        op1, op2, op3 = st.columns(3)
        with op1:
            if st.button('🆕 Nuevo', use_container_width=True):
                reset_editor()
                st.rerun()
        with op2:
            with st.popover('📂 Abrir', use_container_width=True):
                uploaded_file = st.file_uploader(
                    "Selecciona un archivo .kt", 
                    type=['kt'], 
                    accept_multiple_files=False,
                    key='file_uploader'
                )
                if uploaded_file is not None:
                    if st.button('Cargar archivo', use_container_width=True):
                        try:
                            content = uploaded_file.read().decode('utf-8')
                            st.session_state['editor_key'] += 1
                            st.session_state['ace_editor'] = content
                            st.success(f"✅ Archivo '{uploaded_file.name}' cargado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        with op3:
            # Obtener el código del editor actual
            editor_key = f'ace_editor_{st.session_state["editor_key"]}'
            code = st.session_state.get(editor_key, '')
            if code and code.strip():
                st.download_button(
                    label='💾 Guardar',
                    data=code.encode('utf-8'),
                    file_name='codigo.kt',
                    mime='text/plain',
                    use_container_width=True
                )
            else:
                st.button('💾 Guardar', use_container_width=True, disabled=True)

code_section, result = st.columns([3, 1])

with code_section:
    text, button = st.columns([4, 1])
    with text:
        st.subheader("📝 Editor de Código")
    with button:
        st.button('▶️ Ejecutar', on_click=run_analysis, use_container_width=True, type="primary")

    st_ace(
        value=st.session_state.get('ace_editor', ''),
        placeholder="Escribe código Kotlin aquí...",
        language="kotlin",
        theme='monokai',
        keybinding="vscode",
        font_size=20,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        height=600,
        key=f'ace_editor_{st.session_state["editor_key"]}'
    )

with result:
    lex, par, sem = st.tabs(["🔤 Léxico", "🌲 Sintáctico", "🧠 Semántico"])

    with lex:
        st.subheader("Errores Léxicos")
        if st.session_state['lex_ok'] is None:
            st.info("Ejecuta el análisis para ver errores léxicos")
        elif st.session_state['lex_ok']:
            st.success("✅ Sin errores léxicos")
        else:
            st.error("❌ Se encontraron errores léxicos")
            st.code(st.session_state['lex_errors'], language=None, line_numbers=False)

        st.subheader("Tokens")
        if st.session_state['lex_ok'] is None:
            st.info("Ejecuta el análisis para ver los tokens")
        elif st.session_state['all_tokens']:
            st.code(st.session_state['all_tokens'], language=None, line_numbers=False)
        else:
            st.info("No se encontraron tokens")

    with par:
        st.subheader("Errores Sintácticos")
        if st.session_state['sintactic_ok'] is None:
            st.info("Ejecuta el análisis para ver errores sintácticos")
        elif st.session_state['sintactic_ok'] is False and st.session_state['lex_ok'] is False:
            st.error("❌ Errores previos")
        elif st.session_state['sintactic_ok']:
            st.success("✅ Sin errores sintácticos")
        else:
            st.error("❌ Se encontraron errores sintácticos")
            st.code(st.session_state['sintactic_errors'], language=None, line_numbers=False)

        st.subheader("Árbol Sintáctico")
        if st.session_state['sintactic_ok'] is None:
            st.info("Ejecuta el análisis para ver el árbol sintáctico")
        elif st.session_state['parse_tree']:
            st.code(st.session_state['parse_tree'], language='python', line_numbers=False)
        else:
            st.info("No se generó árbol sintáctico")

    with sem:
        st.subheader("Errores Semánticos")
        if st.session_state['semantic_ok'] is None:
            st.info("Ejecuta el análisis para ver errores semánticos")
        elif st.session_state['semantic_ok'] is False and (st.session_state['lex_ok'] is False or st.session_state['sintactic_ok'] is False):
            st.error("❌ Errores previos")
        elif st.session_state['semantic_ok']:
            st.success("✅ Sin errores semánticos")
        else:
            st.error("❌ Se encontraron errores semánticos")
            st.code(st.session_state['semantic_errors'], language=None, line_numbers=False)