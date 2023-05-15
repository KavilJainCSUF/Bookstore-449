from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from pydantic import BaseModel
from typing import List

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["bookstore"]
collection = db["books"]


class Book(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int


@app.post("/books")
async def create_book(book: Book):
    book_data = book.dict()
    try:
        result = collection.insert_one(book_data)
        book_id = str(result.inserted_id)
        return {"message": "Book created successfully", "book_id": book_id}
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to create book") from e


@app.get("/books/{book_id}")
async def get_book(book_id: str):
    try:
        if not ObjectId.is_valid(book_id):
            raise HTTPException(status_code=400, detail="Invalid book_id")

        book = collection.find_one({"_id": ObjectId(book_id)})
        if book:
            book_dict = {
                "title": book["title"],
                "author": book["author"],
                "price": book['price'],
                "stock": book['stock']
            }
            return book_dict
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except PyMongoError as e:
        print("Error fetching book:", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch book") from e



@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book):
    book_data = book.dict()
    try:
        result = collection.update_one({"_id": ObjectId(book_id)}, {"$set": book_data})
        if result.modified_count == 1:
            return {"message": "Book updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to update book") from e


@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    try:
        result = collection.delete_one({"_id": ObjectId(book_id)})
        if result.deleted_count == 1:
            return {"message": "Book deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to delete book") from e


@app.get("/books")
async def get_all_books():
    try:
        books = collection.find()
        books_list = []
        for book in books:
            book["_id"] = str(book["_id"])
            books_list.append(book)
        return books_list
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch books") from e


@app.get("/search")
async def search_books(title: str = None, author: str = None, min_price: float = None, max_price: float = None):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if min_price is not None and max_price is not None:
        query["price"] = {"$gte": min_price, "$lte": max_price}
    elif min_price is not None:
        query["price"] = {"$gte": min_price}
    elif max_price is not None:
        query["price"] = {"$lte": max_price}

    try:
        books = collection.find(query)
        book_list = [book_dict(book) for book in books] 
        return book_list
    except PyMongoError as e:
        print("Error searching books:", str(e))
        raise HTTPException(status_code=500, detail="Failed to search books") from e

@app.get("/aggregation/stats")
async def get_statistics():
    total_books = await collection.count_documents({})
    best_selling_books = await collection.find().sort("stock", -1).limit(5).to_list(length=None)
    top_authors = await collection.aggregate([
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(length=None)
    return {
        "total_books": total_books,
        "best_selling_books": best_selling_books,
        "top_authors": top_authors
    }


def book_dict(book):
    book["_id"] = str(book["_id"])
    return book 