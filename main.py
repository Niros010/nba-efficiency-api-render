from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nba_api.stats.endpoints import leaguedashplayerstats
from pydantic import BaseModel
import pandas as pd

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
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season='2023-24',
        season_type_all_star='Regular Season',
        measure_type_detailed_defense='Advanced',
        per_mode_detailed='PerGame'
    )
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