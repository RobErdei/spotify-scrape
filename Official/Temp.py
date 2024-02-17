import os
main_path = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(main_path, 'EnvResources')
dotenv_path = os.path.join(main_path, 'EnvResources', '.env')
csv_Rep = os.path.join(main_path, 'CSV_Dumps')
json_Rep = os.path.join(main_path, 'JSON_Dumps')

os.chdir(env_path)
print(env_path)
 
import TestFunctions
