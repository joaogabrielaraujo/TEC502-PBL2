// home.js

document.addEventListener('DOMContentLoaded', function() {
    // Lógica para redirecionar para a página de transferência
    const transferButton = document.getElementById('transferButton');
    transferButton.addEventListener('click', function() {
        window.location.href = '/transferencia_page';
    });

    // Lógica para redirecionar para a página de depósito
    const depositButton = document.getElementById('depositButton');
    depositButton.addEventListener('click', function() {
        window.location.href = '/deposito_page'; // Redireciona para a página de depósito
    });

    // Lógica para redirecionar para a página de saque
    const saqueButtons = document.querySelectorAll('[data-conta]');
    saqueButtons.forEach(button => {
        button.addEventListener('click', function() {
            const numeroConta = button.getAttribute('data-conta');
            window.location.href = `/saque_page?numero_conta=${numeroConta}`;
        });
    });
    
});