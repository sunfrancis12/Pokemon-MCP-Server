import httpx
from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP("poke")

POKEAPI_BASE = "https://pokeapi.co/api/v2"

# --- Helper to fetch Pokémon data ---
async def fetch_pokemon_data(name: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{POKEAPI_BASE}/pokemon/{name.lower()}")
            if response.status_code == 200:
                return response.json()
        except httpx.HTTPError:
            pass
    return {}

# --- Tool: Get info about a Pokémon ---
@mcp.tool()
async def get_pokemon_info(name: str) -> str:
    """Get detailed info about a Pokémon by name."""
    data = await fetch_pokemon_data(name)
    if not data:
        return f"No data found for Pokémon: {name}"

    stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
    types_ = [t['type']['name'] for t in data['types']]
    abilities = [a['ability']['name'] for a in data['abilities']]

    return f"""
Name: {data['name'].capitalize()}
Types: {', '.join(types_)}
Abilities: {', '.join(abilities)}
Stats: {', '.join(f"{k}: {v}" for k, v in stats.items())}
"""

# --- Tool: Create a tournament squad ---
@mcp.tool()
async def create_tournament_squad() -> str:
    """Create a powerful squad of Pokémon for a tournament."""
    top_pokemon = ["charizard", "garchomp", "lucario", "dragonite", "metagross", "gardevoir"]
    squad = []

    for name in top_pokemon:
        data = await fetch_pokemon_data(name)
        if data:
            squad.append(data["name"].capitalize())

    return "Tournament Squad:\n" + "\n".join(squad)

# --- Tool: List popular Pokémon ---
@mcp.tool()
async def list_popular_pokemon() -> str:
    """List popular tournament-ready Pokémon."""
    return "\n".join([
        "Charizard", "Garchomp", "Lucario",
        "Dragonite", "Metagross", "Gardevoir"
    ])
    
@mcp.prompt
def introduce_pokemon_prompt(
    pokemon_name: str,
    pokedex_number: int
) -> PromptMessage:
    """Generates a user message simulating Professor Oak introducing a Pokémon."""
    content = f"""
    嗨，[訓練家姓名]！歡迎來到寶可夢的世界！
    今天，我要為你介紹寶可夢圖鑑中編號為 {pokedex_number} 的寶可夢，牠就是... {pokemon_name}！
    {pokemon_name} 是一種非常特別的寶可夢，擁有... [在這裡可以加入對該寶可夢的具體描述，例如屬性、習性、技能等]...
    我希望你和 {pokemon_name} 在未來的旅程中能成為最好的夥伴！
    """
    return PromptMessage(role="user", content=TextContent(type="text", text=content))

# --- Entry point ---
if __name__ == "__main__":
    #mcp.run(transport="stdio")
    mcp.run()
