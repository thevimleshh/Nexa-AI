// =========================
// DOM ELEMENTS
// =========================

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const chatArea =
    document.getElementById("chatArea");

const userName =
    document.getElementById("userName");

const userEmail =
    document.getElementById("userEmail");

const userAvatar =
    document.getElementById("userAvatar");

const logoutButton =
    document.getElementById("logoutButton");

const welcomeScreen =
    document.getElementById("welcomeScreen");

const chatHistory =
    document.getElementById("chatHistory");

const newChatButton =
    document.getElementById("newChatButton");

const settingsButton =
    document.getElementById("settingsButton");

const settingsModal =
    document.getElementById("settingsModal");

const settingsCloseButton =
    document.getElementById("settingsCloseButton");

const settingsUserName =
    document.getElementById("settingsUserName");

const settingsUserEmail =
    document.getElementById("settingsUserEmail");


// =========================
// DELETE MODAL ELEMENTS
// =========================

const deleteModal =
    document.getElementById("deleteModal");

const cancelDeleteButton =
    document.getElementById("cancelDeleteButton");

const confirmDeleteButton =
    document.getElementById("confirmDeleteButton");


// =========================
// CURRENT CONVERSATION
// =========================

let currentConversationId = null;


// =========================
// CONVERSATION TO DELETE
// =========================

let conversationToDelete = null;


// =========================
// CHAT SCROLL STATE
// =========================

let userManuallyScrolled = false;


// =========================
// CHAT SCROLL DETECTION
// =========================

if (chatArea) {

    chatArea.addEventListener(
        "scroll",
        function () {

            const distanceFromBottom =
                chatArea.scrollHeight -
                chatArea.scrollTop -
                chatArea.clientHeight;


            if (distanceFromBottom > 80) {

                userManuallyScrolled = true;

            } else {

                userManuallyScrolled = false;

            }

        }
    );

}


// =========================
// SETTINGS
// =========================

function openSettings() {

    if (!settingsModal) {
        return;
    }

    settingsModal.classList.add("show");

    if (userName && settingsUserName) {

        settingsUserName.textContent =
            userName.textContent;

    }

    if (userEmail && settingsUserEmail) {

        settingsUserEmail.textContent =
            userEmail.textContent;

    }

}


function closeSettings() {

    if (!settingsModal) {
        return;
    }

    settingsModal.classList.remove("show");

}


// =========================
// LOAD CURRENT USER
// =========================

async function loadCurrentUser() {

    try {

        const response =
            await fetch("/api/me");


        const data =
            await response.json();


        if (!data.logged_in) {

            window.location.href =
                "/login";

            return;

        }


        if (userName) {

            userName.textContent =
                data.user.name;

        }


        if (userEmail) {

            userEmail.textContent =
                data.user.email;

        }


        if (userAvatar) {

            userAvatar.textContent =
                data.user.name
                    .charAt(0)
                    .toUpperCase();

        }


    } catch (error) {

        console.error(
            "Failed to load user:",
            error
        );

    }

}


// =========================
// LOGOUT
// =========================

async function logoutUser() {

    try {

        const response =
            await fetch(
                "/api/logout",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (data.success) {

            window.location.href =
                "/login";

        }


    } catch (error) {

        console.error(
            "Logout failed:",
            error
        );

    }

}


// =========================
// COPY CODE
// =========================

async function copyCode(button) {

    const codeBlock =
        button
            .closest(".code-block")
            .querySelector("code");


    const code =
        codeBlock.innerText;


    try {

        await navigator.clipboard.writeText(
            code
        );


        button.textContent =
            "Copied!";


        setTimeout(
            function () {

                button.textContent =
                    "Copy";

            },
            1500
        );


    } catch (error) {

        console.error(
            "Copy failed:",
            error
        );

    }

}


// =========================
// LOAD CHAT HISTORY
// =========================

async function loadChatHistory() {

    try {

        const response =
            await fetch(
                "/api/conversations"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load conversations"
            );

        }


        const data =
            await response.json();


        chatHistory.innerHTML =
            "";


        data.conversations.forEach(
            conversation => {

                const chatItem =
                    document.createElement("div");


                chatItem.className =
                    "chat-history-item";


                chatItem.dataset.id =
                    conversation.id;


                // =========================
                // DATE
                // =========================

                const chatDate =
                    new Date(
                        conversation.created_at
                    );


                const formattedDate =
                    chatDate.toLocaleDateString(
                        "en-IN",
                        {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        }
                    );


                // =========================
                // TIME
                // =========================

                const formattedTime =
                    chatDate.toLocaleTimeString(
                        "en-IN",
                        {
                            hour: "2-digit",
                            minute: "2-digit",
                            hour12: true
                        }
                    );


                // =========================
                // CHAT TITLE
                // =========================

                let chatTitle =
                    conversation.title;


                if (
                    chatTitle.length > 30
                ) {

                    chatTitle =
                        chatTitle.substring(
                            0,
                            30
                        ) + "...";

                }


                // =========================
                // CHAT ITEM
                // =========================

                chatItem.innerHTML = `
                    <div class="chat-info">

                        <div class="chat-title">
                            ${chatTitle}
                        </div>

                        <div class="chat-date">
                            ${formattedDate} • ${formattedTime}
                        </div>

                    </div>

                    <button
                        class="delete-chat-button"
                        title="More options"
                        type="button"
                    >
                        ⋮
                    </button>
                `;


                // =========================
                // DELETE BUTTON
                // =========================

                const deleteButton =
                    chatItem.querySelector(
                        ".delete-chat-button"
                    );


                deleteButton.addEventListener(
                    "click",
                    function (event) {

                        event.stopPropagation();


                        openDeleteModal(
                            conversation.id,
                            conversation.title
                        );

                    }
                );


                // =========================
                // OPEN CONVERSATION
                // =========================

                chatItem.addEventListener(
                    "click",
                    function () {

                        openConversation(
                            conversation.id
                        );

                    }
                );


                chatHistory.appendChild(
                    chatItem
                );

            }
        );


    } catch (error) {

        console.error(
            "Failed to load chat history:",
            error
        );

    }

}


// =========================
// SETTINGS EVENTS
// =========================

if (settingsButton) {

    settingsButton.addEventListener(
        "click",
        openSettings
    );

}


if (settingsCloseButton) {

    settingsCloseButton.addEventListener(
        "click",
        closeSettings
    );

}


if (settingsModal) {

    settingsModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                settingsModal
            ) {

                closeSettings();

            }

        }
    );

}


// =========================
// USER MESSAGE
// =========================

function addUserMessage(message) {

    const userMessage =
        document.createElement("div");


    userMessage.className =
        "message user-message";


    userMessage.innerHTML = `
        <div class="message-content">
            ${message}
        </div>
    `;


    chatArea.appendChild(
        userMessage
    );

}


// =========================
// LOADING MESSAGE
// =========================

function showLoadingMessage() {

    const loadingMessage =
        document.createElement("div");


    loadingMessage.className =
        "message ai-message";


    loadingMessage.id =
        "loadingMessage";


    loadingMessage.innerHTML = `
        <div class="ai-icon">✦</div>

        <div class="message-content loading-text">
            Finding your answer<span class="dots">...</span>
        </div>
    `;


    chatArea.appendChild(
        loadingMessage
    );


    userManuallyScrolled = false;


    chatArea.scrollTop =
        chatArea.scrollHeight;

}


// =========================
// REMOVE LOADING MESSAGE
// =========================

function removeLoadingMessage() {

    const loadingMessage =
        document.getElementById(
            "loadingMessage"
        );


    if (loadingMessage) {

        loadingMessage.remove();

    }

}


// =========================
// MARKDOWN RENDERER
// =========================

function renderMarkdown(message) {

    const renderer =
        new marked.Renderer();


    renderer.code = function (
        code,
        language
    ) {

        let validLanguage =
            language || "plaintext";


        if (
            !hljs.getLanguage(
                validLanguage
            )
        ) {

            validLanguage =
                "plaintext";

        }


        const highlightedCode =
            hljs.highlight(
                code,
                {
                    language:
                        validLanguage
                }
            ).value;


        return `
            <div class="code-block">

                <div class="code-header">

                    <span class="code-language">
                        ${validLanguage}
                    </span>

                    <button
                        class="copy-code-button"
                        type="button"
                        onclick="copyCode(this)"
                    >
                        Copy
                    </button>

                </div>

                <pre><code>${highlightedCode}</code></pre>

            </div>
        `;

    };


    return marked.parse(
        message,
        {
            renderer: renderer
        }
    );

}


// =========================
// NEW AI MESSAGE
// =========================

function addAIMessage(text) {

    const aiMessage =
        document.createElement("div");


    aiMessage.className =
        "message ai-message";


    aiMessage.innerHTML = `
        <div class="ai-icon">✦</div>

        <div class="message-content"></div>
    `;


    chatArea.appendChild(
        aiMessage
    );


    const messageContent =
        aiMessage.querySelector(
            ".message-content"
        );


    userManuallyScrolled = false;


    chatArea.scrollTop =
        chatArea.scrollHeight;


    let index = 0;


    // =========================
    // TYPE RESPONSE
    // =========================

    function typeNextCharacter() {

        if (index < text.length) {

            index++;


            messageContent.innerHTML =
                renderMarkdown(
                    text.substring(
                        0,
                        index
                    )
                );


            if (
                !userManuallyScrolled
            ) {

                chatArea.scrollTop =
                    chatArea.scrollHeight;

            }


            setTimeout(
                typeNextCharacter,
                12
            );

        } else {

            messageContent.innerHTML =
                renderMarkdown(text);


            if (
                !userManuallyScrolled
            ) {

                chatArea.scrollTop =
                    chatArea.scrollHeight;

            }

        }

    }


    typeNextCharacter();

}


// =========================
// OLD AI MESSAGE
// =========================

function addOldAIMessage(message) {

    const aiMessage =
        document.createElement("div");


    aiMessage.className =
        "message ai-message";


    aiMessage.innerHTML = `
        <div class="ai-icon">✦</div>

        <div class="message-content"></div>
    `;


    chatArea.appendChild(
        aiMessage
    );


    const messageContent =
        aiMessage.querySelector(
            ".message-content"
        );


    messageContent.innerHTML =
        renderMarkdown(message);

}


// =========================
// SEND MESSAGE
// =========================

async function sendMessage() {

    // =========================
    // CHECK IMAGE
    // =========================

    const imageInput =
        document.getElementById(
            "imageInput"
        );


    if (
        imageInput &&
        imageInput.files.length > 0
    ) {

        // =========================
        // VISION MESSAGE
        // =========================

        if (
            typeof window.sendVisionMessage ===
            "function"
        ) {

            await window.sendVisionMessage();

        } else {

            console.error(
                "Vision function is not available."
            );

        }


        return;

    }


    // =========================
    // NORMAL TEXT MESSAGE
    // =========================

    const message =
        messageInput.value.trim();


    if (
        message === ""
    ) {

        return;

    }


    // =========================
    // HIDE WELCOME
    // =========================

    welcomeScreen.style.display =
        "none";


    // =========================
    // USER MESSAGE
    // =========================

    addUserMessage(
        message
    );


    // =========================
    // CLEAR INPUT
    // =========================

    messageInput.value =
        "";


    // =========================
    // SHOW LOADING
    // =========================

    showLoadingMessage();


    try {

        const response =
            await fetch(
                "/api/chat",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        message:
                            message,

                        conversation_id:
                            currentConversationId

                    })

                }
            );


        if (!response.ok) {

            throw new Error(
                "API request failed"
            );

        }


        const data =
            await response.json();


        // =========================
        // LOGIN CHECK
        // =========================

        if (
            data.error ===
            "Please login first."
        ) {

            window.location.href =
                "/login";

            return;

        }


        // =========================
        // SAVE CONVERSATION ID
        // =========================

        currentConversationId =
            data.conversation_id;


        // =========================
        // REMOVE LOADING
        // =========================

        removeLoadingMessage();


        // =========================
        // AI RESPONSE
        // =========================

        addAIMessage(
            data.reply
        );


        // =========================
        // REFRESH HISTORY
        // =========================

        await loadChatHistory();


    } catch (error) {

        console.error(
            "Error:",
            error
        );


        removeLoadingMessage();


        addAIMessage(
            "⚠️ **Something went wrong.**\n\nPlease try again in a moment."
        );

    }

}


// =========================
// OPEN CHAT HISTORY
// =========================

async function openConversation(
    conversationId
) {

    if (
        currentConversationId ===
        conversationId
    ) {

        return;

    }


    try {

        const response =
            await fetch(
                `/api/conversations/${conversationId}`
            );


        if (!response.ok) {

            throw new Error(
                "Failed to open conversation"
            );

        }


        const data =
            await response.json();


        if (data.error) {

            console.error(
                data.error
            );

            return;

        }


        // =========================
        // SET CURRENT CONVERSATION
        // =========================

        currentConversationId =
            data.conversation_id;


        // =========================
        // CLEAR CHAT
        // =========================

        chatArea.innerHTML =
            "";


        userManuallyScrolled =
            false;


        // =========================
        // HIDE WELCOME
        // =========================

        welcomeScreen.style.display =
            "none";


        // =========================
        // LOAD MESSAGES
        // =========================

        data.messages.forEach(
            message => {

                if (
                    message.role ===
                    "user"
                ) {

                    addUserMessage(
                        message.content
                    );

                } else if (
                    message.role ===
                    "assistant"
                ) {

                    addOldAIMessage(
                        message.content
                    );

                }

            }
        );


        // =========================
        // GO TO BOTTOM
        // =========================

        chatArea.scrollTop =
            chatArea.scrollHeight;


    } catch (error) {

        console.error(
            "Failed to open conversation:",
            error
        );

    }

}


// =========================
// NEW CHAT
// =========================

function startNewChat() {

    currentConversationId =
        null;


    userManuallyScrolled =
        false;


    chatArea.innerHTML =
        "";


    welcomeScreen.style.display =
        "flex";


    messageInput.value =
        "";


    // =========================
    // CLEAR IMAGE
    // =========================

    const imageInput =
        document.getElementById(
            "imageInput"
        );

    const imagePreview =
        document.getElementById(
            "imagePreview"
        );

    const imagePreviewContainer =
        document.getElementById(
            "imagePreviewContainer"
        );


    if (imageInput) {

        imageInput.value =
            "";

    }


    if (imagePreview) {

        imagePreview.src =
            "";

    }


    if (imagePreviewContainer) {

        imagePreviewContainer.hidden =
            true;

    }


    messageInput.focus();

}


// =========================
// OPEN DELETE MODAL
// =========================

function openDeleteModal(
    conversationId,
    conversationTitle
) {

    conversationToDelete =
        conversationId;


    const deleteChatName =
        document.getElementById(
            "deleteChatName"
        );


    if (deleteChatName) {

        let title =
            conversationTitle;


        if (
            title.length > 40
        ) {

            title =
                title.substring(
                    0,
                    40
                ) + "...";

        }


        deleteChatName.textContent =
            title;

    }


    if (deleteModal) {

        deleteModal.classList.add(
            "show"
        );

    }

}


// =========================
// CLOSE DELETE MODAL
// =========================

function closeDeleteModal() {

    conversationToDelete =
        null;


    if (deleteModal) {

        deleteModal.classList.remove(
            "show"
        );

    }

}


// =========================
// DELETE CONVERSATION
// =========================

async function deleteConversation(
    conversationId
) {

    try {

        const response =
            await fetch(
                `/api/conversations/${conversationId}`,
                {
                    method: "DELETE"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to delete conversation"
            );

        }


        if (
            currentConversationId ===
            conversationId
        ) {

            currentConversationId =
                null;


            chatArea.innerHTML =
                "";


            welcomeScreen.style.display =
                "flex";

        }


        closeDeleteModal();


        await loadChatHistory();


    } catch (error) {

        console.error(
            "Delete error:",
            error
        );


        alert(
            "Unable to delete chat. Please try again."
        );

    }

}


// =========================
// CONFIRM DELETE
// =========================

if (confirmDeleteButton) {

    confirmDeleteButton.addEventListener(
        "click",
        function () {

            if (
                conversationToDelete !==
                null
            ) {

                deleteConversation(
                    conversationToDelete
                );

            }

        }
    );

}


// =========================
// CANCEL DELETE
// =========================

if (cancelDeleteButton) {

    cancelDeleteButton.addEventListener(
        "click",
        function () {

            closeDeleteModal();

        }
    );

}


// =========================
// DELETE MODAL CLICK
// =========================

if (deleteModal) {

    deleteModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                deleteModal
            ) {

                closeDeleteModal();

            }

        }
    );

}


// =========================
// ESCAPE KEY
// =========================

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape"
        ) {

            closeDeleteModal();

        }

    }
);


// =========================
// NEW CHAT BUTTON
// =========================

if (newChatButton) {

    newChatButton.addEventListener(
        "click",
        startNewChat
    );

}


// =========================
// SEND BUTTON
// =========================
// IMPORTANT:
// Sirf script.js Send button
// ko handle karega.
// vision.js direct listener
// nahi lagayega.
// =========================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            sendMessage();

        }
    );

}


// =========================
// ENTER KEY
// =========================

if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


// =========================
// LOGOUT BUTTON
// =========================

if (logoutButton) {

    logoutButton.addEventListener(
        "click",
        logoutUser
    );

}


// =========================
// INITIALIZE APP
// =========================

loadCurrentUser();

loadChatHistory();


// =========================
// THEME TOGGLE
// =========================

const themeToggle =
    document.getElementById(
        "themeToggle"
    );

const themeDescription =
    document.getElementById(
        "themeDescription"
    );


if (themeToggle) {

    themeToggle.addEventListener(
        "change",
        function () {

            if (themeToggle.checked) {

                document.body.classList.add(
                    "light-theme"
                );

                localStorage.setItem(
                    "theme",
                    "light"
                );

                if (themeDescription) {

                    themeDescription.textContent =
                        "Light mode";

                }

            } else {

                document.body.classList.remove(
                    "light-theme"
                );

                localStorage.setItem(
                    "theme",
                    "dark"
                );

                if (themeDescription) {

                    themeDescription.textContent =
                        "Dark mode";

                }

            }

        }
    );


    // =========================
    // LOAD SAVED THEME
    // =========================

    const savedTheme =
        localStorage.getItem(
            "theme"
        );


    if (savedTheme === "light") {

        document.body.classList.add(
            "light-theme"
        );

        themeToggle.checked =
            true;

        if (themeDescription) {

            themeDescription.textContent =
                "Light mode";

        }

    } else {

        document.body.classList.remove(
            "light-theme"
        );

        themeToggle.checked =
            false;

        if (themeDescription) {

            themeDescription.textContent =
                "Dark mode";

        }

    }

}