from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import json
import os
from pydantic import BaseModel

app = FastAPI(title="Indian States and Districts API", version="1.0.0")

# Data models
class District(BaseModel):
    name: str
    code: Optional[str] = None

class State(BaseModel):
    name: str
    code: str
    districts: List[District]

class StatesResponse(BaseModel):
    states: List[Dict[str, str]]

class DistrictsResponse(BaseModel):
    state: str
    districts: List[str]

# Global variable to store data
indian_data = {}

def load_data():
    """Load Indian states and districts data from JSON file"""
    global indian_data
    try:
        # Try to load from the same directory
        with open("indian_states_districts.json", "r", encoding="utf-8") as file:
            indian_data = json.load(file)
    except FileNotFoundError:
        try:
            # Try to load from parent directory
            with open("../indian_states_districts.json", "r", encoding="utf-8") as file:
                indian_data = json.load(file)
        except FileNotFoundError:
            # Fallback sample data if file doesn't exist
            indian_data = {
                "states": {
                    "UP": {
                        "name": "Uttar Pradesh",
                        "districts": [
                            "Agra", "Aligarh", "Allahabad", "Ambedkar Nagar", "Amethi",
                            "Amroha", "Auraiya", "Azamgarh", "Baghpat", "Bahraich",
                            "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly",
                            "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr",
                            "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah",
                            "Faizabad", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar",
                            "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur",
                            "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur",
                            "Jhansa", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj",
                            "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow",
                            "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau",
                            "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit",
                            "Pratapgarh", "Raebareli", "Rampur", "Saharanpur", "Sambhal",
                            "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shrawasti", "Siddharthnagar",
                            "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"
                        ]
                    },
                    "MH": {
                        "name": "Maharashtra",
                        "districts": [
                            "Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed",
                            "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli",
                            "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
                            "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded",
                            "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani",
                            "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara",
                            "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
                        ]
                    },
                    "KA": {
                        "name": "Karnataka",
                        "districts": [
                            "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban",
                            "Bidar", "Chamarajanagar", "Chikballapur", "Chikkamagaluru", "Chitradurga",
                            "Dakshina Kannada", "Davangere", "Dharwad", "Gadag", "Hassan",
                            "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal",
                            "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga",
                            "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"
                        ]
                    }
                }
            }

# Load data immediately
load_data()

# API Endpoints
@app.get("/", summary="API Information")
async def root():
    return {
        "message": "Indian States and Districts API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/states": "Get all states",
            "/states/{state_code}": "Get specific state info",
            "/states/{state_code}/districts": "Get districts of a state",
            "/search/states": "Search states by name",
            "/search/districts": "Search districts by name",
            "/health": "Health check"
        }
    }

@app.get("/health", summary="Health Check")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is running",
        "data_loaded": len(indian_data.get("states", {})) > 0
    }

@app.get("/states", response_model=StatesResponse, summary="Get all states")
async def get_all_states():
    """Get list of all Indian states with their codes"""
    states_list = [
        {"name": state_info["name"], "code": state_code}
        for state_code, state_info in indian_data["states"].items()
    ]
    return {"states": states_list}

@app.get("/states/{state_code}", summary="Get state information")
async def get_state(state_code: str):
    """Get detailed information about a specific state"""
    state_code = state_code.upper()
    
    if state_code not in indian_data["states"]:
        raise HTTPException(status_code=404, detail="State not found")
    
    state_info = indian_data["states"][state_code]
    return {
        "code": state_code,
        "name": state_info["name"],
        "districts_count": len(state_info["districts"]),
        "districts": state_info["districts"]
    }

@app.get("/states/{state_code}/districts", response_model=DistrictsResponse, summary="Get districts of a state")
async def get_state_districts(state_code: str):
    """Get all districts of a specific state"""
    state_code = state_code.upper()
    
    if state_code not in indian_data["states"]:
        raise HTTPException(status_code=404, detail="State not found")
    
    state_info = indian_data["states"][state_code]
    return {
        "state": state_info["name"],
        "districts": state_info["districts"]
    }

@app.get("/search/states", summary="Search states by name")
async def search_states(q: str):
    """Search for states by name (partial match)"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
    
    results = []
    query = q.lower()
    
    for state_code, state_info in indian_data["states"].items():
        if query in state_info["name"].lower():
            results.append({
                "code": state_code,
                "name": state_info["name"]
            })
    
    return {"query": q, "results": results}

@app.get("/search/districts", summary="Search districts by name")
async def search_districts(q: str, state_code: Optional[str] = None):
    """Search for districts by name (partial match). Optionally filter by state."""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
    
    results = []
    query = q.lower()
    
    states_to_search = indian_data["states"]
    if state_code:
        state_code = state_code.upper()
        if state_code not in indian_data["states"]:
            raise HTTPException(status_code=404, detail="State not found")
        states_to_search = {state_code: indian_data["states"][state_code]}
    
    for s_code, state_info in states_to_search.items():
        for district in state_info["districts"]:
            if query in district.lower():
                results.append({
                    "district": district,
                    "state": state_info["name"],
                    "state_code": s_code
                })
    
    return {"query": q, "state_filter": state_code, "results": results}

@app.get("/stats", summary="Get API statistics")
async def get_stats():
    """Get statistics about the data"""
    total_states = len(indian_data["states"])
    total_districts = sum(len(state_info["districts"]) for state_info in indian_data["states"].values())
    
    return {
        "total_states": total_states,
        "total_districts": total_districts,
        "states_breakdown": {
            state_code: {
                "name": state_info["name"],
                "districts_count": len(state_info["districts"])
            }
            for state_code, state_info in indian_data["states"].items()
        }
    }

# Export the app for Vercel
handler = app