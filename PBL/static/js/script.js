document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const identificador = document.getElementById('identificador').value;
    const senha = document.getElementById('senha').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ identificador, senha }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Login bem-sucedido') {
            window.location.href = '/home';
        } else {
            alert(data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});