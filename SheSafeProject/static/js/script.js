function toggleForm() {
  const loginBox = document.getElementById("login-box");
  const signupBox = document.getElementById("signup-box");
  if (loginBox.style.display === "none") {
    loginBox.style.display = "block";
    signupBox.style.display = "none";
  } else {
    loginBox.style.display = "none";
    signupBox.style.display = "block";
  }
}