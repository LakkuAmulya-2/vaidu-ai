"""
Gemini Live API handler for real-time voice/video consultation.
"""
import asyncio
import logging
import os
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# Note: This is a placeholder for Gemini Live API integration
# The actual implementation will depend on the final Gemini Live API structure


class LiveConsultation:
    """
    Handler for Gemini Live API real-time consultations.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.0-flash-live"
        self.active_sessions = {}
    
    async def handle_websocket(self, websocket: WebSocket, session_id: str):
        """
        Handle WebSocket connection for live consultation.
        
        Args:
            websocket: FastAPI WebSocket connection
            session_id: Unique session identifier
        """
        await websocket.accept()
        is_connected = True
        
        try:
            # Send welcome message
            await websocket.send_json({
                "type": "connected",
                "message": "Live consultation connected",
                "session_id": session_id
            })
            
            # Initialize session context
            self.active_sessions[session_id] = {
                "context": "medical_billing_consultation",
                "language": "te",
                "started_at": asyncio.get_event_loop().time()
            }
            
            # Main message loop
            while is_connected:
                try:
                    # Receive message from client
                    data = await websocket.receive()
                    
                    # Check if disconnect message
                    if data.get("type") == "websocket.disconnect":
                        logger.info(f"Client disconnected session {session_id}")
                        is_connected = False
                        break
                    
                    if "text" in data:
                        # Handle text message
                        response = await self._process_text_message(
                            data["text"], 
                            session_id
                        )
                        
                        if is_connected:
                            await websocket.send_json({
                                "type": "text",
                                "content": response
                            })
                    
                    elif "bytes" in data:
                        # Handle audio/video data
                        response = await self._process_media_message(
                            data["bytes"],
                            session_id
                        )
                        
                        if is_connected and response.get("audio"):
                            await websocket.send_bytes(response["audio"])
                        
                        if is_connected and response.get("text"):
                            await websocket.send_json({
                                "type": "text",
                                "content": response["text"]
                            })
                
                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for session {session_id}")
                    is_connected = False
                    break
                except RuntimeError as e:
                    if "disconnect" in str(e).lower():
                        logger.info(f"WebSocket disconnect detected: {e}")
                        is_connected = False
                        break
                    else:
                        logger.error(f"Runtime error in WebSocket loop: {e}")
                        is_connected = False
                        break
                except Exception as e:
                    logger.error(f"Error in WebSocket loop: {e}")
                    if is_connected:
                        try:
                            await websocket.send_json({
                                "type": "error",
                                "message": "An error occurred. Please try again."
                            })
                        except:
                            is_connected = False
                    break
        
        finally:
            # Cleanup session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Close connection if still open
            if is_connected:
                try:
                    await websocket.close()
                except:
                    pass
            
            logger.info(f"Session {session_id} cleaned up")
    
    async def _process_text_message(self, message: str, session_id: str) -> str:
        """
        Process text message using Gemini.
        
        Args:
            message: User's text message
            session_id: Session identifier
            
        Returns:
            AI response text
        """
        try:
            # Get session context
            session = self.active_sessions.get(session_id, {})
            lang = session.get("language", "te")
            
            # For now, use the existing Gemini API
            # In production, this would use Gemini Live API
            from utils.vertex_client import predict_text_with_retry
            
            system_prompt = f"""You are a helpful medical billing assistant speaking in {lang} language.
You help patients understand their medical bills, insurance coverage, and patient rights.
Be empathetic, clear, and supportive. Use simple language.

Current conversation context: Medical billing consultation
"""
            
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"
            
            response = predict_text_with_retry("medgemma_4b", full_prompt)
            return response
        
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            
            if session.get("language") == "te":
                return "క్షమించండి, సమస్య ఎదురైంది. దయచేసి మళ్లీ ప్రయత్నించండి."
            elif session.get("language") == "hi":
                return "क्षमा करें, समस्या हुई। कृपया पुनः प्रयास करें।"
            else:
                return "Sorry, an error occurred. Please try again."
    
    async def _process_media_message(self, media_bytes: bytes, session_id: str) -> dict:
        """
        Process audio/video message.
        
        Args:
            media_bytes: Audio or video data
            session_id: Session identifier
            
        Returns:
            Dictionary with response audio and/or text
        """
        try:
            # This is a placeholder for actual Gemini Live API integration
            # In production, this would:
            # 1. Send audio/video to Gemini Live API
            # 2. Receive real-time audio response
            # 3. Return both audio and text transcription
            
            session = self.active_sessions.get(session_id, {})
            lang = session.get("language", "te")
            
            # For now, return a placeholder response
            if lang == "te":
                text_response = "వాయిస్ సందేశం స్వీకరించబడింది. ఈ ఫీచర్ త్వరలో అందుబాటులోకి వస్తుంది."
            elif lang == "hi":
                text_response = "वॉयस संदेश प्राप्त हुआ। यह सुविधा जल्द ही उपलब्ध होगी।"
            else:
                text_response = "Voice message received. This feature will be available soon."
            
            return {
                "text": text_response,
                "audio": None  # Would contain audio bytes in production
            }
        
        except Exception as e:
            logger.error(f"Error processing media message: {e}")
            return {
                "text": "Error processing audio/video",
                "audio": None
            }
    
    async def update_session_context(self, session_id: str, context_update: dict):
        """
        Update session context (language, bill data, etc.).
        
        Args:
            session_id: Session identifier
            context_update: Dictionary with context updates
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id].update(context_update)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return len(self.active_sessions)


# Singleton instance
live_consultation_handler = LiveConsultation()
