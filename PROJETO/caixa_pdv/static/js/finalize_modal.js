// static/js/finalize_modal.js

document.addEventListener('DOMContentLoaded', function() {
    const finalizeSaleModal = document.getElementById('finalizeSaleModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelModalBtn = document.getElementById('cancelModalBtn');
    const confirmFinalizeSaleBtn = document.getElementById('confirmFinalizeSaleBtn');
    const modalSaleTotalSpan = document.getElementById('modalSaleTotal');
    const clientNameInput = document.getElementById('clientNameInput');
    const paymentDinheiroRadio = document.getElementById('paymentDinheiro');
    const paymentPixRadio = document.getElementById('paymentPix');
    const cashPaymentDetails = document.getElementById('cashPaymentDetails');
    const pixQrCodeDisplay = document.getElementById('pixQrCodeDisplay');
    const amountReceivedInput = document.getElementById('amountReceivedInput');
    const changeAmountSpan = document.getElementById('changeAmount');
    const pixValueQrCodeSpan = document.getElementById('pixValueQrCode');

    // Make global functions accessible (from pdv.html script)
    // These should already be defined globally as window.cart, window.updateCartDisplay, window.getCookie, window.performSearch
    const cart = window.cart;
    const updateCartDisplay = window.updateCartDisplay;
    const getCookie = window.getCookie;
    const performSearch = window.performSearch; // If you need to refresh search results after sale

    // Function to open the modal
    window.openFinalizeSaleModal = function() {
        const total = parseFloat(document.getElementById('cartTotal').textContent);
        modalSaleTotalSpan.textContent = total.toFixed(2);
        pixValueQrCodeSpan.textContent = total.toFixed(2); // Set Pix value
        amountReceivedInput.value = total.toFixed(2); // Pre-fill with total for cash
        changeAmountSpan.textContent = 'R$ 0.00'; // Reset change
        clientNameInput.value = ''; // Clear client name
        paymentDinheiroRadio.checked = true; // Default to Dinheiro
        cashPaymentDetails.style.display = 'block';
        pixQrCodeDisplay.style.display = 'none';
        confirmFinalizeSaleBtn.disabled = false; // Enable confirm button initially
        finalizeSaleModal.style.display = 'flex'; // Show the modal
        amountReceivedInput.focus(); // Focus on amount received
    };

    // Function to close the modal
    function closeFinalizeSaleModal() {
        finalizeSaleModal.style.display = 'none';
    }

    // Event Listeners for modal buttons
    closeModalBtn.addEventListener('click', closeFinalizeSaleModal);
    cancelModalBtn.addEventListener('click', closeFinalizeSaleModal);

    // Payment method change logic
    paymentDinheiroRadio.addEventListener('change', function() {
        if (this.checked) {
            cashPaymentDetails.style.display = 'block';
            pixQrCodeDisplay.style.display = 'none';
            const total = parseFloat(modalSaleTotalSpan.textContent);
            amountReceivedInput.value = total.toFixed(2); // Reset amount received
            calculateChange();
        }
    });

    paymentPixRadio.addEventListener('change', function() {
        if (this.checked) {
            cashPaymentDetails.style.display = 'none';
            pixQrCodeDisplay.style.display = 'block';
        }
    });

    // Calculate change for cash payment
    amountReceivedInput.addEventListener('input', calculateChange);

    function calculateChange() {
        const total = parseFloat(modalSaleTotalSpan.textContent);
        const amountReceived = parseFloat(amountReceivedInput.value) || 0;
        const change = amountReceived - total;
        changeAmountSpan.textContent = `R$ ${change.toFixed(2)}`;

        // Enable/disable confirm button based on amount received
        if (paymentDinheiroRadio.checked && amountReceived < total) {
            confirmFinalizeSaleBtn.disabled = true;
        } else {
            confirmFinalizeSaleBtn.disabled = false;
        }
    }

    // Confirm Finalize Sale button logic
    confirmFinalizeSaleBtn.addEventListener('click', function() {
        if (cart.length === 0) {
            alert("O carrinho está vazio. Adicione produtos antes de finalizar a venda.");
            closeFinalizeSaleModal();
            return;
        }

        const saleData = {
            itens: cart.map(item => ({
                lote_id: item.lotId,
                quantidade: item.quantity,
                preco_unitario: item.price
            })),
            nome_cliente: clientNameInput.value.trim(),
            forma_pagamento: document.querySelector('input[name="paymentMethod"]:checked').value,
            valor_recebido: parseFloat(amountReceivedInput.value) || 0, // Only relevant for cash
            total_venda: parseFloat(modalSaleTotalSpan.textContent)
        };

        if (saleData.forma_pagamento === 'dinheiro' && saleData.valor_recebido < saleData.total_venda) {
            alert("O valor recebido é menor que o total da venda. Por favor, ajuste o valor ou a forma de pagamento.");
            return;
        }

        console.log("Dados da venda a serem enviados:", saleData);

        fetch('/pdv/api/finalizar-venda/', { // Adjust URL if different, use Django's URL if possible
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(saleData)
        })
        .then(response => {
            if (!response.ok) {
                // Try to parse JSON error message from backend
                return response.json().then(errorData => {
                    throw new Error(errorData.message || 'Erro desconhecido ao finalizar a venda.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert("Venda finalizada com sucesso! ID da Venda: " + data.venda_id);
                // Clear cart and update display on success
                cart.length = 0; // Clear the global cart array
                updateCartDisplay();
                // Clear search input and perform new search to refresh results if needed
                if (window.searchProductInput) { // Check if searchProductInput exists in the global scope
                    window.searchProductInput.value = '';
                }
                performSearch(); // Refresh search results or clear them
                closeFinalizeSaleModal();
            } else {
                alert("Erro ao finalizar a venda: " + (data.message || "Detalhes do erro desconhecidos."));
            }
        })
        .catch(error => {
            console.error("Erro na requisição de finalizar venda:", error);
            alert("Erro ao finalizar a venda: " + error.message);
        });
    });

    // Initial calculation for cash payment when modal opens
    amountReceivedInput.addEventListener('change', calculateChange); // Also on change to ensure accuracy
});