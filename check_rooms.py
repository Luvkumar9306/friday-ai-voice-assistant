from livekit import api
import asyncio

async def main():
    lk = api.LiveKitAPI('http://127.0.0.1:7880', 'devkey', 'secret')
    rooms = await lk.room.list_rooms(api.ListRoomsRequest())
    print('Active rooms:')
    for r in rooms.rooms:
        print(f'  - {r.name} (participants: {r.num_participants})')
    if not rooms.rooms:
        print('  (no rooms found)')
    await lk.aclose()

asyncio.run(main())
