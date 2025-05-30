from fastapi import FastAPI, Request
from sqlalchemy import select, update, insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database import async_session, init_db
from models import StopList
import os
import aiohttp

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # из .env или Railway переменных
SEND_DELAY = 5  # секунд на накопление

# Буфер для новых позиций
pending_new_products = {}

@app.on_event("startup")
async def startup():
    await init_db()


@app.post("/stoplist")
async def handle_stoplist_webhook(request: Request):
    data = await request.json()
    product_id = data.get("productId")
    name = data.get("itemName")
    balance = float(data.get("balance", 0))

    async with async_session() as session:
        stmt = select(StopList).where(StopList.product_id == product_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if balance == 0:
            # Добавили в стоп-лист
            if row:
                if not row.is_active:
                    row.is_active = True
                    row.name = name
                    row.balance = balance
                    session.add(row)
                    await session.commit()
                    pending_new_products[product_id] = name
            else:
                # Новая запись
                new = StopList(product_id=product_id, name=name, balance=0, is_active=True)
                session.add(new)
                await session.commit()
                pending_new_products[product_id] = name

        else:
            # Сняли со стопа
            if row and row.is_active:
                row.is_active = False
                row.balance = balance
                session.add(row)
                await session.commit()

    # Если есть новые позиции, через 5 сек. отправим сообщение
    if pending_new_products:
        await wait_and_send()

    return {"status": "ok"}


async def wait_and_send():
    import asyncio
    await asyncio.sleep(SEND_DELAY)

    if not pending_new_products:
        return

    # Собираем сообщение
    text = "Новые блюда в стоп-листе 🚫\n\n"
    for name in pending_new_products.values():
        text += f"☐ {name}\n"

    # Добавляем «уже в стопе»
    async with async_session() as session:
        stmt = select(StopList).where(StopList.is_active == True)
        result = await session.execute(stmt)
        all_rows = result.scalars().all()

        old_items = [
            row.name for row in all_rows
            if row.product_id not in pending_new_products
        ]

        if old_items:
            text += "\nУже в стоп-листе\n"
            for name in old_items:
                text += f"☑ {name}\n"

    await send_to_telegram(text)
    pending_new_products.clear()


async def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                error = await resp.text()
                print("Ошибка Telegram:", error)
