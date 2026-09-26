document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // ELEMENTS
    // =========================

    const imageInput =
        document.getElementById("imageInput");

    const imageUploadOption =
        document.getElementById("imageUploadOption");

    const imagePreviewContainer =
        document.getElementById("imagePreviewContainer");

    const imagePreview =
        document.getElementById("imagePreview");

    const removeImageButton =
        document.getElementById("removeImageButton");

    const messageInput =
        document.getElementById("messageInput");

    const chatArea =
        document.getElementById("chatArea");


    // =========================
    // CHECK ELEMENTS
    // =========================

    if (
        !imageInput ||
        !imageUploadOption ||
        !imagePreviewContainer ||
        !imagePreview ||
        !removeImageButton ||
        !messageInput ||
        !chatArea
    ) {

        console.error(
            "Vision elements not found."
        );

        return;
    }


    // =========================
    // CURRENT IMAGE
    // =========================

    let currentImageFile = null;


    // =========================
    // OPEN IMAGE SELECTOR
    // =========================

    imageUploadOption.addEventListener(
        "click",
        () => {

            imageInput.click();

        }
    );


    // =========================
    // IMAGE SELECTED
    // =========================

    imageInput.addEventListener(
        "change",
        () => {

            const file =
                imageInput.files[0];

            if (!file) {
                return;
            }


            // =========================
            // TYPE CHECK
            // =========================

            if (
                !file.type.startsWith("image/")
            ) {

                alert(
                    "Please select a valid image."
                );

                imageInput.value = "";

                return;
            }


            // =========================
            // SIZE CHECK
            // =========================

            if (
                file.size >
                10 * 1024 * 1024
            ) {

                alert(
                    "Image must be smaller than 10 MB."
                );

                imageInput.value = "";

                return;
            }


            // =========================
            // SAVE IMAGE
            // =========================

            currentImageFile = file;


            // =========================
            // PREVIEW
            // =========================

            const imageURL =
                URL.createObjectURL(file);

            imagePreview.src =
                imageURL;

            imagePreviewContainer.hidden =
                false;


            console.log(
                "Image selected:",
                file.name
            );

        }
    );


    // =========================
    // REMOVE IMAGE
    // =========================

    removeImageButton.addEventListener(
        "click",
        () => {

            currentImageFile = null;

            imageInput.value = "";

            imagePreview.src = "";

            imagePreviewContainer.hidden =
                true;


            console.log(
                "Image removed."
            );

        }
    );


    // =========================
    // ERROR MESSAGE
    // =========================

    function createErrorMessage(
        message
    ) {

        const errorMessage =
            document.createElement("div");

        errorMessage.className =
            "message ai-message";


        errorMessage.innerHTML = `
            <div class="ai-icon">
                ✦
            </div>

            <div class="message-content">
                ${message}
            </div>
        `;


        return errorMessage;
    }


    // =========================
    // ANALYZING ANIMATION
    // =========================

    function startAnalyzingAnimation(
        loadingMessage
    ) {

        const textElement =
            loadingMessage.querySelector(
                ".analyzing-text"
            );

        if (!textElement) {
            return null;
        }


        let dots = 0;


        const interval =
            setInterval(
                () => {

                    dots++;

                    if (dots > 3) {
                        dots = 1;
                    }


                    textElement.textContent =
                        "Analyzing image" +
                        ".".repeat(dots);

                },
                400
            );


        return interval;
    }


    // =========================
    // TYPE AI RESPONSE
    // =========================

    async function typeAIResponse(
        content
    ) {

        const aiMessage =
            document.createElement("div");

        aiMessage.className =
            "message ai-message";


        const aiIcon =
            document.createElement("div");

        aiIcon.className =
            "ai-icon";

        aiIcon.textContent =
            "✦";


        const messageContent =
            document.createElement("div");

        messageContent.className =
            "message-content";


        aiMessage.appendChild(
            aiIcon
        );

        aiMessage.appendChild(
            messageContent
        );


        chatArea.appendChild(
            aiMessage
        );


        // =========================
        // START AT BOTTOM
        // =========================

        chatArea.scrollTop =
            chatArea.scrollHeight;


        // =========================
        // TYPING
        // =========================

        let currentText = "";


        for (
            let i = 0;
            i < content.length;
            i++
        ) {

            currentText +=
                content[i];


            // =========================
            // MARKDOWN
            // =========================

            if (
                typeof marked !== "undefined"
            ) {

                try {

                    messageContent.innerHTML =
                        marked.parse(
                            currentText
                        );

                } catch (error) {

                    console.error(
                        "Markdown rendering error:",
                        error
                    );

                    messageContent.textContent =
                        currentText;

                }

            } else {

                messageContent.textContent =
                    currentText;

            }


            // =========================
            // CODE HIGHLIGHTING
            // =========================

            if (
                typeof hljs !== "undefined"
            ) {

                messageContent
                    .querySelectorAll(
                        "pre code"
                    )
                    .forEach(
                        (block) => {

                            try {

                                hljs.highlightElement(
                                    block
                                );

                            } catch (error) {

                                console.error(
                                    "Highlight error:",
                                    error
                                );

                            }

                        }
                    );

            }


            // =========================
            // AUTO SCROLL
            // =========================

            chatArea.scrollTop =
                chatArea.scrollHeight;


            // =========================
            // TYPING SPEED
            // =========================

            await new Promise(
                (resolve) =>
                    setTimeout(
                        resolve,
                        12
                    )
            );

        }

    }


    // =====================================================
    // SEND VISION MESSAGE
    // =====================================================
    //
    // IMPORTANT:
    // Is function ko window par rakha gaya hai
    // taaki script.js bhi ise call kar sake.
    //
    // Send button aur Enter dono ultimately
    // script.js -> sendMessage()
    // -> sendVisionMessage()
    // ko use karenge.
    //
    // =====================================================

    window.sendVisionMessage =
        async function () {

            // =========================
            // GET CURRENT IMAGE
            // =========================

            const file =
                currentImageFile ||
                imageInput.files[0];


            if (!file) {

                return;

            }


            // =========================
            // QUESTION
            // =========================

            let question =
                messageInput.value.trim();


            if (!question) {

                question =
                    "Describe this image and explain what you can see.";

            }


            // =========================
            // USER MESSAGE
            // =========================

            const userMessage =
                document.createElement("div");

            userMessage.className =
                "message user-message";


            userMessage.innerHTML = `
                <div class="message-content">

                    <img
                        src="${imagePreview.src}"
                        alt="Uploaded image"
                        style="
                            max-width: 220px;
                            max-height: 180px;
                            width: auto;
                            height: auto;
                            border-radius: 12px;
                            display: block;
                            margin-bottom: 10px;
                            object-fit: cover;
                        "
                    >

                    <div>
                        ${question}
                    </div>

                </div>
            `;


            chatArea.appendChild(
                userMessage
            );


            // =========================
            // GO TO BOTTOM
            // =========================

            chatArea.scrollTop =
                chatArea.scrollHeight;


            // =========================
            // CLEAR QUESTION ONLY
            // =========================

            messageInput.value =
                "";


            // =========================
            // FORM DATA
            // =========================

            const formData =
                new FormData();


            formData.append(
                "image",
                file
            );


            formData.append(
                "question",
                question
            );


            // =========================
            // DISABLE SEND
            // =========================

            const sendButton =
                document.getElementById(
                    "sendButton"
                );


            if (sendButton) {

                sendButton.disabled =
                    true;

            }


            // =========================
            // LOADING MESSAGE
            // =========================

            const loadingMessage =
                document.createElement("div");

            loadingMessage.className =
                "message ai-message";


            loadingMessage.innerHTML = `
                <div class="ai-icon">
                    ✦
                </div>

                <div class="message-content">

                    <span class="analyzing-text">
                        Analyzing image.
                    </span>

                </div>
            `;


            chatArea.appendChild(
                loadingMessage
            );


            chatArea.scrollTop =
                chatArea.scrollHeight;


            // =========================
            // START LOADING ANIMATION
            // =========================

            const analyzingInterval =
                startAnalyzingAnimation(
                    loadingMessage
                );


            // =========================
            // API REQUEST
            // =========================

            try {

                const response =
                    await fetch(
                        "/api/vision",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                let data = {};

                try {

                    data =
                        await response.json();

                } catch (jsonError) {

                    console.error(
                        "Invalid JSON response:",
                        jsonError
                    );

                }


                // =========================
                // STOP LOADING
                // =========================

                clearInterval(
                    analyzingInterval
                );


                loadingMessage.remove();


                // =========================
                // API ERROR
                // =========================

                if (
                    !response.ok ||
                    data.error
                ) {

                    const errorText =
                        data.error ||
                        "Unable to analyze the image.";


                    const errorMessage =
                        createErrorMessage(
                            errorText
                        );


                    chatArea.appendChild(
                        errorMessage
                    );


                    chatArea.scrollTop =
                        chatArea.scrollHeight;


                    return;

                }


                // =========================
                // AI RESPONSE
                // =========================

                const aiReply =
                    data.reply ||
                    "I couldn't generate a response.";


                await typeAIResponse(
                    aiReply
                );


                // =========================
                // KEEP IMAGE
                // =========================
                //
                // Image clear nahi hogi.
                // Same image par next question
                // directly pooch sakte ho.
                //
                // =========================

                console.log(
                    "Image retained for follow-up."
                );

            }


            // =========================
            // REQUEST ERROR
            // =========================

            catch (error) {

                console.error(
                    "Vision request error:",
                    error
                );


                clearInterval(
                    analyzingInterval
                );


                loadingMessage.remove();


                const errorMessage =
                    createErrorMessage(
                        "Unable to connect to Vision AI."
                    );


                chatArea.appendChild(
                    errorMessage
                );


                chatArea.scrollTop =
                    chatArea.scrollHeight;

            }


            // =========================
            // ENABLE SEND AGAIN
            // =========================

            if (sendButton) {

                sendButton.disabled =
                    false;

            }

        };

});