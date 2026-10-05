# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import os
from contextlib import asynccontextmanager
from datetime import datetime


# Database connection
DATABASE_URL = "postgresql://nimesh:@localhost:5432/aviation_newsletter"

class Subscription(BaseModel):
    name: str
    email: str
    aircraft: str = ""
    frequency: str = "daily"

app = FastAPI(title="Aviation Newsletter API")

app = FastAPI(title="Aviation Newsletter API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Aviation Newsletter API"}

@app.post("/subscribe")
async def subscribe(subscription: Subscription):
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Insert subscription into database
        await conn.execute(
            "INSERT INTO subscriptions (name, email, aircraft_type, frequency) VALUES ($1, $2, $3, $4)",
            subscription.name,
            subscription.email,
            subscription.aircraft,
            subscription.frequency
        )
        
        # Close connection
        await conn.close()
        
        return {"message": "Successfully subscribed to the newsletter"}
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/subscriptions")
async def get_subscriptions():
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Fetch all subscriptions
        rows = await conn.fetch("SELECT * FROM subscriptions ORDER BY created_at DESC")
        
        # Close connection
        await conn.close()
        
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "aircraft_type": row["aircraft_type"],
                "frequency": row["frequency"],
                "created_at": row["created_at"]
            } for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)