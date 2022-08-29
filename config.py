from dotenv import dotenv_values
import pathlib
base_dir = pathlib.Path(__file__).parent.resolve()
env_dir = pathlib.Path.joinpath(base_dir, '.env')
config_env = dotenv_values(env_dir)
