const API = "https://jurisaiv1.up.railway.app";

function safeAlert(msg) {
    if (msg === null || msg === undefined) {
        alert("Erro desconhecido");
        return;
    }
    if (typeof msg === "string") {
        alert(msg);
    } else if (typeof msg === "object") {
        const errorText = msg.detail || msg.message || JSON.stringify(msg);
        alert(errorText);
    } else {
        alert(String(msg));
    }
}

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
        safeAlert("Preencha todos os campos obrigatórios.");
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

        let data = {};
        try {
            data = await response.json();
        } catch (e) {
            console.error("Erro ao parsear JSON", e);
        }

        if (!response.ok) {
            console.error("Erro backend:", data);
            safeAlert(data);
            return;
        }

        safeAlert("Conta criada com sucesso! Verifique seu e-mail para ativar.");
        window.location.href = "/login.html";

    } catch (err) {
        console.error(err);
        safeAlert("Não foi possível conectar ao servidor. Tente novamente.");
    }
}
