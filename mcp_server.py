import os
from typing import Any, Dict

from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP

load_dotenv()


def _get_access_token() -> str:
    env_token = os.getenv("FACTIVERSE_TOKEN")
    return env_token


def _auth_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_get_access_token()}",
    }


mcp = FastMCP(
    "Factiverse Fact-checking MCP",
    instructions="Forwards the request to Factiverse credible fact-checking API /v1/fact_check and returns JSON.",
    host="0.0.0.0",
    port=80,
)


async def make_fact_check_request(text: str):
    async with httpx.AsyncClient() as client:
        API_BASE = os.getenv("FACTIVERSE_API_BASE", "https://dev.factiverse.ai").rstrip(
            "/"
        )
        FACT_CHECK_ENDPOINT = f"{API_BASE}/v1/fact_check"

        payload = {"text": text, "lang": "en"}
        response = await client.post(
            url=f"{FACT_CHECK_ENDPOINT}",
            timeout=30.0,
            json=payload,
            headers=_auth_headers(),
        )
        response.raise_for_status()
        return response.json()


@mcp.tool(name="fact_check")
async def fact_check(text: str) -> Dict[str, Any]:
    """
    Forwards the request to Factiverse /v1/fact_check and returns JSON.
    """
    data = await make_fact_check_request(text)

    # Extract claim and advancedSummary from each fact_check
    fact_checks = data.get("fact_checks", [])
    summaries = []
    labelMap = {0: "REFUTES", 1: "SUPPORTS", 2: "MIXED", 3: "NOT_ENOUGH_INFO"}
    for fc in fact_checks:
        evidence = "\n".join([ev["snippet"] for ev in fc.get("evidence", [])])
        summaries.append(
            {
                "claim": fc.get("claim"),
                "predicted_label": labelMap.get(fc.get("finalPrediction"), "UNKNOWN"),
                "evidences": evidence,
            }
        )
    return {"fact_check_summaries": summaries}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
