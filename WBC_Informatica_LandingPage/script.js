let cartCount = 0;
const cartCountElement = document.getElementById('cart-count');
const addCartButtons = document.querySelectorAll('.add-cart');

addCartButtons.forEach(button => {
    button.addEventListener('click', () => {
        cartCount++;
        cartCountElement.textContent = cartCount;
        alert('Produto adicionado ao carrinho!');
    });
});