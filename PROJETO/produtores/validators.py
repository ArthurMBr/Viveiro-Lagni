# produtores/validators.py
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re # Para expressões regulares

def validate_cpf_cnpj(value):
    """
    Valida um CPF ou CNPJ.
    Remove caracteres não numéricos antes da validação.
    """
    clean_value = ''.join(filter(str.isdigit, value))

    if not clean_value:
        # Se o campo não é obrigatório e está vazio, não levante ValidationError aqui.
        # A obrigatoriedade deve ser gerenciada no nível do formulário (forms.py).
        # No entanto, se o validador for chamado, ele espera um valor válido,
        # então, para evitar um IndexError, é bom tratar o vazio.
        # Retornamos None ou uma string vazia para indicar que não há valor para validar.
        # A validação de "required" é feita pelo formulário.
        return value # Retorna o valor original para que o formulário possa lidar com 'required'

    if len(clean_value) == 11:  # CPF
        if not re.match(r'^\d{11}$', clean_value):
            raise ValidationError(_("CPF deve conter exatamente 11 dígitos numéricos."))
        
        # Lógica de validação de CPF mais robusta (ex: verificar dígitos verificadores)
        # Exemplo simples para evitar CPFs inválidos óbvios:
        if len(set(clean_value)) == 1: # Checa se todos os dígitos são iguais (ex: 111.111.111-11)
            raise ValidationError(_("CPF inválido: todos os dígitos são iguais."))
        
        # Validação de dígitos verificadores (um exemplo simplificado)
        # Mais completo: https://pt.wikipedia.org/wiki/Cadastro_de_Pessoas_F%C3%ADsicas#Algoritmo
        def calcula_digito(cpf_parcial, peso_inicial):
            soma = 0
            for i, digito in enumerate(cpf_parcial):
                soma += int(digito) * (peso_inicial - i)
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        primeiro_digito = calcula_digito(clean_value[:9], 10)
        segundo_digito = calcula_digito(clean_value[:10], 11)

        if not (clean_value[9] == str(primeiro_digito) and clean_value[10] == str(segundo_digito)):
            raise ValidationError(_("CPF inválido: Dígitos verificadores incorretos."))

        return clean_value # Retorna o valor limpo para uso posterior

    elif len(clean_value) == 14:  # CNPJ
        if not re.match(r'^\d{14}$', clean_value):
            raise ValidationError(_("CNPJ deve conter exatamente 14 dígitos numéricos."))
        
        # Lógica de validação de CNPJ mais robusta (ex: verificar dígitos verificadores)
        # Exemplo simples para evitar CNPJs inválidos óbvios:
        if len(set(clean_value)) == 1: # Checa se todos os dígitos são iguais (ex: 11.111.111/1111-11)
            raise ValidationError(_("CNPJ inválido: todos os dígitos são iguais."))

        # Validação de dígitos verificadores (um exemplo simplificado)
        # Mais completo: https://www.receita.fazenda.gov.br/pessoajuridica/cnpj/cnpjreva/valida/valida.asp
        def calcula_digito_cnpj(cnpj_parcial, pesos):
            soma = 0
            for i, digito in enumerate(cnpj_parcial):
                soma += int(digito) * pesos[i]
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        primeiro_digito = calcula_digito_cnpj(clean_value[:12], pesos1)
        segundo_digito = calcula_digito_cnpj(clean_value[:13], pesos2)

        if not (clean_value[12] == str(primeiro_digito) and clean_value[13] == str(segundo_digito)):
            raise ValidationError(_("CNPJ inválido: Dígitos verificadores incorretos."))

        return clean_value # Retorna o valor limpo para uso posterior

    else:
        raise ValidationError(
            _("CPF/CNPJ inválido: %(value)s deve ter 11 ou 14 dígitos."),
            params={'value': value},
        )