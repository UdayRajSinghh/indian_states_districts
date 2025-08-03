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
            # Try different possible paths for the JSON file
            possible_paths = [
                "indian_states_districts.json",
                "../indian_states_districts.json", 
                "./indian_states_districts.json",
                "/var/task/indian_states_districts.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as file:
                        return json.load(file)
            
            # If no file found, return minimal fallback
            return {
                "states": {
                    "UP": {
                        "name": "Uttar Pradesh",
                        "districts": ["Agra", "Lucknow", "Kanpur", "Ghaziabad", "Varanasi"]
                    },
                    "MH": {
                        "name": "Maharashtra", 
                        "districts": ["Mumbai City", "Pune", "Nagpur", "Nashik", "Aurangabad"]
                    }
                }
            }
        except Exception as e:
            # Fallback data in case of any error
            return {
                "states": {
                    "UP": {
                        "name": "Uttar Pradesh",
                        "districts": ["Agra", "Lucknow", "Kanpur"]
                    }
                }
            }

    def do_GET(self):
        # Parse the URL and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            response_data = self.route_request(path, query_params)
            self.wfile.write(json.dumps(response_data, indent=2).encode())
        except Exception as e:
            error_response = {
                "error": str(e),
                "status": "error",
                "path": path
            }
            self.wfile.write(json.dumps(error_response, indent=2).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def route_request(self, path: str, query_params: Dict) -> Dict[str, Any]:
        """Route the request to appropriate handler"""
        
        # Remove trailing slash
        path = path.rstrip('/')
        
        # Root endpoint
        if path == '' or path == '/':
            return self.get_root()
        
        # Health check
        elif path == '/health':
            return self.get_health()
        
        # Get all states
        elif path == '/states':
            return self.get_all_states()
        
        # Get specific state or state districts
        elif path.startswith('/states/'):
            path_parts = path.split('/')
            if len(path_parts) == 3:  # /states/{state_code}
                state_code = path_parts[2].upper()
                return self.get_state(state_code)
            elif len(path_parts) == 4 and path_parts[3] == 'districts':  # /states/{state_code}/districts
                state_code = path_parts[2].upper()
                return self.get_state_districts(state_code)
        
        # Search endpoints
        elif path == '/search/states':
            query = query_params.get('q', [''])[0]
            return self.search_states(query)
        
        elif path == '/search/districts':
            query = query_params.get('q', [''])[0]
            state_code = query_params.get('state_code', [None])[0]
            return self.search_districts(query, state_code)
        
        # Stats endpoint
        elif path == '/stats':
            return self.get_stats()
        
        # 404 for unknown endpoints
        else:
            raise Exception(f"Endpoint not found: {path}")

    def get_root(self) -> Dict[str, Any]:
        """Root endpoint information"""
        return {
            "message": "Indian States and Districts API",
            "version": "1.0.0",
            "status": "active",
            "total_states": len(self.indian_data.get("states", {})),
            "endpoints": {
                "/health": "Health check",
                "/states": "Get all states",
                "/states/{state_code}": "Get specific state info",
                "/states/{state_code}/districts": "Get districts of a state",
                "/search/states?q={query}": "Search states by name",
                "/search/districts?q={query}&state_code={code}": "Search districts",
                "/stats": "Get API statistics"
            }
        }

    def get_health(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "message": "API is running successfully",
            "data_loaded": len(self.indian_data.get("states", {})) > 0,
            "states_count": len(self.indian_data.get("states", {}))
        }

    def get_all_states(self) -> Dict[str, Any]:
        """Get all states"""
        states_list = [
            {"name": state_info["name"], "code": state_code}
            for state_code, state_info in self.indian_data["states"].items()
        ]
        return {"states": states_list}

    def get_state(self, state_code: str) -> Dict[str, Any]:
        """Get specific state information"""
        if state_code not in self.indian_data["states"]:
            raise Exception(f"State '{state_code}' not found")
        
        state_info = self.indian_data["states"][state_code]
        return {
            "code": state_code,
            "name": state_info["name"],
            "districts_count": len(state_info["districts"]),
            "districts": state_info["districts"]
        }

    def get_state_districts(self, state_code: str) -> Dict[str, Any]:
        """Get districts of a specific state"""
        if state_code not in self.indian_data["states"]:
            raise Exception(f"State '{state_code}' not found")
        
        state_info = self.indian_data["states"][state_code]
        return {
            "state": state_info["name"],
            "state_code": state_code,
            "districts": state_info["districts"],
            "count": len(state_info["districts"])
        }

    def search_states(self, query: str) -> Dict[str, Any]:
        """Search states by name"""
        if len(query) < 2:
            raise Exception("Query must be at least 2 characters long")
        
        results = []
        query_lower = query.lower()
        
        for state_code, state_info in self.indian_data["states"].items():
            if query_lower in state_info["name"].lower():
                results.append({
                    "code": state_code,
                    "name": state_info["name"]
                })
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }

    def search_districts(self, query: str, state_code: Optional[str] = None) -> Dict[str, Any]:
        """Search districts by name"""
        if len(query) < 2:
            raise Exception("Query must be at least 2 characters long")
        
        results = []
        query_lower = query.lower()
        
        states_to_search = self.indian_data["states"]
        if state_code:
            state_code = state_code.upper()
            if state_code not in self.indian_data["states"]:
                raise Exception(f"State '{state_code}' not found")
            states_to_search = {state_code: self.indian_data["states"][state_code]}
        
        for s_code, state_info in states_to_search.items():
            for district in state_info["districts"]:
                if query_lower in district.lower():
                    results.append({
                        "district": district,
                        "state": state_info["name"],
                        "state_code": s_code
                    })
        
        return {
            "query": query,
            "state_filter": state_code,
            "results": results,
            "count": len(results)
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get API statistics"""
        total_states = len(self.indian_data["states"])
        total_districts = sum(len(state_info["districts"]) for state_info in self.indian_data["states"].values())
        
        states_breakdown = {}
        for state_code, state_info in self.indian_data["states"].items():
            states_breakdown[state_code] = {
                "name": state_info["name"],
                "districts_count": len(state_info["districts"])
            }
        
        return {
            "total_states": total_states,
            "total_districts": total_districts,
            "average_districts_per_state": round(total_districts / total_states, 2) if total_states > 0 else 0,
            "states_breakdown": states_breakdown
        }