from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Numeric,
    Boolean,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship, configure_mappers
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True)
    block_height = Column(Integer, ForeignKey("block.height"), nullable=False)
    table_name = Column(String, nullable=False)
    previous_value = Column(JSON)
    next_value = Column(JSON, nullable=False)


class Block(Base):
    __tablename__ = "block"
    height = Column(Integer, primary_key=True)
    hash = Column(String, unique=True, nullable=False)
    parent_hash = Column(String, unique=True, nullable=False)
    block_time = Column(Integer, nullable=False)


class Contract(Base):
    __tablename__ = "contract"
    address = Column(String, primary_key=True)
    contract_type = Column(String, nullable=False)


class BandCommunity(Base):
    __tablename__ = "band_community"
    token_address = Column(String, ForeignKey("token.address"), primary_key=True)
    name = Column(String, nullable=False)
    logo = Column(String)
    banner = Column(String)
    description = Column(String)
    website = Column(String)
    organization = Column(String)
    token = relationship("Token", uselist=False, back_populates="community")



class Token(Base):
    __tablename__ = "token"
    address = Column(String, primary_key=True, nullable=False)
    total_supply = Column(Numeric, nullable=False)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    decimals = Column(Integer, nullable=False)
    community = relationship("BandCommunity", back_populates="token")
    curve = relationship("Curve", uselist=False, back_populates="token")
    parameter = relationship(
        "Parameter", uselist=False, back_populates="token"
    )
    tcrs = relationship("TCR", back_populates="token")
    tcds = relationship("TCD", back_populates="token")


class Balance(Base):
    __tablename__ = "balance"
    token_address = Column(
        String, ForeignKey("token.address"), nullable=False, primary_key=True
    )
    user = Column(String, nullable=False, primary_key=True)
    value = Column(Numeric, nullable=False)
    locked_value = Column(Numeric, nullable=False)


class TokenLocked(Base):
    __tablename__ = "token_locked"
    token_address = Column(
        String, ForeignKey("token.address"), nullable=False, primary_key=True
    )
    locker = Column(String, nullable=False, primary_key=True)
    user = Column(String, nullable=False, primary_key=True)
    value = Column(Numeric, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["token_address", "user"],
            ["balance.token_address", "balance.user"],
            name="fk_balance",
        ),
    )


class Curve(Base):
    __tablename__ = "curve"
    address = Column(String, primary_key=True, nullable=False)
    token_address = Column(
        String, ForeignKey("token.address"), unique=True, nullable=False
    )
    price = Column(Numeric, nullable=False)
    collateral_equation = Column(JSON, nullable=False)
    curve_multiplier = Column(Numeric, nullable=False)
    token = relationship("Token", back_populates="curve")


class Price(Base):
    __tablename__ = "price"
    curve_address = Column(
        String, ForeignKey("curve.address"), primary_key=True, nullable=False
    )
    price = Column(Numeric, nullable=False)
    total_supply = Column(Numeric, nullable=False)
    timestamp = Column(Integer, primary_key=True, nullable=False)


class Order(Base):
    __tablename__ = "order"
    curve_address = Column(
        String, ForeignKey("curve.address"), primary_key=True, nullable=False
    )
    block_height = Column(Integer, primary_key=True, nullable=False)
    log_index = Column(Integer, primary_key=True, nullable=False)
    order_type = Column(String, nullable=False)
    user = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    timestamp = Column(Integer, nullable=False)
    tx_hash = Column(String, nullable=False)


class Transfer(Base):
    __tablename__ = "transfer"
    token_address = Column(
        String, ForeignKey("token.address"), primary_key=True, nullable=False
    )
    block_height = Column(Integer, primary_key=True, nullable=False)
    log_index = Column(Integer, primary_key=True, nullable=False)
    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    value = Column(Numeric, nullable=False)
    timestamp = Column(Integer, nullable=False)
    tx_hash = Column(String, nullable=False)


class Parameter(Base):
    __tablename__ = "parameter"
    address = Column(String, primary_key=True)
    token_address = Column(
        String, ForeignKey("token.address"), unique=True, nullable=False
    )
    current_parameters = Column(JSON, nullable=False)
    token = relationship("Token", back_populates="parameter")


class Proposal(Base):
    __tablename__ = "proposal"
    parameter_address = Column(
        String,
        ForeignKey("parameter.address"),
        primary_key=True,
        nullable=False,
    )
    # proposal part
    proposal_id = Column(Integer, primary_key=True, nullable=False)
    proposer = Column(String, nullable=False)
    changes = Column(JSON, nullable=False)
    reason = Column(JSON)
    reason_hash = Column(String, nullable=False)
    token_snap_shot = Column(Integer, nullable=False)
    total_voting_power = Column(Numeric, nullable=False)
    expiration_time = Column(Integer, nullable=False)
    min_participation = Column(Numeric, nullable=False)
    support_required = Column(Numeric, nullable=False)
    current_yes_count = Column(Numeric, nullable=False)
    current_no_count = Column(Numeric, nullable=False)

    tx_hash = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    status = Column(String, nullable=False)


class ProposalVote(Base):
    __tablename__ = "proposal_vote"
    parameter_address = Column(String, primary_key=True, nullable=False)
    proposal_id = Column(Integer, primary_key=True, nullable=False)
    voter = Column(String, primary_key=True, nullable=False)
    accepted = Column(Boolean, nullable=False)
    tx_hash = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["parameter_address", "proposal_id"],
            ["proposal.parameter_address", "proposal.proposal_id"],
            name="fk_proposal",
        ),
    )


class TCR(Base):
    __tablename__ = "tcr"
    address = Column(String, primary_key=True, nullable=False)
    token_address = Column(String, ForeignKey("token.address"), nullable=False)
    prefix = Column(String, nullable=False)
    token = relationship("Token", back_populates="tcrs")


class Entry(Base):
    __tablename__ = "entry"
    tcr_address = Column(
        String, ForeignKey("tcr.address"), primary_key=True, nullable=False
    )
    entry_hash = Column(String, primary_key=True, nullable=False)
    event_count = Column(Integer, nullable=False)
    entry = Column(JSON)
    proposer = Column(String, nullable=False)
    deposit = Column(Numeric, nullable=False)
    list_at = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    tx_hash = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)


class EntryHistory(Base):
    __tablename__ = "entry_history"
    tcr_address = Column(String, ForeignKey("tcr.address"), nullable=False)
    entry_hash = Column(String, primary_key=True)
    sequence_number = Column(Integer, primary_key=True)
    action_type = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    deposit_changed = Column(Numeric, nullable=False)
    tx_hash = Column(String)
    timestamp = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tcr_address", "entry_hash"],
            ["entry.tcr_address", "entry.entry_hash"],
            name="fk_entry",
        ),
    )


class Challenge(Base):
    __tablename__ = "challenge"
    tcr_address = Column(
        String, ForeignKey("tcr.address"), primary_key=True, nullable=False
    )

    # challenge part
    challenge_id = Column(Integer, primary_key=True, nullable=False)
    entry_hash = Column(String, nullable=False)
    challenger = Column(String, nullable=False)
    reason = Column(JSON)
    reason_hash = Column(String, nullable=False)
    stake = Column(Numeric, nullable=False)
    token_snap_shot = Column(Integer, nullable=False)
    total_voting_power = Column(Numeric, nullable=False)
    commit_end_time = Column(Integer, nullable=False)
    reveal_end_time = Column(Integer, nullable=False)
    min_participation = Column(Numeric, nullable=False)
    remove_vote_required = Column(Numeric, nullable=False)
    current_participation = Column(Numeric, nullable=False)
    current_removed_count = Column(Numeric, nullable=False)
    current_kept_count = Column(Numeric, nullable=False)
    voter_reward_pool = Column(Numeric)
    leader_reward = Column(Numeric)
    tx_hash = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    result = Column(String, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tcr_address", "entry_hash"],
            ["entry.tcr_address", "entry.entry_hash"],
            name="fk_entry",
        ),
    )


class ChallengeVote(Base):
    __tablename__ = "challenge_vote"
    tcr_address = Column(String, primary_key=True, nullable=False)
    challenge_id = Column(Integer, primary_key=True, nullable=False)
    voter = Column(String, primary_key=True, nullable=False)
    commit_hash = Column(String, nullable=False)
    weight = Column(Numeric, nullable=False)
    vote_kept = Column(Boolean)
    reward = Column(Numeric)

    commit_tx_hash = Column(String, nullable=False)
    commit_timestamp = Column(Integer, nullable=False)

    reveal_tx_hash = Column(String)
    reveal_timestamp = Column(Integer)

    reward_tx_hash = Column(String)
    reward_timestamp = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ["tcr_address", "challenge_id"],
            ["challenge.tcr_address", "challenge.challenge_id"],
            name="fk_challenge",
        ),
    )


class TCD(Base):
    __tablename__ = "tcd"
    address = Column(String, primary_key=True, nullable=False)
    token_address = Column(String, ForeignKey("token.address"), nullable=False)
    prefix = Column(String, nullable=False)
    max_provider_count = Column(Integer)
    min_stake = Column(Numeric)
    token = relationship("Token", back_populates="tcds")
    data_sources = relationship("DataProvider", back_populates="tcd")


class DataProvider(Base):
    __tablename__ = "data_provider"
    data_source_address = Column(String, primary_key=True)
    tcd_address = Column(String, ForeignKey("tcd.address"), primary_key=True)
    owner = Column(String, nullable=False)
    stake = Column(Numeric, nullable=False)
    total_ownership = Column(Numeric, nullable=False)
    detail = Column(String)
    status = Column(String, nullable=False)
    endpoint = Column(String)
    tcd = relationship("TCD", back_populates="data_sources")


class DataProviderOwnership(Base):
    __tablename__ = "data_provider_ownership"
    data_source_address = Column(String, primary_key=True)
    tcd_address = Column(String, primary_key=True)
    voter = Column(String, primary_key=True)
    ownership = Column(Numeric, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["data_source_address", "tcd_address"],
            ["data_provider.data_source_address", "data_provider.tcd_address"],
            name="fk_datasource",
        ),
    )


class DataSourceBookkeeping(Base):
    __tablename__ = "data_source_book_keeping"
    address = Column(String, primary_key=True)
    name = Column(
        # PRICE / SPORT / LOTTERY
        String,
        nullable=False,
    )

class DataRead(Base):
    __tablename__ = "data_read"

    reader_address = Column(String, primary_key=True, nullable=False)
    key = Column(String, primary_key=True, nullable=False)
    timestamp = Column(Integer, primary_key=True)
    log_index = Column(Integer, primary_key=True)

    tcd_address = Column(
        String,
        ForeignKey("tcd.address"),
        primary_key=True,
        nullable=False,
    )


class DataPriceFeed(Base):
    __tablename__ = "data_price_feed"

    pair = Column(String, primary_key=True, nullable=False)

    tcd_address = Column(
        String, ForeignKey("tcd.address"), nullable=False
    )

    value = Column(Numeric, nullable=True)

    last_update = Column(Integer, nullable=False)


class DataPriceFeedRaw(Base):
    __tablename__ = "data_price_feed_raw"

    data_source_address = Column(String, primary_key=True)
    tcd_address = Column(String, primary_key=True)
    timestamp = Column(Integer, primary_key=True)
    pair = Column(
        String, ForeignKey("data_price_feed.pair"), primary_key=True, nullable=False
    )

    value = Column(Numeric, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["data_source_address", "tcd_address"],
            ["data_provider.data_source_address", "data_provider.tcd_address"],
            name="fk_datasource",
        ),
    )


class DataLotteryFeed(Base):
    __tablename__ = "data_lottery_feed"

    lottery_type = Column(String, primary_key=True, nullable=False)
    lottery_time = Column(String, primary_key=True, nullable=False)

    tcd_address = Column(
        String, ForeignKey("tcd.address"), nullable=False
    )

    white_ball_1 = Column(Integer, nullable=True)
    white_ball_2 = Column(Integer, nullable=True)
    white_ball_3 = Column(Integer, nullable=True)
    white_ball_4 = Column(Integer, nullable=True)
    white_ball_5 = Column(Integer, nullable=True)
    red_ball = Column(Integer, nullable=True)
    mul = Column(Integer, nullable=True)

    last_update = Column(Integer, nullable=False)


class DataLotteryFeedRaw(Base):
    __tablename__ = "data_lottery_feed_raw"

    data_source_address = Column(String, primary_key=True)
    tcd_address = Column(String, primary_key=True)
    timestamp = Column(Integer, primary_key=True)
    lottery_type = Column(String, primary_key=True)
    lottery_time = Column(String, primary_key=True)

    white_ball_1 = Column(Integer, nullable=False)
    white_ball_2 = Column(Integer, nullable=False)
    white_ball_3 = Column(Integer, nullable=False)
    white_ball_4 = Column(Integer, nullable=False)
    white_ball_5 = Column(Integer, nullable=False)
    red_ball = Column(Integer, nullable=False)
    mul = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["data_source_address", "tcd_address"],
            ["data_provider.data_source_address", "data_provider.tcd_address"],
            name="fk_datasource",
        ),
        ForeignKeyConstraint(
            ["lottery_type", "lottery_time"],
            [
                "data_lottery_feed.lottery_type",
                "data_lottery_feed.lottery_time",
            ],
            name="fk_lottery_feed",
        ),
    )


class DataSportFeed(Base):
    __tablename__ = "data_sport_feed"

    sport_type = Column(String, primary_key=True, nullable=False)
    sport_time = Column(String, primary_key=True, nullable=False)
    sport_start_time = Column(String, primary_key=True, nullable=False)
    year = Column(String, primary_key=True, nullable=False)
    home = Column(String, primary_key=True, nullable=False)
    away = Column(String, primary_key=True, nullable=False)

    tcd_address = Column(
        String, ForeignKey("tcd.address"), nullable=False
    )

    score_home = Column(Integer, nullable=True)
    score_away = Column(Integer, nullable=True)

    last_update = Column(Integer, nullable=False)


class DataSportFeedRaw(Base):
    __tablename__ = "data_sport_feed_raw"

    data_source_address = Column(String, primary_key=True)
    tcd_address = Column(String, primary_key=True)
    timestamp = Column(Integer, primary_key=True)
    sport_type = Column(String, primary_key=True)
    sport_time = Column(String, primary_key=True)
    sport_start_time = Column(String, primary_key=True)
    year = Column(String, primary_key=True)
    home = Column(String, primary_key=True)
    away = Column(String, primary_key=True)

    score_home = Column(Integer, nullable=False)
    score_away = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["data_source_address", "tcd_address"],
            ["data_provider.data_source_address", "data_provider.tcd_address"],
            name="fk_datasource",
        ),
        ForeignKeyConstraint(
            ["sport_type", "sport_time", "sport_start_time", "year", "home", "away"],
            [
                "data_sport_feed.sport_type",
                "data_sport_feed.sport_time",
                "data_sport_feed.sport_start_time",
                "data_sport_feed.year",
                "data_sport_feed.home",
                "data_sport_feed.away",
            ],
            name="fk_sport_feed",
        ),
    )

