# produtores/forms.py
from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import ProdutorRural, ResponsavelTecnico, CertificadoDigitalResponsavel
from .validators import validate_cpf_cnpj

class ProdutorRuralForm(forms.ModelForm):
    cpf_cnpj = forms.CharField(
        label="CPF/CNPJ",
        max_length=18,
        required=False,
        help_text="Informe o CPF (11 dígitos) ou CNPJ (14 dígitos)."
    )
    telefone_principal = forms.CharField(
        label="Telefone Principal",
        max_length=15,
        required=False,
        help_text="Ex: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX"
    )
    telefone_secundario = forms.CharField(
        label="Telefone Secundário",
        max_length=15,
        required=False,
        help_text="Ex: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX"
    )
    cep = forms.CharField(
        label="CEP",
        max_length=9,
        required=False,
        help_text="Ex: XXXXX-XXX"
    )

    def clean_telefone_principal(self):
        telefone = self.cleaned_data.get('telefone_principal')
        if telefone:
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if not (10 <= len(telefone_limpo) <= 11):
                 raise ValidationError("Telefone principal deve ter 10 ou 11 dígitos.")
            return telefone_limpo
        return telefone

    def clean_telefone_secundario(self):
        telefone = self.cleaned_data.get('telefone_secundario')
        if telefone:
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if not (10 <= len(telefone_limpo) <= 11):
                 raise ValidationError("Telefone secundário deve ter 10 ou 11 dígitos.")
            return telefone_limpo
        return telefone

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if cep:
            cep_limpo = ''.join(filter(str.isdigit, cep))
            if len(cep_limpo) != 8:
                raise ValidationError("CEP deve conter 8 dígitos.")
            return cep_limpo
        return cep

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj')
        if cpf_cnpj:
            try:
                clean_cpf_cnpj_value = validate_cpf_cnpj(cpf_cnpj)
                return clean_cpf_cnpj_value
            except ValidationError as e:
                raise e
        return cpf_cnpj

    def clean(self):
        cleaned_data = super().clean()
        telefone_principal = cleaned_data.get('telefone_principal')
        telefone_secundario = cleaned_data.get('telefone_secundario')

        if not telefone_principal and not telefone_secundario:
            if 'telefone_principal' in self.fields:
                self.add_error('telefone_principal', "Pelo menos um telefone (Principal ou Secundário) deve ser fornecido.")
            if 'telefone_secundario' in self.fields:
                self.add_error('telefone_secundario', "Pelo menos um telefone (Principal ou Secundário) deve ser fornecido.")

        cpf_cnpj = cleaned_data.get('cpf_cnpj')
        if not cpf_cnpj:
            self.add_error('cpf_cnpj', "CPF/CNPJ é obrigatório.")

        return cleaned_data

    class Meta:
        model = ProdutorRural
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'data_abertura': forms.DateInput(attrs={'type': 'date'}),
        }
        exclude = ('data_cadastro', 'data_atualizacao',)


class ResponsavelTecnicoForm(forms.ModelForm):
    cpf = forms.CharField(
        label="CPF",
        max_length=14, # Ajustado para 14 para permitir formatação (ex: 999.999.999-99)
        validators=[validate_cpf_cnpj], # Usa o validador customizado
        help_text="Informe o CPF do Responsável Técnico."
    )
    telefone = forms.CharField(
        label="Telefone",
        max_length=15, # Ex: (99) 99999-9999
        required=False,
        help_text="Ex: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX"
    )
    class Meta:
        model = ResponsavelTecnico
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}), # Adicionado para garantir widget de data
        }
        exclude = ('produtor_rural',) # Será definido pelo formset ou view

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if not (10 <= len(telefone_limpo) <= 11):
                 raise ValidationError("Telefone deve ter 10 ou 11 dígitos.")
            return telefone_limpo
        return telefone

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            try:
                clean_cpf_value = validate_cpf_cnpj(cpf)
                return clean_cpf_value
            except ValidationError as e:
                raise e
        return cpf


class CertificadoDigitalResponsavelForm(forms.ModelForm):
    # Campos que você quer sobrescrever ou adicionar widgets
    data_validade = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), # Mantém o widget para calendário
        required=False, # Garante que não é obrigatório no formulário
        label="Data de Validade",
    )
    arquivo_pfx = forms.FileField(
        label="Arquivo Certificado (.pfx)",
        required=False,
        help_text="Arquivo de certificado digital do responsável técnico."
    )
    senha_pfx = forms.CharField(
        label="Senha do Certificado",
        widget=forms.PasswordInput(render_value=True), # render_value=True para preencher no edit
        required=False,
        max_length=255
    )

    class Meta:
        model = CertificadoDigitalResponsavel
        fields = '__all__'
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
        exclude = ('responsavel_tecnico',) # Será definido pelo formset

    def clean_arquivo_pfx(self):
        arquivo = self.cleaned_data.get('arquivo_pfx')
        if arquivo:
            return arquivo
        elif self.instance.pk and self.instance.arquivo_pfx:
            return self.instance.arquivo_pfx
        return None

    def clean_senha_pfx(self):
        senha = self.cleaned_data.get('senha_pfx')
        if senha:
            return senha
        elif self.instance.pk and self.instance.senha_pfx:
            return self.instance.senha_pfx
        return ''

    def clean(self):
        cleaned_data = super().clean()
        arquivo = cleaned_data.get('arquivo_pfx')
        senha = cleaned_data.get('senha_pfx')
        data_validade = cleaned_data.get('data_validade')

        if arquivo and not senha:
            self.add_error('senha_pfx', "A senha do certificado é obrigatória quando um arquivo .pfx é fornecido.")

        if senha and not arquivo and not (self.instance.pk and self.instance.arquivo_pfx):
             self.add_error('arquivo_pfx', "Um arquivo .pfx deve ser fornecido se uma senha for informada.")

        if data_validade and data_validade < date.today():
            self.add_error('data_validade', "A data de validade não pode ser no passado.")

        return cleaned_data