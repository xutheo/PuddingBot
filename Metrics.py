from sqlitedict import SqliteDict
from clan_battle_info import sqlitedict_base_path
from sheets_helper import get_metrics_worksheet
import datetime

class Metric:
    def __init__(self, command, params, author, timestamp):
        self.command = command
        self.params = params
        self.author = author
        self.timestamp = timestamp

    def __str__(self):
        return (f'Command: {self.command} - Params: {self.params},  Author: {self.author} '
                f'Timestmap: {self.timestamp}')


def save_metric_from_context(ctx):
    try:
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        params = []
        for option in ctx.selected_options:
            params.append(f"{option['name']}: {option['value']}")

        save_metric(ctx.command.name, ', '.join(params), ctx.author.name, timestamp)
    except Exception as e:
        print(f"Failed to save metrics due to {e}")


def save_metric(command, params, author, timestamp):
    metrics_store = SqliteDict(sqlitedict_base_path + 'metrics.sqlite', autocommit=True)
    if 'metrics' not in metrics_store:
        metrics_store['metrics'] = []
    metrics = metrics_store['metrics']
    metrics.append([command, params, author, timestamp])
    metrics_store['metrics'] = metrics


def unload_metrics():
    try:
        metrics_store = SqliteDict(sqlitedict_base_path + 'metrics.sqlite', autocommit=True)
        wksht = get_metrics_worksheet()
        wksht.append_table(metrics_store['metrics'])
        #for metric in metrics_store['metrics']:
        #    wksht.append_table(metric)
        metrics_store['metrics'] = []
    except Exception as e:
        print(f"Failed to save metrics due to {e}")


'''#metrics_store = SqliteDict(sqlitedict_base_path + 'metrics.sqlite', autocommit=True)
#metrics_store['metrics'] = []
save_metric('test', 'test', 'zalteo', datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
save_metric('test2', 'test', 'zalteo', datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
save_metric('test3', 'test', 'zalteo', datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
save_metric('test4', 'test', 'zalteo', datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
unload_metrics()'''