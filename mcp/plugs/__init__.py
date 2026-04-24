"""
Alexandria MCP-Therapy · Plug Registry

11 플러그 (7 Gate × 주 플러그 9개 + 백그라운드 2개).

참조: WHITEPAPER-v1.0.md §4
"""
from mcp.plugs.base import Plug
from mcp.plugs.parksy_profile import ParksyProfilePlug
from mcp.plugs.env_trigger import EnvTriggerPlug
from mcp.plugs.freud import FreudPlug
from mcp.plugs.jung import JungPlug
from mcp.plugs.family import FamilySystemsPlug
from mcp.plugs.shaman_ko import ShamanKoPlug
from mcp.plugs.sufi import SufiPlug
from mcp.plugs.ayahuasca import AyahuascaPlug
from mcp.plugs.mass import MassProtocolPlug
from mcp.plugs.narrative_meta import NarrativeMetaPlug
from mcp.plugs.guardrail import GuardrailPlug


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
