import os
import json
from shutil import copyfile

copyfile("../contracts/config.txt", "config.txt")

config = {}
with open("config.txt", "r") as f:
    with open("./config/config.json", "w") as w:
        for line in f:
            if line[0] != "-":
                [name, value] = line.split(":")
                try:
                    config[name.replace('"', "")] = json.loads(value.strip())
                except:
                    config[name.replace('"', "")] = value.strip()
        if "network" in config and config["network"] != "development":
            config["eventDBHost"] = (
                "postgres://root:coinroot1@pricer.cvdthaqocohn.us-east-1.rds.amazonaws.com/"
                + config["network"]
                + "_events"
            )
        else:
            config[
                "eventDBHost"
            ] = "postgresql://postgres:1234@172.18.0.6:5432/events"
        print(config)
        json.dump(config, w, indent=2)

abi_list = []
for filename in os.listdir("../contracts/build/contracts"):
    with open(
        os.path.join("../contracts/build/contracts/", filename), "r"
    ) as r_file:
        contract = json.load(r_file)
        abi_list.append(filename)
        with open(os.path.join("./abis/", filename), "w") as w_file:
            json.dump(contract["abi"], w_file, indent=2)

json.dump(abi_list, open("./config/abi_list.json", "w"), indent=2)

