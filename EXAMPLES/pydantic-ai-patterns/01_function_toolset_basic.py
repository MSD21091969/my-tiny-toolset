"""
Example 1: Basic FunctionToolset Pattern (Pydantic AI)

Source: https://ai.pydantic.dev/toolsets/#function-toolset
Pattern: Local tools (run in agent process)
"""

from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.models.test import TestModel

# ============================================================================
# PYDANTIC AI PATTERN: FunctionToolset with @toolset.tool decorator
# ============================================================================

toolset = FunctionToolset()

@toolset.tool
def get_temperature(city: str) -> float:
    """Get temperature for a city (mock data)"""
    return 21.0

@toolset.tool
def get_conditions(ctx: RunContext, city: str) -> str:
    """Get weather conditions with context access"""
    if ctx.run_step % 2 == 0:
        return "It's sunny"
    else:
        return "It's raining"

# Agent with toolset
agent = Agent(TestModel(), toolsets=[toolset])

# Run agent
result = agent.run_sync('What is the weather in London?')
print(f"Agent response: {result.output}")


# ============================================================================
# YOUR EQUIVALENT PATTERN: @register_service_method
# ============================================================================

"""
In my-tiny-data-collider, you would write:

from pydantic import BaseModel, Field
from pydantic_ai_integration.method_decorator import register_service_method
from pydantic_models.base.types import BaseRequest, BaseResponse

# Define request/response models (structured)
class GetTemperaturePayload(BaseModel):
    city: str = Field(..., description="City name")

class GetTemperatureRequest(BaseRequest[GetTemperaturePayload]):
    operation: Literal["get_temperature"] = "get_temperature"

class TemperatureResultPayload(BaseModel):
    city: str
    temperature: float
    unit: str = "celsius"

class GetTemperatureResponse(BaseResponse[TemperatureResultPayload]):
    pass

# Register method (metadata only, no execution wrapper)
@register_service_method(
    name="get_temperature",
    description="Get temperature for a city",
    service_name="WeatherService",
    service_module="weatherservice.service",
    classification={
        "domain": "external",
        "subdomain": "weather",
        "capability": "query",
        "complexity": "atomic",
        "maturity": "stable",
        "integration_tier": "external"
    }
)
async def get_temperature(
    self, 
    request: GetTemperatureRequest
) -> GetTemperatureResponse:
    # Implementation
    return GetTemperatureResponse(
        request_id=request.client_request_id,
        status="success",
        payload=TemperatureResultPayload(
            city=request.payload.city,
            temperature=21.0,
            unit="celsius"
        )
    )

DIFFERENCES:
- Pydantic AI: Decorator wraps execution, auto-generates schema from signature
- Your pattern: Decorator only registers metadata, schema from Pydantic models
- Pydantic AI: Returns raw data (float)
- Your pattern: Returns structured BaseResponse with request_id, status, payload
- Pydantic AI: Context via RunContext parameter
- Your pattern: Context via MDSContext (user_id, casefile_id, session_id)

WHY YOUR PATTERN:
- Audit trails: Need request_id tracking for compliance
- Structured errors: status field instead of exceptions
- Casefile context: Multi-user sessions require more context than run_step
- Documentation: Auto-generate from Pydantic models (62% code reduction)
"""
