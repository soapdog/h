"""Model code for the NIPSA API.

The public functions in this module provide an interface for creating,
deleting, and retrieving NIPSA'd IDs from the database.

Note that the SQLAlchemy code for the NIPSA database tables is encapsulated in
this module - no SQLAlchemy objects are accepted as arguments to or returned as
values from this module's public functions.

"""
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import declarative


_DB_SESSION = orm.scoped_session(orm.sessionmaker())
_BASE = declarative.declarative_base()


class _NipsaUser(_BASE):

    """A NIPSA entry for a user (SQLAlchemy ORM class)."""

    __tablename__ = 'nipsa_user'
    user_id = sqlalchemy.Column(sqlalchemy.UnicodeText, primary_key=True,
                                index=True)

    def __init__(self, user_id):
        self.user_id = user_id


def _user_read(user_id):
    """Return the _NipsaUser object for the given user_id, or None."""
    session = _DB_SESSION()

    try:
        return (
            session.query(_NipsaUser)
            .filter(_NipsaUser.user_id == user_id)
            .one())
    except sqlalchemy.orm.exc.NoResultFound:
        return None


def user_read(user_id):
    """Return the given user ID if the user is NIPSA'd, False otherwise."""
    if _user_read(user_id):
        return user_id
    else:
        return False


def user_create(user_id):
    """Add the given user_id to the NIPSA list.

    Does nothing if the user is already NIPSA'd.

    """
    session = _DB_SESSION()

    nipsa_user = _user_read(user_id) or _NipsaUser(user_id)
    session.add(nipsa_user)
    session.commit()


def user_index():
    """Return a list of all of the NIPSA'd user IDs.

    :rtype: list of unicode strings

    """
    return [
        nipsa_user.user_id for nipsa_user in _DB_SESSION().query(_NipsaUser)]


def user_delete(user_id):
    """Delete the given user ID from the NIPSA list.

    If the ID isn't on the list nothing will happen.

    """
    nipsa_user = _user_read(user_id)
    if nipsa_user:
        session = _DB_SESSION()
        session.delete(nipsa_user)
        session.commit()


def includeme(config):
    engine = sqlalchemy.engine_from_config(
        config.registry.settings, 'sqlalchemy.')
    _DB_SESSION.configure(bind=engine)
    _BASE.metadata.create_all(engine)
