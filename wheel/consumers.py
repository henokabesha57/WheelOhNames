import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Global in-memory state to coordinate between the wheels and the admin dashboard
# In production, this can be moved to Django cache or database models
SYSTEM_STATE = {
    "forced_winner": None,  # Holds the name of the forced winner, or None for random
    "current_entries": []   # Keeps track of the current active names on the wheel
}

class WheelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "wheel_room"

        # Join the shared channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send the current global state upon initial connection
        await self.send(text_data=json.dumps({
            "type": "state_sync",
            "forced_winner": SYSTEM_STATE["forced_winner"],
            "entries": SYSTEM_STATE["current_entries"]
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        # 1. Sent by the main wheel to synchronize current text entries
        if msg_type == "sync_entries":
            SYSTEM_STATE["current_entries"] = data.get("entries", [])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_entries",
                    "entries": SYSTEM_STATE["current_entries"]
                }
            )

        # 2. Sent by the Admin panel to force-lock the next winner
        elif msg_type == "set_forced_winner":
            SYSTEM_STATE["forced_winner"] = data.get("winner")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast_forced_winner",
                    "forced_winner": SYSTEM_STATE["forced_winner"]
                }
            )

        # 3. Sent by the main wheel when a spin is requested
        elif msg_type == "request_spin":
            client_entries = data.get("entries", [])
            chosen_winner = None
            
            # Use forced winner if set and exists in current entries
            if SYSTEM_STATE["forced_winner"] and SYSTEM_STATE["forced_winner"] in client_entries:
                chosen_winner = SYSTEM_STATE["forced_winner"]
                # Reset the forced winner after one use
                SYSTEM_STATE["forced_winner"] = None
                
                # Notify everyone (especially the admin panel) that the lock has been cleared/used
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "broadcast_forced_winner",
                        "forced_winner": None
                    }
                )
            else:
                # If no force winner is set, pick a random item from client's current wheel list
                import random
                if client_entries:
                    chosen_winner = random.choice(client_entries)

            # Send the determined winner back to the wheel to initiate the spin sequence
            await self.send(text_data=json.dumps({
                "type": "resolve_spin",
                "winner": chosen_winner
            }))

    async def broadcast_entries(self, event):
        await self.send(text_data=json.dumps({
            "type": "update_entries",
            "entries": event["entries"]
        }))

    async def broadcast_forced_winner(self, event):
        await self.send(text_data=json.dumps({
            "type": "update_forced_winner",
            "forced_winner": event["forced_winner"]
        }))