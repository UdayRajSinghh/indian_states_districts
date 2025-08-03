from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import json
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="Indian States and Districts API",
    description="API for Indian states and their districts/cities",
    version="1.0.0"
)

# Data models
class StatesResponse(BaseModel):
    states: List[Dict[str, str]]

class DistrictsResponse(BaseModel):
    state: str
    districts: List[str]

# Sample data - replace this with your full data
INDIAN_DATA = {
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
                "Kaushambi", "Kheri", "Kushinagar", "Lalitpur", "Lucknow"
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
        },
        "TN": {
            "name": "Tamil Nadu",
            "districts": [
                "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
                "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
                "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
                "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
                "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
                "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
                "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
                "Vellore", "Viluppuram", "Virudhunagar"
            ]
        },
        "WB": {
            "name": "West Bengal",
            "districts": [
                "Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur",
                "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram",
                "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia",
                "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur",
                "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas",
                "Uttar Dinajpur"
            ]
        }
    }
}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Indian States and Districts API",
        "version": "1.0.0",
        "status": "active",
        "total_states": len(INDIAN_DATA["states"]),
        "endpoints": {
            "/health": "Health check",
            "/states": "Get all states",
            "/states/{state_code}": "Get specific state info",
            "/states/{state_code}/districts": "Get districts of a state",
            "/search/states?q={query}": "Search states by name",
            "/search/districts?q={query}": "Search districts by name",
            "/stats": "Get API statistics"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API is running successfully",
        "data_loaded": len(INDIAN_DATA["states"]) > 0,
        "timestamp": "2025-01-01T00:00:00Z"
    }

# Get all states
@app.get("/states", response_model=StatesResponse)
async def get_all_states():
    """Get list of all Indian states with their codes"""
    states_list = [
        {"name": state_info["name"], "code": state_code}
        for state_code, state_info in INDIAN_DATA["states"].items()
    ]
    return {"states": states_list}

# Get specific state
@app.get("/states/{state_code}")
async def get_state(state_code: str):
    """Get detailed information about a specific state"""
    state_code = state_code.upper()
    
    if state_code not in INDIAN_DATA["states"]:
        raise HTTPException(status_code=404, detail=f"State '{state_code}' not found")
    
    state_info = INDIAN_DATA["states"][state_code]
    return {
        "code": state_code,
        "name": state_info["name"],
        "districts_count": len(state_info["districts"]),
        "districts": state_info["districts"]
    }

# Get districts of a state
@app.get("/states/{state_code}/districts", response_model=DistrictsResponse)
async def get_state_districts(state_code: str):
    """Get all districts of a specific state"""
    state_code = state_code.upper()
    
    if state_code not in INDIAN_DATA["states"]:
        raise HTTPException(status_code=404, detail=f"State '{state_code}' not found")
    
    state_info = INDIAN_DATA["states"][state_code]
    return {
        "state": state_info["name"],
        "districts": state_info["districts"]
    }

# Search states
@app.get("/search/states")
async def search_states(q: str):
    """Search for states by name (partial match)"""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
    
    results = []
    query = q.lower()
    
    for state_code, state_info in INDIAN_DATA["states"].items():
        if query in state_info["name"].lower():
            results.append({
                "code": state_code,
                "name": state_info["name"]
            })
    
    return {"query": q, "results": results, "count": len(results)}

# Search districts
@app.get("/search/districts")
async def search_districts(q: str, state_code: Optional[str] = None):
    """Search for districts by name (partial match). Optionally filter by state."""
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")
    
    results = []
    query = q.lower()
    
    states_to_search = INDIAN_DATA["states"]
    if state_code:
        state_code = state_code.upper()
        if state_code not in INDIAN_DATA["states"]:
            raise HTTPException(status_code=404, detail=f"State '{state_code}' not found")
        states_to_search = {state_code: INDIAN_DATA["states"][state_code]}
    
    for s_code, state_info in states_to_search.items():
        for district in state_info["districts"]:
            if query in district.lower():
                results.append({
                    "district": district,
                    "state": state_info["name"],
                    "state_code": s_code
                })
    
    return {
        "query": q, 
        "state_filter": state_code, 
        "results": results, 
        "count": len(results)
    }

# Get API statistics
@app.get("/stats")
async def get_stats():
    """Get statistics about the data"""
    total_states = len(INDIAN_DATA["states"])
    total_districts = sum(len(state_info["districts"]) for state_info in INDIAN_DATA["states"].values())
    
    return {
        "total_states": total_states,
        "total_districts": total_districts,
        "average_districts_per_state": round(total_districts / total_states, 2),
        "states_breakdown": {
            state_code: {
                "name": state_info["name"],
                "districts_count": len(state_info["districts"])
            }
            for state_code, state_info in INDIAN_DATA["states"].items()
        }
    }

# Vercel handler
try:
    from mangum import Mangum
    handler = Mangum(app)
except ImportError:
    # Fallback for local development
    def handler(event, context):
        return {"statusCode": 500, "body": "Mangum not available"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)