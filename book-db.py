from fastapi import FastAPI, HTTPException, Path, Depends, status, Response
from pydantic import BaseModel, Field
from typing import Optional, List
from pymongo import MongoClient
from bson.objectid import ObjectId

# Pydantic Models
class Book(BaseModel):
    id: Optional[str] = Field(alias="_id")
    publish_year: int
    author: str
    genre: str
    title: str

class BookCreate(BaseModel):
    publish_year: int
    author: str
    genre: str
    title: str

class BookUpdate(BaseModel):
    publish_year: Optional[int]
    author: Optional[str]
    genre: Optional[str]
    title: Optional[str]

# App init
app = FastAPI(title="Books API with MongoDB")
client = MongoClient("mongodb://localhost:27017")  # MongoDB URI without .env
db = client["book_db"]  # Database name
collection = db["books"] # Collection name

# Utilities
def serialize_book(book) -> dict:
    book["_id"] = str(book["_id"])
    return book

# Routes
@app.post("/books", response_model=Book, status_code=201)
def create_book(book: BookCreate):
    result = collection.insert_one(book.dict())
    new_book = collection.find_one({"_id": result.inserted_id})
    return serialize_book(new_book)

@app.get("/books", response_model=List[Book])
def get_all_books():
    return [serialize_book(b) for b in collection.find()]

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: str = Path(..., description="Mongo ObjectID")):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        raise HTTPException(404, f"Book with id={book_id} not found")
    return serialize_book(book)

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: str, update: BookUpdate):
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    result = collection.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404, f"Book with id={book_id} not found")
    updated_book = collection.find_one({"_id": ObjectId(book_id)})
    return serialize_book(updated_book)

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: str):
    result = collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, f"Book with id={book_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)