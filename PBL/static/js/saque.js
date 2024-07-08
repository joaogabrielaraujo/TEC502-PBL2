// saque.js

document.addEventListener('DOMContentLoaded', function() {
    const saqueForm = document.getElementById('saqueForm');
    const messageDiv = document.getElementById('message');

    saqueForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(saqueForm);
        const jsonData = {};
        formData.forEach((value, key) => {
            jsonData[key] = value;
        });

        fetch('/saque', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
            messageDiv.innerHTML = `<p>${data.message}</p>`;
            // Aqui você pode redirecionar o usuário ou fazer outras ações conforme necessário
        })
        .catch(error => {
            console.error('Erro ao realizar o saque:', error);
            messageDiv.innerHTML = '<p>Ocorreu um erro ao processar o saque. Tente novamente mais tarde.</p>';
        });
    });
});