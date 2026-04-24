"""
Alexandria MCP-Therapy · Plug Registry

11 플러그 (7 Gate × 주 플러그 9개 + 백그라운드 2개).

참조: WHITEPAPER-v1.0.md §4
"""
from alex_mcp.plugs.base import Plug
from alex_mcp.plugs.parksy_profile import ParksyProfilePlug
from alex_mcp.plugs.env_trigger import EnvTriggerPlug
from alex_mcp.plugs.freud import FreudPlug
from alex_mcp.plugs.jung import JungPlug
from alex_mcp.plugs.family import FamilySystemsPlug
from alex_mcp.plugs.shaman_ko import ShamanKoPlug
from alex_mcp.plugs.sufi import SufiPlug
from alex_mcp.plugs.ayahuasca import AyahuascaPlug
from alex_mcp.plugs.mass import MassProtocolPlug
from alex_mcp.plugs.narrative_meta import NarrativeMetaPlug
from alex_mcp.plugs.guardrail import GuardrailPlug


ALL_PLUGS: list[Plug] = [
    ParksyProfilePlug(),
    EnvTriggerPlug(),
    FreudPlug(),
    JungPlug(),
    FamilySystemsPlug(),
    ShamanKoPlug(),
    SufiPlug(),
    AyahuascaPlug(),
    MassProtocolPlug(),
    NarrativeMetaPlug(),
    GuardrailPlug(),
]

__all__ = ["Plug", "ALL_PLUGS"]
