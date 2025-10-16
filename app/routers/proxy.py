#!/usr/bin/env python3

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Optional

from app.utils import get_redis_client, SessionManager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize session manager
redis_client = get_redis_client()
sm = SessionManager(redis_client)

# Dialpad API configuration
DIALPAD_API_BASE = "https://dialpad.com/api/v2"


def get_session_credentials(session_id: str):
    """Get credentials from session ID."""
    session_data = sm.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found or expired"
        )
    return session_data["provider_tokens"], session_data["tenant"]


@router.api_route(
    "/dialpad-proxy/{api_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"]
)
async def dialpad_proxy(
    api_path: str,
    request: Request,
    session_id: str = Query(..., description="Session ID from auth/connect")
):
    """
    Generic proxy endpoint for any Dialpad API call.
    
    This endpoint forwards requests to the Dialpad API with proper authentication.
    Use this for any Dialpad endpoint not explicitly implemented above.
    
    Common endpoints:
    - users - List all users
    - callrouters - List call routers (IVRs)
    - callcenters - List call centers/queues
    - offices - List offices/sites
    - numbers - List phone numbers
    
    Example: GET /dialpad-proxy/users?session_id={session_id}
    """
    try:
        # Get credentials from session
        provider_tokens, tenant = get_session_credentials(session_id)
        api_key = provider_tokens.get('api_key')
        
        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="No Dialpad API key available in session"
            )
        
        # Build full URL
        url = f"{DIALPAD_API_BASE}/{api_path}"
        
        # Extract query parameters (excluding session_id)
        params = dict(request.query_params)
        if "session_id" in params:
            del params["session_id"]
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Get request body for POST/PUT/PATCH
        body = None
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = await request.json()
            except Exception:
                body = None
        
        # Make the request to Dialpad API
        logger.info(f"Proxying {request.method} request to Dialpad: {url}")
        logger.debug(f"Params: {params}, Body: {body}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if request.method == "GET":
                response = await client.get(url, params=params, headers=headers)
            elif request.method == "POST":
                response = await client.post(url, params=params, json=body, headers=headers)
            elif request.method == "PUT":
                response = await client.put(url, params=params, json=body, headers=headers)
            elif request.method == "PATCH":
                response = await client.patch(url, params=params, json=body, headers=headers)
            elif request.method == "DELETE":
                response = await client.delete(url, params=params, headers=headers)
            else:
                raise HTTPException(
                    status_code=405,
                    detail=f"Method {request.method} not allowed"
                )
            
            # Return response
            try:
                response_data = response.json()
            except Exception:
                response_data = {"text": response.text}
            
            if response.status_code >= 400:
                logger.error(f"Dialpad API error: {response.status_code} - {response_data}")
                return JSONResponse(
                    content={
                        "success": False,
                        "error": f"Dialpad API error: {response.status_code}",
                        "details": response_data
                    },
                    status_code=response.status_code
                )
            
            logger.info(f"Successfully proxied request to Dialpad: {response.status_code}")
            return JSONResponse(content=response_data, status_code=response.status_code)
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during Dialpad API call: {e.response.status_code}")
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text
        
        return JSONResponse(
            content={
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "details": error_detail
            },
            status_code=e.response.status_code
        )
    except httpx.RequestError as e:
        logger.error(f"Request error during Dialpad API call: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Request error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Dialpad proxy error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
