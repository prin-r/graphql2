from app.db import TCD, DataProvider, DataProviderOwnership, Contract
from app.utils.check_provider import next_address_list
from app.rpc import rpc
from eth_utils import to_checksum_address
from eth_abi.exceptions import InsufficientDataBytes


def update_list(session, block, tcd_address):
    NOT_AVAILABLE = "0x0"
    tcd = session.query(TCD).get(tcd_address)

    all_data_source = tcd.data_sources

    for ds in all_data_source:
        ds.status = "DISABLED"
        if (
            next_address_list(
                tcd_address, True, ds.data_source_address, block.height
            )
            != NOT_AVAILABLE
        ):
            ds.status = "ACTIVE"
        elif (
            next_address_list(
                tcd_address, False, ds.data_source_address, block.height
            )
            != NOT_AVAILABLE
        ):
            ds.status = "RESERVED"


def update_provider(
    session, current_height, tcd_address, data_source, participant
):
    data_provider = session.query(DataProvider).get((data_source, tcd_address))

    voter_ownership = session.query(DataProviderOwnership).get(
        (data_source, tcd_address, participant)
    )

    data_source_info = rpc.TCDBase(tcd_address, current_height).info_map(
        data_source
    )

    data_provider.stake = data_source_info.stake
    data_provider.total_ownership = data_source_info.total_ownerships
    session.add(data_provider)

    new_voter_ownership = rpc.TCDBase(
        tcd_address, current_height
    ).get_ownership(data_source, participant)

    if voter_ownership is None:
        session.add(
            DataProviderOwnership(
                data_source_address=data_source,
                tcd_address=tcd_address,
                voter=participant,
                ownership=new_voter_ownership,
            )
        )
    else:
        if new_voter_ownership == 0:
            session.delete(voter_ownership)
        else:
            voter_ownership.ownership = new_voter_ownership
            session.add(voter_ownership)


class TCDSubscriber(object):
    @staticmethod
    def handle_data_source_registered(
        session, block, event, data_source, owner, stake
    ):
        try:
            detail = (
                rpc.MockDataSource(data_source)
                .detail()
                .decode("utf-8")
                .rstrip("\0")
            )
        except InsufficientDataBytes:
            detail = ""

        session.add(
            DataProvider(
                data_source_address=data_source,
                tcd_address=event.address,
                owner=owner,
                stake=stake,
                total_ownership=stake,
                detail=detail,
                status="UNLISTED",
            )
        )
        session.flush()
        session.add(
            DataProviderOwnership(
                data_source_address=data_source,
                tcd_address=event.address,
                voter=owner,
                ownership=stake,
            )
        )

        data_source_contract = (
            session.query(Contract).filter_by(address=data_source).first()
        )
        if data_source_contract is None:
            session.add(
                Contract(address=data_source, contract_type="DATA_SOURCE")
            )
        update_list(session, block, event.address)

    @staticmethod
    def handle_data_source_staked(
        session, block, event, data_source, participant, stake
    ):
        update_provider(
            session, block.height, event.address, data_source, participant
        )
        update_list(session, block, event.address)

    @staticmethod
    def handle_data_source_unstaked(
        session, block, event, data_source, participant, unstake
    ):
        update_provider(
            session, block.height, event.address, data_source, participant
        )
        update_list(session, block, event.address)

    @staticmethod
    def handle_fee_distributed(
        session, block, event, data_source, total_reward, owner_reward
    ):
        data_provider = session.query(DataProvider).get(
            (data_source, event.address)
        )

        update_provider(
            session,
            block.height,
            event.address,
            data_source,
            data_provider.owner,
        )
