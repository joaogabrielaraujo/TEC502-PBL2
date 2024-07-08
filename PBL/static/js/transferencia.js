
document.addEventListener('DOMContentLoaded', function() {
  const homeButton = document.getElementById('homeButton');
  homeButton.addEventListener('click', function() {
      window.location.href = '/home';
  });

  const realizarTransferenciaButton = document.getElementById('realizarTransferencia');
  realizarTransferenciaButton.addEventListener('click', function(event) {
      event.preventDefault(); // Evita o comportamento padrão de enviar o formulário

      const nomeBancoDestino = document.getElementById('nomeBancoDestino').value;
      const numeroContaDestino = document.getElementById('numeroContaDestino').value;
      const valorTotal = parseFloat(document.getElementById('valorTotal').value);

      const transferencias = [];

      // Itera sobre os campos de valor das contas
      const valorContaInputs = document.querySelectorAll('.valor-conta');
      valorContaInputs.forEach(input => {
          const valor = parseFloat(input.value);
          if (!isNaN(valor) && valor > 0) {
              const numeroContaOrigem = input.getAttribute('data-conta');
              const nomeBancoOrigem = input.getAttribute('data-banco');
              transferencias.push({
                  numero_conta_origem: parseInt(numeroContaOrigem, 10),
                  nome_banco_origem: nomeBancoOrigem,
                  valor: valor
              });
          }
      });

      const data = {
          nome_banco_destino: nomeBancoDestino,
          numero_conta_destino: numeroContaDestino,
          valor_conta_destino: valorTotal,
          transferencias: transferencias
      };

      console.log(transferencias)

      fetch('/transferir', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(data)
      })
      .then(response => response.json())
      .then(data => {
          document.getElementById('message').innerHTML = `<p>${data.message}</p>`;
      })
      .catch(error => {
          console.error('Erro ao realizar transferência:', error);
          document.getElementById('message').innerHTML = '<p>Ocorreu um erro ao processar a transferência. Tente novamente mais tarde.</p>';
      });
  });

  // Calcula o valor total ao modificar os campos de valor das contas
  const valorContaInputs = document.querySelectorAll('.valor-conta');
  valorContaInputs.forEach(input => {
      input.addEventListener('input', function() {
          calcularValorTotal();
      });
  });

  // Função para calcular o valor total a transferir
  function calcularValorTotal() {
      let valorTotal = 0;
      const valorContaInputs = document.querySelectorAll('.valor-conta');
      valorContaInputs.forEach(input => {
          const valor = parseFloat(input.value);
          if (!isNaN(valor) && valor > 0) {
              valorTotal += valor;
          }
      });

      document.getElementById('valorTotal').value = valorTotal.toFixed(2);
  }
});
