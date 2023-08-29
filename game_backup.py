import requests
import time
import json

'''
lhp1_4:         946w031r
lhp1_4dspsp:    3dx2keg1
lhp5_7:         k6qoom1g    Any%: xd1mqlzd
lhp5_7dspsp:    kdkmzmx1
lhpce           nd288rvd
lhpc            w6jkx51j

lsw2            3dx2251y
'''
game_ids = ["3dx2251y"]

def req(str):
    print(str)
    data = requests.get(str).json()
    time.sleep(0.6)
    return data

total_runs = []

def init():
    for game_id in game_ids:
        offset = 0
        verified_str = "&status=verified"
        runs = req(f"https://www.speedrun.com/api/v1/runs?game={game_id}&offset={offset}&max=200{verified_str}&orderby=verify-date&direction=desc")
        if runs["pagination"]["size"] < 200:
            runs = req(f"https://www.speedrun.com/api/v1/runs?game={game_id}&offset={offset}&max=200{verified_str}&orderby=verify-date&direction=desc")
            for run in runs["data"]:
                total_runs.append(run)
                print(f"Game: {game_id}  Run: {run['id']}  Link: {run['weblink']}")
        else:
            while len(runs["pagination"]["links"]) == 2 or runs["pagination"]["links"][0]["rel"] == "next":
                #print(f"Game: {game_id}  Offset: {offset}")
                runs = req(f"https://www.speedrun.com/api/v1/runs?game={game_id}&offset={offset}&max=200{verified_str}&orderby=verify-date&direction=desc")
                offset += 200
                for run in runs["data"]:
                    total_runs.append(run)
                    print(f"Game: {game_id}  Run: {run['id']}  Link: {run['weblink']}")

init()

f = open("lsw2.txt", "w")
f.write(json.dumps(total_runs, indent=4))
f.close()
