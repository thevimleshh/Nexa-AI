/* =========================================
   NEXA AI - ATTACH MENU
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const attachButton =
        document.getElementById("attachButton");

    const attachMenu =
        document.getElementById("attachMenu");


    // Safety check
    if (!attachButton || !attachMenu) {
        return;
    }


    /* =========================================
       OPEN / CLOSE MENU
    ========================================= */

    attachButton.addEventListener("click", (event) => {

        event.stopPropagation();

        attachMenu.classList.toggle("show");

    });


    /* =========================================
       CLOSE WHEN CLICKING OUTSIDE
    ========================================= */

    document.addEventListener("click", (event) => {

        if (
            !attachMenu.contains(event.target) &&
            !attachButton.contains(event.target)
        ) {

            attachMenu.classList.remove("show");

        }

    });


    /* =========================================
       OPTION BUTTONS
       TEMPORARY
    ========================================= */

    const imageUploadOption =
        document.getElementById("imageUploadOption");

    const imageGenerateOption =
        document.getElementById("imageGenerateOption");

    const voiceOption =
        document.getElementById("voiceOption");

    const pdfOption =
        document.getElementById("pdfOption");


    /* =========================================
   IMAGE UPLOAD
========================================= */

const imageInput =
    document.getElementById("imageInput");


if (imageUploadOption && imageInput) {

    /* OPEN FILE PICKER */

    imageUploadOption.addEventListener("click", () => {

        imageInput.click();

        attachMenu.classList.remove("show");

    });



}


    /* IMAGE GENERATION */

    if (imageGenerateOption) {

        imageGenerateOption.addEventListener("click", () => {

            console.log("Image Generation selected");

        });

    }


    /* VOICE */

    if (voiceOption) {

        voiceOption.addEventListener("click", () => {

            console.log("Voice selected");

        });

    }


    /* PDF */

    if (pdfOption) {

        pdfOption.addEventListener("click", () => {

            console.log("PDF selected");

        });

    }

});