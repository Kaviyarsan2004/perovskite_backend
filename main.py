from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app import dash_app, update_layout
from fastapi import Request
from fastapi.responses import JSONResponse


# Initialize FastAPI app
app = FastAPI()

# CORS settings for FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the Dash app
app.mount("/dash", WSGIMiddleware(dash_app.server))
# MongoDB client setup
client = AsyncIOMotorClient("mongodb+srv://ECD517:bing24@cluster0.6nj4o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["ECD517"]

# Base Models with Config for JSON Encoding
class ElementResponse(BaseModel):
    Dopants: str

class PredictedFormaEnergy(BaseModel):
    Dopant: str
    GPR: float
    NN: float
    RFR: float
    id: str

    class Config:
        json_encoders = {ObjectId: str}

class BandGapResponse(BaseModel):
    Element: str
    GPR: float
    NN: float
    RFR: float
    id: str

    class Config:
        json_encoders = {ObjectId: str}

# FastAPI Endpoints
@app.get("/get-dopant", response_model=List[ElementResponse])
async def get_dopants():
    collection = db["Dopant"]
    try:
        results = await collection.find({}, {"_id": 0, "Dopants": 1}).to_list(length=None)

        if results:
            dopants_list = [ElementResponse(Dopants=doc["Dopants"]) for doc in results if "Dopants" in doc]
            return dopants_list
        else:
            raise HTTPException(status_code=404, detail="No data found!")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/get-ML", response_model=List[PredictedFormaEnergy])
async def get_predicted_formation_energies():
    collection = db["formationfull"]
    formations = await collection.find({}, {"Dopant": 1, "GPR": 1, "NN": 1, "RFR": 1}).to_list(None)
    elements = [
        PredictedFormaEnergy(
            Dopant=form["Dopant"], 
            GPR=form["GPR"], 
            NN=form["NN"],
            RFR=form["RFR"],
            id=str(form["_id"])
        ) for form in formations
    ]
    return elements

@app.get("/get-bandgap", response_model=List[BandGapResponse])
async def get_bandgaps():
    collection = db["bandgapfull"]
    bandgaps = await collection.find({}, {"Element": 1, "GPR": 1, "NN": 1, "RFR": 1}).to_list(None)
    elements = [
        BandGapResponse(
            Element=bg["Element"], 
            GPR=bg["GPR"], 
            NN=bg["NN"],
            RFR=bg["RFR"],
            id=str(bg["_id"])
        ) for bg in bandgaps
    ]
    return elements

# Endpoint to check MongoDB connection
@app.get("/check-db")
async def check_db_connection():
    try:
        collections = await db.list_collection_names()
        return {"status": "Success", "collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")



@app.get("/get_formation_energy")
async def get_formation_energy( dopant: str, charge_state: int):
    """
    Retrieve formation energy based on host material, dopant, and charge state.
    If the charge_value exists in the collection under X_Cs or X_Sn, return the full document.
    """
    # Determine the collection name based on dopant suffix
    update_layout(dopant, charge_state)
    if dopant.endswith("Cs"):
        collection_name = "formation_energy_X_Cs"
        query_field = "X_Cs"
    elif dopant.endswith("Sn"):
        collection_name = "formation_energy_X_Sn"
        query_field = "X_Sn"
    else:
        return {"error": "Invalid dopant. Must end with 'Cs' or 'Sn'."}

    collection = db[collection_name]

    # Construct the charge value format
    charge_value = f"{dopant}+1" if charge_state == 1 else f"{dopant}-0"
    charge_value = charge_value.strip()

    query = {f"{query_field}": f"{charge_value}"}

    document = await collection.find_one(query)

    if document:
    # Ensure any ObjectId fields are converted to string
        document.pop('_id', None)
        return JSONResponse(content=document)
    else:
        return JSONResponse(status_code=404, content={"message": "Document not found"})
    
