import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:5000"

# List of endpoints to verify
# Each entry is (Method, Path, Name)
# We use OPTIONS and GET because they are non-destructive
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

        # Check CORS
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        cors_ok = "+" if cors_header == "*" else "!" if cors_header is None else cors_header
        
        status_code = response.status_code
        status_ok = "+" if status_code < 400 else "!"
        
        return {
            "name": name,
            "path": path,
            "status": f"{status_ok} {status_code}",
            "code": status_code,
            "cors": cors_ok
        }
    except Exception as e:
        return {
            "name": name,
            "path": path,
            "status": f"! ERROR",
            "code": str(e),
            "cors": "-"
        }

async def main():
    print(f"Starting Backend Verification on {BASE_URL}...\n")
    print(f"{'Endpoint Name':<25} | {'Path':<25} | {'Status':<15} | {'CORS':<10}")
    print("-" * 85)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [verify_endpoint(client, m, p, n) for m, p, n in ENDPOINTS]
        results = await asyncio.gather(*tasks)

    for r in results:
        print(f"{r['name']:<25} | {r['path']:<25} | {r['status']:<15} | {r['cors']:<10}")

    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(main())
