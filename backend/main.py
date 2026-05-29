@app.post("/register", status_code=201)
def register(data: RegisterRequest, bg: BackgroundTasks, db=Depends(get_db)):
    from sqlalchemy import select

    user = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    if data.role == "lawyer":
        if not data.oab_number or not data.oab_seccional:
            raise HTTPException(status_code=400, detail="Dados da OAB obrigatórios para advogados.")
        
        oab_exists = db.execute(select(User).where(User.oab_number == data.oab_number)).scalar_one_or_none()
        if oab_exists:
            raise HTTPException(status_code=400, detail="Número de OAB já cadastrado.")

    hashed = pwd_context.hash(data.password)
    new_user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hashed,
        role=data.role,
        oab_number=data.oab_number if data.role == "lawyer" else None,
        oab_seccional=data.oab_seccional if data.role == "lawyer" else None,
        especializacao=data.especializacao if data.role == "lawyer" else None,
        experiencia=data.experiencia if data.role == "lawyer" else None,
        is_active=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_activation_token(new_user.email)
    bg.add_task(send_activation_email, new_user.email, token)

    return {"detail": "Usuário registrado com sucesso. Verifique seu e-mail para ativação."}
