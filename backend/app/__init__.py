from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Додайте цей код ПЕРЕВІД створенням роутерів
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Ваш фронтенд
    allow_credentials=True,
    allow_methods=["*"],  # Дозволити всі методи (GET, POST, тощо)
    allow_headers=["*"],  # Дозволити всі заголовки
)