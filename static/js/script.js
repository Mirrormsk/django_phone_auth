$(document).ready(function() {
    // обработчик нажатия на кнопку с цифрой
    $('.key').click(function() {
        var key = $(this).text(); // получаем текст кнопки (цифру)
        var input = $('#phone-input'); // получаем поле ввода
        var value = input.val(); // получаем текущее значение поля ввода

        if (key === 'Удалить') {
            // если нажата кнопка "Удалить", удаляем последний символ
            input.val(value.slice(0, -1));
        } else if (key !== 'Ввод') {
            // если нажата кнопка с цифрой, добавляем ее к значению поля ввода
            input.val(value + key);
        } else if (key === 'Ввод') {
            $('#phone-form').submit();
        }
    });
});