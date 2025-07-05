function showForm(id) {
      const forms = document.querySelectorAll("form");
      forms.forEach((form) => form.classList.remove("active"));
      document.getElementById(id).classList.add("active");
    }