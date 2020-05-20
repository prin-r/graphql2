import os
from app.db import Token, Curve, Parameter, Contract, TCR, TCD
from app.rpc import rpc
from app.utils.equation import get_children_count
from eth_utils import to_checksum_address

from sqlalchemy import func


class FactorySubscriber(object):
    @staticmethod
    def handle_community_created(
        session, block, event, token, bonding_curve, params
    ):
        name = rpc.ERC20Base(token).name().decode("utf-8")
        symbol = rpc.ERC20Base(token).symbol().decode("utf-8")
        decimals = rpc.ERC20Base(token).decimals()

        session.add(Contract(address=token, contract_type="TOKEN"))
        session.add(
            Token(
                address=token,
                total_supply=0,
                name=name,
                symbol=symbol,
                decimals=decimals,
            )
        )
        session.flush()
        expression = to_checksum_address(
            rpc.BondingCurve(bonding_curve).get_collateral_expression()
        )
        collateral_equation = []
        equation_index = 0
        more_node_count = 1

        while more_node_count != 0:
            more_node_count -= 1
            node_values = rpc.EquationExpression(expression).equation(
                equation_index
            )
            more_node_count += get_children_count(node_values[0])
            collateral_equation.append(str(node_values[0]))
            if node_values[0] == 0:
                collateral_equation.append(str(node_values[5]))

            equation_index += 1
        session.add(Contract(address=bonding_curve, contract_type="CURVE"))
        session.add(
            Curve(
                address=bonding_curve,
                token_address=token,
                price=0,
                collateral_equation=collateral_equation,
                curve_multiplier=10 ** 18,
            )
        )
        session.add(
            Parameter(
                address=params, token_address=token, current_parameters={}
            )
        )

        session.add(Contract(address=params, contract_type="PARAMETER"))

    @staticmethod
    def handle_tcr_created(session, block, event, tcr, creator):
        if os.getenv("BAND_ADDRESS") != to_checksum_address(creator):
            return
        token_address = to_checksum_address(rpc.QueryTCR(tcr).token())
        session.add(
            TCR(
                address=tcr,
                token_address=token_address,
                prefix=rpc.QueryTCR(tcr)
                .prefix()
                .decode("utf-8")
                .replace("\x00", ""),
            )
        )
        session.add(Contract(address=tcr, contract_type="TCR"))

    @staticmethod
    def handle_agg_tcd_created(session, block, event, atcd, creator):
        if os.getenv("BAND_ADDRESS") != to_checksum_address(creator):
            return
        token_address = to_checksum_address(rpc.AggTCD(atcd).token())
        token = session.query(Token).get(token_address)
        current_parameters = token.parameter.current_parameters
        prefix = rpc.TCDBase(atcd).prefix().decode("utf-8").replace("\x00", "")
        print(prefix, len(prefix), flush=True)
        session.add(
            TCD(
                address=atcd,
                token_address=token_address,
                prefix=prefix,
                min_stake=current_parameters[f"{prefix}min_provider_stake"],
                max_provider_count=current_parameters[
                    f"{prefix}max_provider_count"
                ],
            )
        )
        session.add(Contract(address=atcd, contract_type="AGG_TCD"))

    @staticmethod
    def handle_multi_sig_tcd_created(session, block, event, mtcd, creator):
        if os.getenv("BAND_ADDRESS") != to_checksum_address(creator):
            return
        token_address = to_checksum_address(rpc.MultiSigTCD(mtcd).token())
        token = session.query(Token).get(token_address)
        current_parameters = token.parameter.current_parameters
        prefix = rpc.TCDBase(mtcd).prefix().decode("utf-8").replace("\x00", "")
        print(prefix, len(prefix), flush=True)
        session.add(
            TCD(
                address=mtcd,
                token_address=token_address,
                prefix=prefix,
                min_stake=current_parameters[f"{prefix}min_provider_stake"],
                max_provider_count=current_parameters[
                    f"{prefix}max_provider_count"
                ],
            )
        )
        session.add(Contract(address=mtcd, contract_type="MULTISIG_TCD"))

    @staticmethod
    def handle_offchain_agg_tcd_created(session, block, event, mtcd, creator):
        if os.getenv("BAND_ADDRESS") != to_checksum_address(creator):
            return
        token_address = to_checksum_address(rpc.OffchainAggTCD(mtcd).token())
        token = session.query(Token).get(token_address)
        current_parameters = token.parameter.current_parameters
        prefix = rpc.TCDBase(mtcd).prefix().decode("utf-8").replace("\x00", "")
        print(prefix, len(prefix), flush=True)
        session.add(
            TCD(
                address=mtcd,
                token_address=token_address,
                prefix=prefix,
                min_stake=current_parameters[f"{prefix}min_provider_stake"],
                max_provider_count=current_parameters[
                    f"{prefix}max_provider_count"
                ],
            )
        )
        session.add(Contract(address=mtcd, contract_type="OFFCHAIN_AGG_TCD"))
