from app.db import Proposal, ProposalVote, Token, Parameter
from app.utils.ipfs import get_json
from app.rpc import rpc

from decimal import Decimal


class ProposalSubscriber(object):
    @staticmethod
    def handle_proposal_proposed(
        session, block, event, proposal_id, proposer, reason_hash
    ):
        token = session.query(Parameter).get(event.address).token
        proposal = rpc.Parameters(event.address).proposals(proposal_id)
        session.add(
            Proposal(
                parameter_address=event.address,
                proposal_id=proposal_id,
                proposer=proposer,
                reason=get_json(reason_hash),
                reason_hash=reason_hash,
                changes={},
                token_snap_shot=proposal.snapshot_nonce,
                expiration_time=proposal.expiration_time,
                support_required=proposal.vote_support_required_pct,
                min_participation=proposal.vote_min_participation,
                total_voting_power=proposal.total_voting_power,
                current_yes_count=0,
                current_no_count=0,
                status="ACTIVE",
                timestamp=block.time,
                tx_hash=event.tx_hash,
            )
        )

    @staticmethod
    def handle_parameter_proposed(
        session, block, event, proposal_id, key, value
    ):
        proposal = session.query(Proposal).get((event.address, proposal_id))
        new_changes = dict(proposal.changes)
        new_changes[
            bytes.fromhex(key[2:]).decode("utf-8").replace("\x00", "")
        ] = str(value)
        proposal.changes = new_changes
        session.add(proposal)

    @staticmethod
    def handle_proposal_voted(
        session, block, event, proposal_id, voter, vote, voting_power
    ):
        proposal = session.query(Proposal).get((event.address, proposal_id))
        if vote:
            proposal.current_yes_count += Decimal(voting_power)
        else:
            proposal.current_no_count += Decimal(voting_power)

    @staticmethod
    def handle_proposal_accepted(session, block, event, proposal_id):
        proposal = session.query(Proposal).get((event.address, proposal_id))
        proposal.status = "APPROVED"
        session.add(proposal)

    @staticmethod
    def handle_proposal_rejected(session, block, event, proposal_id):
        proposal = session.query(Proposal).get((event.address, proposal_id))
        proposal.status = "REJECTED"
        session.add(proposal)

