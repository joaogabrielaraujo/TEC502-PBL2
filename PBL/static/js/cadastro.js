document.addEventListener('DOMContentLoaded', function() {
    const tipoCadastroSelect = document.getElementById('tipoCadastro');
    const pessoaFisicaDiv = document.getElementById('pessoa_fisica');
    const pessoaJuridicaDiv = document.getElementById('pessoa_juridica');
    const contaConjuntaDiv = document.getElementById('conta_conjunta');

    tipoCadastroSelect.addEventListener('change', function() {
        const selectedOption = tipoCadastroSelect.value;

        // Esconder todos os tipos de cadastro
        pessoaFisicaDiv.style.display = 'none';
        pessoaJuridicaDiv.style.display = 'none';
        contaConjuntaDiv.style.display = 'none';

        // Mostrar o tipo de cadastro selecionado
        if (selectedOption === 'pessoa_fisica') {
            pessoaFisicaDiv.style.display = 'block';
        } else if (selectedOption === 'pessoa_juridica') {
            pessoaJuridicaDiv.style.display = 'block';
        } else if (selectedOption === 'conta_conjunta') {
            contaConjuntaDiv.style.display = 'block';
        }
    });

    const cadastroForm = document.getElementById('cadastroForm');

    cadastroForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const tipoCadastro = tipoCadastroSelect.value;
        let data;

        if (tipoCadastro === 'pessoa_fisica') {
            data = {
                tipoCadastro: tipoCadastro,
                nome: document.getElementById('nome_pf').value,
                cpf: document.getElementById('cpf').value,
                senha: document.getElementById('senha_pf').value
            };
        } else if (tipoCadastro === 'pessoa_juridica') {
            data = {
                tipoCadastro: tipoCadastro,
                nome: document.getElementById('razao_social').value,
                cnpj: document.getElementById('cnpj').value,
                senha: document.getElementById('senha_pj').value
            };
        } else if (tipoCadastro === 'conta_conjunta') {
            data = {
                tipoCadastro: tipoCadastro,
                identificador1: document.getElementById('cpf_cc1').value,
                identificador2: document.getElementById('cpf_cc2').value,
                senha: document.getElementById('senha_cc').value
            };
        }

        const url = `/cadastro_${tipoCadastro}`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Exibe mensagem de sucesso ou erro
            if (data.success) {
                // Redireciona ou executa outra ação se necessário
            }
        })
        .catch((error) => {
            console.error('Erro:', error);
        });
    });
});