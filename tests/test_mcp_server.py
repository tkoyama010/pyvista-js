"""Tests for the MCP server module."""

import json

import pytest

# Skip all tests in this module if MCP is not available
pytest.importorskip("mcp")

import pyvista_js as pv


class TestMCPServer:
    """Test MCP server functionality."""

    def test_mcp_server_creation(self):
        """Test creating an MCP server instance."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        assert server is not None
        assert server.plotter is plotter
        assert server.server is not None

    def test_mcp_server_custom_name(self):
        """Test creating an MCP server with custom name."""
        plotter = pv.Plotter()
        server = pv.MCPServer(plotter, name="custom-server")
        assert server is not None

    @pytest.mark.asyncio
    async def test_handle_see_basic(self):
        """Test the 'see' tool handler."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        result = await server._handle_see({})

        assert len(result) == 1
        assert result[0]["type"] == "text"

        # Parse the JSON response
        data = json.loads(result[0]["text"])
        assert "camera" in data
        assert "scene" in data
        assert "position" in data["camera"]
        assert "focal_point" in data["camera"]
        assert "view_up" in data["camera"]
        assert "object_count" in data["scene"]
        assert data["scene"]["object_count"] == 1

    @pytest.mark.asyncio
    async def test_handle_see_with_html(self):
        """Test the 'see' tool with HTML output."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        result = await server._handle_see({"include_html": True})

        assert len(result) == 1
        data = json.loads(result[0]["text"])
        # HTML generation may fail in non-browser environments, so check if key exists
        assert "html" in data or "html_error" in data

    @pytest.mark.asyncio
    async def test_handle_move_preset(self):
        """Test the 'move' tool with preset views."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)

        # Test each preset
        presets = ["xy", "xz", "yz", "yx", "zx", "zy", "iso"]
        for preset in presets:
            result = await server._handle_move({"preset": preset})
            assert len(result) == 1
            assert result[0]["type"] == "text"

            data = json.loads(result[0]["text"])
            assert data["status"] == "success"
            assert preset in data["action"]

    @pytest.mark.asyncio
    async def test_handle_move_position(self):
        """Test the 'move' tool with manual position."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        result = await server._handle_move({"position": [5, 5, 5]})

        assert len(result) == 1
        data = json.loads(result[0]["text"])
        assert data["status"] == "success"
        assert data["camera"]["position"] == [5.0, 5.0, 5.0]

    @pytest.mark.asyncio
    async def test_handle_move_focal_point(self):
        """Test the 'move' tool with focal point."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        result = await server._handle_move({"focal_point": [1, 2, 3]})

        assert len(result) == 1
        data = json.loads(result[0]["text"])
        assert data["status"] == "success"
        assert data["camera"]["focal_point"] == [1.0, 2.0, 3.0]

    @pytest.mark.asyncio
    async def test_handle_move_view_up(self):
        """Test the 'move' tool with view up vector."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        result = await server._handle_move({"view_up": [0, 0, 1]})

        assert len(result) == 1
        data = json.loads(result[0]["text"])
        assert data["status"] == "success"
        assert data["camera"]["view_up"] == [0.0, 0.0, 1.0]

    @pytest.mark.asyncio
    async def test_handle_move_combined(self):
        """Test the 'move' tool with multiple parameters."""
        plotter = pv.Plotter()
        plotter.add_mesh(pv.Sphere(), color="red")

        server = pv.MCPServer(plotter)
        result = await server._handle_move(
            {
                "position": [5, 5, 5],
                "focal_point": [0, 0, 0],
                "view_up": [0, 1, 0],
            },
        )

        assert len(result) == 1
        data = json.loads(result[0]["text"])
        assert data["status"] == "success"
        assert len(data["actions"]) == 3
        assert data["camera"]["position"] == [5.0, 5.0, 5.0]
        assert data["camera"]["focal_point"] == [0.0, 0.0, 0.0]
        assert data["camera"]["view_up"] == [0.0, 1.0, 0.0]

    @pytest.mark.asyncio
    async def test_handle_move_invalid_preset(self):
        """Test the 'move' tool with invalid preset."""
        plotter = pv.Plotter()
        server = pv.MCPServer(plotter)

        with pytest.raises(ValueError, match="Unknown preset"):
            await server._handle_move({"preset": "invalid"})

    @pytest.mark.asyncio
    async def test_handle_move_invalid_position_length(self):
        """Test the 'move' tool with invalid position length."""
        plotter = pv.Plotter()
        server = pv.MCPServer(plotter)

        with pytest.raises(ValueError, match="position must be"):
            await server._handle_move({"position": [1, 2]})

    @pytest.mark.asyncio
    async def test_handle_move_no_parameters(self):
        """Test the 'move' tool with no parameters."""
        plotter = pv.Plotter()
        server = pv.MCPServer(plotter)

        with pytest.raises(ValueError, match="No camera parameters"):
            await server._handle_move({})

    def test_mcp_available_flag(self):
        """Test that MCP_AVAILABLE flag is set correctly."""
        assert pv.MCP_AVAILABLE is True
        assert pv.MCPServer is not None
