import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:5000"

# List of endpoints to verify
ENDPOINTS = [
    ("GET", "/api/health", "Global Health Check"),
    ("OPTIONS", "/api/login", "Login Endpoint"),
    ("GET", "/api/products", "Products List"),
    ("GET", "/api/billing/bills", "Billing List"),
    ("GET", "/api/suppliers", "Suppliers List"),
    ("GET", "/api/quotation", "Quotations List"),
    ("GET", "/api/services", "Services List"),
    ("GET", "/api/user-types", "User Types List"),
    ("GET", "/api/employees", "Employees List"),
    ("GET", "/api/enquiries", "Enquiries List"),
    ("GET", "/api/attendance/today", "Attendance Today"),
    ("GET", "/api/companies/", "Companies List"),
]

async def verify_endpoint(client, method, path, name):
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = await client.get(url, timeout=5.0)
        elif method == "OPTIONS":
            response = await client.options(url, timeout=5.0)
        else:
            return {"name": name, "path": path, "status": "UNKNOWN", "code": "-", "cors": "-"}

        cors_header = response.headers.get("Access-Control-Allow-Origin")
        cors_ok = cors_header == "*"
        
        return {
            "name": name,
            "path": path,
            "status_code": response.status_code,
            "cors_ok": cors_ok,
            "cors_header": cors_header or "None"
        }
    except Exception as e:
        return {
            "name": name,
            "path": path,
            "error": str(e)
        }

async def main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [verify_endpoint(client, m, p, n) for m, p, n in ENDPOINTS]
        results = await asyncio.gather(*tasks)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
