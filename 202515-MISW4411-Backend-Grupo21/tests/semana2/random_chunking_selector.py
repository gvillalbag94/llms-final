import json, random, sys, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--semana", type=int, default=2)
args = parser.parse_args()
semana = args.semana

with open("./tests/semana2/valid_chunking_config.json") as f:
    options = json.load(f)

unique_strategies = []
for config in options:
    strategy = config.get("chunking_config", {}).get("chunking_strategy")
    if strategy not in unique_strategies:
        unique_strategies.append(config)

if len(unique_strategies) < semana:
    sys.exit(f"Error: Se deben tener al menos {semana} estrategias de chunking")

json_str = json.dumps( random.choice(unique_strategies) )

github_env = os.getenv("GITHUB_ENV")

with open(github_env, "a") as f:
    f.write("RAND_CHUNKING<<EOF\n")
    f.write(json_str + "\n")
    f.write("EOF\n")