import asyncio
import logging
import websockets
import mysql.connector
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Pass1234..',
    database='websocket'
)


cursor = db_connection.cursor()
connected_clients = {}

async def on_connect(websocket, path):
    logger.info(f"client connected")

    try:
        await on_message(websocket)
    except websockets.exceptions.ConnectionClosed:
        pass

    await on_disconnect(get_key_from_value(connected_clients, websocket))


async def on_disconnect(user_idetifier):
    if user_idetifier is not None and user_idetifier in connected_clients:
        delete_query = "DELETE FROM client_connections WHERE connection_id = %s"
        cursor.execute(delete_query, (user_idetifier,))
        db_connection.commit()
        connected_clients.pop(user_idetifier)

        logger.info(f"client: {user_idetifier} disconnected")

def get_key_from_value(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None 

async def on_message(websocket):  
    try:
        async for message in websocket:
            logger.info(f"Received message: {message}")
            data = json.loads(message)
            action = data.get('action')
            client_type = data.get('client_type')
            user_identifier = id(websocket)
            room_name = data.get('room_name')

            if  action == "join" and client_type == 'frontend':
                connected_clients[str(user_identifier)] = websocket

                insert_query = "INSERT INTO client_connections (connection_id, client_type, room_name) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (user_identifier, client_type,  room_name))
                db_connection.commit()
            elif client_type == 'backend' and action == 'message':
                select_query = f"SELECT connection_id FROM client_connections where room_name = '{room_name}' and client_type = 'frontend'"
                cursor.execute(select_query)
                connection_ids = [row[0] for row in cursor.fetchall()]

                for connection_id in connection_ids:
                    await send_message_to_client(connection_id, data)
                    break
    finally:
        await on_disconnect(get_key_from_value(connected_clients, websocket))

async def send_message_to_client(connection_id, message):
    try:
        conn = connected_clients.get(connection_id)
        await conn.send(str(message))

        logger.info(f"Sent message to client with connection ID {connection_id}: {message}")
    except Exception as e:
        logger.error(f"Error sending message to client with connection ID {connection_id}: {e}")

async def main():    
    async with websockets.serve(on_connect, "localhost", 8765):
        logger.info("WebSocket server started.")
        await asyncio.Future()

asyncio.run(main())

            