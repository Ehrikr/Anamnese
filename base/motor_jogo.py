class JogoMedicoRPG:
    def __init__(self):
        self.jogador = None
        self.gemini_api = GeminiAPI(generative_model) # Usa o modelo global configurado
        self.caso_atual = None
        self.casos_concluidos_ids = []

    def _aplicar_habilidades_inicio_caso(self):
        if not self.caso_atual or not self.jogador : return
        if self.jogador.classe == ClassesMedico.CLINICO_GERAL and self.caso_atual.sintomas_reais_ocultos:
            sintomas_nao_revelados_ainda = [s for s in self.caso_atual.sintomas_reais_ocultos if s not in self.caso_atual.sintomas_revelados_jogador]
            if sintomas_nao_revelados_ainda:
                sintoma_revelado_habilidade = random.choice(sintomas_nao_revelados_ainda)
                self.caso_atual.sintomas_revelados_jogador.append(sintoma_revelado_habilidade)
                msg_habilidade = f"💡 ({self.jogador.classe.value['habilidade']}) Você tem um palpite... parece que o paciente também apresenta '{sintoma_revelado_habilidade}', embora não tenha mencionado claramente."
                self.caso_atual.adicionar_progresso_cena(msg_habilidade) 
        elif self.jogador.classe == ClassesMedico.ENFERMEIRO and self.caso_atual.pistas_falsas_criativas:
            pistas_ativas_ainda = [p for p in self.caso_atual.pistas_falsas_criativas if p not in self.caso_atual.pistas_falsas_descartadas]
            if pistas_ativas_ainda:
                pista_descartada_habilidade = random.choice(pistas_ativas_ainda)
                self.caso_atual.pistas_falsas_descartadas.append(pista_descartada_habilidade)
                msg_habilidade = f"🎯 ({self.jogador.classe.value['habilidade']}) Sua intuição de enfermagem apita! A informação sobre '{pista_descartada_habilidade}' parece ser um completo alarme falso."
                self.caso_atual.adicionar_progresso_cena(msg_habilidade)

    def iniciar_novo_jogo(self):
        print_lentamente("Bem-vindo ao Plantão 24h: O Mistério do Paciente X!")
        print_lentamente("Anos 80. Hospital decadente. Você é a nova esperança (ou desastre ambulante).")
        nome = ""
        while not nome.strip(): nome = input("Qual o seu nome, Doutor(a)? ").strip()

        print_lentamente("\nEscolha sua Classe Médica:")
        for i, c_enum in enumerate(ClassesMedico): 
            print_lentamente(f"{i+1}. {c_enum.value['nome']}: {c_enum.value['descricao_habilidade']} (Ex: {c_enum.value['exemplo_uso']})")
        classe_idx = solicitar_input_numerico("Sua Classe: ", 1, len(ClassesMedico))
        classe_esc = list(ClassesMedico)[classe_idx-1]

        print_lentamente("\nEscolha seu Traço de Personalidade:")
        for i, t_enum in enumerate(TracosMedico): 
            ex_traco = TracosMedico[t_enum.name].value.get('exemplo', t_enum.value['descricao']) 
            print_lentamente(f"{i+1}. {t_enum.value['nome']}: {ex_traco}")
        traco_idx = solicitar_input_numerico("Seu Traço: ", 1, len(TracosMedico))
        traco_esc = list(TracosMedico)[traco_idx-1]

        self.jogador = Jogador(nome, classe_esc, traco_esc)
        print_lentamente(f"\nBem-vindo(a), Dr(a). {self.jogador.nome}!")
        print_lentamente(str(self.jogador))
        
        combinacao = self.jogador.verificar_combinacao_especial()
        if combinacao:
            msg_combinacao = combinacao.get("interacao_unica", combinacao if isinstance(combinacao, str) else "Efeito especial ativo!")
            print_lentamente(f"\n✨ Interação Especial Classe/Traço: {msg_combinacao} ✨")
            if isinstance(combinacao, dict) and "respostas_exemplo" in combinacao:
                print_lentamente("  Exemplos de como isso pode se manifestar:")
                for tipo_resp, ex_resp in combinacao["respostas_exemplo"]:
                    print_lentamente(f"  - Se escolher {tipo_resp}: \"{ex_resp}\"")
        
        self.casos_concluidos_ids = []
        self.loop_principal_jogo()

    def carregar_jogo_salvo(self):
        jogador_carregado, cids = carregar_jogo()
        if jogador_carregado:
            self.jogador = jogador_carregado; self.casos_concluidos_ids = cids
            print_lentamente(f"\nBem-vindo(a) de volta, Dr(a). {self.jogador.nome}!")
            print_lentamente(str(self.jogador))
            self.loop_principal_jogo()
        else:
            print_lentamente("Falha ao carregar. Iniciando um novo jogo...")
            time.sleep(1)
            self.iniciar_novo_jogo()

    def _gerar_e_iniciar_novo_caso(self):
        if not self.gemini_api.model:
            print_lentamente("API Gemini não configurada. Impossível gerar caso.")
            return False

        print_lentamente("\nBuscando prontuário de um novo paciente misterioso...")
        temas_possiveis = [
            "Paciente com pele de cor estranha e delírios", "O Homem da Perna Invisível (dor fantasma com complicações)",
            "Acidente com Múltiplas Vítimas (foco em um caso principal, mas com menção ao caos)", 
            "Paciente que Brilha no Escuro (inspirado em House S05E16)", 
            "A Enfermeira que Não Sentia Dor (inspirado em House S02E12, com condição subjacente)", 
            "O Homem que Mordeu o Cão (hipocondria com sintoma real leve)",
            "O Homem que Falava com Plantas (sintomas psicóticos com causa orgânica, tipo Tuberculose cerebral)", 
            "Homem diz que engoliu um Bluetooth (corpo estranho + outra condição inesperada)"
        ]
        if self.jogador.casos_resolvidos < 2: 
            tema_escolhido = random.choice(temas_possiveis[:4] + [None]) 
            dificuldade_sugerida = "fácil" if self.jogador.casos_resolvidos == 0 else "normal"
        else:
            tema_escolhido = random.choice(temas_possiveis + [None, None]) 
            dificuldade_sugerida = random.choice(["normal", "difícil", "bizarro" if self.jogador.fama_de_maluco > 10 else "difícil"])
        
        print_lentamente(f"(Sorteando caso... tema possível: '{tema_escolhido if tema_escolhido else 'Totalmente Aleatório'}', dificuldade: {dificuldade_sugerida})")
        dados_caso_json = self.gemini_api.gerar_caso_clinico(self.jogador, tema_caso=tema_escolhido, dificuldade=dificuldade_sugerida, casos_anteriores_ids=self.casos_concluidos_ids)

        if not isinstance(dados_caso_json, dict): 
            print_lentamente(f"⚠️ Falha crítica ao gerar caso (não é JSON): {str(dados_caso_json)[:500]}...")
            return False
        
        try:
            self.caso_atual = CasoClinico(**dados_caso_json)
            self.caso_atual.jogador = self.jogador 
            print_lentamente(f"\n📜 NOVO CASO: {self.caso_atual.titulo_caso} 📜")
            
            self.caso_atual.adicionar_progresso_cena(self.caso_atual.introducao_narrativa_imersiva)
            self._aplicar_habilidades_inicio_caso() 
            
            self.caso_atual.progresso_narrativa_cena_atual = [self.caso_atual.introducao_narrativa_imersiva.split('\n')[-1]] 
            self._atualizar_opcoes_de_cena_caso_atual() 

            return True
        except TypeError as te: 
            print_lentamente(f"❌ Erro ao criar CasoClinico com dados da API (TypeError): {te}")
            print_lentamente(f"Dados recebidos que causaram o erro: {json.dumps(dados_caso_json, indent=2)}")
            return False
        except KeyError as ke:
            print_lentamente(f"❌ Erro ao criar CasoClinico (Chave faltando: {ke}).")
            print_lentamente(f"Dados recebidos: {json.dumps(dados_caso_json, indent=2)}")
            return False
        except Exception as e:
            print_lentamente(f"❌ Erro inesperado ao iniciar novo caso: {type(e).__name__} - {e}")
            print_lentamente(f"Dados recebidos: {json.dumps(dados_caso_json, indent=2)}")
            return False

    def _atualizar_opcoes_de_cena_caso_atual(self): # NOVO MÉTODO
        if not self.caso_atual: return
        print_lentamente("\n(Gerando novas opções de interação para a cena...)") # Movido para antes da chamada da API
        opcoes_geradas = self.gemini_api.gerar_opcoes_de_cena(
            self.jogador, 
            self.caso_atual,
            self.caso_atual.progresso_narrativo_cena_atual 
        )
        if isinstance(opcoes_geradas, list) and len(opcoes_geradas) == 8 and \
           all(isinstance(opt, dict) and "tom" in opt and "opcao_texto" in opt for opt in opcoes_geradas):
            self.caso_atual.opcoes_cena_atuais = opcoes_geradas
        else:
            print_lentamente(f"⚠️ Aviso: Não foi possível gerar as 8 opções de cena formatadas corretamente.")
            print_lentamente(f"   Resposta da API: {str(opcoes_geradas)[:200]}...")
            self.caso_atual.opcoes_cena_atuais = [
                {"tom": "Pragmática", "opcao_texto": "Reavaliar os sinais vitais do paciente."},
                {"tom": "Empática", "opcao_texto": "Perguntar ao paciente como ele está se sentindo agora."},
                {"tom": "Cautelosa", "opcao_texto": "Aguardar e observar por um momento."} ,
                {"tom": "Cínica", "opcao_texto": "Perguntar se o paciente já pensou em ser ator."},
                {"tom": "Filosófica", "opcao_texto": "Refletir sobre a natureza da queixa principal."},
                {"tom": "Absurda", "opcao_texto": "Verificar se o paciente tem algum objeto amaldiçoado consigo."},
                {"tom": "Heróica", "opcao_texto": "Declarar que este caso será resolvido com brilhantismo."},
                {"tom": "Desastre Iminente", "opcao_texto": "Sugerir um tratamento experimental com sanguessugas."}
            ] 
            random.shuffle(self.caso_atual.opcoes_cena_atuais) 
            self.caso_atual.opcoes_cena_atuais = self.caso_atual.opcoes_cena_atuais[:8]

    def _chance_intervencao_npc(self):
        if not self.caso_atual or random.random() > 0.20: 
            return
        
        npc_nomes = list(NPC_DATA.keys())
        npc_escolhido = random.choice(npc_nomes)
        
        resumo_situacao_para_npc = (
            f"O Dr(a). {self.jogador.nome} está atendendo o caso '{self.caso_atual.titulo_caso}'. "
            f"Sintomas conhecidos pelo jogador: {', '.join(list(set(self.caso_atual.sintomas_revelados_jogador)))}. "
            f"Hipóteses atuais do jogador: {', '.join(self.caso_atual.hipoteses_jogador) if self.caso_atual.hipoteses_jogador else 'nenhuma clara'}."
        )
        
        # Adiciona a última interação da cena para dar mais contexto ao NPC
        ultima_interacao_cena = self.caso_atual.progresso_narrativo_cena_atual[-1] if self.caso_atual.progresso_narrativo_cena_atual else "Início da cena."
        contexto_npc_completo = f"{resumo_situacao_para_npc} Interação mais recente: {ultima_interacao_cena}"


        # Não usar adicionar_progresso_cena aqui para o print inicial, pois ele já será usado para o diálogo do NPC
        print_lentamente(f"\n--- Intervenção Inesperada de {npc_escolhido}! ---")
        dialogo_npc = self.gemini_api.gerar_dialogo_npc(
            npc_escolhido, 
            {"titulo_caso": self.caso_atual.titulo_caso, "resumo_situacao_para_npc": contexto_npc_completo}, 
            self.jogador
        )
        if "Erro" not in dialogo_npc:
            self.caso_atual.adicionar_progresso_cena(f"{npc_escolhido}: \"{dialogo_npc}\"") # Usa adicionar_progresso_cena
            if npc_escolhido == "Dr. Howser": self.caso_atual.dicas_howser_caso.append(dialogo_npc)
            elif npc_escolhido == "Dra. Meridee Grey": self.caso_atual.diario_meridee_caso.append(dialogo_npc)
        else:
            self.caso_atual.adicionar_progresso_cena(f"{npc_escolhido} parece que ia dizer algo, mas se distrai com uma mosca particularmente interessante.")

    def interagir_com_opcao_de_cena(self, opcao_dict): 
        if not self.caso_atual: return
        
        texto_acao = opcao_dict["opcao_texto"]
        tom_acao = opcao_dict["tom"]

        self.caso_atual.adicionar_progresso_cena(f"\nVocê ({tom_acao}): \"{texto_acao}\"") # Usa adicionar_progresso_cena
        
        narrativa_resposta = self.gemini_api.gerar_resposta_interativa(
            self.jogador, 
            self.caso_atual, 
            texto_acao, 
            tom_acao     
        )
        
        if isinstance(narrativa_resposta, str) and "Erro" in narrativa_resposta:
            self.caso_atual.adicionar_progresso_cena(f"Houve um problema na resposta da IA: {narrativa_resposta}")
        else:
            self.caso_atual.adicionar_progresso_cena(narrativa_resposta) 

            for sint_real in self.caso_atual.sintomas_reais_ocultos:
                if f"'{sint_real.lower()}'" in narrativa_resposta.lower() and sint_real not in self.caso_atual.sintomas_revelados_jogador:
                    self.caso_atual.sintomas_revelados_jogador.append(sint_real)
                    self.caso_atual.adicionar_progresso_cena(f"🔎 (Sintoma '{sint_real}' foi revelado/confirmado através da interação!)")
        
        self.caso_atual.opcoes_cena_atuais = [] # Força regenerar opções para a próxima "sub-cena"

    def conduzir_caso(self):
        if not self.caso_atual: 
            print_lentamente("⚠️ Nenhum caso ativo para conduzir.")
            return
        
        while self.caso_atual and not self.caso_atual.resolvido:
            # Não chamar exibir_resumo_mental aqui automaticamente. Deixe como uma ação do jogador.
            print_lentamente(f"\n--- Investigando: {self.caso_atual.titulo_caso} ---")
            self._chance_intervencao_npc() 

            if not self.caso_atual.opcoes_cena_atuais: 
                self._atualizar_opcoes_de_cena_caso_atual()

            menu_acoes_cena = {} 
            menu_acoes_fixas = {} 
            
            print_lentamente("\nEscolha uma Ação/Diálogo para a Cena:")
            if self.caso_atual.opcoes_cena_atuais:
                for i, opcao_data in enumerate(self.caso_atual.opcoes_cena_atuais):
                    menu_acoes_cena[i + 1] = opcao_data 
                    print_lentamente(f"  {i + 1}. [{opcao_data['tom']}] {opcao_data['opcao_texto']}")
            else:
                print_lentamente("  (A IA não gerou opções de cena. Verifique a API ou tente uma ação fixa.)")

            next_fixed_idx = (len(menu_acoes_cena) if menu_acoes_cena else 0) + 1

            print_lentamente("\nOutras Ações Possíveis:")
            idx_hipotese = next_fixed_idx; menu_acoes_fixas[idx_hipotese] = {"tipo": "hipotese", "texto": "Adicionar/Ver hipóteses diagnósticas"}; print_lentamente(f"  {idx_hipotese}. {menu_acoes_fixas[idx_hipotese]['texto']}"); next_fixed_idx += 1
            idx_howser = next_fixed_idx; menu_acoes_fixas[idx_howser] = {"tipo": "dica_howser", "texto": "(Modo Médico) Pedir dica ao Dr. Howser"}; print_lentamente(f"  {idx_howser}. {menu_acoes_fixas[idx_howser]['texto']}"); next_fixed_idx += 1
            idx_meridee = next_fixed_idx; menu_acoes_fixas[idx_meridee] = {"tipo": "dica_meridee", "texto": "(Modo Médico) Consultar diário da Dra. Meridee"}; print_lentamente(f"  {idx_meridee}. {menu_acoes_fixas[idx_meridee]['texto']}"); next_fixed_idx += 1
            
            idx_artista = -1
            if self.jogador.traco == TracosMedico.ARTISTA_FRUSTRADO:
                idx_artista = next_fixed_idx; menu_acoes_fixas[idx_artista] = {"tipo": "desenhar", "texto": "Desenhar um sintoma/observação"}; print_lentamente(f"  {idx_artista}. {menu_acoes_fixas[idx_artista]['texto']}"); next_fixed_idx += 1
            
            idx_resumo = next_fixed_idx; menu_acoes_fixas[idx_resumo] = {"tipo": "resumo_mental", "texto": "Organizar pensamentos / Revisar prontuário"}; print_lentamente(f"  {idx_resumo}. {menu_acoes_fixas[idx_resumo]['texto']}"); next_fixed_idx +=1

            idx_diagnostico = next_fixed_idx; menu_acoes_fixas[idx_diagnostico] = {"tipo": "diagnosticar", "texto": "TENTAR DIAGNÓSTICO FINAL"}; print_lentamente(f"  {idx_diagnostico}. {menu_acoes_fixas[idx_diagnostico]['texto']}"); next_fixed_idx += 1
            idx_salvar = next_fixed_idx; menu_acoes_fixas[idx_salvar] = {"tipo": "salvar", "texto": "Salvar e Voltar ao Menu Principal"}; print_lentamente(f"  {idx_salvar}. {menu_acoes_fixas[idx_salvar]['texto']}"); 
            
            max_total_option_val = next_fixed_idx -1 # Corrigido para pegar o último índice usado

            escolha_num_str = input(f"Sua ação (1-{max_total_option_val}): ").strip()
            if not escolha_num_str: continue
            try:
                escolha_num = int(escolha_num_str)
                if not (1 <= escolha_num <= max_total_option_val): raise ValueError
            except ValueError:
                print_lentamente("Opção inválida. Tente novamente.")
                continue

            if escolha_num in menu_acoes_cena:
                opcao_de_cena_escolhida = menu_acoes_cena[escolha_num]
                self.interagir_com_opcao_de_cena(opcao_de_cena_escolhida)
            elif escolha_num in menu_acoes_fixas:
                acao_fixa_obj = menu_acoes_fixas[escolha_num]
                tipo_acao_fixa = acao_fixa_obj["tipo"]

                if tipo_acao_fixa == "hipotese": self.listar_ou_add_hipoteses()
                elif tipo_acao_fixa == "dica_howser": self.pedir_dica_npc("Dr. Howser")
                elif tipo_acao_fixa == "dica_meridee": self.pedir_dica_npc("Dra. Meridee Grey")
                elif tipo_acao_fixa == "desenhar" and self.jogador.traco == TracosMedico.ARTISTA_FRUSTRADO: self.desenhar_sintoma()
                elif tipo_acao_fixa == "resumo_mental": self.caso_atual.exibir_resumo_mental(self.jogador.nome) 
                elif tipo_acao_fixa == "diagnosticar": self.propor_diagnostico_final()
                elif tipo_acao_fixa == "salvar":
                    salvar_jogo(self.jogador, self.casos_concluidos_ids)
                    self.caso_atual = None 
                    return 
            else:
                print_lentamente("Opção não reconhecida.")

            if self.caso_atual and self.caso_atual.resolvido:
                # A narrativa do desfecho já foi impressa por propor_diagnostico_final
                print_lentamente("\n[CASO CONCLUÍDO]")
                self.caso_atual = None 
                break 
            
            time.sleep(0.3)
    
    # Manter os outros métodos como:
    # listar_ou_add_hipoteses(self) -> usar adicionar_progresso_cena se quiser que faça parte do histórico da cena
    # pedir_dica_npc(self, npc_nome_param) -> usar adicionar_progresso_cena
    # desenhar_sintoma(self) -> usar adicionar_progresso_cena
    # propor_diagnostico_final(self) -> OK
    # finalizar_caso_com_diagnostico(self, diagnostico_proposto) -> OK
    # loop_principal_jogo(self) -> OK

    def listar_ou_add_hipoteses(self):
        if not self.caso_atual: return
        print_lentamente("\n📋 Suas hipóteses diagnósticas atuais:")
        if not self.caso_atual.hipoteses_jogador: print_lentamente("(Nenhuma ainda.)")
        else:
            for i, h in enumerate(self.caso_atual.hipoteses_jogador): print_lentamente(f"  {i+1}. {h}")
        
        nova_h = input("Adicionar/refinar hipótese (ou Enter para voltar): ").strip()
        if nova_h:
            self.caso_atual.hipoteses_jogador.append(nova_h)
            self.caso_atual.adicionar_progresso_cena(f"Você pondera e anota uma nova suspeita: {nova_h}.") 
            if "lúpus" in nova_h.lower().strip() and self.caso_atual.id_caso != "caso_secreto_do_lupus_real_007": 
                self.caso_atual.adicionar_progresso_cena("Uma voz familiar ecoa em sua mente, soando suspeitamente como Dr. Howser: 'É claro que você pensou em lúpus. NUNCA é lúpus.'")
            elif "lúpus" in nova_h.lower().strip() and self.caso_atual.id_caso == "caso_secreto_do_lupus_real_007":
                 self.caso_atual.adicionar_progresso_cena("Por um instante, você quase ouve Dr. Howser engasgar. 'Espera... só desta vez... talvez.'")
            
            if self.jogador.traco == TracosMedico.TEORICO_CONSPIRACAO and random.random() < 0.4:
                hipotese_conspiratoria = self.gemini_api._gerar_conteudo_seguro(
                    f"Dr(a). {self.jogador.nome}, um Teórico da Conspiração, considera a hipótese '{nova_h}'. "
                    f"Gere uma hipótese alternativa BIZARRA e CONSPIRATÓRIA que ele/ela também consideraria para o caso '{self.caso_atual.titulo_caso}' "
                    f"com sintomas {self.caso_atual.sintomas_revelados_jogador}. (1 frase curta)"
                )
                if "Erro" not in hipotese_conspiratoria:
                    self.caso_atual.hipoteses_jogador.append(f"{hipotese_conspiratoria} (Conspiração)")
                    self.caso_atual.adicionar_progresso_cena(f"👽 (E se... e se '{hipotese_conspiratoria}' for a verdadeira causa? Sua mente borbulha com as possibilidades.)")
                    self.jogador.fama_de_maluco +=1

    def pedir_dica_npc(self, npc_nome_param): 
        if not self.caso_atual: return
        lista_dicas_ou_reflexoes = []
        prefixo_narrativo = ""

        if npc_nome_param == "Dr. Howser":
            lista_dicas_ou_reflexoes = self.caso_atual.dicas_howser_caso
            prefixo_narrativo = "Dr. Howser resmunga do canto da sala:"
        elif npc_nome_param == "Dra. Meridee Grey": 
            lista_dicas_ou_reflexoes = self.caso_atual.diario_meridee_caso
            prefixo_narrativo = "(Uma voz interior, como a da Dra. Meridee, sussurra:"

        if lista_dicas_ou_reflexoes:
            item_escolhido = random.choice(lista_dicas_ou_reflexoes)
            self.caso_atual.adicionar_progresso_cena(f"{prefixo_narrativo} \"{item_escolhido}\"")
        else: 
            contexto_geral_para_dica = f"O jogador Dr(a). {self.jogador.nome} está investigando o caso '{self.caso_atual.titulo_caso}'. Sintomas atuais observados: {', '.join(list(set(self.caso_atual.sintomas_revelados_jogador)))}. O diagnóstico real do caso é {self.caso_atual.diagnostico_real_medico} (jogador não sabe)."
            nova_interacao_npc = self.gemini_api.gerar_dialogo_npc(npc_nome_param, 
                {"titulo_caso": self.caso_atual.titulo_caso, "resumo_situacao_para_npc": contexto_geral_para_dica}, 
                self.jogador)
            
            if "Erro" in nova_interacao_npc:
                self.caso_atual.adicionar_progresso_cena(f"{npc_nome_param} parece estar muito ocupado para dar atenção agora. ({nova_interacao_npc})")
            else:
                if npc_nome_param == "Dr. Howser": self.caso_atual.dicas_howser_caso.append(nova_interacao_npc)
                elif npc_nome_param == "Dra. Meridee Grey": self.caso_atual.diario_meridee_caso.append(nova_interacao_npc)
                self.caso_atual.adicionar_progresso_cena(f"{npc_nome_param} aparece de repente e comenta: \"{nova_interacao_npc}\"")

    def desenhar_sintoma(self):
        if not self.caso_atual: return
        if self.jogador.traco != TracosMedico.ARTISTA_FRUSTRADO: 
            # Esta mensagem não deve ser adicionada ao progresso da cena se o jogador não pode fazer
            print_lentamente("Apenas Artistas Frustrados podem usar esta nobre forma de diagnóstico.") 
            return
        
        sint_desenhar = input("Qual sintoma ou observação você quer imortalizar em sua 'arte'?\n> ").strip()
        if not sint_desenhar: 
            self.caso_atual.adicionar_progresso_cena("A inspiração artística não veio desta vez.")
            return

        desc_desenho_gerada = self.gemini_api.gerar_imagem_sintoma_descricao_textual(self.jogador, sint_desenhar)
        self.caso_atual.adicionar_progresso_cena(f"\n--- 🎨 Obra Prima Incompreendida de Dr(a). {self.jogador.nome} 🎨 ---")
        if "Erro" in desc_desenho_gerada:
            self.caso_atual.adicionar_progresso_cena(f"Sua tentativa de desenhar foi... um borrão. (Erro da API: {desc_desenho_gerada})")
        else:
            self.caso_atual.adicionar_progresso_cena(desc_desenho_gerada)
            self.caso_atual.adicionar_progresso_cena("(Como o hospital não tem verba para impressoras coloridas nos anos 80, você descreve sua visão gloriosa aos colegas menos iluminados, esperando que entendam sua genialidade).")
            self.jogador.fama_de_maluco += random.randint(0,1)

    def propor_diagnostico_final(self):
        if not self.caso_atual: return
        
        if not self.caso_atual.opcoes_diagnostico_atuais: 
            self._atualizar_opcoes_diagnostico_caso_atual()

        if not self.caso_atual.opcoes_diagnostico_atuais: # Se ainda falhou
            self.caso_atual.adicionar_progresso_cena("O sistema de classificação de doenças parece estar em manutenção. Impossível listar opções de diagnóstico agora.")
            diag_proposto_texto = input(f"FALLBACK: Qual o seu diagnóstico final para {self.caso_atual.paciente_info.get('nome', 'este paciente')}?\n> ").strip()
            if not diag_proposto_texto:
                 self.caso_atual.adicionar_progresso_cena("Você decide esperar mais um pouco.")
                 return
            self.finalizar_caso_com_diagnostico(diag_proposto_texto)
            return

        print_lentamente("\nEscolha o Diagnóstico Final:")
        for i, diag_opcao in enumerate(self.caso_atual.opcoes_diagnostico_atuais):
            print_lentamente(f"  {i+1}. {diag_opcao}")
        
        escolha_idx_str = input(f"Seu diagnóstico (1-{len(self.caso_atual.opcoes_diagnostico_atuais)}): ").strip()
        try:
            escolha_idx = int(escolha_idx_str) -1
            if not (0 <= escolha_idx < len(self.caso_atual.opcoes_diagnostico_atuais)):
                raise ValueError
            diagnostico_escolhido = self.caso_atual.opcoes_diagnostico_atuais[escolha_idx]
        except (ValueError, IndexError):
            self.caso_atual.adicionar_progresso_cena("Escolha inválida. Você decide ponderar mais.")
            return
        
        self.finalizar_caso_com_diagnostico(diagnostico_escolhido)

    def finalizar_caso_com_diagnostico(self, diagnostico_proposto):
        if not self.caso_atual: return 
        self.caso_atual.adicionar_progresso_cena(f"\nVocê declara com (incerta?) convicção: \"O diagnóstico é... {diagnostico_proposto}!\"")
        # print_lentamente(f"\nProcessando seu veredito: '{diagnostico_proposto}'...") # Removido, já faz parte do adicionar_progresso_cena
        desfecho_obj_json = self.gemini_api.gerar_desfecho_caso(self.jogador, self.caso_atual, diagnostico_proposto)

        if not isinstance(desfecho_obj_json, dict):
            print_lentamente(f"⚠️ Falha crítica ao gerar desfecho (não é JSON válido): {str(desfecho_obj_json)[:500]}...")
            self.caso_atual.adicionar_progresso_cena("O sistema de prontuários explodiu (metaforicamente). O destino do paciente é um mistério cósmico.")
            self.caso_atual.resolvido = True 
            self.jogador.reputacao = max(0, self.jogador.reputacao - 2) 
            return
        
        try:
            # Usar adicionar_progresso_cena para a narrativa do desfecho para manter consistência
            self.caso_atual.adicionar_progresso_cena("\n--- 🩺 DESFECHO DO CASO 🩺 ---")
            self.caso_atual.adicionar_progresso_cena(desfecho_obj_json["desfecho_narrativa"])
            self.caso_atual.resolvido = True
            self.caso_atual.desfecho_final = desfecho_obj_json

            self.jogador.reputacao = max(0, min(100, self.jogador.reputacao + desfecho_obj_json.get("reputacao_delta", 0)))
            self.jogador.pontuacao_diagnostica += desfecho_obj_json.get("pontuacao_diagnostica_delta", 0)
            self.jogador.fama_de_maluco = max(0, self.jogador.fama_de_maluco + desfecho_obj_json.get("fama_de_maluco_delta", 0))
            self.jogador.casos_resolvidos += 1
            if self.caso_atual.id_caso not in self.casos_concluidos_ids:
                 self.casos_concluidos_ids.append(self.caso_atual.id_caso)

            # A Ficha Educativa é mais um relatório, então print_lentamente direto é ok aqui.
            print_lentamente(f"\n--- {desfecho_obj_json.get('ficha_educativa_titulo','Ficha Educativa do Caso')} ---")
            print_lentamente(f"Seu Diagnóstico: {desfecho_obj_json['diagnostico_final_jogador']}")
            print_lentamente(f"Diagnóstico Correto: {desfecho_obj_json['diagnostico_correto_caso']}")
            print_lentamente(f"Você acertou? {'Sim!' if desfecho_obj_json['acertou'] else 'Não desta vez.'}")
            print_lentamente(f"\nDoença Real: {desfecho_obj_json['doenca_real_ficha']}")
            print_lentamente(f"Explicação Simplificada: {desfecho_obj_json['explicacao_doenca_ficha']}")
            print_lentamente(f"Erro Comum: {desfecho_obj_json['erro_comum_ficha']}")
            print_lentamente(f"Dica para Vida Real: {desfecho_obj_json['dica_vida_real_ficha']}")
            
            if desfecho_obj_json.get("comentario_howser_final"): 
                print_lentamente(f"Dr. Howser comenta sarcasticamente: \"{desfecho_obj_json['comentario_howser_final']}\"")
            if desfecho_obj_json.get("comentario_meridee_final"): 
                print_lentamente(f"Dra. Meridee reflete poeticamente: \"{desfecho_obj_json['comentario_meridee_final']}\"")
            
            print_lentamente(f"\nSeu status atual: Reputação {self.jogador.reputacao}, Pontos de Diagnóstico {self.jogador.pontuacao_diagnostica}, Fama de Maluco {self.jogador.fama_de_maluco}")

        except KeyError as e: 
            print_lentamente(f"❌ Erro ao processar dados do desfecho (chave faltando: {e}).")
            print_lentamente(f"Dados recebidos do desfecho: {json.dumps(desfecho_obj_json, indent=2)}")
            self.caso_atual.adicionar_progresso_cena("Um erro bizarro ocorreu nos arquivos do hospital. O desfecho é... nebuloso.")
        except Exception as e: 
            print_lentamente(f"❌ Erro inesperado ao finalizar o caso: {type(e).__name__} - {e}")
            self.caso_atual.adicionar_progresso_cena("O hospital está um caos! Algo deu muito errado com a papelada.")

    def loop_principal_jogo(self):
        if not self.jogador: 
            print_lentamente("Erro crítico: Jogador não foi inicializado. Saindo.")
            return

        rodando = True
        while rodando:
            print_lentamente(f"\n🏥 Hospital Anos 80 - Dr(a). {self.jogador.nome} 🏥")
            print_lentamente(f"Rep: {self.jogador.reputacao} | Casos Resolvidos: {self.jogador.casos_resolvidos} | Diag. Certos: {self.jogador.pontuacao_diagnostica} | Fama de Maluco: {self.jogador.fama_de_maluco}")
            print_lentamente("--- Menu Principal do Plantão ---")
            print_lentamente("1. Atender próximo paciente (Novo Caso Clínico)")
            print_lentamente("2. Ver Status Completo do Médico")
            print_lentamente("3. Salvar Jogo (Progresso do Jogador)")
            print_lentamente("4. Sair do Plantão (Encerrar Jogo)")

            escolha_menu_str = input(f"Sua escolha (1-4): ").strip()
            if not escolha_menu_str: continue 
            
            try:
                escolha_menu = int(escolha_menu_str)
                if not (1 <= escolha_menu <= 4): raise ValueError
            except ValueError:
                print_lentamente("Opção inválida. Tente novamente.")
                continue

            if escolha_menu == 1:
                if self._gerar_e_iniciar_novo_caso(): 
                    self.conduzir_caso()
                    if self.caso_atual is None: 
                        print_lentamente("\nRetornando ao saguão principal do hospital...")
                else: 
                    print_lentamente("⚠️ Não foi possível iniciar um novo caso. Verifique a API ou tente mais tarde.")
            elif escolha_menu == 2: 
                print_lentamente("\n--- Status Completo do Médico ---")
                print_lentamente(str(self.jogador))
            elif escolha_menu == 3: 
                salvar_jogo(self.jogador, self.casos_concluidos_ids)
            elif escolha_menu == 4:
                print_lentamente("Obrigado por jogar 'Plantão 24h: O Mistério do Paciente X'! Até o próximo (caótico) plantão.")
                rodando = False
            
            if self.jogador.reputacao <= 0:
                print_lentamente("\n--- ☠️ FIM DE JOGO POR REPUTAÇÃO NULA ☠️ ---")
                # ... (manter mensagens de game over)
                rodando = False
            
            if self.jogador.fama_de_maluco >= 20 and random.random() < (0.1 * (self.jogador.fama_de_maluco - 19)): 
                print_lentamente("\n--- 🤪 FIM DE JOGO POR LOUCURA EXCESSIVA 🤪 ---")
                # ... (manter mensagens de game over)
                rodando = False
        print_lentamente("Fim da simulação.")