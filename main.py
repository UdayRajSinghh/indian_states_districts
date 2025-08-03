from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import os
from typing import Dict, Any, Optional

class handler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.indian_data = self.load_data()
        super().__init__(*args, **kwargs)
    
    def load_data(self) -> Dict[str, Any]:
        """Load Indian states and districts data from JSON file"""
        try:
            with open("indian_states_districts.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            try:
                with open("./indian_states_districts.json", "r", encoding="utf-8") as file:
                    return json.load(file)
            except:
                return {"states": {}}

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            response_data = self.route_request(path, query_params)
            self.wfile.write(json.dumps(response_data, indent=2).encode())
        except Exception as e:
            error_response = {"error": str(e), "status": "error"}
            self.wfile.write(json.dumps(error_response, indent=2).encode())

    def route_request(self, path: str, query_params: Dict) -> Dict[str, Any]:
        path = path.rstrip('/')
        
        if path == '' or path == '/':
            return {
                "message": "Indian States and Districts API",
                "version": "1.0.0",
                "total_states": len(self.indian_data.get("states", {})),
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
        
        elif path == '/health':
            return {
                "status": "healthy",
                "data_loaded": len(self.indian_data.get("states", {})) > 0,
                "states_count": len(self.indian_data.get("states", {}))
            }
        
        elif path == '/states':
            states_list = [
                {"name": state_info["name"], "code": state_code}
                for state_code, state_info in self.indian_data["states"].items()
            ]
            return {"states": states_list}
        
        elif path.startswith('/states/'):
            path_parts = path.split('/')
            if len(path_parts) == 3:
                state_code = path_parts[2].upper()
                if state_code not in self.indian_data["states"]:
                    raise Exception(f"State '{state_code}' not found")
                
                state_info = self.indian_data["states"][state_code]
                return {
                    "code": state_code,
                    "name": state_info["name"],
                    "districts_count": len(state_info["districts"]),
                    "districts": state_info["districts"]
                }
            elif len(path_parts) == 4 and path_parts[3] == 'districts':
                state_code = path_parts[2].upper()
                if state_code not in self.indian_data["states"]:
                    raise Exception(f"State '{state_code}' not found")
                
                state_info = self.indian_data["states"][state_code]
                return {
                    "state": state_info["name"],
                    "districts": state_info["districts"]
                }
        
        elif path == '/search/states':
            query = query_params.get('q', [''])[0]
            if len(query) < 2:
                raise Exception("Query must be at least 2 characters long")
            
            results = []
            for state_code, state_info in self.indian_data["states"].items():
                if query.lower() in state_info["name"].lower():
                    results.append({"code": state_code, "name": state_info["name"]})
            
            return {"query": query, "results": results}
        
        elif path == '/search/districts':
            query = query_params.get('q', [''])[0]
            state_code = query_params.get('state_code', [None])[0]
            
            if len(query) < 2:
                raise Exception("Query must be at least 2 characters long")
            
            results = []
            states_to_search = self.indian_data["states"]
            
            if state_code:
                state_code = state_code.upper()
                if state_code not in self.indian_data["states"]:
                    raise Exception(f"State '{state_code}' not found")
                states_to_search = {state_code: self.indian_data["states"][state_code]}
            
            for s_code, state_info in states_to_search.items():
                for district in state_info["districts"]:
                    if query.lower() in district.lower():
                        results.append({
                            "district": district,
                            "state": state_info["name"],
                            "state_code": s_code
                        })
            
            return {"query": query, "results": results}
        
        elif path == '/stats':
            total_states = len(self.indian_data["states"])
            total_districts = sum(len(state_info["districts"]) for state_info in self.indian_data["states"].values())
            
            return {
                "total_states": total_states,
                "total_districts": total_districts,
                "states_breakdown": {
                    state_code: {
                        "name": state_info["name"],
                        "districts_count": len(state_info["districts"])
                    }
                    for state_code, state_info in self.indian_data["states"].items()
                }
            }
        
        else:
            raise Exception(f"Endpoint not found: {path}")