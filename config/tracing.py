import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import tracing_v2_enabled
from contextlib import contextmanager

# LangSmith configuration
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_PROJECT"] = "Amit_newsanalyzer"

# Initialize LangSmith client and tracer
client = Client()
tracer = None

@contextmanager
def create_trace(run_name: str, run_id: str = None, **kwargs):
    """Create a trace context"""
    with tracing_v2_enabled(
        project_name="Amit_newsanalyzer",
        tags=kwargs.get("tags", []),
    ) as cb:
        try:
            yield cb
        except Exception as e:
            if cb:
                cb.on_chain_error(error=str(e), run_id=run_id)
            raise

def init_tracing():
    """Initialize LangSmith tracing"""
    global tracer
    try:
        # Test the connection
        projects = list(client.list_projects())
        if len(projects) > 0:
            # Initialize tracer
            tracer = LangChainTracer(
                project_name="Amit_newsanalyzer",
                client=client
            )
            return True
    except Exception as e:
        print(f"❌ Error initializing LangSmith: {str(e)}")
        return False
