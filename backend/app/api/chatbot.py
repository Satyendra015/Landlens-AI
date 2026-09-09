from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from backend.app.services.gemini_service import gemini_chat_service

router = APIRouter(tags=["Gemini 3.1 Pro Chatbot & Land Intelligence"])


class ChatMessageRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []
    api_key: Optional[str] = None


class ChatMessageResponse(BaseModel):
    reply: str
    model: str
    source: str
    suggestions: List[str]


@router.post("/api/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Send text conversation message to Gemini 3.1 Pro Assistant.
    Returns authoritative responses on land circle rates, government mega projects,
    and verification procedures, along with real-time contextual follow-up suggestions.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty."
        )

    res = await gemini_chat_service.generate_chat_response(
        message=request.message.strip(),
        conversation_history=request.history,
        custom_api_key=request.api_key
    )
    return ChatMessageResponse(**res)


@router.get("/api/chat/suggestions")
async def get_chat_suggestions_and_updates():
    """
    Returns real-time contextual suggestions and live government revenue news alerts.
    """
    return {
        "suggestions": gemini_chat_service.get_suggestions(),
        "realtime_updates": gemini_chat_service.get_realtime_updates(),
    }


@router.get("/api/land-rates")
async def get_state_land_rates(state: Optional[str] = None):
    """
    Returns official state government land circle rates, ready reckoner values,
    guidance values, stamp duty rates, and district benchmarks.
    """
    rates = gemini_chat_service.get_state_land_rates(state_name=state)
    return {
        "total": len(rates),
        "rates": rates
    }


@router.get("/api/land-rates/{state_name}")
async def get_specific_state_land_rate(state_name: str):
    """
    Returns land valuation details for a specific Indian state.
    """
    rates = gemini_chat_service.get_state_land_rates(state_name=state_name)
    if not rates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State '{state_name}' not found in land rates registry."
        )
    return rates[0]


@router.get("/api/gov-projects")
async def get_government_projects(
    state: Optional[str] = None,
    sector: Optional[str] = None
):
    """
    Returns active mega government infrastructure projects with real-time
    land acquisition percentages, total budgets, and compensation packages.
    """
    projects = gemini_chat_service.get_government_projects(state=state, sector=sector)
    return {
        "total": len(projects),
        "projects": projects
    }
