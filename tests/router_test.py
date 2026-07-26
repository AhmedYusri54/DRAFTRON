import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models.router import get_extraction_model, get_matching_model, get_draft_generation_model, get_critique_model



print("Extraction model:")
result = get_extraction_model().invoke("Hello, how are you?")
print(result.content)

print("Matching model:")
result = get_matching_model().invoke("Hello, how are you?")
print(result.content)

print("Draft generation model:")
result = get_draft_generation_model().invoke("Hello, how are you?")
print(result.content)

print("Draft critique model:")
result = get_critique_model().invoke("Hello, how are you?")
print(result.content)

