from sqlalchemy import event, func
from sqlalchemy.orm import attributes, object_mapper
from sqlalchemy.orm.properties import RelationshipProperty

from app.db import Base, Block, History, Transfer


REVERTING = False


def get_table(fullname):
    for table in Base._decl_class_registry.values():
        if hasattr(table, "__table__") and table.__table__.fullname == fullname:
            return table


def revert(session):
    global REVERTING
    REVERTING = True
    session.rollback()

    block_height = session.query(func.max(Block.height)).scalar()
    block = session.query(Block).get(block_height)

    for history in (
        session.query(History)
        .filter_by(block_height=block_height)
        .order_by(History.id.desc())
        .all()
    ):
        table = get_table(history.table_name)

        if history.next_value is None:
            obj = table()
            session.add(obj)
        else:
            history_keys = {
                k: v
                for k, v in history.next_value.items()
                if not isinstance(v, (list, dict))
            }
            obj = session.query(table).filter_by(**history_keys).one()

        if history.previous_value is None:
            session.delete(obj)
        else:
            for key, value in history.previous_value.items():
                setattr(obj, key, value)

        session.delete(history)
        session.flush()

    session.delete(block)
    session.commit()
    REVERTING = False


def process_version(session, obj, new, deleted):
    if REVERTING or isinstance(obj, (History, Block)):
        return
    obj_mapper = object_mapper(obj)

    history = History()
    history.block_height = session.query(func.max(Block.height)).scalar()
    history.table_name = obj.__table__.fullname
    history.next_value = None if deleted else {}
    history.previous_value = None if new else {}

    for prop in obj_mapper.iterate_properties:
        if isinstance(prop, RelationshipProperty):
            continue

        key = prop.key
        hs = attributes.get_history(obj, key)
        old_value = hs.non_added()
        new_value = hs.non_deleted()
        if not new:
            history.previous_value[key] = None if old_value == [] else old_value[0]
        if not deleted:
            history.next_value[key] = None if new_value == [] else new_value[0]

    session.add(history)


def versioned_session(session):
    @event.listens_for(session, "before_flush")
    def before_flush(session, flush_context, instances):
        for obj in session.new:
            process_version(session, obj, new=True, deleted=False)
        for obj in session.dirty:
            process_version(session, obj, new=False, deleted=False)
        for obj in session.deleted:
            process_version(session, obj, new=False, deleted=True)

    return session
