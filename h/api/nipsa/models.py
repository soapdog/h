import pyramid_basemodel
import sqlalchemy
from sqlalchemy.orm import exc


class NipsaUser(pyramid_basemodel.Base):

    """A NIPSA entry for a user (SQLAlchemy ORM class)."""

    __tablename__ = 'nipsa_user'
    user_id = sqlalchemy.Column(sqlalchemy.UnicodeText, primary_key=True,
                                index=True)

    def __init__(self, user_id):
        self.user_id = user_id


def get_user(user_id):
    """Return the NipsaUser object for the given user_id, or None."""
    try:
        return pyramid_basemodel.Session.query(NipsaUser).filter(
            NipsaUser.user_id == user_id).one()
    except exc.NoResultFound:
        return None


def all_users():
    """Return a list of all NipsaUser objects in the db."""
    return pyramid_basemodel.Session.query(NipsaUser).all()
