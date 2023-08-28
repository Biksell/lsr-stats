import requests
import gspread
import time
import json
import itertools

'''
# Google sheets setup
gsheets_creds = 'gsheets_creds.json'

gc = gspread.service_account(filename=gsheets_creds)

sh = gc.open("lsr_test")
worksheet = sh.worksheet("raw_data")
'''

'''
id:      string
name: string

'''
class Game:
    def __init__(self, id, name, abbreviation):
        self.id = id
        self.name = name
        self.abbreviation = abbreviation
        self.runs = []
        self.runners = []
        self.categories = Categories(self)

    def __str___(self):
        return self.name

    def add_category(self, category):
        self.categories.add_category(category)

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "abbreviation": self.abbreviation,
                "runs": self.runs,
                "runners": self.runners,
                "categories": self.categories.get_categories_dict()}

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_categories(self):
        return self.categories

'''
games = [Game]
'''
class Games:
    def __init__(self):
        self.games = []

    def add_game(self, game: Game):
        self.games.append(game)

    def get_game(self, field, term):
        for game in self.games:
            match field:
                case "id":
                    if game.get_id() == term:
                        return game
                case "name":
                    if game.get_name() == term:
                        return game
        return "not found"

    def get_games(self):
        return self.games

    def get_games_dict(self):
        temp = {}
        for game in self.games:
            temp[game.get_id()] = game.to_dict()
        return temp


'''
id: str
name: str
game: id (str)
runs: [id (str)]
runners = [id (str)]
vars = [Variable]
'''
class Category:
    def __init__(self, id, name, game):
        self.id = id
        self.name = name
        self.game = game
        self.runs = []
        self.runners = []
        self.vars = []

    def __str___(self):
        return self.name

    def add_var(self, var):
        self.vars.append(var)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_game(self):
        return self.game

    def get_vars(self):
        return self.vars

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "runs": self.runs,
                "runners": self.runners,
                "vars": [o.to_dict() for o in self.vars]}

'''
game: id (str)
categories = [Category]
'''
class Categories:
    def __init__(self, game):
        self.game = game
        self.categories = []

    def add_category(self, category):
        self.categories.append(category)

    def get_category(self, field, term):
        for category in self.categories:
            match field:
                case "id":
                    if category.get_id() == term:
                        return category
                case "name":
                    if category.get_name() == term:
                        return category
        return "not found"

    def get_categories(self):
        return self.categories

    def get_categories_dict(self):
        temp = {}
        for category in self.categories:
            temp[category.get_id()] = category.to_dict()
        return temp


    def get_game(self):
        return self.game


"""
id: str
name: str
values: [val_id (str), display_name (str)]
category: id (str)
"""
class Variable:
    def __init__(self, id, name, values, category):
        self.id = id
        self.name = name
        self.values = values
        self.category = category

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_values(self):
        return self.values

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "values": self.values}

'''
id: str
runners: [id (str)]
time: int
game: id (str)
category: id (str)
vars: {var_id: var_value_id}
link: str
placement: int
'''
class Run:
    def __init__(self, id, runners, time, game, category, vars, link, placement=9999):
        self.id = id
        self.runners = runners # [id]
        self.time = time
        self.placement = placement
        self.game = game
        self.category = category
        self.vars = vars # dict {var_id: var_value_id...}
        self.link = link
        '''
        for runner in self.runners:
            runner.runs.append(self)'''

    def __str___(self):
        return f"{self.game}, {self.category} ({self.vars}) in {self.time} by {self.runners}"

    def get_runners(self):
        return self.runners

    def get_id(self):
        return self.id

    def get_category(self):
        return self.category

    def get_game(self):
        return self.game

    def get_placement(self):
        return self.placement

    def to_dict(self):
        return {"id": self.id,
                "runners": self.runners,
                "time": self.time,
                "placement": self.placement,
                "category": self.category.to_dict(),
                "vars": [o.to_dict() for o in self.vars],
                "link": self.link,
                "game": self.game.id}

'''
game: str
runs = [Run]
'''
class Runs:
    def __init__(self, game="global"):
        self.game = game
        self.runs = []

    def add_run(self, run):
        self.runs.append(run)

    def get_run(self, id):
        for run in self.runs:
            if run.get_id() == id:
                return run
        return "not found"

    def get_runs(self, field="", term=""):
        runs = []
        for run in self.runs:
            match field:
                case "runner_id":
                    for runner in run.get_runners():
                        if runner.get_id() == term:
                            runs.append(run)
                case "runner_name":
                    for runner in run.get_runners():
                        if runner.get_name() == term:
                            runs.append(run)
                case "category_id":
                    if run.get_category().get_id() == term:
                        runs.append(run)
                case "category_name":
                    if run.get_category().get_name() == term:
                        runs.append(run)
                case "game_id":
                    if run.get_game().get_id() == term:
                        runs.append(run)
                case "game_name":
                    if run.get_game().get_name() == term:
                        runs.append(run)
                case "placement":
                    if run.get_placement() == term:
                        runs.append(run)
        return runs if len(runs) > 0 else "not found"

    def get_all_runs(self):
        return self.runs

    def get_all_runs_dict(self):
        temp = {}
        for run in self.runs:
            temp[run.get_id()] = run.to_dict()

'''
id: str
name: str
color: TODO [NON-URGENT]: Add color from API ()
points: int
multi: int
'''
class Runner:
    def __init__(self, id, name, color):
        self.id = id
        self.name = name
        self.color = color
        self.points = 0
        self.multi = 1

    def __str__(self):
        return self.name

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def to_dict(self):
        return {"id": self.id,
                "name": self.name,
                "color": self.color,
                "runs": [o.to_dict() for o in self.runs],
                "points": self.points,
                "multi": self.multi}

'''
not sure if used anymore?
'''
class Runners:
    def __init__(self, runners = [], parent="global"):
        self.parent=parent
        self.runners = []

    def add_runner(self, runner):
        if self.get_runner("id", runner.get_id()):
            self.runners.append(runner)
            return True
        else:
            return False

    def get_runner(self, field, term):
        for runner in self.runners:
            match field:
                case "runner_id":
                    if runner.get_id() == term:
                        return runner
                case "runner_name":
                    if runner.get_name() == term:
                        return runner
        return False

    def get_runners(self):
        return self.runners

    def get_runners_dict(self):
        temp = {}
        for runner in self.runners:
            temp[runner.get_id()] = runner.to_dict()
        return temp

'''
Board is meant to be a completely unique data structure with already set variables
game: id (str)
category: id (str)
vars: {var_id: value_id, var_id2: value_id2...}
'''
class Board:
    def __init__(self, game, category, vars):
        self.game = game
        self.category = category
        self.vars = vars  # {var1_id: value, var2_id: value}
        self.id = Board.generate_id(self.game, self.category, self.vars)

    def get_id(self):
        return self.id

    def get_game(self):
        return self.game

    def get_category(self):
        return self.category

    def get_vars(self):
        return self.vars

    def generate_id(game, category, vars):
        id = f"g_{game}-c_{category}-"
        for var in vars:
            for value in var[0]:
                id += f"var_{var}:{value}-"
        return id

'''
boards: [Board]
'''
class Boards:
    def __init__(self):
        self.boards = []

    def add_board(self, board):
        if self.get_board(board.get_id()): self.boards.append(id)

    def get_board(self, id):
        for board in self.boards:
            if board.get_id() == id: return board
        return False


'''
Sleep every 0.6s so the request limit doesn't get met (100 /min)
'''
def req(str):
    print(str)
    data = requests.get(str).json()
    time.sleep(0.6)
    return data

series_name = "the_elder_scrolls"
games_data = []
ignored_games = []
for game in games_data:
    if game["id"] in ignored_games:
        games_data.remove(game)

games = Games()
runners = Runners()
runs = Runs()

'''
Only handles game fetching from a given series at the moment. Also supports saving a backup of the database locally to /backups/games.json
'''
def fullInitialization(save_locally):
    # Games data
    games_data = req(f"https://www.speedrun.com/api/v1/series/{series_name}/games?max=200")["data"]
    for game in games_data:
        new_game = Game(game["id"], game["names"]["international"], game["abbreviation"])
        games.add_game(new_game)
        print(f"[ADDED] Game {new_game.get_id()}: {new_game.get_name()}")

        # Categories data
        categories_data = req(f"https://www.speedrun.com/api/v1/games/{new_game.get_id()}/categories?embed=variables")["data"]
        for category in categories_data:
            if category["type"] == "per-level": # Gets rid of ILs
                continue
            new_category = Category(category["id"], category["name"], new_game)
            print(f"[ADDED] Category {new_category.get_id()}: {new_category.get_name()}")

            # Variables
            for variable in category["variables"]["data"]:
                if variable["is-subcategory"]: # Only care about variables that are sub-categories (TODO: store other ones for later usage?)
                    values = []

                    # Iterate through every variable_id
                    for id in variable["values"]["values"].keys():
                        values.append((id, variable["values"]["values"][id]["label"])) # Var added as a tuple (id, name)
                    var = Variable(variable["id"], variable["name"], values, new_category) # Variable(str, str, [(id, name)], Category)
                    new_category.add_var(var)
                    print(f"[ADDED] Variable {var.get_name()} to the category {new_category.get_name()}")
            new_game.add_category(new_category)
    print(games)
    if save_locally:
        with open("backups/games.json", "w+") as f:
            f.write(json.dumps(games.get_games_dict(), indent=4))

    '''
    # Runs data
    offset = 0
    for game in games.get_games():
        runs_data = req(f"https://www.speedrun.com/api/v1/runs?game={game.get_id()}&max=200&offset={offset}&status=verified&embed=players")
        while True:
            runs_data = runs_data["data"]
            for run in runs_data:
                players = []
                for player in run["players"]:
                    if player["rel"] != "user": continue
                    new_runner = Runner(player["id"], player["names"]["international"], None)
                    if runners.add_runner(new_runner):
                        players.append(new_runner.get_id())
                new_run = Run(run["id"], players, run["times"]["primary_t"], game, run["category"]["data"]["id"], run["values"])
                runs.add_run(new_run)
            offset += 200
            if (runs_data["pagination"]["size"] < 200): break
    print(len(runs))
'''

def leaderboards_test():
    offset = 0
    for game in games.get_games():
        print(game.get_name())
        for category in game.get_categories().get_categories():
            if category.get_id() != "9d8xz4q2": continue
            # Initialize a temporary directory for the board variables & values
            temp = {} # {var_id: [(var_val_id, var_val_name)), var_value2], var_id2: [var_value]}

            # Iterate through every variable in the given category
            for variable in category.get_vars():
                temp[variable.get_id()] = [] # Initialize and empty array for the given variable to store possible values to

                # Iterate through all values and add them to the array
                for value in variable.get_values():
                    temp[variable.get_id()].append(value)

            print(temp)

            # Transform the values of the dictionary to a list
            temp_list = list(temp.values())

            # Find all possible combinations in order to create every single board with the variables (subcategories)
            new_boards = itertools.product(*temp_list)
            #print(f"{list(new_boards)}, {len(temp)}")

            # Create boards by iterating through the generated unique combinations of subcategories, index is used to get the variable_id from temp
            for board in new_boards:
                #new_board = Board(game.get_id(), category.get_id(), board)
                print(board)
                vars = {}
                board = list(board)
                for index, value in enumerate(board):
                    if len(temp) == 0: continue
                    vars[list(temp.keys())[index]] = value[0]
                board = Board(game.get_id(), category.get_id(), vars)
                print(f"Game: {games.get_game('id', game.get_id()).get_name()}, Category: {game.get_categories().get_category('id', (category.get_id())).get_name()}, Vars: {vars}")
                print()


        #runs_data = req(f"https://www.speedrun.com/api/v1/leaderboar")

def test():
    offset = 0
    for game in games.get_games():
        runs_data = req(f"https://www.speedrun.com/api/v1/runs?game={game.get_id()}&max=200&offset={offset}&status=verified&embed=players")
        #print(runs_data)
        while True:
            runs_data = runs_data["data"]
            for run in runs_data:
                players = []
                for player in run["players"]["data"]:
                    print(player)
                    if player["rel"] != "user": continue
                    new_runner = Runner(player["id"], player["names"]["international"], None)
                    if runners.add_runner(new_runner):
                        players.append(new_runner.get_id())
                new_run = Run(run["id"], players, run["times"]["primary_t"], )
                runs.add_run(new_run)
            offset += 200
            if (runs_data["pagination"]["size"] < 200): break
    print(len(runs.get_all_runs()))

'''
TODO: Fix variables and categories (not saving everything at it's current state?)
'''
def loadLocalGames():
    with open("backups/games.json") as json_file:
        data = json.load(json_file)
        for game_id, game in data.items():
            new_game = Game(game_id, game["name"], game["abbreviation"])
            games.add_game(new_game)
            for category_id, category in game["categories"].items():
                new_category = Category(category_id, category["name"], new_game)
                for variable in category["vars"]:
                    var = Variable(variable["id"], variable["name"], variable["values"], new_category)
                    new_category.add_var(var)
            new_game.add_category(new_category)



'''
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
        f = open("backups/runners_{}.txt".format(time.strftime("%Y%m%d-%H%M%S")), "a")
        f.write(json.dumps([o.to_dict() for o in runners.values()], indent=4))
        f.close()
'''

def main():
    fullInitialization(True)
    #loadLocalGames()
    #print(games.get_game("name", "The Elder Scrolls Online").get_id())
    leaderboards_test()


if __name__ == "__main__":
    main()


