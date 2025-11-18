import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="CCTV Store API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class IdModel(BaseModel):
    id: str

def serialize_doc(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    # format datetime fields if exist
    for k in ("created_at", "updated_at"):
        if k in doc and hasattr(doc[k], "isoformat"):
            doc[k] = doc[k].isoformat()
    return doc

@app.get("/")
def read_root():
    return {"message": "CCTV Store API running"}

@app.get("/api/products")
def list_products(category: Optional[str] = None):
    try:
        query = {"category": category} if category else {}
        products = get_documents("product", query)
        return [serialize_doc(p) for p in products]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products")
def create_product(product: Product):
    try:
        new_id = create_document("product", product)
        doc = db["product"].find_one({"_id": ObjectId(new_id)})
        return serialize_doc(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        return serialize_doc(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders")
def create_order(order: Order):
    try:
        computed_subtotal = sum(item.price * item.quantity for item in order.items)
        total = computed_subtotal + (order.shipping or 0)
        doc = order.model_dump()
        doc["subtotal"] = computed_subtotal
        doc["total"] = total
        new_id = create_document("order", doc)
        saved = db["order"].find_one({"_id": ObjectId(new_id)})
        return serialize_doc(saved)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
def list_orders(limit: int = 50):
    try:
        orders = get_documents("order", {}, limit)
        return [serialize_doc(o) for o in orders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seed/cctv")
def seed_products():
    try:
        count = db["product"].count_documents({}) if db is not None else 0
        if count > 0:
            return {"inserted": 0, "message": "Products already exist"}
        sample_products = [
            {
                "title": "4K Ultra HD Dome Camera",
                "description": "Weatherproof dome camera with night vision up to 30m and motion detection.",
                "price": 149.99,
                "category": "camera",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.7,
                "specs": ["4K UHD", "IR Night Vision", "IP67", "PoE"]
            },
            {
                "title": "8-Channel NVR Recorder",
                "description": "Network Video Recorder supporting up to 8 IP cameras, H.265+ compression.",
                "price": 219.0,
                "category": "nvr",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1587300003388-59208cc962cb?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.6,
                "specs": ["8-Channel", "H.265+", "2x SATA", "Remote View"]
            },
            {
                "title": "Wireless Bullet Camera",
                "description": "1080p wireless bullet camera with two-way audio and smart alerts.",
                "price": 89.5,
                "category": "camera",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1520975682031-ae5b83d52b36?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.4,
                "specs": ["1080p", "Wi‑Fi", "IP66", "Two‑way Audio"]
            },
            {
                "title": "POE Switch 8-Port",
                "description": "8-Port PoE switch for powering IP cameras and network devices.",
                "price": 69.99,
                "category": "accessory",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1581091226825-c6a8d07bcd5d?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.5,
                "specs": ["8x PoE", "Gigabit", "Rack Mount", "Fanless"]
            },
            {
                "title": "Complete 4-Camera Kit",
                "description": "All-in-one CCTV kit with 4x 5MP cameras, NVR, and cables.",
                "price": 499.0,
                "category": "kit",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop",
                "rating": 4.8,
                "specs": ["4x 5MP", "1TB NVR", "Plug & Play", "Remote App"]
            }
        ]
        result = db["product"].insert_many(sample_products)
        return {"inserted": len(result.inserted_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
