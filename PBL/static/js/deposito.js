document.addEventListener('DOMContentLoaded', function() {
    // Código JavaScript para a página de depósito
    
    const depositForm = document.getElementById('depositForm');
    const messageDiv = document.getElementById('message');

    depositForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Evita o comportamento padrão de enviar o formulário

        const numeroConta = document.getElementById('numeroConta').value;
        const valor = document.getElementById('valor').value;
        const nomeBanco = document.getElementById('nomeBanco').value;

        // Monta os dados para enviar na requisição POST
        const data = {
            numero_conta: numeroConta,
            nome_banco: nomeBanco,
            valor: parseFloat(valor) // Converte para float
        };

        // Envia a requisição POST para a rota /deposito
        fetch('/deposito', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            // Exibe a mensagem de retorno
            messageDiv.innerHTML = `<p>${data.message}</p>`;
        })
        .catch(error => {
            console.error('Erro ao realizar depósito:', error);
            messageDiv.innerHTML = `<p>Erro ao realizar depósito. Por favor, tente novamente mais tarde.</p>`;
        });
    });
});