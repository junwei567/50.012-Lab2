from fastapi import FastAPI, Depends, Response, Header
from typing import Optional
from pydantic import BaseModel, Field

import redis
import random
import pickle

app = FastAPI()

class Game(BaseModel):
    name: str
    id: Optional[str]
    price: float
    description: Optional[str] = Field(
        None, title = "The description of the game", max_length = 300
    )

class BatchGameDelete(BaseModel):
    name: Optional[str]
    above_price: Optional[float]
    below_price: Optional[float]

def get_redis_client():
    return redis.Redis(host="redis")

def flush():
    r = redis.Redis(host="redis")
    r.execute_command("FLUSHALL ASYNC")
    print("ready to go!")

@app.get("/")
def read_root():
    return "Welcome to the Game Shop!"

@app.get("/games")
def get_all_games(response: Response, redis_client: redis.Redis = Depends(get_redis_client), sortBy: Optional[str] = None, count: Optional[int] = None, offset: Optional[int] = None):
    all_game_ids = redis_client.smembers("/game/ids")
    all_game_ids = [x.decode('utf-8') for x in all_game_ids]
    game_collection = []
    for game_id in all_game_ids:
        game = pickle.loads(redis_client.get(f"/game/{game_id}"))
        game_collection.append(game)

    if sortBy:
        if sortBy == "name":
            game_collection = sorted(game_collection, key=lambda k:k.name)
        elif sortBy == "price":
            game_collection = sorted(game_collection, key=lambda k:k.price)
        elif sortBy == "id":
            game_collection = sorted(game_collection, key=lambda k:k.id)
        else:
            response.status_code = 500
            return "invalid sortBy condition"

    if offset:
        if offset > -1:
            game_collection = game_collection[offset:]
        else:
            response.status_code = 500
            return "please offset count > -1"

    if count:
        if count > 0:
            game_collection = game_collection[:count]
        else:
            response.status_code = 500
            return "please input count > 0"

    response.status_code = 200
    return game_collection


@app.get("/games/{game_id}")
def find_game(game_id: str, response: Response, redis_client: redis.Redis = Depends(get_redis_client)):
    all_game_ids = redis_client.smembers("/game/ids")
    all_game_ids=[x.decode('utf-8') for x in all_game_ids]
    print(all_game_ids)
    if game_id in all_game_ids:
        game = pickle.loads(redis_client.get(f"/game/{game_id}"))
        response.status_code = 200
        return game

    response.status_code = 404
    return None

@app.post("/games")
def create_game(game: Game, response: Response, apikey: Optional[str] = Header(None), redis_client: redis.Redis = Depends(get_redis_client)):
    if apikey == "password123":
        game.id = random.randint(1000001, 9999999)
        all_game_ids = redis_client.smembers("/game/ids")
        all_game_ids=[x.decode('utf-8') for x in all_game_ids]
        while (game.id in all_game_ids):
            game.id = random.randint(1000001, 9999999)

        print("Creating", game.id, game.name, game.price, game.description)
        redis_client.sadd("/game/ids", game.id)
        redis_client.set(f"/game/{game.id}", pickle.dumps(game))
        response.status_code = 201
        return f"Game created: {game.id}"
    else:
        response.status_code = 401
        return "Unauthorized"

@app.delete("/games/{game_id}")
def delete_game(game_id: str, response: Response, apikey: Optional[str] = Header(None), redis_client: redis.Redis = Depends(get_redis_client)):
    if apikey == "password123":
        all_game_ids = redis_client.smembers("/game/ids")
        all_game_ids=[x.decode('utf-8') for x in all_game_ids]
        if game_id in all_game_ids:
            redis_client.delete(f"/game/{game_id}")
            redis_client.srem("/game/ids", game_id)
            response.status_code = 200
            return "Game deleted"

        else:
            response.status_code = 404
            return "Game does not exist in database"

    else:
        response.status_code = 401
        return "Unauthorized"

@app.delete("/games_batch")
def delete_games(response: Response, info: BatchGameDelete, apikey: Optional[str] = Header(None), redis_client: redis.Redis = Depends(get_redis_client)):
    if apikey == "password123":
        all_game_ids = redis_client.smembers("/game/ids")
        all_game_ids=[x.decode('utf-8') for x in all_game_ids]
        game_collection = []
        for game_id in all_game_ids:
            game = pickle.loads(redis_client.get(f"/game/{game_id}"))
            game_collection.append(game)

        if info.name:
            for game in game_collection:
                if info.name in game.name:
                    redis_client.delete(f"/game/{game.id}")
                    redis_client.srem("/game/ids", game.id)
        if info.above_price:
            for game in game_collection:
                if game.price >= info.above_price:
                    redis_client.delete(f"/game/{game.id}")
                    redis_client.srem("/game/ids", game.id)
        if info.below_price:
            for game in game_collection:
                if game.price < info.below_price:
                    redis_client.delete(f"/game/{game.id}")
                    redis_client.srem("/game/ids", game.id)

        response.status_code = 200
        return "batch delete operation completed"

    else:
        response.status_code = 401
        return "Unauthorized"
