#!/usr/bin/env python3

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import requests

from app.utils import get_redis_client, SessionManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize managers
redis_client = get_redis_client()
sm = SessionManager(redis_client)

DIALPAD_API_BASE_URL = "https://dialpad.com/api/v2"


def get_token_from_session(session_id: str) -> str:
    """Get Dialpad API key (access token) from session ID."""
    session_data = sm.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found or expired")
    
    provider_tokens = session_data.get("provider_tokens", {})
    access_token = provider_tokens.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token found in session")
    
    return access_token


def make_dialpad_request(method: str, endpoint: str, token: str, params: dict = None, data: dict = None):
    """Make a request to Dialpad API."""
    url = f"{DIALPAD_API_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.exceptions.HTTPError as e:
        logger.error(f"Dialpad API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text
        )
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Users/Operators
@router.get("/users", tags=["Users"])
async def list_users(
    session_id: str = Query(..., description="Session ID from auth/connect"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List all Dialpad users/operators."""
    token = get_token_from_session(session_id)
    params = {"limit": limit, "offset": offset}
    return make_dialpad_request("GET", "/users", token, params=params)


@router.get("/users/{user_id}", tags=["Users"])
async def get_user(
    user_id: str,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Get detailed information for a specific user."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", f"/users/{user_id}", token)


@router.patch("/users/{user_id}", tags=["Users"])
async def update_user(
    user_id: str,
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Update user information."""
    token = get_token_from_session(session_id)
    data = await request.json()
    return make_dialpad_request("PATCH", f"/users/{user_id}", token, data=data)


@router.post("/users/{user_id}/assign_number", tags=["Users"])
async def assign_number_to_user(
    user_id: str,
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Assign a phone number to a user."""
    token = get_token_from_session(session_id)
    data = await request.json()
    return make_dialpad_request("POST", f"/users/{user_id}/assign_number", token, data=data)


@router.post("/users/{user_id}/unassign_number", tags=["Users"])
async def unassign_number_from_user(
    user_id: str,
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Unassign a phone number from a user."""
    token = get_token_from_session(session_id)
    data = await request.json()
    return make_dialpad_request("POST", f"/users/{user_id}/unassign_number", token, data=data)


# Call Routers (IVRs)
@router.get("/callrouters", tags=["Call Routers"])
async def list_call_routers(
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """List all call routers (IVRs)."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", "/callrouters", token)


@router.get("/callrouters/{router_id}", tags=["Call Routers"])
async def get_call_router(
    router_id: str,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Get detailed information for a specific call router."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", f"/callrouters/{router_id}", token)


@router.patch("/callrouters/{router_id}", tags=["Call Routers"])
async def update_call_router(
    router_id: str,
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Update call router settings."""
    token = get_token_from_session(session_id)
    data = await request.json()
    return make_dialpad_request("PATCH", f"/callrouters/{router_id}", token, data=data)


# Offices (Sites)
@router.get("/offices", tags=["Offices"])
async def list_offices(
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """List all offices/sites."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", "/offices", token)


@router.get("/offices/{office_id}", tags=["Offices"])
async def get_office(
    office_id: str,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Get detailed information for a specific office."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", f"/offices/{office_id}", token)


# Phone Numbers
@router.get("/numbers", tags=["Phone Numbers"])
async def list_numbers(
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """List all phone numbers."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", "/numbers", token)


@router.get("/numbers/{number}", tags=["Phone Numbers"])
async def get_number(
    number: str,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Get detailed information for a specific phone number."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", f"/numbers/{number}", token)


@router.post("/numbers/assign", tags=["Phone Numbers"])
async def assign_number(
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Assign a phone number."""
    token = get_token_from_session(session_id)
    data = await request.json()
    return make_dialpad_request("POST", "/numbers/assign", token, data=data)


# Call Centers (Queues)
@router.get("/callcenters", tags=["Call Centers"])
async def list_call_centers(
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """List all call centers/queues."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", "/callcenters", token)


@router.get("/callcenters/{center_id}", tags=["Call Centers"])
async def get_call_center(
    center_id: str,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Get detailed information for a specific call center."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", f"/callcenters/{center_id}", token)


# Stats/Call Logs
@router.get("/stats", tags=["Stats"])
async def get_stats(
    session_id: str = Query(..., description="Session ID from auth/connect"),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None)
):
    """Get call statistics."""
    token = get_token_from_session(session_id)
    params = {}
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    return make_dialpad_request("GET", "/stats", token, params=params)


@router.get("/stats/{stat_id}", tags=["Stats"])
async def get_stat_details(
    stat_id: str,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """Get detailed statistics for a specific stat ID."""
    token = get_token_from_session(session_id)
    return make_dialpad_request("GET", f"/stats/{stat_id}", token)


# Generic Dialpad Proxy
@router.api_route("/dialpad-proxy/{api_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["Proxy"])
async def dialpad_proxy(
    api_path: str,
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """
    Generic proxy endpoint for any Dialpad API call.
    
    This endpoint forwards requests to the Dialpad API with proper authentication.
    Use this for any Dialpad endpoint not explicitly implemented above.
    
    Example: GET /dialpad-proxy/users?session_id={session_id}
    """
    token = get_token_from_session(session_id)
    
    # Get query parameters (excluding session_id)
    params = dict(request.query_params)
    if "session_id" in params:
        del params["session_id"]
    
    # Get request body for POST/PUT/PATCH
    data = None
    if request.method in {"POST", "PUT", "PATCH"}:
        try:
            data = await request.json()
        except Exception:
            data = None
    
    # Make request to Dialpad API
    return make_dialpad_request(request.method, f"/{api_path}", token, params=params, data=data)
