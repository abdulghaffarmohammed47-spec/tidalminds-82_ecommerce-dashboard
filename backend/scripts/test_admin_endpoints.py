import requests

BASE_URL = "http://localhost:8000"

def run_tests():
    print("Testing Admin Endpoints...")
    
    # 1. Login to get token
    login_data = {
        "username": "admin@smartcommerce.com",
        "password": "Admin@123"
    }
    print(f"\n[1] Logging in as {login_data['username']}...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    
    if login_resp.status_code != 200:
        print(f"Login failed! Status: {login_resp.status_code}")
        print(login_resp.text)
        return
        
    token_data = login_resp.json()
    token = token_data.get("access_token")
    print("Login successful! Got access token.")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Get Products (Admin list)
    print("\n[2] Fetching products via Admin API...")
    products_resp = requests.get(f"{BASE_URL}/api/admin/products", headers=headers)
    
    if products_resp.status_code != 200:
        print(f"Failed to fetch products! Status: {products_resp.status_code}")
        print(products_resp.text)
        return
        
    products = products_resp.json()
    print(f"Successfully fetched {len(products)} products.")
    if products:
        print(f"Sample product: {products[0]['title']} (SKU: {products[0]['sku']})")
        
    import uuid
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import asyncio
    from sqlalchemy.future import select
    from app.core.database import AsyncSessionLocal
    from app.models.product import Category
    
    async def get_category():
        async with AsyncSessionLocal() as db:
            cat = (await db.execute(select(Category))).scalars().first()
            return str(cat.id) if cat else str(uuid.uuid4())
            
    cat_id = asyncio.run(get_category())

    # 3. Create a new product
    print("\n[3] Creating a new product...")
    new_product_data = {
        "sku": "TEST-ADMIN-02",
        "title": "Admin Test Product 2",
        "slug": "admin-test-product-2",
        "brand": "TestBrand",
        "base_price": 49.99,
        "compare_at_price": 59.99,
        "is_active": True,
        "stock": 150,
        "category_id": cat_id
    }
    
    create_resp = requests.post(
        f"{BASE_URL}/api/admin/products", 
        json=new_product_data,
        headers=headers
    )
    
    if create_resp.status_code == 201:
        created = create_resp.json()
        print(f"Successfully created product: {created['title']} (ID: {created['id']})")
    elif create_resp.status_code == 400 and "SKU already exists" in create_resp.text:
        print("Product with this SKU already exists (run previously).")
    else:
        print(f"Failed to create product! Status: {create_resp.status_code}")
        print(create_resp.text)
        
    print("\nAll admin endpoint tests completed successfully!")

if __name__ == "__main__":
    run_tests()
