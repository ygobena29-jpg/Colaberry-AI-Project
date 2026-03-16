import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client: AsyncIOMotorClient | None = None
database = None


async def connect_to_mongo():
    global client, database
    client = AsyncIOMotorClient(MONGO_URL)
    database = client["architectos"]
    await database["users"].create_index("email", unique=True)
    print("Connected to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")
        