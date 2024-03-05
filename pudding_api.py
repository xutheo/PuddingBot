from flask import Flask, request, abort
import Timelines
import json
import Homework
from Users import worry_users, chorry_users

class SimpleTimeline:
    def __init__(self, id, ev, units):
        self.id = id
        self.ev = ev
        self.units = units

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

app = Flask('PuddingBot')
port = 8080
host = "0.0.0.0"

@app.route('/timelines', methods=['GET'])
def get_timeline():
    id = request.args.get('id')
    boss = int(id[1])
    timeline = Timelines.get_from_db(boss, id)
    if timeline:
        simple_timeline = SimpleTimeline(id, timeline.ev, timeline.units)
    #print(simple_timeline.to_json())
    return simple_timeline.to_json()

@app.route('/homework', methods=['GET'])
def get_homework():
    id = request.args.get('id').lower()
    worry_hw = Homework.get_homework(cache=True)
    chorry_hw = Homework.get_homework(chorry=True, cache=True)

    for hw in worry_hw:
        if hw.id and id == str(hw.id):
            print(hw)
            return hw.to_json()
    for hw in chorry_hw:
        if hw.id and id == str(hw.id):
            print(hw)
            return hw.to_json()
    abort(404)

#homeworks = Homework.get_homework(cache=True)
#for hw in homeworks:
    #print(hw)

app.run(host=host, port=port)