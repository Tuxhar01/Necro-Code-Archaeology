"""
Main application entry point.
This is the control case - well-documented, clearly used, normal code.
"""

from utils import validate_input


def process_request(request_data):
    """
    Main request processor - handles incoming requests.
    
    Args:
        request_data: Dictionary containing request information
        
    Returns:
        dict: Processed response with status and data
    """
    if not validate_input(request_data):
        return {
            "status": "error",
            "message": "Invalid request data"
        }
    
    return {
        "status": "success",
        "data": request_data,
        "processed": True
    }


def handle_request(request_data):
    """
    Handle validated request and perform business logic.
    
    Args:
        request_data: Validated request data
        
    Returns:
        dict: Response with processed results
    """
    result = {
        "id": request_data.get("id"),
        "timestamp": request_data.get("timestamp"),
        "result": "processed"
    }
    return result


if __name__ == "__main__":
    # Example usage
    sample_request = {
        "id": "req_123",
        "timestamp": "2026-09-26T18:00:00Z",
        "data": {"user_id": 42, "action": "login"}
    }
    
    response = process_request(sample_request)
    print(f"Response: {response}")

# Made with Bob
