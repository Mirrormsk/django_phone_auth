const phoneInput = document.querySelector('#phone');
const keys = document.querySelectorAll('.key');
const form = document.querySelector('#form');

keys.forEach(key => {
    key.addEventListener('click', () => {
        if (key.textContent === 'Удалить') {
            phoneInput.value = phoneInput.value.slice(0, -1);
        } else if (key.textContent === 'Enter') {
            form.submit();
        } else {
            phoneInput.value += key.textContent;
        }
    });
});
