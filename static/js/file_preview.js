document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file");
    const fileNameDisplay = document.getElementById("filename-display");

    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener("change", function () {
            if (fileInput.files.length > 0) {
                fileNameDisplay.textContent = fileInput.files[0].name;
            } else {
                fileNameDisplay.textContent = "Файл не выбран";
            }
        });
    }
});