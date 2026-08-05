document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.getElementById("fileInput");
    const dropZone = document.getElementById("dropZone");
    const preview = document.getElementById("preview");
    const previewCard = document.getElementById("previewCard");
    const loader = document.getElementById("loader");
    const form = document.getElementById("uploadForm");

    // Click to upload
    dropZone.addEventListener("click", () => fileInput.click());

    // Drag & Drop
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.background = "#dcedc8";
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.background = "transparent";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        fileInput.files = e.dataTransfer.files;
        showPreview(fileInput.files[0]);
    });

    // File select
    fileInput.addEventListener("change", function () {
        showPreview(this.files[0]);
    });

    function showPreview(file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            previewCard.classList.remove("d-none");
        };

        reader.readAsDataURL(file);
    }

    // Show loader on submit
    form.addEventListener("submit", function () {
        loader.classList.remove("d-none");
    });

});