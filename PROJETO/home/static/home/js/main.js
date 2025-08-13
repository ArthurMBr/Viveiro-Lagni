// home/static/home/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    const themeSelect = document.getElementById('theme-select');
    const logoUpload = document.getElementById('logo-upload');
    const appLogo = document.getElementById('app-logo');
    const openSettingsPopupBtn = document.getElementById('open-settings-popup');
    const settingsPopup = document.getElementById('settings-popup');
    const overlay = document.getElementById('overlay');
    const saveSettingsBtn = document.getElementById('save-settings');
    const cancelSettingsBtn = document.getElementById('cancel-settings');

    // Funções para gerenciar o popup
    function openSettingsPopup() {
        settingsPopup.style.display = 'block';
        overlay.style.display = 'block';
        // Define o valor do select de tema para o tema atual do body
        const currentTheme = localStorage.getItem('appTheme') || 'default';
        themeSelect.value = currentTheme;
    }

    function closeSettingsPopup() {
        settingsPopup.style.display = 'none';
        overlay.style.display = 'none';
    }

    // Carrega o tema salvo no localStorage e aplica
    function loadTheme() {
        const savedTheme = localStorage.getItem('appTheme');
        if (savedTheme) {
            body.className = `theme-${savedTheme}`; // Aplica a classe diretamente
        } else {
            body.className = 'theme-default'; // Garante que o tema padrão seja aplicado
        }
        themeSelect.value = savedTheme || 'default'; // Sincroniza o select
    }

    // Carrega a logo salva no localStorage
    function loadLogo() {
        const savedLogo = localStorage.getItem('appLogo');
        if (savedLogo) {
            appLogo.src = savedLogo;
        } else {
            // Se não houver logo salva, garante que a logo padrão do Django seja usada
            // Isso já é feito no HTML com {% static 'home/images/default_logo.png' %}
            // mas é bom ter uma fallback aqui se a imagem não carregar ou for removida do storage.
            // Não é necessário definir aqui, pois o src já está no HTML
        }
    }

    // Aplica o tema selecionado e salva no localStorage
    function applyTheme() {
        const selectedTheme = themeSelect.value;
        localStorage.setItem('appTheme', selectedTheme);
        body.className = `theme-${selectedTheme}`; // Aplica o tema na tag body
    }

    // Event listener para visualização instantânea do tema
    themeSelect.addEventListener('change', function() {
        const selectedTheme = themeSelect.value;
        body.className = `theme-${selectedTheme}`; // Aplica o tema imediatamente para visualização
    });

    // Salva a logo no localStorage quando um arquivo é selecionado
    logoUpload.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                localStorage.setItem('appLogo', e.target.result); // Salva como Data URL
                appLogo.src = e.target.result; // Atualiza a logo na página
            };
            reader.readAsDataURL(file); // Lê o arquivo como Data URL
        }
    });

    // Event listeners para o popup
    openSettingsPopupBtn.addEventListener('click', openSettingsPopup);
    cancelSettingsBtn.addEventListener('click', closeSettingsPopup);
    overlay.addEventListener('click', closeSettingsPopup); // Fecha ao clicar fora do popup

    saveSettingsBtn.addEventListener('click', function() {
        applyTheme(); // Aplica e salva o tema
        // A logo já é salva no evento 'change' do input file
        closeSettingsPopup();
    });

    // Inicializa carregando o tema e a logo ao carregar a página
    loadTheme();
    loadLogo();
});