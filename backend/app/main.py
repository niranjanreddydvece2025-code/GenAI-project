from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, auth, employees, resumes, search, shortlist
from app.core.config import settings
from app.core.db import Base, engine
from app.embeddings.faiss_index import employee_index

app = FastAPI(title="GenAI Resource Allocation Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    employee_index.load()


app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(search.router)
app.include_router(resumes.router)
app.include_router(shortlist.router)
app.include_router(analytics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
