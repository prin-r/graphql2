from app.db import Entry, EntryHistory, Challenge
from app.utils.ipfs import get_json

from datetime import datetime


class EntrySubscriber(object):
    @staticmethod
    def handle_begin_block(session, block):
        entries = session.query(Entry).all()

        for entry in entries:
            if entry.status == "APPLIED" and entry.list_at <= block.time:
                entry.status = "LISTED"
                event_count = entry.event_count
                entry.event_count = event_count + 1
                session.add(entry)
                session.add(
                    EntryHistory(
                        tcr_address=entry.tcr_address,
                        sequence_number=event_count + 1,
                        entry_hash=entry.entry_hash,
                        action_type="LISTED",
                        actor=entry.proposer,
                        deposit_changed=0,
                        timestamp=block.time,
                    )
                )

    @staticmethod
    def handle_application_submitted(
        session, block, event, data, proposer, list_at, deposit
    ):
        entry = session.query(Entry).get((event.address, data))
        sequence_number = 0
        if entry is None:
            session.add(
                Entry(
                    tcr_address=event.address,
                    event_count=0,
                    entry_hash=data,
                    entry=get_json(data),
                    proposer=proposer,
                    deposit=deposit,
                    list_at=list_at,
                    status="APPLIED",
                    tx_hash=event.tx_hash,
                    timestamp=block.time,
                )
            )
        else:
            sequence_number = entry.event_count + 1
            entry.event_count = sequence_number
            entry.proposer = proposer
            entry.deposit = deposit
            entry.list_at = list_at
            entry.status = "APPLIED"
            entry.tx_hash = event.tx_hash
            entry.timestamp = block.time
            session.add(entry)
        session.flush()

        # Add to entry history
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=sequence_number,
                action_type="SUBMITTED",
                actor=proposer,
                deposit_changed=deposit,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

    @staticmethod
    def handle_entry_deposited(session, block, event, data, value):
        entry = session.query(Entry).get((event.address, data))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="DEPOSITED",
                actor=entry.proposer,
                deposit_changed=value,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

        entry.deposit += value
        entry.event_count += 1
        session.add(entry)

    @staticmethod
    def handle_entry_withdrawn(session, block, event, data, value):
        entry = session.query(Entry).get((event.address, data))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="WITHDRAWN",
                actor=entry.proposer,
                deposit_changed=-value,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

        entry.deposit -= value
        entry.event_count += 1
        session.add(entry)

    @staticmethod
    def handle_entry_exited(session, block, event, data):
        entry = session.query(Entry).get((event.address, data))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="EXITED",
                actor=entry.proposer,
                deposit_changed=-entry.deposit,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

        entry.status = "EXITED"
        entry.deposit = 0
        entry.event_count += 1
        session.add(entry)

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
        entry = session.query(Entry).get((event.address, data))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="CHALLENGED",
                actor=challenger,
                deposit_changed=0,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

        entry.status = "CHALLENGED"
        entry.event_count += 1
        session.add(entry)

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
        entry = session.query(Entry).get((event.address, data))
        challenge = session.query(Challenge).get((event.address, challenge_id))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="REJECTED",
                actor=challenge.challenger,
                deposit_changed=-entry.deposit,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )

        entry.status = "REJECTED"
        entry.deposit = 0
        entry.event_count += 1
        session.add(entry)

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
        entry = session.query(Entry).get((event.address, data))
        challenge = session.query(Challenge).get((event.address, challenge_id))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="KEPT",
                actor=challenge.challenger,
                deposit_changed=proposer_reward,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )
        if entry.list_at <= block.time:
            entry.status = "LISTED"
            session.add(
                EntryHistory(
                    tcr_address=entry.tcr_address,
                    sequence_number=entry.event_count + 2,
                    entry_hash=entry.entry_hash,
                    action_type="LISTED",
                    actor=entry.proposer,
                    deposit_changed=0,
                    timestamp=block.time,
                )
            )
            entry.event_count += 2
        else:
            entry.status = "APPLIED"
            entry.event_count += 1
        entry.deposit += proposer_reward
        session.add(entry)

    @staticmethod
    def handle_challenge_inconclusive(
        session, block, event, data, challenge_id
    ):
        entry = session.query(Entry).get((event.address, data))
        challenge = session.query(Challenge).get((event.address, challenge_id))
        session.add(
            EntryHistory(
                tcr_address=event.address,
                entry_hash=data,
                sequence_number=entry.event_count + 1,
                action_type="KEPT",
                actor=challenge.challenger,
                deposit_changed=0,
                tx_hash=event.tx_hash,
                timestamp=block.time,
            )
        )
        if entry.list_at <= block.time:
            entry.status = "LISTED"
            session.add(
                EntryHistory(
                    tcr_address=entry.tcr_address,
                    sequence_number=entry.event_count + 2,
                    entry_hash=entry.entry_hash,
                    action_type="LISTED",
                    actor=entry.proposer,
                    deposit_changed=0,
                    timestamp=block.time,
                )
            )
            entry.event_count += 2
        else:
            entry.status = "APPLIED"
            entry.event_count += 1
        session.add(entry)

