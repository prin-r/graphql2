from app.db import ProposalVote


class ProposalVoteSubscriber(object):
    @staticmethod
    def handle_proposal_voted(
        session, block, event, proposal_id, voter, vote, voting_power
    ):
        session.add(
            ProposalVote(
                parameter_address=event.address,
                proposal_id=proposal_id,
                voter=voter,
                accepted=vote,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )
