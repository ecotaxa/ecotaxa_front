import os
import re
from typing import List

CONF_TEMPLATE = os.path.join(os.path.dirname(__file__), 'config-model.cfg')
assert os.path.exists(CONF_TEMPLATE)


def _read_config_keys() -> List[str]:
    """
    Reads keys from the config template file, including those commented out with '# '.
    Returns a list of all keys found.
    """
    ret = []
    # Combined pattern for active and commented keys: [# ] KEY = VALUE
    pattern = re.compile(r'^(?:#\s+)?([A-Z0-9_]+)\s*=')

    with open(CONF_TEMPLATE, 'r') as f:
        for line in f:
            line = line.strip()
            match = pattern.match(line)
            if match:
                ret.append(match.group(1))

    return ret


def augment_from_env(conf: dict):
    """
    Transfers from os.environ the values from read_config_keys if they are present.
    """
    keys = _read_config_keys()
    for key in keys:
        if key in os.environ:
            env_val = os.environ[key]
            try:
                conf[key] = eval(env_val)  # flask uses exec() for the whole file
            except:
                conf[key] = env_val


if __name__ == "__main__":
    # TODO: Transfer to UT
    # Test with the default config-model.cfg
    found_keys = _read_config_keys()
    print(f"Found {len(found_keys)} keys:")
    for k in sorted(found_keys):
        print(f"  {k}")

    print("\nTesting augment_from_env:")
    # Use a key that is actually in config-model.cfg (e.g. SECRET_KEY)
    test_conf = {"SECRET_KEY": "original"}
    os.environ["SECRET_KEY"] = "from_env"
    os.environ["SOME_OTHER_VAR"] = "should_not_be_added"
    augment_from_env(test_conf)
    print(f"Updated conf: {test_conf}")
    if test_conf.get("SECRET_KEY") == "from_env" and "SOME_OTHER_VAR" not in test_conf:
        print("augment_from_env check passed!")
    else:
        print("augment_from_env check failed!")
