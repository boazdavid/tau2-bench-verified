"""
MCP Environment Server - Exposes tau2 Environment tools via Model Context Protocol (MCP).

This module provides an MCP server implementation that wraps a tau2 Environment,
making its tools available through the MCP protocol using FastMCP.
"""

import logging
from typing import Optional

from fastmcp import FastMCP

from tau2.environment.environment import Environment

# Configure verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MCPEnvironmentServer:
    """
    An MCP server that exposes the tools of an Environment via the Model Context Protocol.
    
    This server uses FastMCP to create an MCP-compatible interface for tau2 environments,
    allowing AI assistants to discover and use environment tools through the MCP protocol.
    """

    def __init__(self, environment: Environment, server_name: Optional[str] = None):
        """
        Initialize the MCP server with an environment.

        Args:
            environment: The tau2 Environment to serve
            server_name: Optional custom name for the MCP server.
                        Defaults to "tau2-{domain_name}"
        """
        logger.info("Initializing MCPEnvironmentServer")
        self.environment = environment
        self.server_name = server_name or f"tau2-{environment.get_domain_name()}"
        logger.info(f"Server name: {self.server_name}")
        logger.debug(f"Environment domain: {environment.get_domain_name()}")
        
        # Create FastMCP instance
        logger.debug("Creating FastMCP instance")
        self.mcp = FastMCP(
            name=self.server_name,
            instructions="bla",
        )
        logger.info("FastMCP instance created successfully")
        
        # Register tools
        logger.info("Starting tool registration")
        self._register_tools()
        logger.info("MCPEnvironmentServer initialization complete")


    def _register_tools(self):
        """Register all environment tools with the MCP server directly."""
        if self.environment.tools is None:
            return
        
        # Get the tools dictionary from the toolkit
        tools_dict = self.environment.tools.get_tools()
        
        # Register each tool directly with FastMCP
        for tool_name, tool in tools_dict.items():
            # Get the actual function from the tool
            tool_func = tool._func
            
            # Register the tool function directly with FastMCP
            self.mcp.tool(tool_func)

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8765):
        """
        Run the MCP server.

        Args:
            transport: The transport to use. Options:
                      - "stdio": Standard input/output (default for MCP)
                      - "http": HTTP with Server-Sent Events
            host: Host to bind to (only for HTTP transport)
            port: Port to bind to (only for HTTP transport)
        """
        if transport == "stdio":
            self.mcp.run()
        elif transport == "http":
            # Run with HTTP transport (SSE)
            self.mcp.run(transport="http", host=host, port=port)
        else:
            raise ValueError(f"Unknown transport: {transport}. Use 'stdio' or 'http'.")


if __name__ == "__main__":
    from tau2.domains.airline.environment import get_environment
    
    # Configuration
    HOST = "127.0.0.1"
    PORT = 8765
    
    # Create airline environment
    print("Initializing airline environment...")
    airline_env = get_environment() # Airline!
    
    # Create MCP server
    print(f"Creating MCP server for domain: {airline_env.get_domain_name()}")
    mcp_server = MCPEnvironmentServer(
        environment=airline_env,
        server_name="tau2-airline"
    )
    
    # Run the server with HTTP/SSE transport
    print(f"Starting MCP server on http://{HOST}:{PORT}")
    print("Server is ready to accept MCP protocol messages over HTTP.")
    print(f"MCP endpoint: http://{HOST}:{PORT}/mcp")
    mcp_server.run(transport="http", host=HOST, port=PORT)
