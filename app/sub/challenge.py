from app.db import Challenge, TCR
from app.utils.ipfs import get_json

from app.rpc import rpc


class ChallengeSubscriber(object):
    @staticmethod
    def handle_challenge_initiated(
        session,
        block,
        event,
        data,
        challenge_id,
        challenger,
        stake,
        reason_data,
        proposer_vote,
        challenger_vote,
    ):
        token = session.query(TCR).get(event.address).token
        challenge = rpc.TCRBase(event.address).challenges(challenge_id)
        session.add(
            Challenge(
                tcr_address=event.address,
                challenge_id=challenge_id,
                entry_hash=data,
                challenger=challenger,
                reason=get_json(reason_data),
                reason_hash=reason_data,
                stake=stake,
                token_snap_shot=challenge.snapshot_nonce,
                total_voting_power=token.total_supply,
                commit_end_time=challenge.commit_end_time,
                reveal_end_time=challenge.reveal_end_time,
                min_participation=challenge.vote_min_participation,
                remove_vote_required=challenge.vote_remove_required_pct,
                current_participation=proposer_vote + challenger_vote,
                current_removed_count=challenger_vote,
                current_kept_count=proposer_vote,
                result="INIT",
                timestamp=block.time,
                tx_hash=event.tx_hash,
            )
        )

    @staticmethod
    def handle_challenge_success(
        session,
        block,
        event,
        data,
        challenge_id,
        voter_reward_pool,
        challenger_reward,
    ):
        challenge = session.query(Challenge).get((event.address, challenge_id))
        challenge.voter_reward_pool = voter_reward_pool
        challenge.leader_reward = challenger_reward
        challenge.result = "SUCCESS"
        session.add(challenge)

    @staticmethod
    def handle_challenge_failed(
        session,
        block,
        event,
        data,
        challenge_id,
        voter_reward_pool,
        proposer_reward,
    ):
        challenge = session.query(Challenge).get((event.address, challenge_id))
        challenge.voter_reward_pool = voter_reward_pool
        challenge.leader_reward = proposer_reward
        challenge.result = "FAILED"
        session.add(challenge)

    @staticmethod
    def handle_challenge_inconclusive(
        session, block, event, data, challenge_id
    ):
        challenge = session.query(Challenge).get((event.address, challenge_id))
        challenge.result = "INCONCLUSIVE"
        session.add(challenge)
