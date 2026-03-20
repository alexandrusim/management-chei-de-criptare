from fastapi import FastAPI
from database import engine
import sql_models
import routes

sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistem management chei - Proiect SI")

app.include_router(routes.router)