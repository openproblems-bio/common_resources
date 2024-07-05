import subprocess
from os import path
from ruamel.yaml import YAML

## VIASH START
meta = {
    'executable': 'foo'
}
## VIASH END

print(meta["resources_dir"])


task_template = "/tmp/task_template"
output_path = f"{task_template}/src/methods/test_method"

cmd = [
    meta['executable'],
    '--task', 'task_template',
    '--type', 'method',
    '--name', 'test_method',
    '--language', 'python'
]

print('>> Running the script as test', flush=True)
out = subprocess.run(cmd, stderr=subprocess.STDOUT, cwd=task_template)

if out.stdout:
    print(out.stdout)

if out.returncode:
    print(f"script: '{cmd}' exited with an error.")
    exit(out.returncode)

print('>> Checking whether output files exist', flush=True)
assert path.exists(output_path), "Output dir does not exist"

conf_f = path.join(output_path, 'config.vsh.yaml')
assert path.exists(conf_f), "Config file does not exist"

script_f = path.join(output_path, "script.py")
assert path.exists(script_f), "Script file does not exist"

print('>> Checking file contents', flush=True)
yaml = YAML(typ='safe', pure=True)
with open(conf_f) as f:
    conf_data = yaml.load(f)

assert conf_data['name'] == 'test_method', "Name should be equal to 'test_method'"


print('All checks succeeded!', flush=True)

