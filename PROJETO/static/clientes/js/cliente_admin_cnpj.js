// static/clientes/js/cliente_admin_cnpj.js

jQuery(function($) {
    // Ao perder o foco do campo CNPJ no Admin, disparamos a busca da ReceitaWS:
    $('#id_cnpj_admin').on('blur', function() {
        var raw = $(this).val();
        var cnpj = raw.replace(/\D/g, '');  // só números

        if (cnpj.length === 14) {
            // Opcional: exibir "Buscando..." antes de receber a resposta
            $('#id_razao_admin').val('Buscando...');
            $('#id_endereco_admin').val('');

            $.ajax({
                url: '/clientes/ajax/buscar_cnpj/',
                data: { 'cnpj': cnpj },
                dataType: 'json',
                success: function(data) {
                    if (data.success) {
                        $('#id_razao_admin').val(data.razao_social);
                        $('#id_endereco_admin').val(data.endereco);
                    } else {
                        alert('Erro ao buscar CNPJ: ' + data.error);
                        $('#id_razao_admin').val('');
                        $('#id_endereco_admin').val('');
                    }
                },
                error: function() {
                    alert('Falha na requisição. Verifique sua conexão.');
                    $('#id_razao_admin').val('');
                    $('#id_endereco_admin').val('');
                }
            });
        } else {
            alert('Informe um CNPJ válido de 14 dígitos.');
            $('#id_razao_admin').val('');
            $('#id_endereco_admin').val('');
        }
    });
});
