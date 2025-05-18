class ClassesMedico(Enum):
    CLINICO_GERAL = {"nome": "Clínico Geral", "habilidade": "Diagnóstico Rápido", "descricao_habilidade": "Revela 1 sintoma real oculto.", "exemplo_uso": "Nota febre persistente."}
    ENFERMEIRO = {"nome": "Enfermeiro(a)", "habilidade": "Triagem Afiada", "descricao_habilidade": "Descarta 1 pista falsa.", "exemplo_uso": "Relato de unicórnios é irrelevante."}
    DERMATOLOGISTA = {"nome": "Dermatologista", "habilidade": "Olho Clínico", "descricao_habilidade": "Identifica doenças de pele com precisão.", "exemplo_uso": "Manchas são psoríase, não aliens."}
    CIRURGIAO = {"nome": "Cirurgião(ã)", "habilidade": "Mãos de Aço", "descricao_habilidade": "Permite cirurgias arriscadas.", "exemplo_uso": "Opera sem exames... tumor benigno. Sorte!"}
    PSICOLOGO = {"nome": "Psicólogo(a)", "habilidade": "Leitura Emocional", "descricao_habilidade": "Descobre traumas ocultos.", "exemplo_uso": "Paciente mentiu, medo de hospitais."}
    FARMACEUTICO = {"nome": "Farmacêutico(a)", "habilidade": "Interação Química", "descricao_habilidade": "Detecta conflitos medicamentosos.", "exemplo_uso": "Remédio causa alucinações. Bingo!"}
    PEDIATRA = {"nome": "Pediatra", "habilidade": "Voz Acalmante", "descricao_habilidade": "Reduz resistência de crianças/pais.", "exemplo_uso": "Mãe se acalma e conta que criança comeu tinta."}
    CARDIOLOGISTA = {"nome": "Cardiologista", "habilidade": "Ritmo Cardíaco", "descricao_habilidade": "Detecta problemas cardíacos sem equipamento.", "exemplo_uso": "ECG normal, mas sente sopro... embolia!"}

class TracosMedico(Enum):
    CINICO = {"nome": "Cínico", "descricao": "+Sarcasmo, NPCs reagem."}
    EMPATICO = {"nome": "Empático", "descricao": "+Cooperação, -precisão."}
    TEORICO_CONSPIRACAO = {"nome": "Teórico da Conspiração", "descricao": "Pistas absurdas, acertos acidentais."}
    PERFECCIONISTA = {"nome": "Perfeccionista", "descricao": "Exige 100% certeza, demora."}
    DESASTRADO = {"nome": "Desastrado", "descricao": "Erros hilários, ganha simpatia."}
    VICIADO_TRABALHO = {"nome": "Viciado em Trabalho", "descricao": "Ignora cansaço, -empatia."}
    CURIOSO = {"nome": "Curioso", "descricao": "Perguntas aleatórias revelam pistas."}
    ARTISTA_FRUSTRADO = {"nome": "Artista Frustrado", "descricao": "Desenha sintomas (descrição textual)."}

COMBINACOES_ESPECIAIS = {
    ("CIRURGIAO", "DESASTRADO"): {"interacao_unica": "Opera o joelho errado... mas descobre um tumor!"},
    ("PSICOLOGO", "TEORICO_CONSPIRACAO"): {"interacao_unica": "Paciente controlado por aliens... Você concorda! (Revela esquizofrenia)"},
    ("CLINICO_GERAL", "TEORICO_CONSPIRACAO"): {
        "interacao_unica": "Sintomas comuns são 'sinais de controle mental'.",
        "respostas_exemplo": [("Pragmático", "Checar virose... ou chip da CIA."), ("Absurdo", "Radiação de torre 5G!")],
        "reacao_paciente_absurdo": "Doutor, só comi batata estragada..."
    },
    # ... (adicione TODAS as suas outras combinações aqui)
     ("DERMATOLOGISTA", "ARTISTA_FRUSTRADO"): {
        "interacao_unica": "Desenha sintomas como obras de arte, confundindo todos.",
        "respostas_exemplo": [("Pragmático", "Essa micose parece um Van Gogh!"), ("Absurdo", "Vou chamar essa doença de 'Monstro das Pústulas'.")],
        "reacao_paciente_absurdo": "Isso é uma emergência ou uma exposição?"
    },
}


class OpcoesDialogo(Enum):
    CINICO = "Cínica"; EMPATICO = "Empática"; PRAGMATICO = "Pragmático"; CAUTELOSO = "Cauteloso"
    FILOSOFICO = "Filosófico"; ABSURDO = "Absurdo"; HEROI = "Herói"; DESASTRE_IMINENTE = "Desastre Iminente"

NPC_DATA = {
    "Dr. Howser": {"descricao": "Cínico, manca.", "falas_iconicas": ["Todo mundo mente.", "NÃO é lúpus!"], "personalidade_prompt": "Genial, cínico, sarcástico."},
    "Dra. Meridee Grey": {"descricao": "Passional, introspectiva.", "falas_iconicas": ["Escolha-me. Ame-me."], "personalidade_prompt": "Comentários como voice-overs dramáticos."},
    "Enf. Cristina": {"descricao": "Competitiva, focada.", "falas_iconicas": ["Alguem opere para eu operar!"], "personalidade_prompt": "Ambiciosa, brilhante, direta."},
    "Dr. McSteamy": {"descricao": "Charmoso, confiante.", "falas_iconicas": ["Precisa de cirurgia... ou café?"], "personalidade_prompt": "Cirurgião plástico charmoso e bom no que faz."}
}

class Jogador:
    def __init__(self, nome, classe_medico: ClassesMedico, traco_medico: TracosMedico):
        self.nome = nome
        self.classe = classe_medico
        self.traco = traco_medico
        self.reputacao = 50
        self.pontuacao_diagnostica = 0
        self.fama_de_maluco = 0
        self.casos_resolvidos = 0

    def __str__(self):
        return (f"Dr(a). {self.nome}\n"
                f"  Classe: {self.classe.value['nome']} ({self.classe.value['habilidade']})\n"
                f"  Traço: {self.traco.value['nome']} ({self.traco.value['descricao']})\n"
                f"  Reputação: {self.reputacao}, Diagnósticos Certos: {self.pontuacao_diagnostica}, Fama de Maluco: {self.fama_de_maluco}")

    def verificar_combinacao_especial(self):
        chave = (self.classe.name, self.traco.name)
        return COMBINACOES_ESPECIAIS.get(chave)

class CasoClinico:
    def __init__(self, id_caso, titulo_caso, descricao_inicial_paciente, paciente_info, 
                 sintomas_reais_ocultos, pistas_falsas_criativas, diagnostico_real_medico,
                 doenca_explicacao_simplificada, erro_comum_relacionado, dica_vida_real,
                 introducao_narrativa_imersiva=None, 
                 referencia_npc_howser=None, referencia_npc_meridee=None, **kwargs):
        
        # ... (atributos existentes como id_caso, titulo_caso, etc. permanecem) ...
        self.id_caso = id_caso
        self.titulo_caso = titulo_caso
        self.introducao_narrativa_imersiva = introducao_narrativa_imersiva if introducao_narrativa_imersiva else descricao_inicial_paciente
        self.descricao_inicial_paciente = descricao_inicial_paciente 
        self.paciente_info = paciente_info
        self.sintomas_reais_ocultos = sintomas_reais_ocultos
        self.sintomas_revelados_jogador = list(self.paciente_info.get('sintomas_visiveis_gemini', []))
        self.pistas_falsas_criativas = pistas_falsas_criativas
        self.pistas_falsas_descartadas = []
        self.diagnostico_real_medico = diagnostico_real_medico
        self.doenca_explicacao_simplificada = doenca_explicacao_simplificada
        self.erro_comum_relacionado = erro_comum_relacionado
        self.dica_vida_real = dica_vida_real
        self.hipoteses_jogador = []
        self.exames_realizados = [] 
        self.progresso_narrativo_cena_atual = [] # Para dar contexto ao Gemini para as 8 opções
        self.resolvido = False
        self.desfecho_final = None
        self.dicas_howser_caso = [referencia_npc_howser] if referencia_npc_howser and isinstance(referencia_npc_howser, str) else []
        self.diario_meridee_caso = [referencia_npc_meridee] if referencia_npc_meridee and isinstance(referencia_npc_meridee, str) else []
        self.dados_extras_gemini = kwargs

        # SUBSTITUIR os atributos de opções anteriores por este:
        self.opcoes_cena_atuais = [] # Irá armazenar a lista de 8 dicionários {"tom": ..., "opcao_texto": ...}
        
        # Manter para opções de diagnóstico final
        self.opcoes_diagnostico_atuais = []


    def adicionar_progresso_cena(self, texto_narrativo: str):
        """Adiciona à narrativa da cena atual e imprime."""
        if not isinstance(texto_narrativo, str): texto_narrativo = str(texto_narrativo)
        # Limita o tamanho do histórico recente para não sobrecarregar o prompt
        if len(self.progresso_narrativo_cena_atual) > 5:
            self.progresso_narrativo_cena_atual.pop(0) # Remove o mais antigo
        self.progresso_narrativo_cena_atual.append(texto_narrativo)
        
        # Imprime a nova informação imediatamente
        wrapped_text = "\n".join(textwrap.wrap(texto_narrativo, width=90, replace_whitespace=False, drop_whitespace=False))
        print_lentamente(wrapped_text)

    def exibir_resumo_mental(self, jogador_nome): # SUBSTITUI exibir_informacoes_caso
        """Gera e exibe um resumo narrativo do que o jogador sabe (estilo Disco Elysium)."""
        # Este método pode ser chamado menos frequentemente ou como uma ação do jogador "Refletir".
        # Para o fluxo principal, a narrativa contínua é mais importante.
        # Por enquanto, vamos manter a impressão manual do resumo, mas o ideal seria gerar com IA.
        
        print_lentamente(f"\n--- Dr(a). {jogador_nome} reflete sobre o caso: {self.titulo_caso} ---")
        if self.sintomas_revelados_jogador:
            sintomas_str = ", ".join(list(set(self.sintomas_revelados_jogador)))
            print_lentamente(f"Pelo que pude apurar até agora, o paciente {self.paciente_info.get('nome')} apresenta: {sintomas_str}.")
        else:
            print_lentamente(f"Ainda estou tentando entender os sintomas principais de {self.paciente_info.get('nome')}.")
        
        if self.exames_realizados:
            print_lentamente("Resultados de exames já vistos:")
            for exame, resultado_narrativa in self.exames_realizados:
                resumo_resultado = resultado_narrativa.split('\n')[0] 
                print_lentamente(f"- {exame}: {resumo_resultado}...")
        
        if self.hipoteses_jogador:
            hipoteses_str = "; ".join(self.hipoteses_jogador)
            print_lentamente(f"Minhas suspeitas atuais são: {hipoteses_str}.")
        print_lentamente("----------------------------------------------------")


    def resetar_opcoes_cena(self):
        self.opcoes_cena_atuais = []
        # self.progresso_narrativo_cena_atual = [] # Não resetar aqui, acumula dentro da cena. Resetar no início de uma nova "cena" maior.
