#!/usr/bin/env python3
"""DB module for the user authentication service."""
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

from user import Base, User


class DB:
    """DB class.

    Attributes:
        _engine (Engine): The database engine.
        __session (Session): The database session.
    """
    def __init__(self) -> None:
        """Initializes the DB object.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Returns a session object.
        """
        if self.__session is None:
            sessionFactory = sessionmaker(bind=self._engine)
            self.__session = sessionFactory()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Adds a user record to the database.
        """
        try:
            createdUser = User(email=email, hashed_password=hashed_password)
            self._session.add(createdUser)
            self._session.commit()
        except Exception:
            self._session.rollback()
            createdUser = None
        return createdUser

    def find_user_by(self, **kwargs) -> User:
        """Returns the first row that matches the query.
        """
        search_fields, user_values = [], []
        for key, value in kwargs.items():
            if hasattr(User, key):
                search_fields.append(getattr(User, key))
                user_values.append(value)
            else:
                raise InvalidRequestError()
        result = self._session.query(User).filter(
            tuple_(*search_fields).in_([tuple(user_values)])
        ).first()
        if result is None:
            raise NoResultFound()
        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        """Updates a user record.
        """
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        update_fields = {}
        for key, value in kwargs.items():
            if hasattr(User, key):
                update_fields[getattr(User, key)] = value
            else:
                raise ValueError()
        self._session.query(User).filter(User.id == user_id).update(
            update_fields,
            synchronize_session=False,
        )
        self._session.commit()
