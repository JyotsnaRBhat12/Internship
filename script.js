document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("contactForm");
    const emailInput = document.getElementById("email");
    const messageBox = document.getElementById("formMessage");

    if (!form) return; 

    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,}$/i;

    emailInput.addEventListener("input", () => {
        if (!emailInput.value.match(emailPattern)) {
            emailInput.style.borderColor = "red";
        } else {
            emailInput.style.borderColor = "#00e5ff";
        }
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        if (!emailInput.value.match(emailPattern)) {
            messageBox.style.color = "red";
            messageBox.innerText = "Please enter a valid email address!";
            return;
        }

        messageBox.style.color = "#00e5ff";
        messageBox.innerText = "Message sent successfully ";

        form.reset();
    });

});



