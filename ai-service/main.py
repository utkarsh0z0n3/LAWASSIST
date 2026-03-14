from fastapi imports FASTAPI
from rag.ra_chain import ask


app = FASTAPI();


@app.post("/ask")
def query(q:str):

    answer  = ask(q);
    return {"answer" : answer}