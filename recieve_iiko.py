from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/stoplist")
async def handle_stoplist_webhook(request: Request):
    data = await request.json()
    print("📩 Вебхук получен:", data)
    product_id = data.get("productId")
    name = data.get("itemName")
    balance = float(data.get("balance", 0))

    if balance == 0:
        print(f"❌ Блюдо в стоп-листе: {name} (productId: {product_id})")
    else:
        print(f"✅ Блюдо снято со стопа: {name} (productId: {product_id}, остаток: {balance})")

    return {"status": "received"}
