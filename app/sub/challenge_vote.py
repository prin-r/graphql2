from app.db import Challenge, ChallengeVote

from decimal import Decimal


class ChallengeVoteSubscriber(object):
    @staticmethod
    def handle_challenge_vote_committed(
        session, block, event, challenge_id, voter, commit_value, weight
    ):
        challenge = session.query(Challenge).get((event.address, challenge_id))
        vote = session.query(ChallengeVote).get(
            (event.address, challenge_id, voter)
        )
        if vote is None:
            session.add(
                ChallengeVote(
                    tcr_address=event.address,
                    challenge_id=challenge_id,
                    voter=voter,
                    commit_hash=commit_value,
                    weight=weight,
                    commit_tx_hash=event.tx_hash,
                    commit_timestamp=block.time,
                )
            )
        else:
            challenge.current_participation -= vote.weight
            vote.commit_hash = commit_value
            vote.weight = weight
            vote.commit_tx_hash = event.tx_hash
            vote.commit_timestamp = block.time
            session.add(vote)

        challenge.current_participation += Decimal(weight)
        session.add(challenge)

    @staticmethod
    def handle_challenge_vote_revealed(
        session, block, event, challenge_id, voter, vote_keep
    ):
        challenge = session.query(Challenge).get((event.address, challenge_id))
        vote = session.query(ChallengeVote).get(
            (event.address, challenge_id, voter)
        )
        vote.vote_kept = vote_keep
        vote.reveal_tx_hash = event.tx_hash
        vote.reveal_timestamp = block.time
        if vote_keep:
            challenge.current_kept_count += vote.weight
        else:
            challenge.current_removed_count += vote.weight

        session.add(vote)
        session.add(challenge)

    @staticmethod
    def handle_challenge_reward_claimed(
        session, block, event, challenge_id, voter, reward
    ):
        vote = session.query(ChallengeVote).get(
            (event.address, challenge_id, voter)
        )
        vote.reward = reward
        vote.reward_tx_hash = event.tx_hash
        vote.reward_timestamp = block.time
        session.add(vote)
