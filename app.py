# app.py
from flask import Flask, request, jsonify, render_template
import os
import sys

# Adiciona o diretório do módulo do jogo ao path para importação
# Isso é necessário se app.py está um nível acima de seu_codigo_rpg
sys.path.append(os.path.join(os.path.dirname(__file__), 'seu_codigo_rpg'))

# Agora importe suas classes do jogo
# A forma exata do import dependerá de como você estruturou os arquivos
# dentro de 'seu_codigo_rpg'
try:
    from jogo_classes import JogoMedicoRPG, Jogador, ClassesMedico, TracosMedico # Supondo que JogoMedicoRPG está aqui
    from gemini_api import GeminiAPI # Supondo que GeminiAPI está aqui
    # Se você dividiu mais, importe de acordo
except ImportError as e:
    print(f"Erro ao importar módulos do jogo: {e}")
    print("Verifique a estrutura de pastas e os nomes dos arquivos em 'seu_codigo_rpg'.")
    # Definir classes placeholder para evitar crash total se o import falhar durante o dev
    class JogoMedicoRPG: pass 
    class GeminiAPI: pass
    # Você precisará corrigir os imports para o jogo funcionar


app = Flask(__name__)

# --- Configuração da API Gemini ---
# É CRUCIAL que a GOOGLE_API_KEY esteja configurada como variável de ambiente
# ao rodar este servidor Flask.
# Ou, para desenvolvimento rápido, você pode (não recomendado para produção):
# from dotenv import load_dotenv
# load_dotenv()
# GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY_RPG')
# No entanto, para este exemplo, vamos assumir que está no ambiente.

# Inicialização global do jogo e da API (simplificado para um único "jogo" por servidor)
# Em uma aplicação real, você gerenciaria sessões de jogo por usuário.
# Tentar inicializar o modelo Gemini aqui
try:
    # Este bloco de configuração do Gemini deve ser movido para gemini_api.py
    # e o 'generative_model' deve ser um atributo da classe GeminiAPI
    # Aqui, vamos apenas instanciar GeminiAPI, que deve lidar com isso internamente.
    if 'google.generativeai' not in sys.modules: # Pequena verificação
        raise ImportError("Biblioteca google-generativeai não parece estar disponível.")

    # Supondo que sua classe GeminiAPI lida com a configuração do modelo ao ser instanciada
    # ou tem um método de inicialização que usa a variável de ambiente.
    # A chave GOOGLE_API_KEY_RPG precisa estar no ambiente do servidor Flask.
    # No Colab, userdata.get() funciona. Para Flask local, use variáveis de ambiente.
    # Exemplo: export GOOGLE_API_KEY_RPG="sua_chave_aqui" no terminal antes de rodar Flask.
    
    # Mova a configuração do generative_model para dentro da sua classe GeminiAPI
    # e passe a chave para ela, ou deixe que ela pegue da variável de ambiente.
    
    # Adapte a inicialização da GeminiAPI conforme sua implementação.
    # Exemplo:
    # api_key_flask = os.environ.get("GOOGLE_API_KEY_RPG")
    # if not api_key_flask:
    #     print("AVISO: GOOGLE_API_KEY_RPG não definida no ambiente do servidor Flask!")
    #     # Você pode querer lançar um erro ou ter um modo de fallback
    # generative_model_instance = # ... configure o modelo aqui ou dentro da GeminiAPI
    
    # Esta é uma simplificação. A classe GeminiAPI deve lidar com a obtenção da chave
    # e configuração do modelo.
    gemini_handler = GeminiAPI(model=None) # O modelo será configurado dentro da classe
    if not gemini_handler.model: # Adicione um check na sua classe GeminiAPI
        print("AVISO: Modelo Gemini não foi carregado corretamente na GeminiAPI.")
    
    jogo_global = JogoMedicoRPG()
    jogo_global.gemini_api = gemini_handler # Garante que o jogo use o handler correto

except Exception as e:
    print(f"Erro crítico na inicialização da API Gemini ou Jogo: {e}")
    jogo_global = None # Impede o jogo de rodar

# --- Rotas da API ---

@app.route('/')
def home():
    # Servir o arquivo HTML principal
    # Se o HTML estiver na pasta 'static', use send_from_directory
    # Se estiver em 'templates', use render_template
    return render_template('index.html')

@app.route('/api/novo_jogo', methods=['POST'])
def api_novo_jogo():
    if not jogo_global or not hasattr(jogo_global, 'iniciar_novo_jogo_api'):
        return jsonify({"erro": "Instância do jogo não inicializada corretamente."}), 500
    
    data = request.json
    nome = data.get('nome')
    classe_str = data.get('classe') # Ex: "CLINICO_GERAL"
    traco_str = data.get('traco')   # Ex: "CINICO"

    if not all([nome, classe_str, traco_str]):
        return jsonify({"erro": "Dados incompletos para novo jogo."}), 400

    try:
        # Você precisará de um método em JogoMedicoRPG para lidar com isso
        # ou adaptar o iniciar_novo_jogo para não usar input() direto
        # Para simplificar, vamos assumir que você adaptou iniciar_novo_jogo ou criou um novo
        
        # Exemplo de como poderia ser (requer modificação em JogoMedicoRPG):
        # jogo_global.jogador = jogo_global.criar_jogador_api(nome, classe_str, traco_str)
        # return jsonify({"status": "Novo jogo iniciado", "jogador": str(jogo_global.jogador)})

        # Versão simplificada para este exemplo:
        # A lógica de seleção de classe/traço e criação do jogador aconteceria aqui
        # ou em um método dedicado em JogoMedicoRPG que não dependa de input()
        # Por ora, vamos apenas simular e avançar para o primeiro caso.
        
        # Este é um placeholder - você precisará de uma lógica real para criar o jogador
        # com base nos enums e strings recebidas.
        # Ex:
        # classe_enum = ClassesMedico[classe_str.upper()]
        # traco_enum = TracosMedico[traco_str.upper()]
        # jogo_global.jogador = Jogador(nome, classe_enum, traco_enum)
        # print(f"Jogador criado: {jogo_global.jogador}")
        
        # Como iniciar_novo_jogo já tem a lógica de input, vamos criar um wrapper
        # ou uma nova função para o setup via API. Por ora, vamos focar no fluxo do caso.
        # Supondo que o jogador já foi criado (o frontend lidaria com a seleção de classe/traço
        # e enviaria os nomes para um endpoint /criar_jogador)
        
        # Para este protótipo, vamos pular a criação de personagem via API
        # e assumir que o jogador será criado com valores padrão ao iniciar o primeiro caso,
        # ou que o frontend fará uma chamada separada para isso.
        # Apenas para testar o fluxo do caso:
        if not jogo_global.jogador: # Se nenhum jogador, cria um padrão para teste
             jogo_global.jogador = Jogador("Dr. Estranho (Teste API)", ClassesMedico.CLINICO_GERAL, TracosMedico.CURIOSO)
             print("Jogador de teste criado para API.")

        return jsonify({"status": "Jogador configurado/pronto para iniciar caso."})

    except KeyError as e:
        return jsonify({"erro": f"Classe ou Traço inválido: {e}"}), 400
    except Exception as e:
        return jsonify({"erro": f"Erro ao iniciar novo jogo: {str(e)}"}), 500


@app.route('/api/iniciar_caso', methods=['GET'])
def api_iniciar_caso():
    if not jogo_global or not jogo_global.jogador or not hasattr(jogo_global, '_gerar_e_iniciar_novo_caso'):
        return jsonify({"erro": "Jogo ou jogador não pronto, ou método não encontrado."}), 500

    if jogo_global._gerar_e_iniciar_novo_caso():
        caso = jogo_global.caso_atual
        # A introdução narrativa já é impressa no servidor por adicionar_progresso_cena
        # Vamos retornar a introdução e as primeiras opções
        return jsonify({
            "titulo_caso": caso.titulo_caso,
            "introducao_narrativa": caso.introducao_narrativa_imersiva, # Ou o primeiro item de progresso_narrativo_cena_atual
            "opcoes_cena": caso.opcoes_cena_atuais,
            "jogador_status": str(jogo_global.jogador) # Para atualizar a UI
        })
    else:
        return jsonify({"erro": "Falha ao gerar novo caso."}), 500

@app.route('/api/processar_acao', methods=['POST'])
def api_processar_acao():
    if not jogo_global or not jogo_global.caso_atual or not hasattr(jogo_global, 'interagir_com_opcao_de_cena'):
        return jsonify({"erro": "Nenhum caso ativo ou método de interação não encontrado."}), 500

    data = request.json
    opcao_escolhida_dict = data.get('opcao') # Espera um dict {"tom": "...", "opcao_texto": "..."}

    if not opcao_escolhida_dict or "opcao_texto" not in opcao_escolhida_dict or "tom" not in opcao_escolhida_dict:
        return jsonify({"erro": "Opção escolhida inválida ou mal formatada."}), 400

    # Limpar o histórico da cena anterior ANTES de adicionar a nova interação
    # para que o Gemini não fique preso em loops de opções.
    jogo_global.caso_atual.progresso_narrativo_cena_atual = [] 
    
    # A função interagir_com_opcao_de_cena já imprime e adiciona ao progresso_narrativo_cena_atual
    jogo_global.interagir_com_opcao_de_cena(opcao_escolhida_dict) 
    
    # Após a interação, gerar novas opções para a cena
    if not jogo_global.caso_atual.resolvido:
        jogo_global._atualizar_opcoes_de_cena_caso_atual() # Gera novas opções

    # O progresso_narrativo_cena_atual agora contém o resultado da última ação
    # e a IA usou isso para gerar as novas opções.
    return jsonify({
        "nova_narrativa_parte": "\n".join(jogo_global.caso_atual.progresso_narrativo_cena_atual), # Envia o que foi adicionado à cena
        "opcoes_cena": jogo_global.caso_atual.opcoes_cena_atuais if not jogo_global.caso_atual.resolvido else [],
        "caso_resolvido": jogo_global.caso_atual.resolvido,
        "desfecho": jogo_global.caso_atual.desfecho_final if jogo_global.caso_atual.resolvido else None,
        "jogador_status": str(jogo_global.jogador)
    })

@app.route('/api/acao_fixa', methods=['POST'])
def api_acao_fixa():
    if not jogo_global or not jogo_global.caso_atual:
        return jsonify({"erro": "Nenhum caso ativo."}), 500
    
    data = request.json
    tipo_acao = data.get('tipo_acao')
    parametro_acao = data.get('parametro') # ex: nome da hipótese, ou NPC para dica

    # Limpar o histórico da cena ANTES da nova interação
    jogo_global.caso_atual.progresso_narrativo_cena_atual = []

    if tipo_acao == "hipotese":
        # Simular a adição de hipótese e obter uma narrativa de feedback
        if parametro_acao: # parametro_acao é a nova hipótese
            jogo_global.caso_atual.hipoteses_jogador.append(parametro_acao)
            # A função original já imprime, então precisamos capturar essa "impressão" ou refatorar.
            # Por simplicidade, vamos gerar uma resposta genérica aqui.
            # Idealmente, listar_ou_add_hipoteses retornaria a string para a API.
            # Aqui vamos chamar adicionar_progresso_cena diretamente.
            texto_narrativo = f"Você pondera e anota uma nova suspeita: {parametro_acao}."
            if "lúpus" in parametro_acao.lower(): # Exemplo de lógica interna
                texto_narrativo += "\nUma voz familiar ecoa em sua mente, soando suspeitamente como Dr. Howser: 'É claro que você pensou em lúpus. NUNCA é lúpus.'"
            jogo_global.caso_atual.adicionar_progresso_cena(texto_narrativo)

    elif tipo_acao == "dica_howser":
        jogo_global.pedir_dica_npc("Dr. Howser") # Esta função já usa adicionar_progresso_cena
    elif tipo_acao == "dica_meridee":
        jogo_global.pedir_dica_npc("Dra. Meridee Grey") # Esta função já usa adicionar_progresso_cena
    elif tipo_acao == "desenhar":
        if jogo_global.jogador.traco == TracosMedico.ARTISTA_FRUSTRADO:
             # parametro_acao seria o que desenhar
            sint_desenhar = parametro_acao if parametro_acao else "algo clinicamente relevante"
            jogo_global.desenhar_sintoma_api(sint_desenhar) # Criar versão API que retorna string
        else:
            jogo_global.caso_atual.adicionar_progresso_cena("Apenas Artistas Frustrados sentem o impulso de desenhar.")
    elif tipo_acao == "resumo_mental":
        # exibir_resumo_mental já imprime. Precisamos que retorne o texto.
        # Por ora, vamos simular.
        # texto_resumo = jogo_global.caso_atual.gerar_texto_resumo_mental(jogo_global.jogador.nome)
        # jogo_global.caso_atual.adicionar_progresso_cena(texto_resumo)
        jogo_global.caso_atual.adicionar_progresso_cena(f"Você para um momento para organizar seus pensamentos sobre o caso de {jogo_global.caso_atual.paciente_info.get('nome')}. Os sintomas {jogo_global.caso_atual.sintomas_revelados_jogador} são os mais evidentes...")

    else:
        return jsonify({"erro": "Tipo de ação fixa desconhecida."}), 400

    # Após a ação fixa, gerar novas opções de cena
    if not jogo_global.caso_atual.resolvido:
        jogo_global._atualizar_opcoes_de_cena_caso_atual()

    return jsonify({
        "nova_narrativa_parte": "\n".join(jogo_global.caso_atual.progresso_narrativo_cena_atual),
        "opcoes_cena": jogo_global.caso_atual.opcoes_cena_atuais if not jogo_global.caso_atual.resolvido else [],
        "jogador_status": str(jogo_global.jogador)
    })


@app.route('/api/tentar_diagnostico', methods=['POST'])
def api_tentar_diagnostico():
    if not jogo_global or not jogo_global.caso_atual:
        return jsonify({"erro": "Nenhum caso ativo."}), 500

    # Gerar opções de diagnóstico
    jogo_global._atualizar_opcoes_diagnostico_caso_atual()
    if not jogo_global.caso_atual.opcoes_diagnostico_atuais:
        return jsonify({"erro": "Não foi possível gerar opções de diagnóstico."}), 500
    
    return jsonify({
        "opcoes_diagnostico": jogo_global.caso_atual.opcoes_diagnostico_atuais
    })

@app.route('/api/finalizar_diagnostico', methods=['POST'])
def api_finalizar_diagnostico():
    if not jogo_global or not jogo_global.caso_atual:
        return jsonify({"erro": "Nenhum caso ativo."}), 500
    
    data = request.json
    diagnostico_escolhido = data.get('diagnostico')
    if not diagnostico_escolhido:
        return jsonify({"erro": "Diagnóstico não fornecido."}), 400

    # Limpar progresso da cena antes do desfecho
    jogo_global.caso_atual.progresso_narrativo_cena_atual = []
    
    # finalizar_caso_com_diagnostico já lida com a chamada à Gemini e atualização do jogador.
    # Precisamos garantir que ele não imprima diretamente, mas retorne os dados.
    # Por agora, vamos assumir que o método já existente foi chamado e o desfecho_final foi populado.
    # Na prática, você chamaria um método que executa a lógica e retorna os dados.
    
    # Adaptar finalizar_caso_com_diagnostico para não depender de input e para retornar o desfecho
    # jogo_global.finalizar_caso_com_diagnostico(diagnostico_escolhido) 
    # Este método original já chama a GeminiAPI e atualiza o jogador, e imprime a ficha.
    # Para API, precisaríamos que ele retornasse o JSON do desfecho.

    # Simulando a chamada e obtenção do desfecho
    desfecho_json = jogo_global.gemini_api.gerar_desfecho_caso(jogo_global.jogador, jogo_global.caso_atual, diagnostico_escolhido)
    if isinstance(desfecho_json, dict):
        # Aplicar o desfecho ao jogo (lógica de JogoMedicoRPG.finalizar_caso_com_diagnostico)
        jogo_global.caso_atual.resolvido = True
        jogo_global.caso_atual.desfecho_final = desfecho_json
        jogo_global.jogador.reputacao = max(0, min(100, jogo_global.jogador.reputacao + desfecho_json.get("reputacao_delta", 0)))
        jogo_global.jogador.pontuacao_diagnostica += desfecho_json.get("pontuacao_diagnostica_delta", 0)
        jogo_global.jogador.fama_de_maluco = max(0, jogo_global.jogador.fama_de_maluco + desfecho_json.get("fama_de_maluco_delta", 0))
        jogo_global.jogador.casos_resolvidos += 1
        if jogo_global.caso_atual.id_caso not in jogo_global.casos_concluidos_ids:
             jogo_global.casos_concluidos_ids.append(jogo_global.caso_atual.id_caso)
        
        # A narrativa do desfecho já está no JSON. A Ficha Educativa também.
        return jsonify({
            "desfecho_completo": desfecho_json, # Envia todo o objeto do desfecho
            "jogador_status": str(jogo_global.jogador)
        })
    else:
        return jsonify({"erro": f"Falha ao gerar desfecho do diagnóstico: {str(desfecho_json)}"}),500


if __name__ == '__main__':
    # Verificar se a chave API está disponível, senão o Flask não será útil
    api_key = os.environ.get("GOOGLE_API_KEY_RPG")
    if not api_key and not (hasattr(gemini_handler, 'model') and gemini_handler.model): # Segundo check
        print("****************************************************************************")
        print("ATENÇÃO: A variável de ambiente GOOGLE_API_KEY_RPG não está definida.")
        print("O servidor Flask iniciará, mas as chamadas à API Gemini falharão.")
        print("Defina a chave antes de rodar: export GOOGLE_API_KEY_RPG='sua_chave_aqui'")
        print("****************************************************************************")
    
    # Cria a pasta 'templates' se não existir, para render_template funcionar
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # Cria um index.html básico em templates se não existir
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write('<h1>Anamnese - Carregando...</h1><div id="app"></div><script src="/static/script.js"></script>')
            print("Criado templates/index.html básico.")
            
    # Cria a pasta 'static' se não existir
    if not os.path.exists('static'):
        os.makedirs('static')
        print("Criada pasta static/.")


    app.run(debug=True) # debug=True é bom para desenvolvimento