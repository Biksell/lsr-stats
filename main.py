import requests
import gspread
import time
import json
import jsonpickle

# Google sheets setup
gsheets_creds = 'gsheets_creds.json'

gc = gspread.service_account(filename=gsheets_creds)

sh = gc.open("lsr_test")
worksheet = sh.worksheet("raw_data")

class Game:
    def __init__(self, id, name, abbreviation):
        self.id = id
        self.name = name
        self.abbreviation = abbreviation
        self.runs = []
        self.runners = []
        self.categories = []

    def __str___(self):
        return self.name

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "abbreviation": self.abbreviation,
                "runs": self.runs,
                "runners": self.runners,
                "categories": [o.to_dict() for o in self.categories]}

class Category:
    def __init__(self, id, name, game):
        self.id = id
        self.name = name
        self.game = game
        self.game.categories.append(self)
        self.runs = []
        self.runners = []
        self.vars = []

    def __str___(self):
        return self.name

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "runs": self.runs,
                "runners": self.runners,
                "vars": [o.to_dict() for o in self.vars]}

class Variable:
    def __init__(self, id, name, values, category):
        self.id = id
        self.name = name
        self.values = values
        self.category = category
        self.category.vars.append(self)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "values": self.values}

class Run:
    def __init__(self, id, runners, time, pos, category, vars, link):
        self.id = id
        self.runners = runners
        self.time = time
        self.pos = pos
        self.category = category
        self.vars = vars
        self.link = link
        for runner in self.runners:
            runner.runs.append(self)
        self.game = self.category.game
        self.game.append(self)

    def __str___(self):
        return f"{self.game}, {self.category} ({self.vars}) in {self.time} by {self.runners}"

    def to_dict(self):
        return {"id": self.id,
                "runners": [o.to_dict() for o in self.runners],
                "time": self.time,
                "pos": self.pos,
                "category": self.category.to_dict(),
                "vars": [o.to_dict() for o in self.vars],
                "link": self.link,
                "game": self.game.id}

class Runner:
    def __init__(self, id, name, color):
        self.id = id
        self.name = name
        self.color = color
        self.runs = []
        self.points = 0
        self.multi = 1

    def __str__(self):
        return self.name

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "color": self.color,
                "runs": [o.to_dict() for o in self.runs],
                "points": self.points,
                "multi": self.multi}



def req(str):
    print(str)
    data = requests.get(str).json()
    time.sleep(0.6)
    return data

series_name = "lego"
games_data = req(f"https://www.speedrun.com/api/v1/series/{series_name}/games?max=200")["data"]
ignored_games = []
for game in games_data:
    if game["id"] in ignored_games:
        games_data.remove(game)

games = {}
runners = {}

def updateGames(save_locally):
    games_data = req(f"https://www.speedrun.com/api/v1/series/{series_name}/games?max=200")["data"]
    for game in games_data:
        game_id = game["id"]
        games[game_id] = Game(game_id, game["names"]["international"], game["abbreviation"])
        print(games[game_id].id)
        print(f"Added {game_id}: {game['names']['international']}")
        categories = {}
        categories_data = req(f"https://www.speedrun.com/api/v1/games/{game_id}/categories?embed=variables")["data"]
        for category in categories_data:
            if category["type"] == "per-level":
                continue
            cat_id = category["id"]
            categories[cat_id] = Category(cat_id, category["name"], games[game_id])
            print(f"Added {cat_id}: {category['name']}")
            for variable in category["variables"]["data"]:
                if variable["is-subcategory"]:
                    values = []
                    for value in variable["values"]["values"].keys():
                        values.append((value, variable["values"]["values"][value]["label"]))
                    var = Variable(variable["id"], variable["name"], values, categories[cat_id])
                    print(f"Added variable {var} to the category {categories[cat_id]}")
    print(games)
    if save_locally:
        f = open("backups/games_{}.txt".format(time.strftime("%Y%m%d-%H%M%S")), "a")
        f.write(json.dumps([o.to_dict() for o in games.values()], indent=4))
        f.close()

def updateRunners(save_locally):
    for game in games.values():
        for category in game.categories:
            board_runners = req(f"https://www.speedrun.com/api/v1/leaderboards/{game.id}/category/{category.id}?embed=players&max=200")["data"]["players"]["data"]
            if len(board_runners) == 0:
                continue
            for board_runner in board_runners:
                try:
                    if board_runner["id"] not in runners.keys():
                        runner = Runner(board_runner["id"], board_runner["names"]["international"], None)
                        runners[board_runner["id"]] = runner
                        print(f"Added player {runner}")
                        print(f"Runner count: {len(runners)}")
                except:
                    continue

    if save_locally:
        f = open("backups/runners_{}.txt".format(time.strftime("%Y%m%d-%H%M%S"), "a")
        f.write(json.dumps([o.to_dict() for o in runners.values()], indent=4))
        f.close()



def main():
    #update_players()
    #print(type(worksheet.col_values(1)))
    #print(worksheet.col_values(1))
    updateGames(True)
    updateRunners(True)


if __name__ == "__main__":
    main()


