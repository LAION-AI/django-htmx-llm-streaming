// static/streaming/chat.js
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const chatArea = document.getElementById("chat-area");
    
    form.addEventListener("submit", function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const message = formData.get("message");

        // Clear previous chat area
        chatArea.innerHTML = "";

        // Send the user message via EventSource
        const eventSource = new EventSource(`/stream/${message}/`);
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.response) {
                chatArea.innerHTML += `${data.response}`;
            }
            if (data.done) {
                console.log("Stream done, closing connection.");
                eventSource.close();
            }
        };
        
        eventSource.onerror = function(event) {
            console.error("EventSource failed:", event);
            eventSource.close();
        };

        eventSource.onopen = function() {
            console.log("Connection to server opened.");
        };

        eventSource.onclose = function() {
            console.log("Connection to server closed.");
        };
    });
});
