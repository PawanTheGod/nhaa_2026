import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    async with engine.begin() as conn:
        for val in ['dsp', 'sp', 'ig']:
            try:
                await conn.execute(text(f"ALTER TYPE officer_role ADD VALUE IF NOT EXISTS '{val}'"))
                print(f"Added '{val}' to officer_role enum")
            except Exception as e:
                print(f"Error for '{val}': {e}")

if __name__ == "__main__":
    asyncio.run(main())
