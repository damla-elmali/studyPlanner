


app = FastAPI()

app.include_router(auth_router)
app.include_router(_router)

Base.metadata.create_all(bind=engine)