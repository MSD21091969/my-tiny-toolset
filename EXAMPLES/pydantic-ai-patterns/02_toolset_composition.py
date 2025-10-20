"""
Example 2: Toolset Composition (Pydantic AI)

Source: https://ai.pydantic.dev/toolsets/#toolset-composition
Pattern: Combining, filtering, prefixing, renaming toolsets
"""

from pydantic_ai import Agent, FunctionToolset, CombinedToolset
from pydantic_ai.models.test import TestModel

# ============================================================================
# PYDANTIC AI PATTERN: Multiple toolsets composed together
# ============================================================================

# Weather toolset
weather_toolset = FunctionToolset()

@weather_toolset.tool
def temperature_celsius(city: str) -> float:
    return 21.0

@weather_toolset.tool
def temperature_fahrenheit(city: str) -> float:
    return 69.8

# Time toolset
time_toolset = FunctionToolset()
time_toolset.add_function(lambda: "2025-10-20", name='current_date')

# Combine with prefixes (avoid name collisions)
combined = CombinedToolset([
    weather_toolset.prefixed('weather'),
    time_toolset.prefixed('time')
])

agent = Agent(TestModel(), toolsets=[combined])
result = agent.run_sync('What tools are available?')

# Available tools: weather_temperature_celsius, weather_temperature_fahrenheit, time_current_date


# ============================================================================
# FILTERING TOOLSETS (conditional availability)
# ============================================================================

# Only expose certain tools based on context
filtered = combined.filtered(
    lambda ctx, tool_def: 'fahrenheit' not in tool_def.name
)

agent_filtered = Agent(TestModel(), toolsets=[filtered])
# Now only celsius tools available


# ============================================================================
# YOUR EQUIVALENT PATTERN: Registry + Classification
# ============================================================================

"""
In my-tiny-data-collider, tool composition happens via MANAGED_METHODS registry:

# All methods registered with classification taxonomy
@register_service_method(
    name="get_temperature_celsius",
    classification={
        "domain": "external",
        "subdomain": "weather",
        "capability": "query",
        "complexity": "atomic",
        "maturity": "stable",
        "integration_tier": "external"
    }
)
async def get_temperature_celsius(self, request): ...

@register_service_method(
    name="get_current_date",
    classification={
        "domain": "external",
        "subdomain": "time",
        "capability": "query",
        ...
    }
)
async def get_current_date(self, request): ...

# Filter by classification (not by toolset)
from pydantic_ai_integration.method_registry import MANAGED_METHODS

def get_weather_methods():
    return {
        name: method 
        for name, method in MANAGED_METHODS.items()
        if method.domain == "external" and method.subdomain == "weather"
    }

def get_methods_for_user(user_permissions):
    return {
        name: method
        for name, method in MANAGED_METHODS.items()
        if method.integration_tier in user_permissions
    }

DIFFERENCES:
- Pydantic AI: Dynamic composition at runtime via toolset objects
- Your pattern: Static registry with classification-based filtering
- Pydantic AI: Prefix names to avoid collisions (weather_temp, time_temp)
- Your pattern: Fully qualified names (weather.get_temperature, time.get_timestamp)

WHY YOUR PATTERN:
- Discoverability: All methods in one registry (MANAGED_METHODS)
- Documentation: Generate tool catalog from registry (methods_inventory_v1.yaml)
- Drift detection: Compare YAML vs actual registered methods
- Fine-grained filtering: 6-field classification (domain/subdomain/capability/complexity/maturity/tier)
- Permission-based: Filter by user role, not just by toolset name

WHEN TO USE PYDANTIC AI PATTERN:
- Rapid prototyping: Quick tool combinations
- Dynamic loading: Load tools from plugins
- Context-dependent: Different tools per conversation
- External toolsets: MCP servers, LangChain tools

WHEN TO USE YOUR PATTERN:
- Enterprise: Need audit trails, permissions, documentation
- Stability: Tools don't change during runtime
- Multi-user: Different users see different tools based on roles
- Compliance: Must track which tools were available when
"""
