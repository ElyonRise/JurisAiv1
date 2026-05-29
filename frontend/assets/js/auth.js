const API = "https://jurisaiv1.up.railway.app";

async function register() {
    const full_name = document.getElementById("full_name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const role = document.getElementById("role").value;

    const oab_number = document.getElementById("oab_number") ? document.getElementById("oab_number").value.trim() : null;
    const oab_seccional = document.getElementById("oab_seccional") ? document.getElementById("oab_seccional").value.trim() : null;
    const especializacao = document.getElementById("especializacao") ? document.getElementById("especializacao").value.trim() : null;
    const experiencia = document.getElementById("experiencia") ? parseInt(document.getElementById("experiencia").value) : null;

    if (!full_name || !email || !password || !role) {
        alert("Preencha todos os campos obrigatórios.");
        return;
    }

    try {
        const body = { full_name, email, password, role };
        if (role === "lawyer") {
            if (oab_number) body.oab_number = oab_number;
            if (oab_seccional) body.oab_seccional = oab_seccional;
            if (especializacao) body.especializacao = especializacao;
            if (experiencia) body.experiencia = experiencia;
        }

        const response = await fetch(`${API}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || data.message || "Erro ao criar conta.");
            return;
        }

        alert("Conta criada com sucesso! Verifique seu e-mail para ativar.");
        window.location.href = "/login.html";
    } catch (err) {
        alert("Não foi possível conectar ao servidor.");
        console.error(err);
    }
}

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Preencha e-mail e senha.");
        return;
    }

    try {
        const response = await fetch(`${API}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || data.message || "Credenciais inválidas.");
            return;
        }

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("userRole", data.role);
        localStorage.setItem("userEmail", email);
        localStorage.setItem("userName", data.full_name);

        alert("Login realizado com sucesso!");
        window.location.href = "/dashboard.html";
    } catch (err) {
        alert("Não foi possível conectar ao servidor.");
        console.error(err);
    }
}

async function forgotPassword() {
    const email = document.getElementById("email").value.trim();
    if (!email) {
        alert("Informe seu e-mail.");
        return;
    }

    try {
        const response = await fetch(`${API}/forgot-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });
        const data = await response.json();
        alert(data.message || "Se o e-mail existir, você receberá as instruções.");
    } catch (err) {
        alert("Não foi possível conectar ao servidor.");
        console.error(err);
    }
}
