const API = "http://127.0.0.1:8000";

async function register() {

    const full_name = document.getElementById("full_name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    const response = await fetch(`${API}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            full_name,
            email,
            password,
            role
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail);
        return;
    }

    alert("Conta criada! Verifique seu email.");
}

async function login() {

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: email,
            password: password
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.detail);
        return;
    }

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("userRole", data.role);
    localStorage.setItem("userEmail", data.email);
    localStorage.setItem("userName", data.full_name);

    window.location.href = "/dashboard.html";
}
