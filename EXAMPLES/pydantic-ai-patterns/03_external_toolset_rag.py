"""
Example 3: External Toolset & RAG Pattern (Pydantic AI + Issue #58)

Sources: 
- https://ai.pydantic.dev/toolsets/#external-toolset
- https://github.com/pydantic/pydantic-ai/issues/58 (RAG discussion)

Pattern: Tools executed externally (not in agent process)
Use case: Vector search, embeddings, RAG
"""

from pydantic_ai import (
    Agent, 
    ExternalToolset, 
    ToolDefinition,
    DeferredToolRequests,
    DeferredToolResults,
    ModelRequest,
    UserPromptPart
)

# ============================================================================
# PYDANTIC AI PATTERN: ExternalToolset (deferred execution)
# ============================================================================

# Define tool schemas (no implementation - runs elsewhere)
external_tools = [
    ToolDefinition(
        name='search_casefiles',
        parameters_json_schema={
            'type': 'object',
            'properties': {
                'query': {'type': 'string'},
                'casefile_id': {'type': 'string'},
                'top_k': {'type': 'integer', 'default': 5}
            },
            'required': ['query', 'casefile_id']
        },
        description="Semantic search within casefile using embeddings"
    ),
    ToolDefinition(
        name='get_casefile_context',
        parameters_json_schema={
            'type': 'object',
            'properties': {
                'casefile_id': {'type': 'string'}
            },
            'required': ['casefile_id']
        },
        description="Get casefile metadata and summary"
    )
]

toolset = ExternalToolset(external_tools)
agent = Agent('openai:gpt-4o', toolsets=[toolset], output_type=[str, DeferredToolRequests])

# Agent run returns deferred tool requests
messages = [
    ModelRequest(parts=[
        UserPromptPart(content='Search for user permissions in casefile cf_abc123')
    ])
]

result = agent.run_sync(message_history=messages)

if isinstance(result.output, DeferredToolRequests):
    print(f"Agent wants to call: {result.output.calls}")
    # [ToolCallPart(tool_name='search_casefiles', args={'query': 'user permissions', 'casefile_id': 'cf_abc123'})]
    
    # Execute tools externally (your implementation)
    deferred_results = DeferredToolResults()
    for tool_call in result.output.calls:
        if tool_call.tool_name == 'search_casefiles':
            # Your actual implementation here
            search_results = await execute_semantic_search(
                tool_call.args['query'],
                tool_call.args['casefile_id']
            )
            deferred_results.calls[tool_call.tool_call_id] = search_results
    
    # Resume agent with results
    result = agent.run_sync(
        message_history=result.all_messages(),
        deferred_tool_results=deferred_results
    )


# ============================================================================
# RAG PATTERN: Local Embeddings (Issue #58 discussion)
# ============================================================================

"""
Tom Aarsen (Sentence Transformers maintainer) proposed:

from sentence_transformers import SentenceTransformer

# Local embedding model (no API calls, privacy-preserving)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Embed documents (100 docs/sec on CPU)
documents = [
    "User john@example.com has read permission on casefile cf_123",
    "User jane@example.com has write permission on casefile cf_123",
    "Casefile cf_123 contains medical records"
]
embeddings = model.encode(documents)  # Shape: (3, 384)

# Embed query
query = "Who can access casefile cf_123?"
query_embedding = model.encode(query)  # Shape: (384,)

# Find similar documents (cosine similarity)
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity([query_embedding], embeddings)[0]
top_indices = similarities.argsort()[-2:][::-1]  # Top 2

print("Most relevant:")
for idx in top_indices:
    print(f"  {documents[idx]} (score: {similarities[idx]:.3f})")

# Output:
#   User john@example.com has read permission on casefile cf_123 (score: 0.712)
#   User jane@example.com has write permission on casefile cf_123 (score: 0.698)
"""


# ============================================================================
# YOUR EQUIVALENT PATTERN: CasefileSearchService (with RAG)
# ============================================================================

"""
In my-tiny-data-collider, implement RAG as a registered service method:

from sentence_transformers import SentenceTransformer
from chromadb import Client as ChromaClient
from pydantic import BaseModel, Field
from pydantic_models.base.types import BaseRequest, BaseResponse

# Request/Response models
class SemanticSearchPayload(BaseModel):
    query: str = Field(..., description="Natural language search query")
    casefile_id: CasefileId = Field(..., description="Casefile to search within")
    top_k: int = Field(5, description="Number of results to return")
    filters: Optional[dict] = Field(None, description="Metadata filters")

class SemanticSearchRequest(BaseRequest[SemanticSearchPayload]):
    operation: Literal["semantic_search"] = "semantic_search"

class SearchResult(BaseModel):
    content: str
    score: float
    metadata: dict

class SearchResultsPayload(BaseModel):
    query: str
    results: List[SearchResult]
    total_found: int

class SemanticSearchResponse(BaseResponse[SearchResultsPayload]):
    pass


# Service implementation
class CasefileSearchService:
    def __init__(self):
        # Local embeddings (privacy + speed)
        self.embeddings = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_store = ChromaClient()
        self.collection = self.vector_store.get_or_create_collection("casefiles")
    
    async def index_casefile(self, casefile_id: str, documents: List[dict]):
        '''Index casefile documents for semantic search'''
        texts = [doc['content'] for doc in documents]
        embeddings = self.embeddings.encode(texts)
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[{**doc, 'casefile_id': casefile_id} for doc in documents],
            ids=[f"{casefile_id}_{i}" for i in range(len(texts))]
        )
    
    @register_service_method(
        name="semantic_search_casefile",
        description="Semantic search within casefile using local embeddings",
        service_name="CasefileSearchService",
        service_module="casefileservice.search",
        classification={
            "domain": "workspace",
            "subdomain": "search",
            "capability": "semantic_search",
            "complexity": "composite",
            "maturity": "experimental",
            "integration_tier": "internal"
        }
    )
    async def semantic_search(
        self, 
        request: SemanticSearchRequest
    ) -> SemanticSearchResponse:
        # Generate query embedding
        query_embedding = self.embeddings.encode(request.payload.query)
        
        # Search vector store
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=request.payload.top_k,
            where={"casefile_id": request.payload.casefile_id}
        )
        
        # Format results
        search_results = [
            SearchResult(
                content=results['documents'][0][i],
                score=1 - results['distances'][0][i],  # Convert distance to similarity
                metadata=results['metadatas'][0][i]
            )
            for i in range(len(results['documents'][0]))
        ]
        
        return SemanticSearchResponse(
            request_id=request.client_request_id,
            status="success",
            payload=SearchResultsPayload(
                query=request.payload.query,
                results=search_results,
                total_found=len(search_results)
            )
        )


# Usage example
search_service = CasefileSearchService()

# Index casefile when it's created/updated
await search_service.index_casefile("cf_abc123", [
    {"content": "User john@example.com has read permission", "type": "acl"},
    {"content": "Casefile contains medical records", "type": "metadata"}
])

# Search semantically
search_request = SemanticSearchRequest(
    client_request_id="search_001",
    payload=SemanticSearchPayload(
        query="Who can access this casefile?",
        casefile_id="cf_abc123",
        top_k=5
    )
)

response = await search_service.semantic_search(search_request)
print(f"Found {response.payload.total_found} results")
for result in response.payload.results:
    print(f"  {result.content} (score: {result.score:.3f})")


ADVANTAGES OF YOUR PATTERN:
- Privacy: Embeddings run locally (no data sent to OpenAI/Google)
- Cost: No per-query API fees (Sentence Transformers is free)
- Speed: 100 docs/sec on CPU (vs 200ms+ API latency)
- Audit: SemanticSearchRequest/Response tracked in ToolEvents
- Context: Casefile-scoped search (built-in multi-tenancy)
- Offline: Works without internet

WHEN TO USE EXTERNAL TOOLSET (PYDANTIC AI):
- Rapid prototyping: Quick RAG experiments
- External services: Call existing vector DB APIs
- Multi-agent: Tools shared across multiple agents
- Frontend tools: User-provided search functions

WHEN TO USE YOUR PATTERN:
- Production: Need audit trails, permissions, tracking
- Privacy: Medical/legal data can't leave infrastructure
- Cost control: Avoid per-query API fees at scale
- Integration: RAG as part of casefile workflow
"""
