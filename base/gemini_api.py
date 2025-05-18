class GeminiAPI:
    def __init__(self, model):
        self.model = model

    def _gerar_conteudo_seguro(self, prompt_text, is_json_output=False, max_retries=3):
        # ... (manter o método _gerar_conteudo_seguro como antes)
        if not self.model:
            print_lentamente("❌ Modelo Gemini não inicializado. Verifique a configuração da API Key.")
            return "Erro: Modelo Gemini não configurado."
        
        for attempt in range(max_retries):
            try:
                print_lentamente(f"... (API Gemini processando solicitação - Tentativa {attempt+1}/{max_retries}) ...")
                response = self.model.generate_content(prompt_text)
                
                if not response.candidates or not response.candidates[0].content.parts:
                    finish_reason_name = "DESCONHECIDO"
                    safety_ratings_text = "N/A"
                    if response.candidates and response.candidates[0].finish_reason:
                        finish_reason_name = response.candidates[0].finish_reason.name
                    if response.candidates and response.candidates[0].safety_ratings:
                         safety_ratings_text = "".join(f"\n  - {sr.category}: {sr.probability.name}" for sr in response.candidates[0].safety_ratings)
                    
                    error_message = (f"API Gemini bloqueou ou não gerou conteúdo. "
                                     f"Razão: {finish_reason_name}. Safety Ratings: {safety_ratings_text}")
                    print_lentamente(f"⚠️ Aviso da API (tentativa {attempt+1}/{max_retries}): {error_message}")
                    
                    if "SAFETY" in finish_reason_name or (response.prompt_feedback and response.prompt_feedback.block_reason == 'SAFETY'):
                        return f"Erro Crítico de Segurança da API: {error_message}. O prompt pode precisar de ajuste."
                    
                    time.sleep(1.8 ** attempt) 
                    continue

                generated_text = response.text.strip()

                if is_json_output:
                    if generated_text.startswith("```json"): generated_text = generated_text[7:]
                    elif generated_text.startswith("```"): generated_text = generated_text[3:]
                    if generated_text.endswith("```"): generated_text = generated_text[:-3]
                    generated_text = generated_text.strip()

                    try:
                        parsed_json = json.loads(generated_text)
                        return parsed_json
                    except json.JSONDecodeError as json_e:
                        print_lentamente(f"❌ Erro ao decodificar JSON da API (tentativa {attempt+1}): {json_e}.")
                        print_lentamente(f"Texto recebido (início): {generated_text[:600]}...")
                        if attempt == max_retries - 1:
                            return f"Erro Crítico de formato JSON: {generated_text[:600]}"
                        time.sleep(1.8 ** attempt)
                        continue 
                return generated_text
            
            except Exception as e:
                print_lentamente(f"❌ Erro inesperado na chamada da API Gemini (tentativa {attempt+1}): {type(e).__name__} - {e}")
                if attempt == max_retries - 1:
                    return f"Erro Crítico: Falha na API Gemini após {max_retries} tentativas. ({type(e).__name__})"
                time.sleep(1.8 ** attempt)
        
        return f"Erro Crítico: Falha ao gerar conteúdo após {max_retries} tentativas (esgotado)."

    def gerar_caso_clinico(self, jogador: Jogador, tema_caso=None, dificuldade="normal", casos_anteriores_ids=None):
        # MODIFICAR ESTE PROMPT PARA O ESTILO NARRATIVO (Etapa 2)
        # Por agora, vamos manter o foco nas opções, mas adicionaremos o campo introducao_narrativa_imersiva
        if casos_anteriores_ids is None: casos_anteriores_ids = []
        prompt_base = f"""
        Você é um roteirista de "Plantão 24h: O Mistério do Paciente X".
        Jogador: Dr(a). {jogador.nome}, {jogador.classe.value['nome']} com traço "{jogador.traco.value['nome']}".
        Hospital decadente, anos 80. Tom: drama médico, educativo, humor, absurdo.
        Reputação: {jogador.reputacao}, Pontos Diag: {jogador.pontuacao_diagnostica}, Fama Maluco: {jogador.fama_de_maluco}.
        Não repita IDs: {', '.join(map(str, casos_anteriores_ids)) if casos_anteriores_ids else 'Nenhum'}.
        {f"Tema Sugerido: {tema_caso}" if tema_caso else ""} Dificuldade: {dificuldade}.

        Gere um caso clínico NOVO e ÚNICO em formato JSON ESTRITO com os seguintes campos:
        "id_caso", "titulo_caso", 
        "introducao_narrativa_imersiva" (string, 2-3 parágrafos descrevendo a chegada do paciente, ambiente, sintomas iniciais e histórico breve de forma orgânica, estilo Disco Elysium),
        "descricao_inicial_paciente" (string, resumo factual da situação para referência interna, pode ser similar à introdução mas mais direto), 
        "paciente_info": {{"nome", "idade", "historico_breve" /*ESTE HISTÓRICO BREVE DEVE ESTAR NA INTRODUÇÃO NARRATIVA*/, "sintomas_visiveis_gemini": [/*Sintomas que ficam óbvios pela introdução*/]}},
        "sintomas_reais_ocultos": ["sint_oculto1"], "pistas_falsas_criativas": ["pista_falsa1"],
        "diagnostico_real_medico", "doenca_explicacao_simplificada", "erro_comum_relacionado", "dica_vida_real",
        "dificuldade_estimada",
        "potenciais_interacoes_classe_traco",
        "referencia_npc_howser" (opcional), "referencia_npc_meridee" (opcional).

        ATENÇÃO: O JSON DEVE SER VÁLIDO.
        Exemplo para "introducao_narrativa_imersiva": 
        "O cheiro de antisséptico barato e desespero mal disfarçado pairava no ar da emergência do St. Jude's como uma mortalha invisível. Dr(a). {jogador.nome} suspirou, o café requentado fazendo pouco para afastar o cansaço da noite anterior. Foi quando as portas automáticas se abriram com um chiado asmático, revelando um homem cambaleante, Sr. Bartholomew Quibble, uns 30 e poucos anos, pele de um tom laranja-abóbora vibrante que faria um agente de trânsito sentir inveja. 'Doutor... acho que comi algo... estranho', ele murmurou, os olhos arregalados e inquietos vasculhando a sala. Ele mencionou ser artista de circo, com uma 'noite agitada' e um 'lanche misterioso'. Sua confusão era palpável."
        (O campo "sintomas_visiveis_gemini" para este exemplo seria: ["Pele laranja-abóbora vibrante", "Confusão mental", "Inquietação"])
        (O campo "descricao_inicial_paciente" seria um resumo: "Homem de 37 anos, artista de circo, chega com pele laranja, confusão e inquietação após noite agitada e lanche misterioso.")
        """
        return self._gerar_conteudo_seguro(prompt_base, is_json_output=True)

    
    def gerar_opcoes_de_cena(self, jogador: Jogador, caso: CasoClinico, historico_recente_cena: list):
        sintomas_conhecidos_str = ", ".join(list(set(caso.sintomas_revelados_jogador))) if caso.sintomas_revelados_jogador else "pouco se sabe ainda"
        exames_feitos_str = ", ".join([ex[0] for ex in caso.exames_realizados]) if caso.exames_realizados else "nenhum exame realizado"
        hipoteses_str = ", ".join(caso.hipoteses_jogador) if caso.hipoteses_jogador else "nenhuma hipótese clara"
        
        # Pega as últimas 2-3 interações para dar contexto recente
        contexto_recente_str = "\n".join(historico_recente_cena[-3:]) if historico_recente_cena else "Início da cena."

        prompt = f"""
        Você é o mestre do jogo RPG médico "Plantão 24h: O Mistério do Paciente X", com um estilo narrativo inspirado em Disco Elysium.
        Jogador: Dr(a). {jogador.nome} (Classe: {jogador.classe.value['nome']}, Traço: {jogador.traco.value['nome']}).
        Caso Atual: '{caso.titulo_caso}' - Paciente: {caso.paciente_info.get('nome')}.
        Situação Resumida: Sintomas conhecidos: {sintomas_conhecidos_str}. Exames feitos: {exames_feitos_str}. Hipóteses do jogador: {hipoteses_str}.
        Últimos eventos na cena: {contexto_recente_str}
        Diagnóstico Real (SEU CONHECIMENTO APENAS, NÃO REVELE AO JOGADOR NAS OPÇÕES): {caso.diagnostico_real_medico}.

        Gere EXATAMENTE 8 opções de ação/diálogo que o Dr(a). {jogador.nome} pode tomar AGORA.
        Cada opção deve corresponder a um dos seguintes tons distintos e ser uma ação/fala concreta e interessante:
        1.  **Cínica:** Exemplo: "Claro, essa sua 'dor excruciante' melhora na hora de receber alta, né?"
        2.  **Empática:** Exemplo: "Vejo que você está sofrendo. Vamos encontrar juntos a causa disso, conte comigo."
        3.  **Pragmática:** Exemplo: "Precisamos de dados. Vou solicitar um hemograma e um raio-X de tórax imediatamente."
        4.  **Cautelosa:** Exemplo: "Antes de qualquer conclusão, quero observar a evolução dos sintomas por mais algumas horas e refazer aquele exame."
        5.  **Filosófica:** Exemplo: "Essa erupção na pele... seria um mapa das suas angústias internas ou apenas uma dermatite comum? O que é 'comum', afinal?"
        6.  **Absurda:** Exemplo: "Tenho uma teoria: isso tudo é obra de gnomos radiologistas infiltrados no sistema de ventilação!"
        7.  **Heróica:** Exemplo: "Não se preocupe! Com a minha experiência e dedicação, vamos vencer essa doença misteriosa, custe o que custar!"
        8.  **Desastre Iminente:** Exemplo: "Vou tentar aquela manobra experimental que vi num filme B... O que pode dar errado?"

        As opções podem incluir:
        - Fazer perguntas específicas ao paciente.
        - Realizar uma observação ou exame físico detalhado.
        - Sugerir um exame complementar específico.
        - Tomar uma decisão sobre o próximo passo do tratamento (se aplicável).
        - Expressar um pensamento ou teoria (que pode ou não ser útil).
        - Realizar uma ação que possa ter consequências diretas (boas ou ruins).

        Considere a CLASSE '{jogador.classe.value['nome']}' e o TRAÇO '{jogador.traco.value['nome']}' do jogador ao formular as opções, tornando-as mais personalizadas dentro de cada tom.
        Por exemplo, um Cirurgião Pragmático pode sugerir "Preparar para cirurgia exploratória", enquanto um Clínico Pragmático pode dizer "Vamos começar com os exames básicos e ver onde isso nos leva".
        Um Psicólogo Empático pode sugerir "Explorar como esses sintomas estão afetando seu estado emocional".

        Retorne as opções como uma lista JSON de 8 dicionários. Cada dicionário deve ter as chaves "tom" (string, o nome do tom ex: "Cínica") e "opcao_texto" (string, o texto da ação/diálogo).
        A ordem dos tons na lista deve ser a mesma listada acima (Cínica, Empática, etc.).

        Exemplo de formato de retorno:
        [
            {{"tom": "Cínica", "opcao_texto": "Então, essa 'quase morte' foi antes ou depois do seu terceiro prato de feijoada?"}},
            {{"tom": "Empática", "opcao_texto": "Respire fundo, estou aqui para ajudar. Pode me contar exatamente como se sente?"}},
            {{"tom": "Pragmática", "opcao_texto": "Vamos direto aos fatos. Preciso de uma amostra de sangue para análise agora."}},
            {{"tom": "Cautelosa", "opcao_texto": "Não quero me precipitar. Vamos monitorar seus sinais vitais por uma hora antes de decidir."}},
            {{"tom": "Filosófica", "opcao_texto": "O que é a dor, senão um lembrete da nossa frágil existência? Mas, falando em existência, quando isso começou?"}},
            {{"tom": "Absurda", "opcao_texto": "Suspeito de influência lunar. Você notou algo estranho durante a última lua cheia... como o desejo incontrolável de uivar?"}},
            {{"tom": "Heróica", "opcao_texto": "Não tema, cidadão! Com o poder da medicina moderna e minha intuição infalível, desvendaremos este mistério!"}},
            {{"tom": "Desastre Iminente", "opcao_texto": "Acho que vou testar aquele coquetel de medicamentos vencidos que encontrei no fundo da gaveta. Para fins científicos, claro."}}
        ]
        """
        return self._gerar_conteudo_seguro(prompt, is_json_output=True)

    def gerar_resposta_interativa(self, jogador: Jogador, caso: CasoClinico, acao_escolhida_texto: str, tom_da_acao: str):
        sintomas_conhecidos_str = ", ".join(list(set(caso.sintomas_revelados_jogador))) if caso.sintomas_revelados_jogador else "pouco claro"
        
        prompt_interacao = f"""
        Mestre do jogo "Plantão 24h" (estilo Disco Elysium).
        Jogador: Dr(a). {jogador.nome} (Classe: {jogador.classe.value['nome']}, Traço: {jogador.traco.value['nome']}).
        Caso: '{caso.titulo_caso}' - Paciente: {caso.paciente_info.get('nome')}.
        Sintomas conhecidos pelo jogador: {sintomas_conhecidos_str}.
        (Seu conhecimento APENAS: Sintomas Reais Ocultos que o jogador ainda não descobriu: {', '.join(s for s in caso.sintomas_reais_ocultos if s not in caso.sintomas_revelados_jogador)}, Diag.Real: {caso.diagnostico_real_medico})
        
        O jogador escolheu a seguinte AÇÃO/DIÁLOGO, imbuída de um tom '{tom_da_acao}':
        "{acao_escolhida_texto}"

        Descreva o RESULTADO NARRATIVO desta ação/diálogo (2-5 frases).
        Mantenha o tom do jogo (anos 80, hospital decadente, humor negro, drama, introspecção).
        A narrativa deve fluir, como se fosse uma continuação da cena.
        -   Se a ação foi uma pergunta/exame físico: Descreva a reação do paciente, o que o jogador observa, e qualquer nova informação ou sintoma revelado. Se um sintoma for revelado DIRETAMENTE pela fala do paciente, coloque-o entre aspas simples na narrativa (ex: O paciente aperta os olhos e confessa: 'Doutor, para ser honesto, também sinto uma tontura estranha desde ontem.')
        -   Se a ação sugeriu um exame complementar (ex: uma opção "Pragmática" foi "Pedir um Raio-X"): Descreva a cena e APRESENTE O RESULTADO DO EXAME de forma narrativa e interessante.
        -   Se a ação foi mais um comentário ou uma decisão com consequências (especialmente "Desastre Iminente" ou "Heróica"): Descreva as consequências diretas.
        Considere o tom '{tom_da_acao}' ao descrever a reação do mundo ou o resultado. Uma ação "Cínica" pode irritar o paciente. Uma "Desastre Iminente" deve levar a um problema (geralmente cômico ou que complica o caso). Uma "Heróica" pode inspirar ou ser vista como exagero.
        Seja criativo e faça a história progredir! A resposta DEVE SER APENAS A NARRATIVA DO RESULTADO.
        """
        return self._gerar_conteudo_seguro(prompt_interacao)
    
    # Manter os outros métodos da GeminiAPI (gerar_caso_clinico, gerar_opcoes_diagnostico_final, etc.)
    # O prompt de gerar_caso_clinico já está ajustado para pedir "introducao_narrativa_imersiva".
    # O prompt de gerar_dialogo_npc (para intervenções aleatórias) também está ok.

  

    def gerar_opcoes_diagnostico_final(self, jogador: Jogador, caso: CasoClinico):
        sintomas_conhecidos_str = ", ".join(list(set(caso.sintomas_revelados_jogador)))

        prompt = f"""
        No jogo "Plantão 24h", Dr(a). {jogador.nome} ({jogador.classe.value['nome']}, traço: {jogador.traco.value['nome']}) está prestes a dar o diagnóstico final para o caso '{caso.titulo_caso}'.
        Paciente: {caso.paciente_info.get('nome')}. Sintomas conhecidos: {sintomas_conhecidos_str}.
        O DIAGNÓSTICO CORRETO para este caso é: "{caso.diagnostico_real_medico}".

        Gere uma lista JSON com 6 OPÇÕES DE DIAGNÓSTICO.
        1.  Uma das opções DEVE SER EXATAMENTE o diagnóstico correto: "{caso.diagnostico_real_medico}".
        2.  As outras 5 opções devem ser diagnósticos INCORRETOS. Estes devem ser:
            * Plausíveis, considerando alguns dos sintomas apresentados.
            * Ou tematicamente interessantes/divertidos/bizarros, especialmente se o traço do jogador for Teórico da Conspiração ou Desastrado, ou se o caso tiver elementos estranhos.
            * Não torne os errados ridiculamente óbvios se o caso tiver um tom mais sério, a menos que o objetivo seja humorístico.
            * Tente variar a natureza dos diagnósticos errados (ex: uma síndrome rara, uma condição comum mas errada para os sintomas chave, uma interpretação errada de um sintoma).
        3.  A ordem das 6 opções na lista JSON deve ser aleatória.

        Retorne APENAS a lista JSON de strings. Exemplo (o correto aqui é "Apendicite Aguda"):
        [
            "Gastroenterite Viral Aguda",
            "Apendicite Aguda",
            "Síndrome do Intestino Irritável com exacerbação",
            "Cólica Renal Direita",
            "Infecção Urinária Alta (Pielonefrite)",
            "Obstrução Intestinal por Ingestão de Lego (se o paciente for criança ou Desastrado)"
        ]
        """
        return self._gerar_conteudo_seguro(prompt, is_json_output=True)
    
    # Os métodos gerar_dialogo_npc, gerar_resposta_interativa, gerar_desfecho_caso, gerar_imagem_sintoma_descricao_textual
    # permanecem como no seu código original, mas lembre-se de que os prompts deles podem precisar de ajustes
    # para se alinharem com o novo estilo narrativo e as opções pré-definidas.
    # Por exemplo, gerar_resposta_interativa agora recebe uma *ação escolhida de uma lista*, não texto livre.
    def gerar_resposta_interativa(self, jogador: Jogador, caso: CasoClinico, acao_escolhida: str, tipo_acao: str): # tipo_acao: "investigacao" ou "exame"
        # O prompt aqui precisa ser ajustado para refletir que 'acao_escolhida' é uma das opções geradas.
        sintomas_conhecidos_str = ", ".join(list(set(caso.sintomas_revelados_jogador))) if caso.sintomas_revelados_jogador else "nenhum sintoma claro ainda"
        
        prompt_interacao = f"""
        Mestre de "Plantão 24h". Jogador: Dr(a). {jogador.nome} ({jogador.classe.value['nome']}, {jogador.traco.value['nome']}). Rep: {jogador.reputacao}, FamaMaluco: {jogador.fama_de_maluco}.
        Caso: {caso.id_caso} - {caso.paciente_info.get('nome', 'Paciente')}.
        Sintomas conhecidos pelo jogador: {sintomas_conhecidos_str}.
        (Seu conhecimento: Sintomas Reais Ocultos que o jogador ainda não descobriu: {', '.join(s for s in caso.sintomas_reais_ocultos if s not in caso.sintomas_revelados_jogador)}, Diag.Real: {caso.diagnostico_real_medico})
        
        O jogador escolheu a seguinte AÇÃO de {tipo_acao}: "{acao_escolhida}"

        Gere a NARRAÇÃO do resultado desta ação (2-5 frases). Mantenha o tom (anos 80, humor, drama, estilo Disco Elysium com descrições vívidas e diálogos).
        A resposta DEVE SER APENAS A NARRATIVA DO RESULTADO DA AÇÃO.
        - Se a ação foi uma pergunta/exame físico: Descreva a reação do paciente, o que o jogador observa, e qualquer nova informação ou sintoma revelado. Se um sintoma for revelado DIRETAMENTE pela fala do paciente, coloque-o entre aspas simples na narrativa (ex: O paciente geme: 'Ah, doutor, também sinto uma pontada forte aqui no peito quando respiro fundo.')
        - Se a ação foi solicitar um exame: Descreva a cena da realização do exame (se relevante) e APRESENTE O RESULTADO DO EXAME de forma narrativa. Ex: "A enfermeira volta com o resultado do Hemograma. Você analisa os números: Leucócitos em 18.000, com desvio à esquerda. Claramente há uma infecção em curso." ou "O Raio-X de tórax não mostra nada além de um coração um pouco grande demais para o gosto do Dr. Howser, que resmunga algo sobre 'excesso de sentimentalismo'."
        Considere a classe/traço do jogador para nuances na descrição ou na reação dos outros.
        Seja criativo!
        """
        return self._gerar_conteudo_seguro(prompt_interacao)

    # Manter os outros métodos da GeminiAPI (gerar_dialogo_npc, gerar_desfecho_caso, gerar_imagem_sintoma_descricao_textual)
    # Lembre-se de que o prompt de gerar_dialogo_npc para NPCs aleatórios precisará ser contextual.
    def gerar_dialogo_npc(self, npc_nome, situacao_atual, jogador: Jogador, historico_conversa=None):
        npc_info = NPC_DATA.get(npc_nome)
        if not npc_info: return "NPC desconhecido."
        # (MANTENHA SEU PROMPT DETALHADO ORIGINAL PARA gerar_dialogo_npc AQUI)
        prompt_dialogo = f"""
        Você é {npc_nome} ({npc_info['descricao']}) em "Plantão 24h".
        {npc_info['personalidade_prompt']}
        Jogador: Dr(a). {jogador.nome} ({jogador.classe.value['nome']}, traço: {jogador.traco.value['nome']}).
        Situação atual no caso '{situacao_atual.get('titulo_caso','desconhecido')}': {situacao_atual.get('resumo_situacao_para_npc','O jogador está investigando.')}
        Gere uma fala CURTA (1-2 frases) e característica do {npc_nome} para esta situação. Pode ser um comentário, uma dica velada, ou uma observação sarcástica/dramática.
        Considere falas icônicas: {', '.join(npc_info['falas_iconicas'])}.
        """
        return self._gerar_conteudo_seguro(prompt_dialogo)

    def gerar_desfecho_caso(self, jogador: Jogador, caso: CasoClinico, diagnostico_jogador: str):
        # (Mantenha o método gerar_desfecho_caso como no seu código original, com a lógica de acerto e o prompt detalhado para o JSON do desfecho)
        # A lógica de acerto já foi melhorada.
        diag_j_lower = diagnostico_jogador.lower().strip()
        diag_r_lower = caso.diagnostico_real_medico.lower().strip()
        
        acertou = False
        if diag_j_lower == diag_r_lower: acertou = True
        elif diag_j_lower in diag_r_lower or diag_r_lower in diag_j_lower: acertou = True
        else: 
            palavras_j = set(diag_j_lower.split())
            palavras_r = set(diag_r_lower.split())
            intersecao = palavras_j.intersection(palavras_r)
            uniao = palavras_j.union(palavras_r)
            if uniao and (len(intersecao) / len(uniao) > 0.6 or (len(intersecao) >=2 and len(diag_j_lower)>5)):
                acertou = True
        
        base_rep_acerto = 10; base_rep_erro_leve = -5; base_rep_erro_grave = -10
        dificuldade_caso = caso.dados_extras_gemini.get("dificuldade_estimada", "normal")

        if acertou:
            if dificuldade_caso == "difícil": base_rep_acerto = 15
            elif dificuldade_caso == "bizarro": base_rep_acerto = 20
            elif dificuldade_caso == "fácil": base_rep_acerto = 7
            rep_delta = base_rep_acerto
        else:
            if dificuldade_caso == "difícil": base_rep_erro_grave = -15
            elif dificuldade_caso == "bizarro": base_rep_erro_grave = -20
            elif dificuldade_caso == "fácil": base_rep_erro_leve = -3; base_rep_erro_grave = -7
            rep_delta = base_rep_erro_grave 

        prompt_desfecho = f"""
        Mestre de "Plantão 24h". Jogador: Dr(a). {jogador.nome} ({jogador.classe.value['nome']}, {jogador.traco.value['nome']}).
        Caso: {caso.id_caso}. Diag.Real: {caso.diagnostico_real_medico}. Jogador diagnosticou: "{diagnostico_jogador}".
        O jogador acertou o diagnóstico? {"Sim" if acertou else "Não"}.

        Gere o DESFECHO NARRATIVO e a FICHA EDUCATIVA em JSON ESTRITO.
        Desfecho: Consequências do diagnóstico. Considere traço/classe. Se o jogador for Teórico da Conspiração e o diagnóstico for absurdo mas ACERTAR um caso bizarro, crie uma cena memorável. Se ERRAR com teoria da conspiração, as consequências podem ser piores ou mais cômicas.
        
        JSON ESTRITO com os campos:
        "desfecho_narrativa" (string), 
        "diagnostico_final_jogador": "{diagnostico_jogador}",
        "diagnostico_correto_caso": "{caso.diagnostico_real_medico}", 
        "acertou": {acertou},
        "ficha_educativa_titulo": "Ficha Educativa: {caso.titulo_caso}",
        "doenca_real_ficha": "{caso.diagnostico_real_medico}",
        "explicacao_doenca_ficha": "{caso.doenca_explicacao_simplificada}",
        "erro_comum_ficha": "{caso.erro_comum_relacionado}",
        "dica_vida_real_ficha": "{caso.dica_vida_real}",
        "comentario_howser_final" (string opcional), 
        "comentario_meridee_final" (string opcional),
        "reputacao_delta" (int: use {rep_delta} como base, mas pode ajustar +/-2 com base na criatividade/gravidade do acerto/erro narrado),
        "pontuacao_diagnostica_delta" (int: +1 se acertou, 0 se errou),
        "fama_de_maluco_delta" (int: +0 a +5 se ação/diag bizarro, mesmo que acerte. +0 se normal).

        ATENÇÃO: O JSON DEVE SER VÁLIDO. Envolva todas as chaves e strings do JSON com aspas duplas.
        """
        return self._gerar_conteudo_seguro(prompt_desfecho, is_json_output=True)

    def gerar_imagem_sintoma_descricao_textual(self, jogador: Jogador, sintoma_para_desenhar: str):
        prompt_desenho = f"""
        Dr(a). {jogador.nome} ({jogador.classe.value['nome']}, Artista Frustrado) desenhou: "{sintoma_para_desenhar}".
        Descreva, de forma cômica/exagerada, como um artista incompreendido, esse desenho (1-2 frases).
        Ex: Sintoma: "Rash cutâneo". Descrição: "Behold! 'A Agonia Rubra'! Pápulas como luas sangrentas! Ou só bolhas. Mas com alma!"
        """
        return self._gerar_conteudo_seguro(prompt_desenho)