# app/models.py
from pydantic import BaseModel
from typing import List, Dict, Literal

Triple = List[str]

class SpeechAnalysisResult(BaseModel):
    id: str
    created_at: str
    triples: List[Triple]

class DiagnosticReport(BaseModel):
    risk_group: Literal[
        "подозрение на дислексию",
        "имеются нарушения, требуется наблюдение",
        "отсутствуют значимые нарушения"
    ]
    marker_statistics: Dict[str, float]
    temporal_analysis: Dict[str, List[str]] = {}

class DiagnosticRequest(BaseModel):
    analyses: List[SpeechAnalysisResult]
