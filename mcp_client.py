import json
from fastmcp.client import Client
from fastmcp.client.transports import StreamableHttpTransport


PORT = 8765

async def run_client():        
    transport = StreamableHttpTransport(
        url=f"http://127.0.0.1:{PORT}/mcp"
    )
    async with Client(transport) as client:
        print("Calling list_tools...")
        tools = await client.list_tools()
        # print(tools[0].model_dump_json(indent=2))
        print("Available tools:")
        for t in tools:
            print("-", t.name)                        
            print("INPUT SCHEMA:")
            print(json.dumps(t.inputSchema, indent=2))
            print("OUTPUT SCHEMA:")
            print(json.dumps(t.outputSchema, indent=2))
            print("-" * 40)

        result = await client.call_tool(
            "get_reservation_details",
            {"reservation_id": "4WQ150"}
        )
        print(result.data)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_client())