import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# DB Config
# Ensure directory exists for persistent storage
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR}/sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class ProdutoDB(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    preco = Column(Float)
    descricao = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

app = FastAPI(title="Produtos API", version="1.0.0")

# Schemas
class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=1)
    preco: float = Field(..., gt=0)
    descricao: Optional[str] = None

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    id: int
    class Config: from_attributes = True

# Endpoints
@app.get("/api/produtos", response_model=List[Produto])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(ProdutoDB).all()

@app.get("/api/produtos/{produto_id}", response_model=Produto)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.post("/api/produtos", response_model=Produto, status_code=201)
def criar_produto(produto_in: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = ProdutoDB(**produto_in.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.put("/api/produtos/{produto_id}", response_model=Produto)
def atualizar_produto(produto_id: int, produto_in: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    for key, value in produto_in.model_dump().items():
        setattr(db_produto, key, value)
    
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.delete("/api/produtos/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    db.delete(db_produto)
    db.commit()
    return {"message": "Produto deletado com sucesso"}
