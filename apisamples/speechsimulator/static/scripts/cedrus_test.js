// ==================== Нужные функции ================================

async function initCom() {
    const port = await navigator.serial.requestPort();
    await port.open({ baudRate: 115200, stopBits: 1, parity: "none" });
    const com_writer = port.writable.getWriter();
    return [port, com_writer];
}

// https://cedrus.com/support/xid/commands.htm - тут описаны команды.

// Символы идут по одному байту (числа от 0 до 255), подаются команды mhXX, XX - два байта с меткой,
// по ASCII таблице m в байтовом представлении это 109, h - 104. 
// Метки кодируется хитрее, и проще это понять, если посмотреть на двоичное представление в HEX-editior'е.

// Есть некоторые особенности оборудования при получении меток:
// Метки 1-15 отправляются без проблем.
// Метка 0 не отображается (и на запись скорее всего тоже не попадает).
// Метки 16 и далее уже закодировать не получается из-за блокировки битов 5-8;

async function sendLabel(label_number, com_writer) {
    if ((label_number < 0) || (label_number > 255)) {
        console.error('Плохая метка:', label_number);
        return;
    }

    await com_writer.write(
        new Uint8Array([109, 104, label_number, 0]));
}

// Порядковый номер метки в ее битовую маску.
function labelNumberToMask(label_number) {
    if (typeof label_number != 'number') {
        console.error(label_number, 'is not a number');
        return;
    }
    if ((label_number < 0) | (label_number > 127)) {
        console.error(label_number, 'is not in range [0; 127]');
        return;
    }
    mask = Array(8);
    mask[0] = 0;
    current_bit = 1
    while (label_number != 0) {
        mask[current_bit++] = label_number % 2
        label_number = Math.floor(label_number / 2)
    }
    return mask;
}

// Маска метки в ее порядковый номер.
function maskToLabelNumber(mask) {
    if (!Array.isArray(mask) || (mask.length != 8)) {
        console.error(mask, 'not an array of length 8!');
        return;
    }
    label_number = 0;
    for (current_bit = 1; current_bit < 8; current_bit++) {
        label_number += mask[current_bit] * Math.pow(2, current_bit - 1);
    }
    return label_number;
}

// Маска метки в ее код, отправляемый на стимтрекер. 
// Отличается от функции выше из-за порядка битов и сдвига на один бит вправо.
function maskToLabelCode(mask) {
    if (!Array.isArray(mask) || (mask.length != 8)) {
        console.error(mask, 'not an array of length 8!');
        return;
    }
    label_number = 0;
    for (current_bit = 0; current_bit < 8; current_bit++) {
        label_number += mask[current_bit] * Math.pow(2, 7 - current_bit);
    }
    return label_number;
}

// ==================== Хэндлеры для элементов HTML ======================

connect_com_button = document.getElementById('connect_com_button');
close_com_button = document.getElementById('close_com_button');
select_label_slider = document.getElementById('select_label_slider');
send_label_button = document.getElementById('send_label_button');
mask_bit_checkboxes = document.getElementsByClassName('mask_bit');

async function onConnectComButtonClicked() {
    [port, com_writer] = await initCom();
    port = port;
    com_writer = com_writer;
    enable_com_operations(open_enabled=false);
}

async function onCloseComButtonClicked() {
    if (!window.port) {
        alert('Подключитесь к COM порту!');
        return;
    }

    await com_writer.close();
    port.close();
    enable_com_operations(open_enabled=true);
}

function updateButtonText() {
    label_mask = getMaskFromCheckboxes();
    label_code = maskToLabelCode(label_mask);
    label_number = maskToLabelNumber(label_mask);
    send_label_button.textContent =
        `Отправить метку №${(label_mask[0] == 1) ? '?' : ''}${label_number} (с кодом ${label_code})`;
}

function onSliderChanged() {
    unmaped_bit_set = getMaskFromCheckboxes()[0];
    label_mask = labelNumberToMask(parseInt(select_label_slider.value));
    for (bit_number = 0; bit_number < 7; bit_number++) {
        document.getElementById(`mask_bit_${bit_number}`).checked = label_mask[bit_number + 1];
    }
    document.getElementById('mask_bit_?').checked = unmaped_bit_set;
    updateButtonText();
}

function onSendLabelButtonClicked() {
    if (!window.com_writer) {
        alert('Подключитесь к COM порту!');
        return;
    }
    sendLabel(maskToLabelCode(getMaskFromCheckboxes()), com_writer);
}

function getMaskFromCheckboxes() {
    unmaped_bit_set = false;
    mask = Array(8);
    for (let mask_bit_checkbox of mask_bit_checkboxes) {
        bit_number = mask_bit_checkbox.id.split('_')[2];
        if (bit_number === '?') {
            if (mask_bit_checkbox.checked) {
                unmaped_bit_set = true;
            }
        } else {
            bit_number = parseInt(bit_number);
            mask[bit_number + 1] = Number(mask_bit_checkbox.checked);
        }
    }
    mask[0] = Number(unmaped_bit_set);

    return mask;
}

function onMaskBitCheckboxChanged() {
    mask = getMaskFromCheckboxes();
    updateButtonText();
    select_label_slider.value = maskToLabelNumber(mask);
    return mask;
}

function enable_com_operations(open_enabled) {
    connect_com_button.disabled = !open_enabled;
    close_com_button.disabled = open_enabled;
    send_label_button.disabled = open_enabled;
}

connect_com_button.onclick = onConnectComButtonClicked;
close_com_button.onclick = onCloseComButtonClicked;
select_label_slider.oninput = onSliderChanged;
send_label_button.onclick = onSendLabelButtonClicked;
for (let mask_bit_checkbox of mask_bit_checkboxes) {
    mask_bit_checkbox.addEventListener('change', onMaskBitCheckboxChanged);
}

enable_com_operations(open_enabled = true);
select_label_slider.value = 1
select_label_slider.oninput();