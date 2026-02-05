from dependencies.concurency import get_games_runner
from domain.serialization import prepare_results, save_result
from share.logging_config import setup_logging

setup_logging()

games_runner = get_games_runner()
games_results = games_runner.run_games()

benchmarking_result = prepare_results(games_results)
save_result(benchmarking_result)
