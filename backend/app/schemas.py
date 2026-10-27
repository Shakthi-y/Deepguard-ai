from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ForensicEvidence(BaseModel):
    mime_type: str
    file_size_kb: float
    dimensions: str
    format: str
    has_exif: bool
    exif_summary: Dict[str, Any] = {}
    estimated_compression: str
    aspect_ratio: float
    color_mode: str
    flags: List[str] = []

class DetectionResult(BaseModel):
    fake_probability: float
    real_probability: float
    predicted_label: str
    model_confidence: float
    threshold_used: float

class VerificationResult(BaseModel):
    verdict: str
    consistent: bool
    reasoning: str

class ConfidenceResult(BaseModel):
    model_confidence: float
    system_confidence: float
    confidence_band: str

class AnalysisResponse(BaseModel):
    id: str
    filename: str
    timestamp: str
    verdict: str
    verdict_color: str
    detection: DetectionResult
    forensic: ForensicEvidence
    verification: VerificationResult
    confidence: ConfidenceResult
    explanation: str
    agent_log: List[Dict[str, str]]
    disclaimer: str
    error: Optional[str] = None
