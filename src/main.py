from fastapi import FastAPI
from database import engine
import sql_models
import routes
import time
from sqlalchemy.exc import OperationalError

MAX_RETRIES = 5
RETRY_DELAY = 5  # secunde

for attempt in range(MAX_RETRIES):
    try:
        sql_models.Base.metadata.create_all(bind=engine)
        break
    except OperationalError as e:
        if attempt == MAX_RETRIES - 1:
            raise e
        time.sleep(RETRY_DELAY)

app = FastAPI(title="Sistem management chei - Proiect SI")

app.include_router(routes.router)