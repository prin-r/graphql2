import argparse
import time
from app.db.db import Database
from app.looper import Looper


def main():
    parser = argparse.ArgumentParser(
        description="Start Band Protocol's pricer process",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("mode", type=str, help="Mode of script init or tick")
    parser.add_argument(
        "--dburi",
        type=str,
        default="postgres://localhost:5432",
        help="PostgreSQL connection URI",
    )
    parser.add_argument(
        "--dbname",
        type=str,
        help="PostreSQL database name, or random if not provided",
    )

    args = parser.parse_args()
    if args.mode == "INIT":
        db = Database(args.dburi, args.dbname, True)
        looper = Looper(db)
        looper.init()
    elif args.mode == "TICK":
        db = Database(args.dburi, args.dbname, False)
        looper = Looper(db)
        looper.run()
    elif args.mode == "LOOP":
        db = Database(args.dburi, args.dbname, True)
        looper = Looper(db)
        looper.loop()
    else:
        raise Exception("Command not found")


if __name__ == "__main__":
    main()
