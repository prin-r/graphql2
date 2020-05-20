#!/bin/bash

source venv/bin/activate
find abis/ -name "*.json" -type f -delete
python abi.py
docker container rm graphql2
docker create --name graphql2 --net band-event-core_app_net -v $(pwd):/app band_subscriber-dev
docker start graphql2

sleep 15
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "insert into band_community(token_address, name) select address, name from token where name='CoinHatcher';"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "insert into band_community(token_address, name) select address, name from token where name='Financial Data Feeds';"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
"insert into band_community(token_address, name) select address, name from token where name='Lottery Data Feeds';"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "insert into band_community(token_address, name) select address, name from token where name='Sport Data Feeds';"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "insert into band_community(token_address, name) select address, name from token where name='Web Request Oracle';"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "update band_community set \
    logo='QmZfA5NvuSGi7oFSZFfVkJJniHuezS18JhZ1cnL2UZKxCG', \
    banner='QmWSyKeafT5x43F2jMeJeUFzLmWJLzQkKYzF32NbV6C3RX', \
    description='The Bloomberg of Crypto. Coinhatcher is a \
    decentralized data curation with a mission to provide trusted and reliable information in blockchain industry. \
    Ranging from daily news to founder’s directory and crypto economics, Coinhatcher has you covered! Tokens are given \
    as reward and are used to curate reliable information through TCR mechanism.', \
    website='https://coinhatcher.com', \
    organization='Band Protocol' \
    where name='CoinHatcher'"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "update band_community set \
    logo='QmSGqpUvEth6CqaN9KgsDjn3vVagjvrJyb34UaU1gv2gDo', \
    banner='QmUN4k5RUPWFVVphcakkvzmm4jqtgWrSWUgCMc3nPQhQfp', \
    description='Get current prices of any trading currency pairs.', \
    website='https://data.bandprotocol.com/dataset/price', \
    organization='Band Protocol' \
    where name='Financial Data Feeds'"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "update band_community set \
    logo='QmagTE4zEJ2xim8Ji2kXcgCJUwRnzxef3Bsu9KXw8yvjUv', \
    banner='Qmd1aoCaY93UdA8RqzxVmusq4midYp3KSbZxtE2yQwVCKX', \
    description='Accurate live scores from soccer, basketball, American football and baseball.', \
    website='https://data.bandprotocol.com/dataset/sport', \
    organization='Band Protocol' \
    where name='Sport Data Feeds'"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "update band_community set \
    logo='QmYsuRV8ECszj8oAEZJ7Ap3qPKusdK6DeHDzvSryLczFU1', \
    banner='QmaPDwCxEGPdVA2Y8encd1RHXj97yA7SdDP5qe2E5Covjt', \
    description='Get winning numbers of lotteries all around the world.', \
    website='https://data.bandprotocol.com/dataset/lottery', \
    organization='Band Protocol' \
    where name='Lottery Data Feeds'"
PGPASSWORD=1234 psql -h localhost -p 5433 -U postgres -d graph_test -c \
    "update band_community set \
    logo='QmYsuRV8ECszj8oAEZJ7Ap3qPKusdK6DeHDzvSryLczFU1', \
    banner='QmQQLZr8GR1CYjKnd22ScPbE9pG6z5nZ8mXxnbJy8hEmLN', \
    description='Bring outside api to blockchain world', \
    website='https://data.bandprotocol.com/dataset/lottery', \
    organization='Band Protocol' \
    where name='Web Request Oracle'"
