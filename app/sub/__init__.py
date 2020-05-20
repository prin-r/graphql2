from app.sub.balance import BalanceSubscriber
from app.sub.challenge import ChallengeSubscriber
from app.sub.challenge_vote import ChallengeVoteSubscriber
from app.sub.curve import CurveSubscriber
from app.sub.tcd import TCDSubscriber
from app.sub.entry import EntrySubscriber
from app.sub.factory import FactorySubscriber
from app.sub.order import OrderSubscriber
from app.sub.parameter import ParameterSubscriber
from app.sub.price import PriceSubscriber
from app.sub.proposal import ProposalSubscriber
from app.sub.proposal_vote import ProposalVoteSubscriber
from app.sub.token import TokenSubscriber
from app.sub.transfer import TransferSubscriber
from app.sub.data.data_price_feed_raw import DataPriceFeedRawSubscriber
from app.sub.data.data_lottery_feed_raw import DataLotteryFeedRawSubscriber
from app.sub.data.data_sport_feed_raw import DataSportFeedRawSubscriber
from app.sub.data.data_read import DataReadSubscriber
from app.sub.lock_token import TokenLockedSubscriber

ALL_SUBSRIBERS = [
    ###
    FactorySubscriber,
    TokenSubscriber,
    CurveSubscriber,
    TransferSubscriber,
    BalanceSubscriber,
    PriceSubscriber,
    OrderSubscriber,
    ParameterSubscriber,
    ProposalSubscriber,
    ProposalVoteSubscriber,
    EntrySubscriber,
    ChallengeSubscriber,
    ChallengeVoteSubscriber,
    TCDSubscriber,
    DataPriceFeedRawSubscriber,
    DataLotteryFeedRawSubscriber,
    DataSportFeedRawSubscriber,
    DataReadSubscriber,
    TokenLockedSubscriber,
]

