// clientes_fornecedores/static/clientes_fornecedores/js/admin_form_dinamico.js

document.addEventListener('DOMContentLoaded', function() {
    function toggle_fields() {
        const tipoClienteSelect = document.querySelector('#id_tipo_cliente');
        const pfFields = document.querySelector('.form-pf');
        const pjFields = document.querySelector('.form-pj');

        if (!tipoClienteSelect || !pfFields || !pjFields) {
            return;
        }

        const tipo = tipoClienteSelect.value;
        if (tipo === 'PF') {
            pfFields.style.display = 'block';
            pjFields.style.display = 'none';
        } else if (tipo === 'PJ') {
            pfFields.style.display = 'none';
            pjFields.style.display = 'block';
        }
    }

    // Executa a função ao carregar a página
    toggle_fields();

    // Adiciona um listener para quando o valor do campo 'tipo_cliente' mudar
    const tipoClienteSelect = document.querySelector('#id_tipo_cliente');
    if (tipoClienteSelect) {
        tipoClienteSelect.addEventListener('change', toggle_fields);
    }
});