from fastapi import FastAPI #as fa

app= FastAPI()
@app.get("/")
async def root():
    return {"message": "i am back in fastapi"}
