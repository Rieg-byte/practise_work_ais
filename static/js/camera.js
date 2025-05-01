const video = document.getElementById('videoStream');
const button = document.getElementById('toggleCameraBtn');
const statusText = document.getElementById('status');

let streaming = false;

async function toggleCamera() {
    if (!streaming) {
        try {
            statusText.textContent = 'Подключение к камере...';
            video.src = VIDEO_FEED_URL;

            button.textContent = 'Выключить камеру';
            statusText.textContent = 'Камера включена';
            streaming = true;

        } catch (err) {
            console.error("Ошибка подключения к камере:", err);
            alert("Не удалось запустить камеру");
            statusText.textContent = 'Ошибка подключения к камере';
        }
    } else {
        video.src = '';
        button.textContent = 'Включить камеру';
        statusText.textContent = 'Камера выключена';
        streaming = false;
    }
}

button.addEventListener('click', toggleCamera);