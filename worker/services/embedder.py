from config import API_KEY
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

def create_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768),
    )

    values = response.embeddings[0].values
    norm = sum(v * v for v in values) ** 0.5 # NORMALIZING VECTOR FOR MORE PRECISE ANSWERS

    return [v / norm for v in values]