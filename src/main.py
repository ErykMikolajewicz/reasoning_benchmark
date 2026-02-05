from dependencies.concurency import get_games_runner
from dependencies.serialization import get_result_saver
from share.logging_config import setup_logging

setup_logging()

games_runner = get_games_runner()
games_results = games_runner.run_games()

result_serializer = get_result_saver()
result_serializer.save_results(games_results)
