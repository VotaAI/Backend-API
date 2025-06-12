from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app import models, schemas
from fastapi import HTTPException, status
from app.security import hash_password, verify_password
from datetime import datetime
from app.token import criar_token_acesso



def atualizar_status_votacoes_expiradas(db):
    agora = datetime.utcnow()
    votacoes = db.query(models.Votacao).filter(models.Votacao.status == "aberta", models.Votacao.data_fim < agora).all()

    for votacao in votacoes:
        votacao.status = "fechada"
    db.commit()


def create_user_with_login(db: Session, user_data: schemas.UserCreate, senha: str):
    # Verifica se o e-mail já existe
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já está em uso."
        )

    try:
        # Cria usuário
        new_user = models.User(nome_completo=user_data.nome_completo,cpf=user_data.cpf,email=user_data.email,user_type=user_data.user_type)
        db.add(new_user)
        db.flush()  # Garante que o id_user está disponível (sem commit)

        # Cria login com o id do usuário recém-criado
        login = models.Login(id_user=new_user.id_user, senha=hash_password(senha))
        db.add(login)

        db.commit()
        db.refresh(new_user)
        return new_user

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

def get_users(db: Session, limit=10, offset=0):
    return db.query(models.User).limit(limit).offset(offset).all()

def get_user_id(db: Session, id):
    return db.query(models.User).filter(id == models.User.id_user).first()







def get_all_votacao(db: Session, limit=10, offset=0):
    atualizar_status_votacoes_expiradas(db)
    return db.query(models.Votacao).limit(limit).offset(offset).all()

def get_votacoes_abertas(db: Session, limit=10, offset=0):
    atualizar_status_votacoes_expiradas(db)
    return db.query(models.Votacao).filter(models.Votacao.status == "aberta").limit(limit).offset(offset).all()

def get_votacoes_fechadas(db: Session, limit=10, offset=0):
    atualizar_status_votacoes_expiradas(db)
    return db.query(models.Votacao).filter(models.Votacao.status == "fechada").limit(limit).offset(offset).all()

def get_votacao_id(db: Session, id):
    atualizar_status_votacoes_expiradas(db)
    return db.query(models.Votacao).filter(models.Votacao.id_votacao == id).first()

def get_votacao_categoria(db: Session, id_category, limit=10, offset=0 ):
    atualizar_status_votacoes_expiradas(db)
    return db.query(models.Votacao).filter(models.Votacao.id_categoria == id_category).limit(limit).offset(offset).all()

def get_votacao_nome(db: Session, nome, limit=10, offset=0):
    atualizar_status_votacoes_expiradas(db)
    return db.query(models.Votacao).filter(nome in models.Votacao.titulo).limit(limit).offset(offset).all()




def get_opcoes(db: Session):
    opcoes = db.query(models.Opcoes).all()
    if opcoes:
        return opcoes
    else:
        return {"msg": "Votação e/ou opções não encontradas"}

def get_opcoes_id(db: Session, id_votacao):
    opcoes = db.query(models.Opcoes).filter(id_votacao == models.Opcoes.id_votacao).all()
    if opcoes:
        return opcoes
    else:
        return {"msg": "Votação e/ou opções não encontradas"}

def get_votos_votacao(db: Session, id_votacao):
    votos = db.query(models.Opcoes.titulo, func.count(models.Voto.id_voto).label("total_votos")).join(models.Voto, models.Voto.id_opcao == models.Opcoes.id_opcao).filter(models.Voto.id_votacao == id_votacao).group_by(models.Opcoes.titulo).all()
    if votos:
        return votos
    else:
        return {"msg": "Votação e/ou opções não encontradas"}







def get_candidaturas(db: Session, limit=10, offset=0):
    return db.query(models.Candidatura).limit(limit).offset(offset).all()

def get_candidaturas_pendentes(db: Session, limit=10, offset=0):
    return db.query(models.Candidatura).filter(models.Candidatura.status == 'pendente').limit(limit).offset(offset).all()

def get_candidaturas_aprovadas(db: Session, limit=10, offset=0):
    return db.query(models.Candidatura).filter(models.Candidatura.status == 'aprovada').limit(limit).offset(offset).all()

def get_candidaturas_recusadas(db: Session, limit=10, offset=0):
    return db.query(models.Candidatura).filter(models.Candidatura.status == 'recusada').limit(limit).offset(offset).all()





def atualizar_votacao(db: Session, id: int, dados: schemas.VotacaoUpdate):
    votacao = db.query(models.Votacao).filter(models.Votacao.id_votacao == id).first()
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(votacao, key, value)
    db.commit()
    db.refresh(votacao)
    return votacao

def atualizar_login(db: Session, id_user: int, dados: schemas.LoginUpdate):
    login = db.query(models.Login).filter(models.Login.id_user == id_user).first()
    if dados.senha:
        hashed = login.senha = hash_password(login.senha)
        dados.senha = hashed
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(login, key, value)
    db.commit()
    db.refresh(login)
    return login





def atualizar_candidatura(db: Session, id: int, dados: schemas.CandidaturaUpdate):
    candidatura = db.query(models.Candidatura).filter(models.Candidatura.id_candidatura == id).first()
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(candidatura, key, value)

    # Se o status foi alterado para "aprovada", cria automaticamente uma opção
    if dados.status and dados.status.lower() == "aprovada":
        candidato = db.query(models.User).filter(models.User.id_user == candidatura.id_user).first()
        nova_opcao = models.Opcoes(
            id_votacao=candidatura.id_votacao,
            titulo=candidato.nome_completo,  # ou outro campo que represente a opção
            detalhes = candidatura.detalhes
        )
        db.add(nova_opcao)

    # if candidatura.status == 'aprovada':
    #     candidato = db.query(models.User).filter(models.User.id_user == candidatura.id_user).first()
    #     titulo, detalhes, id_votacao = (candidato.nome_completo, candidatura.detalhes, candidatura.id_votacao)

    db.commit()
    db.refresh(candidatura)
    return candidatura


def atualizar_opcao(db: Session, id: int, dados: schemas.OpcaoUpdate):
    opcao = db.query(models.Opcoes).filter(models.Opcoes.id_opcao == id).first()
    for key, value in dados.model_dump(exclude_unset=True).items():
        setattr(opcao, key, value)
    db.commit()
    db.refresh(opcao)
    return opcao




def criar_votacao(db: Session, votacao: schemas.VotacaoCreate):
    nova = models.Votacao(**votacao.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

def criar_candidatura(db: Session, candidatura: schemas.CandidaturaCreate):
    nova = models.Candidatura(**candidatura.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

def criar_opcao(db: Session, opcao: schemas.OpcaoCreate):
    nova = models.Opcoes(**opcao.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

def criar_voto(db: Session, voto: schemas.VotoCreate):
    novo = models.Voto(**voto.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo















def login_user(db: Session, username: str, senha: str):
    result = (
        db.query(models.User, models.Login).join(models.Login, models.Login.id_user == models.User.id_user).filter(models.User.email == username).first()
    )

    if not result:
        result = (
            db.query(models.User, models.Login).join(models.Login, models.Login.id_user == models.User.id_user).filter(models.User.cpf == username).first()
        )
        if not result:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user, login = result

    if not verify_password(senha, login.senha):
        raise HTTPException(status_code=401, detail="Senha incorreta")

    token = criar_token_acesso({"id": str(user.id_user), "email": user.email, "user_type": user.user_type, "nome_completo": user.nome_completo})
    #return user
    return {"access_token": token, "token_type": "bearer", "user":user }

def get_logins(db: Session):
    return db.query(models.User.email, models.Login.senha).join(models.Login, models.Login.id_user == models.User.id_user).all()