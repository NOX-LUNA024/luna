from backend.cognitive import CognitiveContext


def test_cognitive_context_defaults():
    context = CognitiveContext()

    assert context.memory == {}
    assert context.emotion == {}
    assert context.curiosity is None
    assert context.identity == {}
    assert context.recent_context == []


def test_cognitive_context_prompt_dict():
    context = CognitiveContext(
        memory={"favorite": "Pokémon"},
        emotion={"mood": "bright"},
        curiosity="What are you building next?",
        identity={"name": "Luna", "creator": "Arman"},
        recent_context=[
            {"role": "user", "content": "I'm working on Luna."}
        ],
    )

    result = context.to_prompt_dict()

    assert result["memory"]["favorite"] == "Pokémon"
    assert result["emotion"]["mood"] == "bright"
    assert result["curiosity"] == "What are you building next?"
    assert result["identity"]["name"] == "Luna"
    assert len(result["recent_context"]) == 1


def test_cognitive_context_prompt_string():
    context = CognitiveContext(
        memory={"favorite": "Pokémon"},
        emotion={"mood": "bright"},
        curiosity="What are you building next?",
        identity={"name": "Luna", "creator": "Arman"},
    )

    result = context.to_prompt_string()

    assert "Identity: Luna" in result
    assert "Emotional State: bright" in result
    assert "Pending Question: What are you building next?" in result
    assert "Active Memories:" in result