from app.db import Reward, RewardClaim
from app.rpc import rpc


class RewardSubscriber(object):
    @staticmethod
    def handle_reward_distribution_submitted(
        session,
        block,
        event,
        reward_id,
        submitter,
        total_reward,
        total_portion,
        reward_portion_root_hash,
    ):
        session.add(
            Reward(
                token_address=rpc.RewardDistributor(event.address).token(),
                reward_id=reward_id,
                submitter=submitter,
                total_reward=total_reward,
                total_portion=total_portion,
                root_hash=reward_portion_root_hash,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

    @staticmethod
    def handle_reward_claimed(
        session, block, event, reward_id, member, reward_portion, amount
    ):
        session.add(
            RewardClaim(
                token_address=rpc.RewardDistributor(event.address).token(),
                reward_id=reward_id,
                member=member,
                reward_portion=reward_portion,
                amount=amount,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )
