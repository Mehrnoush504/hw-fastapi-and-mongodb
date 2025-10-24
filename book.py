# uvicorn book:app
from fastapi import FastAPI, HTTPException, Depends, Path, Response, status
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import csv
# --- Pydantic models --------------------------------------

class Book(BaseModel):
    id: int
    publish_year: int
    author: str
    genre: str
    title: str

class BookIDParam(BaseModel):
    id: int = Path(..., gt=0, description="Book ID (must be >0)")

class BookUpdate(BaseModel):
    publish_year: Optional[int]
    author: Optional[str]
    gener: Optional[str]
    title: Optional[str]

# --- App initialization -----------------------------------

books: List[Book] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with open("book.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    books.append(Book(
                        id=int(r["id"]),
                        publish_year=int(r["publish_year"]),
                        author=r["author"].strip(),
                        genre=r["genre"].strip(),
                        title=r["title"].strip(),
                    ))
                except ValueError as e:
                    print(f"⚠️ Skipping row due to error: {e} → {r}")
    except FileNotFoundError:
        print("⚠️ books.csv not found. Starting with an empty list.")
    
    yield
    books.clear()


app = FastAPI(title="Book Library API", version="1.0", lifespan=lifespan)


# --- Routes -----------------------------------------------

@app.get("/books/count", response_model=int)
def count_books():
    return len(books)

@app.get("/books", response_model=List[Book])
def get_books():
    return books

@app.get("/books/{id}", response_model=Book)
def get_book_by_id(params: BookIDParam = Depends()):
    for b in books:
        if b.id == params.id:
            return b
    return HTTPException(status_code=404, detail=f"Book with id={params.id} not found")

@app.put("/books/{id}", response_model=Book)
def update_book(
    params: BookIDParam = Depends(),
    update: BookUpdate = Depends()
):
    for idx, b in enumerate(books):
        if b.id == params.id:
            updated = b.copy(update=update.dict(exclude_unset=True))
            books[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail=f"Book with id={params.id} not found")

@app.delete("/books/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(params: BookIDParam = Depends()):
    for idx, b in enumerate(books):
        if b.id == params.id:
            books.pop(idx)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Book with id={params.id} not found")