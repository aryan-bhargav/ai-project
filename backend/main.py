from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from game_logic import Connect4Game
from ai_agent import Connect4AI, PLAYER_1, PLAYER_2

app = FastAPI(title="AI Game Engine Backend")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the single global game instance
current_game = Connect4Game()
# Set AI depth: depth 6 provides good challenge and pruning stats.
ai_agent = Connect4AI(depth_limit=6)

class MoveRequest(BaseModel):
    col: int

@app.get("/get_game_state")
def get_game_state():
    """Retrieve the current board, player turn, and game status."""
    return {
        "board": current_game.get_board_as_list(),
        "current_player": current_game.current_player,
        "game_over": current_game.game_over,
        "winner": current_game.winner,
    }

@app.post("/player_move")
def player_move(request: MoveRequest):
    """Handles human player (Player 1) drop piece request."""
    if current_game.game_over:
        raise HTTPException(status_code=400, detail="Game already finished.")
    if current_game.current_player != PLAYER_1:
         raise HTTPException(status_code=400, detail="Not player 1's turn.")
    if not current_game.is_valid_move(request.col):
        raise HTTPException(status_code=400, detail="Invalid column.")

    current_game.drop_piece(request.col)
    return get_game_state()

@app.post("/ai_move")
def ai_move():
    """Triggers the AI agent to compute and make its move (Player 2)."""
    if current_game.game_over:
        raise HTTPException(status_code=400, detail="Game already finished.")
    if current_game.current_player != PLAYER_2:
        raise HTTPException(status_code=400, detail="Not AI's turn.")
    
    # AI calculates the best move and statistics
    best_col, ai_stats = ai_agent.get_best_move(current_game)
    current_game.drop_piece(best_col)
    
    response = get_game_state()
    response["ai_computation_stats"] = ai_stats
    return response

@app.post("/reset_game")
def reset_game():
    current_game.reset()
    return get_game_state()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)