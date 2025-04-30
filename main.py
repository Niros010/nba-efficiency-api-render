from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nba_api.stats.endpoints import leaguedashplayerstats
from pydantic import BaseModel
import pandas as pd
import time
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Player(BaseModel):
    id: int
    name: str
    team: str
    gamesPlayed: int
    oes: float
    odes: float
    avgPlusMinus: float

@app.get("/api/players")
def get_players():
    try:
        # שימוש ב headers מתאימים כדי למנוע חסימה
        custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.nba.com'
        }

        # נסיון לטעון את הנתונים עם זמן המתנה
        start_time = time.time()
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season='2023-24',
            season_type_all_star='Regular Season',
            measure_type_detailed_defense='Advanced',
            per_mode_detailed='PerGame',
            headers=custom_headers,
            timeout=15
        )
        print(f"NBA API response time: {time.time() - start_time:.2f}s")

        df = stats.get_data_frames()[0]

        df['OES'] = 0.35 * df['AST_PCT'] + 0.25 * df['USG_PCT'] + 0.25 * df['TS_PCT'] * 100
        df['ODES'] = df['DEF_RATING']
        df['AVG_PLUS_MINUS'] = df['PLUS_MINUS']

        df = df[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'OES', 'ODES', 'AVG_PLUS_MINUS']]
        df = df.rename(columns={
            'PLAYER_ID': 'id',
            'PLAYER_NAME': 'name',
            'TEAM_ABBREVIATION': 'team',
            'GP': 'gamesPlayed',
            'AVG_PLUS_MINUS': 'avgPlusMinus'
        })

        players = df.to_dict(orient="records")
        return players

    except Exception as e:
        return {"error": str(e)}