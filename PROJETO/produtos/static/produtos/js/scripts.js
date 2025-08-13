// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    // Esconde todas as abas, exceto a primeira que tem a classe 'active'
    // Este código assume que você tem um sistema de abas.
    // Se não tiver, pode removê-lo.
    const tabPanes = document.querySelectorAll('.tab-pane');
    if (tabPanes.length > 0) {
        tabPanes.forEach(pane => pane.style.display = 'none');
        const activeTabPane = document.querySelector('.tab-pane.active');
        if (activeTabPane) {
            activeTabPane.style.display = 'block';
        }

        // Adiciona evento de clique aos botões de aba
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove a classe 'active' de todos os botões e painéis
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabPanes.forEach(pane => {
                    pane.classList.remove('active');
                    pane.style.display = 'none';
                });

                // Adiciona a classe 'active' ao botão clicado
                this.classList.add('active');

                // Mostra o painel correspondente ao botão clicado
                const targetTabId = this.dataset.tabTarget;
                const targetTab = document.querySelector(targetTabId);
                if (targetTab) {
                    targetTab.classList.add('active');
                    targetTab.style.display = 'block';
                }

                // Opcional: Rolagem suave para o topo do formulário se necessário
                // const tabContainer = document.querySelector(".tab-container");
                // if (tabContainer) {
                //     window.scrollTo({
                //         top: tabContainer.offsetTop - 20, // Ajuste o 20 conforme necessário
                //         behavior: 'smooth'
                //     });
                // }
            });
        });
    }

    // Função para fechar mensagens automaticamente após um tempo
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            // Verifica se a mensagem ainda existe no DOM antes de tentar fechar
            if (message && message.parentNode) {
                // Adiciona uma classe para animar o fade-out antes de remover
                message.classList.add('fade-out');
                message.addEventListener('transitionend', function() {
                    message.remove();
                });
            }
        }, 5000); // Mensagem some após 5 segundos
    });

    // Adicionar funcionalidade para o botão de limpar filtro (se não for recarregar a página)
    // O ideal é que o botão "Limpar" já redirecione para a URL base (sem parâmetros de filtro)
    // Se o seu botão de limpar tiver a classe 'btn-clear-filter' e você quiser usar JS para limpar
    // os campos sem recarregar a página, descomente e ajuste o código abaixo:
    // const clearFilterBtn = document.querySelector('.btn-clear-filter');
    // if (clearFilterBtn) {
    //     clearFilterBtn.addEventListener('click', function(event) {
    //         event.preventDefault(); // Impede o comportamento padrão do link/botão
    //         document.querySelector('.form-control-search').value = ''; // Limpa o campo de busca
    //         // Se você tiver selects para tipo e status, limpe-os também:
    //         // document.querySelector('select[name="tipo"]').value = '';
    //         // document.querySelector('select[name="status"]').value = '';
    //         // Se o formulário não for enviado automaticamente, você precisaria submetê-lo aqui:
    //         // this.closest('form').submit();
    //     });
    // }

    // Pré-visualização de imagem no formulário de produto
    const imageInput = document.getElementById('id_imagem'); // Assumindo id_imagem como ID do input
    const imagePreview = document.getElementById('image-preview');
    const fileNameDisplay = document.getElementById('file-name-display');

    if (imageInput && imagePreview && fileNameDisplay) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block'; // Mostra a pré-visualização
                };
                reader.readAsDataURL(file);
                fileNameDisplay.textContent = file.name; // Exibe o nome do arquivo
            } else {
                imagePreview.src = '';
                imagePreview.style.display = 'none';
                fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
            }
        });

        // Configura o label inicial do input de arquivo se já houver um arquivo
        const existingImageSrc = imagePreview.getAttribute('data-existing-src');
        const existingImageName = imagePreview.getAttribute('data-existing-name');
        if (existingImageSrc && existingImageName) {
            imagePreview.src = existingImageSrc;
            imagePreview.style.display = 'block';
            fileNameDisplay.textContent = existingImageName;
        }
    }
});