// Variables
const form = document.getElementById("contactForm");
const statusText = document.getElementById("status");

// Function
function validateForm(name, email, message) {
    if (name === "" || email === "" || message === "") {
        statusText.textContent = "All fields are required!";
        statusText.style.color = "red";
        return false;
    }

    let emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
    if (!email.match(emailPattern)) {
        statusText.textContent = "Invalid email format!";
        statusText.style.color = "red";
        return false;
    }

    return true;
}

form?.addEventListener("submit", function (e) {
    e.preventDefault();

    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let message = document.getElementById("message").value;

    if (validateForm(name, email, message)) {
        statusText.textContent = "Message sent successfully (Dummy)";
        statusText.style.color = "green";
        form.reset();
    }
});
