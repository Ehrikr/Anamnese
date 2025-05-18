// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const setupDiv = document.getElementById('setup-jogo');
    const jogoPrincipalDiv = document.getElementById('jogo-principal');
    const narrativaContainer = document.getElementById('narrativa-container');
    const opcoesCenaContainer = document.getElementById('opcoes-cena-container');
    const acoesFixasContainer = document.getElementsByClassName('acoes-fixas-container')[0]; // Ajuste se necessário
    const diagnosticoOpcoesContainer = document.getElementById('diagnostico-opcoes-container');
    const desfechoContainer = document.getElementById('desfecho-container');
    const tituloCasoElem = document.getElementById('titulo-caso');
    const statusJogadorElem = document.getElementById('status-jogador');

    const btnIniciarPersonagem = document.getElementById('btn-iniciar-personagem');
    const nomeJogadorInput = document.getElementById('nome-jogador');
    const classeSelect = document.getElementById('classe-jogador');
    const tracoSelect = document.getElementById('traco-jogador');
    const setupFeedback = document.getElementById('setup-feedback');
    const btnDesenhar = document.getElementById('btn-desenhar');


    // Popular selects de classe e traço (exemplo, idealmente viria da API ou de um JSON)
    const classesMedicas = ["CLINICO_GERAL", "ENFERMEIRO", "DERMATOLOGISTA", "CIRURGIAO", "PSICOLOGO", "FARMACEUTICO", "PEDIATRA", "CARDIOLOGISTA"];
    const tracosMedicos = ["CINICO", "EMPATICO", "TEORICO_CONSPIRACAO", "PERFECCIONISTA", "DESASTRADO", "VICIADO_TRABALHO", "CURIOSO", "ARTISTA_FRUSTRADO"];

    classesMedicas.forEach(c => {
        const option = document.createElement('option');
        option.value = c;
        option.textContent = c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        classeSelect.appendChild(option);
    });
    tracosMedicos.forEach(t => {
        const option = document.createElement('option');
        option.value = t;
        option.textContent = t.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        tracoSelect.appendChild(option);
    });


    async function chamarAPI(endpoint, metodo = 'GET', corpo = null) {
        try {
            const opcoesReq = {
                method: metodo,
                headers: { 'Content-Type': 'application/json' },
            };
            if (corpo) {
                opcoesReq.body = JSON.stringify(corpo);
            }
            const resposta = await fetch(endpoint, opcoesReq);
            if (!resposta.ok) {
                const erroData = await resposta.json();
                throw new Error(erroData.erro || `Erro HTTP: ${resposta.status}`);
            }
            return await resposta.json();
        } catch (erro) {
            console.error(`Erro na API (${endpoint}):`, erro);
            narrativaContainer.innerHTML = `<p style="color:red;">Erro ao comunicar com o servidor: ${erro.message}</p>`;
            return null;
        }
    }

    function atualizarStatusJogador(statusStr) {
        if (statusJogadorElem && statusStr) {
            statusJogadorElem.innerText = statusStr;
        }
    }
    
    function exibirNarrativa(texto) {
        // Adiciona nova narrativa, não substitui tudo sempre
        const p = document.createElement('p');
        p.innerText = texto; // innerText para preservar quebras de linha do servidor
        narrativaContainer.appendChild(p);
        // Scroll para a nova narrativa
        narrativaContainer.scrollTop = narrativaContainer.scrollHeight;
    }

    function exibirOpcoesCena(opcoes) {
        opcoesCenaContainer.innerHTML = '<h3>Escolha uma Ação/Diálogo para a Cena:</h3>';
        if (opcoes && opcoes.length > 0) {
            opcoes.forEach((opt, index) => {
                const btn = document.createElement('button');
                btn.innerHTML = `<em>[${opt.tom}]</em> ${opt.opcao_texto}`; // innerHTML para o em
                btn.addEventListener('click', () => processarAcaoCena(opt));
                opcoesCenaContainer.appendChild(btn);
            });
        } else {
            opcoesCenaContainer.innerHTML += '<p>(Nenhuma opção de cena disponível no momento.)</p>';
        }
    }

    async function iniciarNovoCaso() {
        narrativaContainer.innerHTML = '<p>Iniciando novo caso...</p>';
        opcoesCenaContainer.innerHTML = '';
        diagnosticoOpcoesContainer.innerHTML = '';
        diagnosticoOpcoesContainer.classList.add('hidden');
        desfechoContainer.innerHTML = '';
        desfechoContainer.classList.add('hidden');

        const data = await chamarAPI('/api/iniciar_caso');
        if (data) {
            tituloCasoElem.textContent = data.titulo_caso || "Caso Misterioso";
            narrativaContainer.innerHTML = ''; // Limpa "Carregando..."
            exibirNarrativa(data.introducao_narrativa);
            exibirOpcoesCena(data.opcoes_cena);
            atualizarStatusJogador(data.jogador_status);

            // Verificar se o jogador é Artista Frustrado para mostrar/ocultar botão
            if (data.jogador_status && data.jogador_status.includes("Artista Frustrado")) {
                btnDesenhar.style.display = 'block';
            } else {
                btnDesenhar.style.display = 'none';
            }
        }
    }

    async function processarAcaoCena(opcaoDict) {
        // Limpar narrativa anterior antes de adicionar a da ação e da resposta
        // narrativaContainer.innerHTML = ''; // Ou apenas adicionar
        exibirNarrativa(`\nVocê (${opcaoDict.tom}): "${opcaoDict.opcao_texto}"`);
        
        const data = await chamarAPI('/api/processar_acao', 'POST', { opcao: opcaoDict });
        if (data) {
            exibirNarrativa(data.nova_narrativa_parte);
            atualizarStatusJogador(data.jogador_status);
            if (data.caso_resolvido) {
                exibirDesfecho(data.desfecho);
            } else {
                exibirOpcoesCena(data.opcoes_cena);
            }
        }
    }

    async function processarAcaoFixa(tipoAcao) {
        let parametro = null;
        if (tipoAcao === 'hipotese') {
            parametro = prompt("Digite sua nova hipótese diagnóstica:");
            if (parametro === null || !parametro.trim()) return; // Cancelado ou vazio
        } else if (tipoAcao === 'desenhar') {
            parametro = prompt("O que você gostaria de desenhar?");
            if (parametro === null || !parametro.trim()) return;
        }
        
        // narrativaContainer.innerHTML = ''; // Limpar para nova narrativa
        const data = await chamarAPI('/api/acao_fixa', 'POST', { tipo_acao: tipoAcao, parametro: parametro });
        if (data) {
            exibirNarrativa(data.nova_narrativa_parte);
            exibirOpcoesCena(data.opcoes_cena); // Ações fixas também podem gerar novas opções de cena
            atualizarStatusJogador(data.jogador_status);
        }
    }
    
    async function tentarDiagnostico() {
        const data = await chamarAPI('/api/tentar_diagnostico', 'POST'); // POST para consistência, mesmo sem corpo
        if (data && data.opcoes_diagnostico) {
            diagnosticoOpcoesContainer.innerHTML = '<h3>Escolha o Diagnóstico Final:</h3>';
            data.opcoes_diagnostico.forEach(diagOpt => {
                const btn = document.createElement('button');
                btn.textContent = diagOpt;
                btn.addEventListener('click', () => finalizarDiagnostico(diagOpt));
                diagnosticoOpcoesContainer.appendChild(btn);
            });
            diagnosticoOpcoesContainer.classList.remove('hidden');
            opcoesCenaContainer.classList.add('hidden'); // Esconde opções de cena
            if (acoesFixasContainer) acoesFixasContainer.classList.add('hidden');
        } else {
            exibirNarrativa("Não foi possível carregar as opções de diagnóstico.");
        }
    }

    async function finalizarDiagnostico(diagnosticoEscolhido) {
        // narrativaContainer.innerHTML = ''; // Limpar para o desfecho
        diagnosticoOpcoesContainer.classList.add('hidden');

        const data = await chamarAPI('/api/finalizar_diagnostico', 'POST', { diagnostico: diagnosticoEscolhido });
        if (data) {
            exibirDesfecho(data.desfecho_completo);
            atualizarStatusJogador(data.jogador_status);
        }
    }

    function exibirDesfecho(desfecho) {
        if (!desfecho) {
            desfechoContainer.innerHTML = "<p>Ocorreu um erro ao carregar o desfecho.</p>";
            desfechoContainer.classList.remove('hidden');
            return;
        }
        opcoesCenaContainer.innerHTML = ''; // Limpa opções de cena
        if (acoesFixasContainer) acoesFixasContainer.classList.add('hidden'); // Esconde ações fixas
        
        let htmlDesfecho = `<h3>${desfecho.ficha_educativa_titulo || "Desfecho do Caso"}</h3>`;
        htmlDesfecho += `<p><strong>Sua tentativa de diagnóstico:</strong> ${desfecho.diagnostico_final_jogador}</p>`;
        htmlDesfecho += `<p><strong>Diagnóstico Correto:</strong> ${desfecho.diagnostico_correto_caso}</p>`;
        htmlDesfecho += `<p><strong>Resultado:</strong> ${desfecho.acertou ? "Você Acertou! 🎉" : "Não foi desta vez. 😕"}</p>`;
        htmlDesfecho += `<hr><p><strong>Narrativa do Desfecho:</strong></p><p>${desfecho.desfecho_narrativa.replace(/\n/g, '<br>')}</p><hr>`;
        htmlDesfecho += `<h4>Ficha Educativa</h4>`;
        htmlDesfecho += `<p><strong>Doença Real:</strong> ${desfecho.doenca_real_ficha}</p>`;
        htmlDesfecho += `<p><strong>Explicação:</strong> ${desfecho.explicacao_doenca_ficha}</p>`;
        htmlDesfecho += `<p><strong>Erro Comum:</strong> ${desfecho.erro_comum_ficha}</p>`;
        htmlDesfecho += `<p><strong>Dica para Vida Real:</strong> ${desfecho.dica_vida_real_ficha}</p>`;

        if (desfecho.comentario_howser_final) {
            htmlDesfecho += `<p><strong>Dr. Howser:</strong> <em>"${desfecho.comentario_howser_final}"</em></p>`;
        }
        if (desfecho.comentario_meridee_final) {
            htmlDesfecho += `<p><strong>Dra. Meridee:</strong> <em>"${desfecho.comentario_meridee_final}"</em></p>`;
        }
        htmlDesfecho += `<hr><button id="btn-proximo-caso">Próximo Caso / Voltar ao Menu</button>`; // Ou voltar ao menu

        desfechoContainer.innerHTML = htmlDesfecho;
        desfechoContainer.classList.remove('hidden');
        
        document.getElementById('btn-proximo-caso').addEventListener('click', () => {
            desfechoContainer.classList.add('hidden');
            desfechoContainer.innerHTML = '';
            if (acoesFixasContainer) acoesFixasContainer.classList.remove('hidden');
            // Aqui você decidiria se volta ao menu principal do jogo ou inicia um novo caso direto.
            // Por simplicidade, vamos recarregar as opções para um novo caso
            // ou permitir que o jogador vá para o menu principal do jogo (não implementado no frontend ainda)
            // Apenas limpa e permite que o jogador peça um novo caso pelo menu principal (se existisse)
            // Por ora, vamos chamar iniciarNovoCaso() para testar o ciclo
            iniciarNovoCaso(); 
        });
    }


    btnIniciarPersonagem.addEventListener('click', async () => {
        const nome = nomeJogadorInput.value;
        const classe = classeSelect.value;
        const traco = tracoSelect.value;

        if (!nome.trim()) {
            setupFeedback.textContent = "Por favor, insira o nome do(a) médico(a).";
            return;
        }
        setupFeedback.textContent = "Criando personagem e iniciando o primeiro caso...";

        // Chamada à API para "criar" o jogador no backend (ou apenas configurar)
        const setupData = await chamarAPI('/api/novo_jogo', 'POST', { nome, classe, traco });

        if (setupData && setupData.status) {
            setupFeedback.textContent = setupData.status;
            setupDiv.classList.remove('setup-active');
            setupDiv.classList.add('hidden');
            jogoPrincipalDiv.classList.remove('hidden');
            iniciarNovoCaso();
        } else {
            setupFeedback.textContent = "Erro ao configurar o personagem no servidor. " + (setupData ? setupData.erro : "");
        }
    });

    // Adicionar event listeners para botões de ações fixas
    document.querySelectorAll('.acao-fixa').forEach(button => {
        button.addEventListener('click', () => {
            const tipoAcao = button.dataset.tipo;
            if (tipoAcao === 'diagnosticar') {
                tentarDiagnostico();
            } else {
                processarAcaoFixa(tipoAcao);
            }
        });
    });

    // Inicialmente, apenas a tela de setup é visível
    setupDiv.classList.add('setup-active');
    jogoPrincipalDiv.classList.add('hidden');
    desfechoContainer.classList.add('hidden');

});