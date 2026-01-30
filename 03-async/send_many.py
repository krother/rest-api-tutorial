
import asyncio
import httpx
import random



async def send_request(number):
    """calls the /wait endpoint"""
    s = random.randint(1, 10)
    url = f"http://localhost:8000/wait?secs={s}"
    async with httpx.AsyncClient() as client:
        result = await client.get(url, timeout=60)
    print("request number", number, "resulted in", result)
    print(result.json())


async def main():
    # create concurrent tasks
    tasks = []
    for i in range(100):
        tasks.append(asyncio.create_task(send_request(i)))

    # wait for tasks to finish
    # (all have to be awaited)
    for t in tasks:
        await t


# run the toplevel async function
asyncio.run(main())
