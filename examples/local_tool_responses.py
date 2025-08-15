"""
Local Tool Responses Module

This module allows users to define custom tool functions that can be executed
when tool calls are received via the LiveKit data channel.

To create a new tool:
1. Define a function with any name
2. Decorate it with @tool(name="tool_name")
3. The function will receive arguments from the JSON tool call

Example:
    @tool(name="get_weather")
    def fetch_weather(location: str, unit: str = "celsius") -> dict:
        # Your implementation here
        return {"temperature": 22, "unit": unit, "location": location}
"""

from typing import Any, Callable, Dict, Optional
import functools
import logging
import asyncio
from time import sleep

logger = logging.getLogger(__name__)

# Registry to store all available tools
TOOL_REGISTRY: Dict[str, Callable] = {}

# Global reference to allow tools to control the application
_app_controller = None

def set_app_controller(controller):
    """Set the app controller reference for tools that need to control the application."""
    global _app_controller
    _app_controller = controller


def tool(name: str, description: Optional[str] = None):
    """
    Decorator to register a function as a tool that can be called remotely.
    
    Args:
        name: The name that will be used to invoke this tool
        description: Optional description of what the tool does
        
    Example:
        @tool(name="calculator", description="Performs basic calculations")
        def calculate(operation: str, a: float, b: float) -> float:
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata with the function
        func._tool_name = name
        func._tool_description = description or func.__doc__ or "No description available"
        
        # Register the function
        TOOL_REGISTRY[name] = func
        logger.info(f"Registered tool '{name}': {func._tool_description}")
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Executing tool '{name}' with args={args}, kwargs={kwargs}")
                result = func(*args, **kwargs)
                logger.debug(f"Tool '{name}' completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error executing tool '{name}': {e}")
                raise
                
        return wrapper
    return decorator


def get_available_tools() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all registered tools.
    
    Returns:
        Dictionary mapping tool names to their metadata
    """
    tools = {}
    for name, func in TOOL_REGISTRY.items():
        tools[name] = {
            "name": name,
            "description": getattr(func, '_tool_description', 'No description'),
            "function": func.__name__,
            "module": func.__module__
        }
    return tools


# ============== User Tool Definitions ==============
# Users can add their own tools below this line

# Template function as requested
@tool(name="template", description="Template tool function for demonstration")
def template_function(**kwargs) -> Dict[str, Any]:
    """
    Template function that accepts any keyword arguments.
    This demonstrates how to create a flexible tool that can handle various inputs.
    
    All arguments passed in the JSON tool call will be available as kwargs.
    """
    # Print the tool name and arguments as requested
    print(f"Tool called: template")
    print(f"Arguments: {kwargs}")
    
    return {
        "tool": "template",
        "received_arguments": kwargs,
        "argument_count": len(kwargs),
        "message": "This is a template function. Replace with your own implementation."
    }


# ============== Coffee Order Tools ==============

@tool(name="add_to_order", description="Add an item to the coffee order")
def add_to_order(
    coffee_type: str,
    milk_type: str,
    size: str = "medium",
    quantity: int = 1,
    special_instructions: str = ""
) -> Dict[str, Any]:
    """Add an item to the coffee order."""
    
    # Print the order details
    special_text = f" with {special_instructions}" if special_instructions else ""
    print(f"☕ Adding to order: {quantity}x {size} {coffee_type} with {milk_type} milk{special_text}")
    
    return {
        "tool": "add_to_order",
        "success": True,
        "item": {
            "coffee_type": coffee_type,
            "milk_type": milk_type,
            "size": size,
            "quantity": quantity,
            "special_instructions": special_instructions
        },
        "message": f"Added {quantity}x {size} {coffee_type} with {milk_type} milk to order"
    }


@tool(name="get_current_order", description="Get the current coffee order")
def get_current_order() -> Dict[str, Any]:
    """Get the current coffee order."""
    
    print("📋 Getting current coffee order")
    
    return {
        "tool": "get_current_order",
        "success": True,
        "order": [],  # In a real implementation, this would contain the actual order items
        "message": "Current order retrieved (mock implementation - order is empty)"
    }


@tool(name="amend_order", description="Modify or remove an item from the current order")
def amend_order(
    item_id: str = "",
    coffee_type: str = "",
    milk_type: str = "",
    size: str = "",
    quantity: int = 0,
    special_instructions: str = "",
    action: str = "update"
) -> Dict[str, Any]:
    """Modify or remove an item from the current order."""
    
    if action == "remove":
        print(f"🗑️ Removing item {item_id} from order")
    else:
        changes = []
        if coffee_type:
            changes.append(f"coffee type: {coffee_type}")
        if milk_type:
            changes.append(f"milk type: {milk_type}")
        if size:
            changes.append(f"size: {size}")
        if quantity > 0:
            changes.append(f"quantity: {quantity}")
        if special_instructions:
            changes.append(f"special instructions: {special_instructions}")
        
        changes_text = ", ".join(changes) if changes else "no changes"
        print(f"✏️ Amending order item {item_id}: {changes_text}")
    
    return {
        "tool": "amend_order",
        "success": True,
        "item_id": item_id,
        "action": action,
        "message": f"Order item {action}d successfully"
    }


@tool(name="send_order", description="Send the current order to the coffee robot")
def send_order(customer_name: str = "", special_notes: str = "") -> Dict[str, Any]:
    """Send the current order to the coffee robot."""
    
    customer_text = f" for {customer_name}" if customer_name else ""
    notes_text = f" (Notes: {special_notes})" if special_notes else ""
    print(f"🚀 Sending coffee order to robot{customer_text}{notes_text}")
    
    return {
        "tool": "send_order",
        "success": True,
        "customer_name": customer_name,
        "special_notes": special_notes,
        "message": f"Order sent to coffee robot{customer_text}"
    }


# ============== Robot Control Tools ==============

@tool(name="dance_tool", description="Trigger dance motion on robot by simulating joystick button press")
def dance_tool(**kwargs) -> Dict[str, Any]:
    """
    Triggers a dance motion on the robot by publishing a joystick button press to ROS.
    Simulates pressing button[0] (first button) on the joystick.
    Accepts any kwargs from the AI agent (like dance_style, duration) but uses fixed button press.
    """
    # Log any extra arguments from the AI
    if kwargs:
        print(f"🕺 Dance requested with params: {kwargs}")
    
    try:
        import rospy
        from sensor_msgs.msg import Joy
        import time
        
        # Try to initialize ROS node with disable_signals to avoid threading issues
        if not rospy.core.is_initialized():
            try:
                rospy.init_node('lightberry_joy_publisher', anonymous=True, disable_signals=True)
                print("✓ ROS node initialized")
            except Exception as init_error:
                print(f"⚠️ ROS init warning: {init_error}")
                # Continue anyway - node might already be initialized
        
        # Create publisher for /joy_input topic
        joy_pub = rospy.Publisher('/joy_input', Joy, queue_size=1)
        
        # Use regular time.sleep instead of rospy.sleep to avoid threading issues
        time.sleep(0.1)
        
        # Create Joy message with button[0] pressed
        joy_msg = Joy()
        
        # Try to use rospy.Time if available, otherwise use header without timestamp
        try:
            joy_msg.header.stamp = rospy.Time.now()
        except:
            # Skip timestamp if ROS time not available
            pass
        
        joy_msg.header.frame_id = "/dev/input/js0"
        
        # Set axes (8 axes, all at default positions)
        joy_msg.axes = [0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0]
        
        # Set buttons (11 buttons, first one pressed)
        joy_msg.buttons = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Publish button press
        print("🕺 Triggering dance motion - button press")
        joy_pub.publish(joy_msg)
        
        # Hold button for a moment using regular sleep
        time.sleep(0.2)
        
        # Release button (optional - send all zeros)
        joy_msg.buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        try:
            joy_msg.header.stamp = rospy.Time.now()
        except:
            pass
        joy_pub.publish(joy_msg)
        print("🕺 Dance motion triggered - button released")
        
        return {
            "tool": "dance_tool",
            "success": True,
            "message": "Dance motion triggered successfully",
            "button_pressed": 0,
            "duration_ms": 200
        }
        
    except ImportError:
        print("❌ ROS not installed or not sourced. Please install ROS and source the setup.bash")
        return {
            "tool": "dance_tool", 
            "success": False,
            "error": "ROS not available - please install and source ROS environment"
        }
    except Exception as e:
        print(f"❌ Error triggering dance: {e}")
        return {
            "tool": "dance_tool",
            "success": False,
            "error": str(e)
        }


# ============== Session Control Tools ==============

@tool(name="end_session", description="End the current conversation session")
def end_session(farewell_message: str) -> Dict[str, Any]:
    """End the current conversation session and disconnect from the room."""
    
    print("Received end session message. Letting audio play.")
    print(f"👋 {farewell_message}")
    sleeplength = len(farewell_message)/13 + 2 #approximation + buffer
    sleep(sleeplength)
    print("🔌 Disconnecting from LiveKit room...")
    
    # Signal the application to disconnect
    if _app_controller:
        _app_controller.request_disconnect()
    
    return {
        "tool": "end_session",
        "success": True,
        "farewell_message": farewell_message,
        "message": "Session ending, disconnecting from room"
    }