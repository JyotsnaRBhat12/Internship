function validate() {
  const nameField = document.getElementById("name");
  const emailField = document.getElementById("email");
  const msgField = document.getElementById("msg");

  if (
    nameField.value.trim() === "" ||
    emailField.value.trim() === "" ||
    msgField.value.trim() === ""
  ) {
    alert("Fill all fields");
    return false;
  }

  // Email format validation
  const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
  if (!emailPattern.test(emailField.value)) {
    alert("Enter a valid email");
    return false;
  }

  alert("Message sent successfully (dummy submit)");
  return false; // prevents page reload
}
