# Standard library imports
from datetime import datetime
from enum import Enum
import logging
import re
from typing import Final, TypeVar

# Third party imports
try:
    from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
    from sqlalchemy.orm import relationship, validates
except ImportError:
    logging.warning("Package sqlalchemy need to be installed")
    raise ImportError("Package sqlalchemy need to be installed")

# Local specific imports
try:
    from database import Base
except ImportError:
    logging.warning("Package database need to be near this package")
    raise ImportError("Package database need to be near this package")


T = TypeVar('T', bound='AppType')


class AppType(Enum):
    T_SENSOR = "temperature_sensor"
    W_SENSOR = "water_sensor"
    WEBAPP = "web"
    ZABBIX = "zabbix"

    @classmethod
    def get_app_type(cls, app_type: str) -> T:
        if not app_type:
            return cls.WEBAPP

        for val in cls.__iter__():
            if val.value == app_type:
                return val


class Service(Base):
    __tablename__ = 'service'

    app_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=False)
    route = Column(String, nullable=False)
    user = Column(String, nullable=True)
    password = Column(String, nullable=True)
    status = Column(String, nullable=False)
    app_type = Column(String, nullable=False)
    other_data1 = Column(String, nullable=True)
    other_data2 = Column(String, nullable=True)
    other_data3 = Column(String, nullable=True)
    other_data4 = Column(String, nullable=True)
    other_data5 = Column(String, nullable=True)
    logs = relationship("ServiceLog", back_populates="service")

    # Pattern variables correspond to:
    # <action>: write, click, obtain, blank
    # <tag_name>: html element like input, a, div, etc...
    # <tag_attribute>: id, class, name
    # <attribute_value>: attribute value as found in the html
    # e.g.: write:input:id:login_user
    # e.g.: click:input:name:login_button
    # e.g.: obtain:div:class:infoContainer
    # Ensure that the chosen attributes identify a single element in the html page
    __route_pattern: Final[str] = "<action>:<tag_name>:<tag_attribute>:<attribute_value>"

    def __init__(self,
                 name: str,
                 description: str,
                 url: str,
                 route: str,
                 app_type: AppType,
                 user: str = "",
                 password: str = "",
                 other_data1: str = "",
                 other_data2: str = "",
                 other_data3: str = "",
                 other_data4: str = "",
                 other_data5: str = ""
                 ):
        """

        :param name:
        :param description:
        :param url:
        :param route:
        :param user:
        :param password:
        :param app_type:
        :param other_data1:
        :param other_data2:
        :param other_data3:
        :param other_data4:
        :param other_data5:
        :raise ValueError if the route provided doesn't follow the pattern
        action:tag_name:tag_attribute:attribute_value
        """
        self.name = name
        self.description = description
        self.url = url
        self.route = route
        self.user = user
        self.password = password
        self.status = "active"
        self.app_type = app_type.value
        self.other_data1 = other_data1
        self.other_data2 = other_data2
        self.other_data3 = other_data3
        self.other_data4 = other_data4
        self.other_data5 = other_data5

    def __repr__(self):
        return f'{type(self).__name__}({self.name}, {self.description}, {self.url}, {self.route}, ' \
               f'{self.user}, {self.password}, {self.status}, {self.app_type}, ' \
               f'{self.other_data1}, {self.other_data2}, {self.other_data3}, {self.other_data4}, {self.other_data5})'

    def __str__(self):
        return f'{self.name} - {self.description} - {self.url}'

    @validates("route")
    def validate_route(self, key, value):
        is_valid = True
        for route in value.split("|"):
            route = route.split(":")
            if len(route) != self.route_pattern_len or \
                    route[0] not in ("write", "click", "obtain", "blank") or \
                    route[2] not in ("id", "class", "name", "blank"):
                is_valid = False

        if is_valid:
            return "".join(value.split())
        raise ValueError(f"The route must have the pattern {self.__route_pattern}")

    @validates("app_type")
    def validate_app_type(self, key, value):
        app_type_values = [app_type.value for app_type in AppType]
        if value in app_type_values:
            return value
        raise ValueError(f"The service type must be one of the list: {', '.join(app_type_values)}")

    @property
    def route_pattern(self) -> str:
        return self.__route_pattern

    @property
    def route_pattern_len(self) -> int:
        return len(self.__route_pattern.split(":"))

    def to_dict(self):
        return {
                "name": self.name,
                "description": self.description,
                "url": self.url,
                "route": self.route,
                "user": self.user,
                "password": self.password,
                "status": self.status,
                "app_type": self.app_type
        }


class ServiceLog(Base):
    __tablename__ = 'service_log'

    log_id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    status_date = Column(DateTime, nullable=False)
    other_data = Column(String, nullable=True)
    app_id = Column(Integer, ForeignKey('service.app_id'))
    service = relationship("Service", back_populates="logs", lazy="joined")

    def __init__(self,
                 status: str,
                 status_date: datetime,
                 service,
                 other_data: str = None):
        self.status = status
        self.status_date = status_date
        self.other_data = other_data
        self.service = service

    def to_dict(self):
        return {
                "status": self.status,
                "status_date": self.status_date,
                "other_data": self.other_data,
                "service_name": self.service.name
        }

    def __repr__(self):
        return f'{type(self).__name__}({self.status}, {self.status_date.strftime("%d/%m/%Y %H:%M:%S")}, ' \
               f'{self.other_data}, {self.service})'

    def __str__(self):
        return f'{self.service} - {self.status} - {self.status_date.strftime("%d/%m/%Y %H:%M:%S")}'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), unique=True, nullable=False)
    password = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    type_ = Column(String(250), nullable=False)
    status = Column(String(250), nullable=False, default="active")
    role = Column(String(250), nullable=True)

    @validates("type_")
    def validate_type(self, key, value):
        type_values = ["admin", "user"]
        if value in type_values:
            return value
        raise ValueError(f"The user type must be one of the list: {', '.join(type_values)}")

    @validates("email")
    def validate_email(self, key, value):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if re.fullmatch(regex, value):
            return value
        raise ValueError(f"You must provide a valid email")

    def __str__(self):
        return f'{self.email} - {self.name} - {self.type_}'
