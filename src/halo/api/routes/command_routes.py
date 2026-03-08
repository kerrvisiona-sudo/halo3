"""Command endpoint with Chain of Responsibility intent classification.

Uses tiered classification:
1. ExactMatchClassifier (0ms, cached)
2. EmbeddingClassifier (5-10ms, semantic similarity)
3. KeywordClassifier (<1ms, regex patterns)
4. LLMClassifier (7s, fallback)
"""

from fastapi import APIRouter, HTTPException, Depends
from ...backend import Backend, get_backend
from ...tools.pipeline import get_pipeline
from ...tools.executor import ToolCallError
from ...intent.factory import create_default_chain
from ...intent.classifiers import ExactMatchClassifier, EmbeddingClassifier
from ..models import CommandRequest, CommandResponse, CommandResult, ToolCall, TokenUsage
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Global classifier chain (initialized on first request)
_classifier_chain = None


def get_chain(backend: Backend):
    """Get or create the classifier chain (singleton pattern)."""
    global _classifier_chain
    if _classifier_chain is None:
        _classifier_chain = create_default_chain(backend, enable_embeddings=True)
    return _classifier_chain


@router.post("/command", response_model=CommandResponse)
async def command(
    request: CommandRequest, backend: Backend = Depends(get_backend)
) -> CommandResponse:
    """Smart home command endpoint with Chain of Responsibility classification.

    Uses tiered classification strategy:
    1. ExactMatch (0ms) → 2. Embedding (5ms) → 3. Keyword (1ms) → 4. LLM (7s)

    Args:
        request: Command request with message and context
        backend: Backend instance (injected)

    Returns:
        CommandResponse with result, context, and token usage
    """
    chain = get_chain(backend)

    # Classify intent using the chain
    classification = chain.classify(request.message, request.context)

    if not classification:
        raise HTTPException(status_code=500, detail="No classifier handled the request")

    # Handle special tool types
    if classification.tool_name == "conversation":
        # LLM responded with conversation instead of tool
        return CommandResponse(
            result=CommandResult(
                status="completed",
                message=classification.parameters.get("response", ""),
            ),
            context=request.context,
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )

    if classification.tool_name == "error":
        raise HTTPException(
            status_code=500, detail=classification.parameters.get("error", "Unknown error")
        )

    # Execute the tool through the filter pipeline
    # Philosophy: QUALITY > SPEED - all filters run for validation and formatting
    pipeline = get_pipeline(enable_nlg=True)

    try:
        # Run through complete pipeline (pre-filters → execute → post-filters)
        pipeline_result = pipeline.execute(
            tool_name=classification.tool_name,
            parameters=classification.parameters,
            context=request.context,
        )

        tool_result = pipeline_result["result"]
        context_updates = pipeline_result["context_updates"]
        filter_metadata = pipeline_result["metadata"]

        # Log filter execution details
        logger.info(
            f"Pipeline executed for {classification.tool_name} "
            f"(pre-filters: {list(filter_metadata['pre_filters'].keys())}, "
            f"post-filters: {list(filter_metadata['post_filters'].keys())})"
        )

        result = CommandResult(
            status=tool_result.get("status", "completed"),
            message=tool_result.get("message", ""),
            device_state=tool_result.get("device_state", {}),
            tool_call=ToolCall(tool=classification.tool_name, parameters=classification.parameters),
        )

        # Update context with pipeline updates
        updated_context = request.context.copy()
        updated_context.update(context_updates)

        # Learn from this interaction (for future caching)
        _learn_from_result(classification, request.message)

        # Token usage (0 for non-LLM classifiers)
        tokens_used = 0 if classification.classifier_used != "llm" else 400  # Estimate for LLM

        return CommandResponse(
            result=result,
            context=updated_context,
            usage=TokenUsage(
                prompt_tokens=tokens_used // 2,
                completion_tokens=tokens_used // 2,
                total_tokens=tokens_used,
            ),
        )

    except ToolCallError as e:
        # Pipeline validation failed
        logger.error(f"Tool pipeline validation failed: {e}")
        return CommandResponse(
            result=CommandResult(status="error", message=str(e)),
            context=request.context,
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )
    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error in pipeline: {e}")
        return CommandResponse(
            result=CommandResult(status="error", message=f"Error inesperado: {str(e)}"),
            context=request.context,
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )


def _learn_from_result(classification, user_input: str):
    """Learn from successful classifications for future caching.

    Args:
        classification: ClassificationResult from the chain
        user_input: Original user input
    """
    # Learn for exact match cache (if not already cached)
    if not classification.cached and classification.confidence >= 0.9:
        for classifier in _classifier_chain.classifiers:
            if isinstance(classifier, ExactMatchClassifier):
                classifier.learn(user_input, classification.tool_name, classification.parameters)
            elif isinstance(classifier, EmbeddingClassifier) and classification.confidence >= 0.95:
                # Only add to embeddings if very high confidence
                classifier.learn(user_input, classification.tool_name, classification.parameters)


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/classifier-chain")
async def get_classifier_chain_info(backend: Backend = Depends(get_backend)):
    """Get information about the classifier chain.

    Returns:
        Info about active classifiers and their configuration
    """
    chain = get_chain(backend)
    return {
        "chain": chain.get_chain_info(),
        "cache_stats": {
            "exact_match_count": len(_classifier_chain.classifiers[0].cache._exact_cache)
            if _classifier_chain
            else 0,
            "embedding_examples": _classifier_chain.classifiers[1].get_examples_count()
            if _classifier_chain and len(_classifier_chain.classifiers) > 1
            else 0,
        },
    }
