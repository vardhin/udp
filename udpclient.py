import asyncio
import socket
import sys
from typing import Optional

class UDPClient:
    def __init__(self):
        self.transport = None
        self.remote_addr = None
        self.remote_port = None
        self.local_addr = None
        self.local_port = None

    async def start_client(self, host: str, port: int):
        self.local_addr = host
        self.local_port = port
        loop = asyncio.get_event_loop()
        
        # Create datagram endpoint
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPClientProtocol(self),
            local_addr=(host, port)
        )
        print(f"Client started on {host}:{port}")

    async def connect_to_server(self, host: str, port: int):
        self.remote_addr = host
        self.remote_port = port
        print(f"Connected to server at {host}:{port}")
        # Send initial connection message
        self.send_message("Client connected")

    def send_message(self, message: str):
        if self.transport and self.remote_addr and self.remote_port:
            self.transport.sendto(message.encode(), (self.remote_addr, self.remote_port))
        else:
            print("No connection established")

    def close(self):
        if self.transport:
            self.transport.close()
            self.transport = None
            print("Connection closed")

class UDPClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, client):
        self.client = client

    def connection_made(self, transport):
        pass

    def datagram_received(self, data, addr):
        message = data.decode()
        if self.client.remote_addr is None:
            self.client.remote_addr = addr[0]
            self.client.remote_port = addr[1]
        print(f"\nReceived from {addr[0]}:{addr[1]}: {message}")
        print("Enter message (or 'menu' for options): ", end='', flush=True)

async def get_user_input(client: UDPClient):
    while True:
        print("\nEnter message (or 'menu' for options): ", end='', flush=True)
        message = await asyncio.get_event_loop().run_in_executor(None, input)
        
        if message.lower() == 'menu':
            show_menu()
        elif message.lower() == 'quit':
            client.close()
            break
        elif message.lower() == 'connect':
            host = input("Enter server host IP: ")
            port = int(input("Enter server port: "))
            await client.connect_to_server(host, port)
        else:
            client.send_message(message)

def show_menu():
    print("\n=== UDP Client Menu ===")
    print("1. Type 'connect' to connect to a server")
    print("2. Type your message to send")
    print("3. Type 'quit' to exit")
    print("4. Type 'menu' to show this menu again")

async def main():
    client = UDPClient()
    
    # Get local client details
    host = input("Enter client host IP (default: 127.0.0.1): ").strip() or "127.0.0.1"
    port = int(input("Enter client port (default: 5001): ").strip() or "5001")
    
    try:
        await client.start_client(host, port)
        show_menu()
        await get_user_input(client)
    except KeyboardInterrupt:
        print("\nShutting down client...")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
