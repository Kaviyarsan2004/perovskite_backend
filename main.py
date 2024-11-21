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
    element: str
    formation_energy: float
    charge_transition: float
    id: str  # Include ObjectId as string

    class Config:
        json_encoders = {ObjectId: str}

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
    collection = db["CsSnI3"]
    farms = await collection.find({}, {"Element": 1, "formation energy (eV)": 1, "charge transition (+/0) (eV)": 1}).to_list(None)
    elements = [
        ElementResponse(
            element=farm["Element"], 
            formation_energy=farm["formation energy (eV)"], 
            charge_transition=farm["charge transition (+/0) (eV)"],
            id=str(farm["_id"])
        ) for farm in farms
    ]
    return elements

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

@app.post("/select-dopant")
async def select_dopant(request: Request):
    data = await request.json()  # Receive the POST request data
    selected_dopant_data = data.get("element")

    if selected_dopant_data:
        if update_layout(selected_dopant_data):
            return JSONResponse({"message": "Data updated successfully", "element": selected_dopant_data})
        else:
            return JSONResponse({"message": "Failed to update the structure."}, status_code=500)
    
    return JSONResponse({"message": "Element not provided"}, status_code=400)