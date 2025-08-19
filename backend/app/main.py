# # backend/app/main.py
# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from . import models, database
# models.Base.metadata.create_all(bind=database.engine)
# app = FastAPI(title="Bhagavad Gita Daily API")

# # Dependency
# def get_db():
#     db = database.SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.get("/slokams/today")
# def get_today_slokam(db: Session = Depends(get_db)):
#     # Simple rotation based on day of year
#     import datetime
#     today_index = datetime.date.today().toordinal() % db.query(models.Slokam).count()
#     slokam = db.query(models.Slokam).offset(today_index).first()
#     if not slokam:
#         raise HTTPException(status_code=404, detail="No slokam found")
#     return {
#         "chapter": slokam.chapter,
#         "verse": slokam.verse,
#         "translation": slokam.translation,
#         "purport": slokam.purport,
#         "bhavam": slokam.bhavam,
#     }

# @app.get("/slokams/{id}")
# def get_slokam(id: int, db: Session = Depends(get_db)):
#     slokam = db.query(models.Slokam).filter(models.Slokam.id == id).first()
#     if not slokam:
#         raise HTTPException(status_code=404, detail="Slokam not found")
#     return slokam.__dict__




# # 📌 NEW FEATURE 1: Get all slokams in a chapter
# @app.get("/slokams/chapter/{chapter_number}")
# def get_chapter_slokams(chapter_number: int, db: Session = Depends(get_db)):
#     slokams = db.query(models.Slokam).filter(models.Slokam.chapter == chapter_number).all()
#     if not slokams:
#         raise HTTPException(status_code=404, detail="No slokams found for this chapter")
#     return slokams


# # 📌 NEW FEATURE 2: Search slokams by keyword
# @app.get("/slokams/search")
# def search_slokams(query: str, db: Session = Depends(get_db)):
#     results = db.query(models.Slokam).filter(
#         models.Slokam.translation.contains(query) |
#         models.Slokam.purport.contains(query) |
#         models.Slokam.bhavam.contains(query)
#     ).all()
#     if not results:
#         raise HTTPException(status_code=404, detail="No matching slokams found")
#     return results


# # 📌 NEW FEATURE 3: Get a random slokam
# @app.get("/slokams/random")
# def get_random_slokam(db: Session = Depends(get_db)):
#     total = db.query(models.Slokam).count()
#     if total == 0:
#         raise HTTPException(status_code=404, detail="No slokams found")
#     random_index = random.randint(0, total - 1)
#     return db.query(models.Slokam).offset(random_index).first()

# backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import datetime, random
from . import models, database

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Static routes first

@app.get("/slokams/today")
def get_today_slokam(db: Session = Depends(get_db)):
    total = db.query(models.Slokam).count()
    if total == 0:
        raise HTTPException(status_code=404, detail="No slokams found")
    today_index = datetime.date.today().toordinal() % total
    return db.query(models.Slokam).offset(today_index).first()


@app.get("/slokams/random")
def get_random_slokam(db: Session = Depends(get_db)):
    total = db.query(models.Slokam).count()
    if total == 0:
        raise HTTPException(status_code=404, detail="No slokams found")
    random_index = random.randint(0, total - 1)
    return db.query(models.Slokam).offset(random_index).first()


@app.get("/slokams/search")
def search_slokams(query: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    results = db.query(models.Slokam).filter(
        models.Slokam.translation.contains(query) |
        models.Slokam.purport.contains(query) |
        models.Slokam.bhavam.contains(query)
    ).all()
    if not results:
        raise HTTPException(status_code=404, detail="No matching slokams found")
    return results


@app.get("/slokams/chapter/{chapter_number}")
def get_chapter_slokams(chapter_number: int, db: Session = Depends(get_db)):
    slokams = db.query(models.Slokam).filter(models.Slokam.chapter == chapter_number).all()
    if not slokams:
        raise HTTPException(status_code=404, detail="No slokams found for this chapter")
    return slokams


# ✅ Dynamic route last
@app.get("/slokams/{id}")
def get_slokam(id: int, db: Session = Depends(get_db)):
    slokam = db.query(models.Slokam).filter(models.Slokam.id == id).first()
    if not slokam:
        raise HTTPException(status_code=404, detail="Slokam not found")
    return slokam
