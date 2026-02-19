import json
from pathlib import Path


def test_data_ingestion_workflow_includes_history_embedding_path() -> None:
    workflow_path = Path(__file__).resolve().parents[2] / "n8n" / "data-ingestion-workflow.json"
    workflow = json.loads(workflow_path.read_text())

    node_names = {node.get("name") for node in workflow.get("nodes", [])}
    required_nodes = {
        "Fetch Historia Vasca",
        "Normalize History",
        "OpenAI Embeddings (History)",
        "Build History Embedding Insert",
        "Insert History Embedding",
    }
    assert required_nodes.issubset(node_names)

    insert_node = next(node for node in workflow["nodes"] if node.get("name") == "Insert History Embedding")
    query = insert_node.get("parameters", {}).get("query", "")

    assert "source_type = 'history'" in query
    assert "metadata->>'history_id'" in query
