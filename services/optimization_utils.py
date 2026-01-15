# optimization_utils.py
from typing import Dict
from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)

def create_compact_item(code: str, name: str) -> Dict:
    """Create compact JSON item to minimize tokens"""
    # Removed debug log - creates excessive log bloat (logged for every item created)
    if Config.abbreviate_keys:
        return {"c": code, "n": name}  # c=code, n=name
    else:
        return {"code": code, "name": name}

def expand_compact_result(item: Dict, group_type: str = "first") -> Dict:
    """Expand compact result back to full format"""
    # Removed debug log - creates excessive log bloat (logged 100+ times per batch)
    if Config.abbreviate_keys:
        if group_type == "mapping":
            return {
                "First Group Code": item.get("fc", item.get("firstCode", "")),
                "First Group Name": item.get("fn", item.get("firstName", "")),
                "Second Group Code": item.get("sc", item.get("secondCode", None)),
                "Second Group Name": item.get("sn", item.get("secondName", None)),
                "similarity score": item.get("s", item.get("score", 0)),
                "reason for similarity score": item.get("r", item.get("reason", ""))
            }
    return item