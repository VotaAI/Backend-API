from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from datetime import datetime
from app.auth import get_current_user, admin_required
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

admin_router = APIRouter(dependencies=[Depends(admin_required)])

# === ROTAS GET ===

@admin_router.get("/users/", response_model=List[schemas.UserResponse])
def list_users(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_users(db, limit, offset)

@app.get("/users/{id}", response_model=schemas.UserResponse)
def list_user_by_id(db: Session = Depends(get_db), id=int):
    return crud.get_user_id(db, id)

@app.get("/votacoes")
def list_votacoes(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_all_votacao(db, limit, offset)

@app.get("/votacoes/open")
def list_votacoes_open(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_votacoes_abertas(db, limit, offset)

@app.get("/votacoes/closed")
def list_votacoes_closed(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_votacoes_fechadas(db, limit, offset)

@app.get("/votacoes/{id_votacao}")
def list_votacao_id(db: Session = Depends(get_db), id_votacao=int):
    return crud.get_votacao_id(db,id_votacao)

@app.get("/votacoes/{id_votacao}/votos")
def list_votacao_votos(db: Session = Depends(get_db), id_votacao=int):
    resultados = crud.get_votos_votacao(db, id_votacao)
    return [
        {"id_opcao": id_opcao, "total_votos": total}
        for id_opcao, total in resultados
    ]

@app.get("/votacoes/{id_votacao}/opcoes")
def list_votacao_opcoes(db: Session = Depends(get_db), id_votacao=int):
    return crud.get_opcoes(db, id_votacao)

@app.get("/candidaturas")
def list_candidaturas(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_candidaturas(db)

@app.get("/candidaturas/aprovadas")
def list_candidaturas_aprovadas(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_candidaturas_aprovadas(db)

@app.get("/candidaturas/pendentes")
def list_candidaturas_pendentes(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_candidaturas_pendentes(db)

@app.get("/candidaturas/recusadas")
def list_candidaturas_recusadas(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_candidaturas_recusadas(db)

@app.get("/opcoes")
def opcoes_list(db: Session = Depends(get_db), limit: int = 10, offset:int=0):
    return crud.get_opcoes(db)






# === ROTAS POST ===

@app.post("/cadastro/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user_with_login(db, user_data=user, senha=user.senha)

@admin_router.post("/votacoes/")
def criar_votacao(votacao: schemas.VotacaoCreate, db: Session = Depends(get_db)):
    return crud.criar_votacao(db, votacao)

@app.post("/candidaturas/")
def criar_candidatura(candidatura: schemas.CandidaturaCreate, db: Session = Depends(get_db)):
    return crud.criar_candidatura(db, candidatura)

@admin_router.post("/opcoes/")
def criar_opcao(opcao: schemas.OpcaoCreate, db: Session = Depends(get_db)):
    return crud.criar_opcao(db, opcao)

@app.post("/votos/")
def criar_voto(voto: schemas.VotoCreate, db: Session = Depends(get_db)):
    return crud.criar_voto(db, voto)

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    dados = crud.login_user(db, form_data.username, form_data.password)
    return {
        "access_token" : dados["access_token"],
        "token_type" : dados["token_type"],
        "user" : dados["user"],
    }

# === ROTAS PUT ===

@admin_router.put("/votacoes/{id}/")
def atualizar_votacao(id: int, dados: schemas.VotacaoUpdate, db: Session = Depends(get_db)):
    return crud.atualizar_votacao(db, id, dados)

@app.put("/login/{id_user}/")
def atualizar_login(id_user: int, dados: schemas.LoginUpdate, db: Session = Depends(get_db),):
    return crud.atualizar_login(db, id_user, dados)

@admin_router.put("/candidaturas/{id}/")
def atualizar_candidatura(id: int, dados: schemas.CandidaturaUpdate, db: Session = Depends(get_db)):
    return crud.atualizar_candidatura(db, id, dados)

@admin_router.put("/opcoes/{id}/")
def atualizar_opcao(id: int, dados: schemas.OpcaoUpdate, db: Session = Depends(get_db)):
    return crud.atualizar_opcao(db, id, dados)



# CHECAGEM DE PERMISSAO DE CANDIDATURA
# a = crud.get_votacao_id(db,id_votacao).permite_candidatura
# return a



@admin_router.delete("/votacoes/{votacao_id}")
def deletar_votacao(votacao_id: int, db: Session = Depends(get_db)):
    votacao = db.query(models.Votacao).filter(models.Votacao.id_votacao == votacao_id).first()

    if not votacao:
        raise HTTPException(status_code=404, detail="Votação não encontrada")

    db.delete(votacao)
    db.commit()

    return {"mensagem": f'Votação "{votacao.titulo}" foi deletada com sucesso.'}





app.include_router(admin_router, prefix="/admin", tags=["Admin"])