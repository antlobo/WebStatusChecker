# Standard library imports
import os
from datetime import datetime, date, timedelta
import inspect
import logging
from typing import Optional, Literal

# Third party imports
try:
    import sqlalchemy.exc
    from sqlalchemy.orm import joinedload
    from sqlalchemy.sql.functions import max
except ImportError:
    logging.warning("Package sqlalchemy need to be installed")
    raise ImportError("Package sqlalchemy need to be installed")

# Local specific imports
try:
    from database import Base, get_session, get_engine
    from common.models import Service, ServiceLog, AppType, User
except ImportError:
    logging.warning("Packages database and common need to be near this package")
    raise ImportError("Packages database and common need to be near this package")


class DataManager:
    __logger = logging.getLogger(__name__)

    def __init__(self):
        Base.metadata.create_all(get_engine())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # ++++++++++++++++++++ Create information ++++++++++++++++++++ #
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    @classmethod
    def add_service(cls, service: Service) -> tuple[bool, str]:
        """
        Adds a new service to the database
        :param service: a Service object
        :return: a tuple with a bool True if the service was created or False otherwise
        and a string with an error or a result message
        """
        if not isinstance(service, Service):
            cls.__logger.error(f"It was sent a not recognized object to the Database: {service}")
            return False, f"[Error] The object sent is not a {Service.__name__}"

        session = get_session()

        with session as sm:
            sm.add(service)
            cls.__logger.debug(f"Adding this service to DB: {service.__repr__()}")
            try:
                cls.__logger.info(f"Committing service {service.name} to Database")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"Service {service.name} couldn't be created", exc_info=True)
                return False, "[Error] Couldn't create the service"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"Service {service.name} couldn't be created", exc_info=True)
                return False, "[Error] Couldn't create the service"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"Couldn't find the table {Service.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {Service.__tablename__}"
            else:
                cls.__logger.info(f"[Success] Created the Service {service.name} in the Database")
                return True, "Success"

    @classmethod
    def bulk_add_service(cls, services: list[Service]) -> tuple[bool, str]:
        """
        Adds new services to the database
        :param services: a list of Service object
        :return: a tuple with a bool True if the service was created or False otherwise
        and a string with an error or a result message
        """
        session = get_session()

        with session as sm:
            services_name = []
            for service in services:
                if isinstance(service, Service):
                    services_name.append(service.name)
                    sm.add(service)
                else:
                    cls.__logger.error(f"It was sent a not recognized object to the Database: {service}")

            try:
                cls.__logger.info(f"Committing to Database next Services: {', '.join(services_name)}")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"Service {service.name} couldn't be created", exc_info=True)
                return False, "[Error] Couldn't create the service"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"Service {service.name} couldn't be created", exc_info=True)
                return False, "[Error] Couldn't create the service"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"Couldn't find the table {Service.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {Service.__tablename__}"
            else:
                cls.__logger.info(f"[Success] Services created: {', '.join(services_name)}")
                return True, "Success"

    @classmethod
    def add_log_service(cls, service_log: ServiceLog) -> tuple[bool, str]:
        """
        Add a new log to the database
        :param service_log: a ServiceLog object
        :return: a tuple with a bool True if the service's log was created or False otherwise
        and a string with an error or a result message
        """
        if not isinstance(service_log, ServiceLog):
            cls.__logger.error(f"It was sent a not recognized object to the Database: {service_log}")
            return False, f"[Error] The object sent is not a {ServiceLog.__name__}"

        session = get_session()

        with session as sm:
            sm.add(service_log)
            cls.__logger.debug(f"Adding this log to DB: {service_log.__repr__()}")
            try:
                cls.__logger.info(f"Committing log to Database for the Service: {service_log.service.name}")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't create log"
                                       f" for the Service {service_log.service.name}", exc_info=True)
                return False, "[Error] Couldn't add the service log"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"There was a problem with the Database and couldn't create log"
                                       f" for the Service {service_log.service.name}", exc_info=True)
                return False, "[Error] Couldn't add the service log"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {Service.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {ServiceLog.__tablename__}"
            else:
                cls.__logger.info(f"[Success] Log created for the Service {service_log.service.name}")
                return True, "Success"

    @classmethod
    def bulk_add_log_service(cls, service_logs: list[ServiceLog]) -> tuple[bool, str]:
        """
        Add a list of logs to the database
        :param service_logs: a ServiceLog object list
        :return: a tuple with a bool True if the service's log was created or False otherwise
        and a string with an error or a result message
        """
        session = get_session()

        with session as sm:
            services_name = []
            for service_log in service_logs:
                if isinstance(service_log, ServiceLog):
                    services_name.append(service_log.service.name)
                    sm.add(service_log)
                else:
                    cls.__logger.error(f"It was sent a not recognized object to the Database: {service_log}")
            try:
                cls.__logger.info(f"Committing logs to Database for the Services: {', '.join(services_name)}")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't create log"
                                       f" for the Services: {', '.join(services_name)}", exc_info=True)
                return False, "[Error] Couldn't add the service logs"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"There was a problem with the Database and couldn't create log"
                                       f" for the Services: {', '.join(services_name)}", exc_info=True)
                return False, "[Error] Couldn't add the service logs"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {Service.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {ServiceLog.__tablename__}"
            else:
                cls.__logger.info(f"[Success] Log created for the Services: {', '.join(services_name)}")
                return True, "Success"

    @classmethod
    def add_user(cls, user: User) -> tuple[bool, str]:
        """

        :param user:
        :return:
        """
        if not isinstance(user, User):
            cls.__logger.error(f"It was sent a not recognized object to the Database: {user}")
            return False, "The information sent is not a valid User type"

        session = get_session()

        with session as sm:
            sm.add(user)
            cls.__logger.debug(f"Adding this user to DB: {user.__repr__()}")
            try:
                cls.__logger.info(f"Committing user {user.email} to Database")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"User couldn't be created", exc_info=True)
                return False, f"User couldn't be created"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"User couldn't be created", exc_info=True)
                return False, f"User couldn't be created"
            except sqlalchemy.exc.IntegrityError:
                cls.__logger.exception(f"User {user.email} couldn't be created because it already exist", exc_info=True)
                return False, f"User couldn't be created because it already exist"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"Couldn't find the table {User.__tablename__}", exc_info=True)
                return False, f"Couldn't find the table {User.__tablename__}"
            else:
                cls.__logger.info(f"[Success] Created the user {user.email} in the Database")
                return True, f"User created"

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # ++++++++++++++++++++ Read information ++++++++++++++++++++ #
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    @classmethod
    def get_service(cls, app_id: int = None,
                    name: str = None,
                    url: str = None,
                    status: Optional[Literal["active", "inactive"]] = "active",
                    app_type: AppType = None) -> tuple[Optional[Service], str]:
        """
        Gets a service specified by the search criteria
        :param app_id: an integer with the service id
        :param name: a string with the service's name
        :param url: a string with the service's url
        :param status: a string with the service's status
        :param app_type: an object AppType with the service's type
        :return: a Service object and a 'Success' string if a record was found or a None and an error message otherwise
        """
        if (name or app_id or url or status or app_type) and not \
                (isinstance(name, str) or
                 isinstance(app_id, int) or
                 isinstance(url, str) or
                 isinstance(status, str) or
                 isinstance(app_type, AppType)):
            cls.__logger.debug(f"It wasn't provided a valid search value: {name=}, {app_id=}, "
                               f"{url=}, {status=}, {app_type=}")
            return None, "It wasn't provided a valid search value"

        session = get_session()

        with session as sm:
            query = sm.query(Service)

            if app_id:
                query = query.get(app_id)
            if name and not isinstance(query, Service):
                query = query.filter(Service.name.ilike(f"%{name}%"))
            if url and not isinstance(query, Service):
                query = query.filter(Service.url.ilike(f"%{url}%"))
            if status and not isinstance(query, Service):
                query = query.filter(Service.status == status)
            if app_type and not isinstance(query, Service):
                query = query.filter(Service.app_type.ilike(f"%{app_type.value}%"))

            cls.__logger.debug(f"Query constructed is: {query}")

            try:
                if not isinstance(query, Service):
                    service = query.first()
                else:
                    service = query
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None, "[Error] Couldn't obtain the values"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None, f"[Error] Couldn't find the table {Service.__tablename__}"
            else:
                if service:
                    return service, "Success"

                cls.__logger.info(f"No record matched the value queried")
                return None, "No record matches the value queried"

    @classmethod
    def get_services(cls,
                     app_id: int = None,
                     name: str = None,
                     url: str = None,
                     status: Optional[Literal["active", "inactive"]] = "active",
                     app_type: AppType = None) -> tuple[Optional[list[Service]], str]:
        """
        Gets a list of services specified by the search criteria
        :rtype: object
        :param app_id: an integer with the service id
        :param name: a string with the service's name
        :param url: a string with the service's url
        :param status: a string with the service's status
        :param app_type: an object AppType with the service's type
        :return: a Service object and a 'Success' string if a record was found or a None and an error message otherwise
        """
        if (name or app_id or url or app_type or status) and not \
                (isinstance(name, str) or
                 isinstance(app_id, int) or
                 isinstance(url, str) or
                 isinstance(status, str) or
                 isinstance(app_type, AppType)):
            cls.__logger.debug(f"It wasn't provided a valid search value: {name=}, {app_id=}, "
                               f"{url=}, {status=}, {app_type=}")
            return None, "It wasn't provided a valid search value"

        session = get_session()

        with session as sm:
            query = sm.query(Service)

            if app_id:
                query = query.filter(Service.app_id == app_id)
            if name:
                query = query.filter(Service.name.ilike(f"%{name}%"))
            if url:
                query = query.filter(Service.url.ilike(f"%{url}%"))
            if status:
                query = query.filter(Service.status == status)
            if app_type:
                query = query.filter(Service.app_type.ilike(f"%{app_type.value}%"))

            cls.__logger.debug(f"Query constructed is: {query}")

            try:
                services = query.all()
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None, "[Error] Couldn't obtain the values"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {Service.__tablename__}", exc_info=True)
                return None, f"[Error] Couldn't find the table {Service.__tablename__}"
            else:
                if services:
                    return services, "Success"

                cls.__logger.info(f"No record matched the value queried")
                return None, "No record matched the value queried"

    @classmethod
    def get_services_by_type(cls) -> tuple[Optional[list[Service]], str]:
        """
        Gets a list of service ordered by the column app_type
        :return: a list of Services and a success message or None and an error message otherwise
        """

        session = get_session()

        with session as sm:
            try:
                cls.__logger.info(f"Querying the Database: getting Services ordered by type")
                services = sm.query(Service).order_by(Service.app_type).all()
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None, "[Error] Couldn't obtain the values"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {Service.__tablename__}", exc_info=True)
                return None, f"[Error] Couldn't find the table {Service.__tablename__}"
            else:
                if services:
                    return services, "Success"

                cls.__logger.info(f"No record matched the value queried")
                return None, "No record matches the value queried"

    @classmethod
    def get_logs(cls, start_date_: date = None,
                 end_date_: date = None,
                 name: str = None,
                 app_id: int = None,
                 app_type: AppType = None) -> tuple[Optional[list[ServiceLog]], str]:
        """

        :param start_date_:
        :param end_date_:
        :param name:
        :param app_id:
        :param app_type:
        :return:
        """
        if (name or app_id or start_date_ or end_date_ or app_type) and not \
                (isinstance(name, str) or
                 isinstance(app_id, int) or
                 isinstance(start_date_, date) or
                 isinstance(end_date_, date) or
                 isinstance(app_type, AppType)):
            cls.__logger.debug(f"It wasn't provided a valid search value: {name=}, {app_id=}, "
                               f"{start_date_=}, {end_date_=}, {app_type=}")
            return None, "It wasn't provided a valid search value"

        session = get_session()

        with session as sm:
            query = sm.query(ServiceLog)

            if start_date_:
                start_date = datetime(start_date_.year, start_date_.month, start_date_.day, 0, 0, 0)
                query = query.filter(ServiceLog.status_date >= start_date)
            if not end_date_ and start_date_:
                end_date = start_date + timedelta(hours=23, minutes=59, seconds=59)
                query = query.filter(ServiceLog.status_date <= end_date)
            elif start_date_ and end_date_ and end_date_ < start_date_:
                end_date = start_date + timedelta(hours=23, minutes=59, seconds=59)
                query = query.filter(ServiceLog.status_date <= end_date)
            elif end_date_ and start_date_:
                end_date = datetime(end_date_.year, end_date_.month, end_date_.day, 23, 59, 59)
                query = query.filter(ServiceLog.status_date <= end_date)
            if end_date_ and not start_date_:
                end_date = datetime(end_date_.year, end_date_.month, end_date_.day, 23, 59, 59)
                start_date = end_date - timedelta(hours=23, minutes=59, seconds=59)
                query = query.filter(ServiceLog.status_date >= start_date)

            if app_id or name or app_type:
                query = query.join(Service).options(joinedload(Service.app_id == ServiceLog.app_id))
                if app_id:
                    query = query.filter(Service.app_id == app_id)
                if name:
                    query = query.filter(Service.name.ilike(f"%{name}%"))
                if app_type:
                    query = query.filter(Service.app_type.ilike(f"%{app_type.value}%"))

            cls.__logger.debug(f"Query constructed is: {query}")

            try:
                cls.__logger.info(f"Querying the Database: getting logs")
                logs = query.order_by(ServiceLog.status_date).all()
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None, "[Error] Couldn't obtain the values"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {ServiceLog.__tablename__} or {Service.__tablename__}", exc_info=True)
                return None, f"[Error] Couldn't find the table {ServiceLog.__tablename__} or {Service.__tablename__}"
            else:
                return logs, "Success"

    @classmethod
    def get_last_active_time(cls, app_id: int = None) -> tuple[Optional[list[ServiceLog]], str]:
        if app_id and not isinstance(app_id, int):
            cls.__logger.debug(f"It wasn't provided a valid search value: {app_id=}")
            return None, "It wasn't provided a valid search value"

        session = get_session()
        with session as sm:
            query = sm.query(max(ServiceLog.status_date).label("status_date"), ServiceLog.app_id).filter(ServiceLog.status == "Running").group_by(ServiceLog.app_id)
            if app_id:
                query = query.filter(ServiceLog.app_id == app_id)

            cls.__logger.debug(f"Query constructed is: {query}")

            try:
                cls.__logger.info(f"Querying the Database: getting logs")
                logs = query.order_by(ServiceLog.status_date).all()
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None, "[Error] Couldn't obtain the values"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {ServiceLog.__tablename__}", exc_info=True)
                return None, f"[Error] Couldn't find the table {ServiceLog.__tablename__}"
            else:
                return logs, "Success"

    @classmethod
    def get_user_id(cls, user_id: int) -> Optional[User]:
        """

        :param user_id:
        :return:
        """

        session = get_session()

        with session as sm:
            try:
                cls.__logger.info(f"Querying the Database: getting User")
                user = sm.query(User).get(user_id)
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                return None
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {User.__tablename__}", exc_info=True)
                return None
            else:
                if user:
                    return user

                cls.__logger.info(f"No record matched the value queried")
                return None

    @classmethod
    def get_user_email(cls, email: str) -> Optional[User]:
        """

        :param email:
        :return:
        """

        session = get_session()

        with session as sm:
            try:
                cls.__logger.info(f"Querying the Database: getting User")
                user = sm.query(User).filter_by(email=email).first()
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                user = None
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {User.__tablename__}", exc_info=True)
                user = None
            else:
                if not user:
                    cls.__logger.info(f"No record matched the value queried")
            finally:
                return user

    @classmethod
    def get_users(cls) -> tuple[Optional[list[User]], str]:
        session = get_session()

        with session as sm:
            try:
                cls.__logger.info(f"Querying the Database: getting Users")
                users = sm.query(User).all()
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't retrieve "
                                       f"a record", exc_info=True)
                users = None, f"There was a problem with the Database and couldn't retrieve a record"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {User.__tablename__}", exc_info=True)
                users = None, f"There was a problem with the Database, couldn't find the table {User.__tablename__}"
            else:
                if not users:
                    cls.__logger.info(f"No record matched the value queried")
            finally:
                return users, "Success"

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    # ++++++++++++++++++++ Update information ++++++++++++++++++++ #
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
    @classmethod
    def update_service(cls, service_: Service) -> tuple[bool, str]:
        """
        Updates multiple values of a service by its id
        :param service_: Service object with the values to update
        :return: a tuple with a bool: True if the service's status was updated or False otherwise and a string
        with an error or a result message
        """
        if not service_.app_id:
            cls.__logger.info(f"No valid Service was passed to update {service_}")
            return False, "[Error] No service was passed"

        session = get_session()

        with session as sm:
            try:
                cls.__logger.debug(f"Service to update is: {service_.__repr__()}")
                cls.__logger.info(f"Querying the Database")
                service = sm.query(Service).get(service_.app_id)

                attributes = inspect.getmembers(Service, lambda a: not (inspect.isroutine(a)))
                property_list = [
                    a[0] for a in attributes
                    if "__" not in a[0] and
                    a[0] not in ("app_id", "logs", "metadata", "registry") and
                    not ("route_pattern" in a[0]) and
                    not a[0].startswith('_sa')
                ]

                for property_ in property_list:
                    setattr(service, property_, getattr(service_, property_))

                cls.__logger.info(f"Committing updated values to the Database")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                       f"the Service: {service_.__repr__()}", exc_info=True)
                return False, "[Error] Couldn't update the service"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                       f"the Service: {service_.__repr__()}", exc_info=True)
                return False, "[Error] Couldn't update the service"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {Service.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {Service.__tablename__}"
            except AttributeError:
                cls.__logger.exception(f"There was a problem with a value passed to update "
                                       f"the Service: {service_.__repr__()}", exc_info=True)
                return False, "[Error] There was a problem with a value passed to update the service"
            else:
                return True, "Service was updated"

    @classmethod
    def update_service_status(cls, app_id: int, status: Literal["active", "inactive"]) -> tuple[bool, str]:
        """
        Changes status of the service
        :param app_id: service id (set by the database) to update
        :param status: new status of the service
        :return: a tuple with a bool: True if the service's status was updated or False otherwise and a string
        with an error or a result message
        """
        if not app_id or not isinstance(app_id, int):
            cls.__logger.info(f"No valid value was passed to update a Service {app_id} must be an integer")
            return False, "[Error] No service was passed"

        session = get_session()

        with session as sm:
            try:
                cls.__logger.info(f"Querying the Database")
                cls.__logger.debug(f"Trying to find the service with the {app_id=}")

                service = sm.query(Service).get(app_id)
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                       f"the Service", exc_info=True)
                return False, "[Error] There was a problem with the Database and couldn't update the service"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {Service.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {Service.__tablename__}"
            else:
                service.status = status
                try:
                    cls.__logger.debug(f"Trying to update the Service status: {service.name}")
                    sm.commit()
                except sqlalchemy.exc.OperationalError:
                    cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                           f"the Service", exc_info=True)
                    return False, "[Error] Couldn't update the service"
        cls.__logger.info(f"[Success] Status changed to: {status}")
        return True, f"Service's status changed to: {status}"

    @classmethod
    def update_user(cls, user_: User) -> tuple[bool, str]:
        """
        Updates multiple values of a service by its id
        :param user_: Service object with the values to update
        :return: a tuple with a bool: True if the service's status was updated or False otherwise and a string
        with an error or a result message
        """
        if not user_.id:
            cls.__logger.info(f"No valid User was passed to update {user_}")
            return False, "[Error] No user was passed"

        session = get_session()

        with session as sm:
            try:
                cls.__logger.debug(f"User to update is: {user_.__repr__()}")
                cls.__logger.info(f"Querying the Database")
                user = sm.query(User).get(user_.id)

                attributes = inspect.getmembers(User, lambda a: not (inspect.isroutine(a)))
                property_list = [
                    a[0] for a in attributes
                    if "__" not in a[0] and
                    a[0] not in ("id", "metadata", "registry") and
                    not a[0].startswith('_sa')
                ]

                for property_ in property_list:
                    setattr(user, property_, getattr(user_, property_))

                cls.__logger.info(f"Committing updated values to the Database")
                sm.commit()
            except sqlalchemy.exc.OperationalError or sqlalchemy.orm.exc.FlushError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                       f"the Service: {user_.__repr__()}", exc_info=True)
                return False, "[Error] Couldn't update the service"
            except sqlalchemy.exc.SAWarning:
                cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                       f"the Service: {user_.__repr__()}", exc_info=True)
                return False, "[Error] Couldn't update the service"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {User.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {User.__tablename__}"
            except AttributeError:
                cls.__logger.exception(f"There was a problem with a value passed to update "
                                       f"the Service: {user_.__repr__()}", exc_info=True)
                return False, "[Error] There was a problem with a value passed to update the service"
            else:
                return True, f"User {user.email} was updated"

    @classmethod
    def update_user_status(cls, user_id: int, status: Literal["active", "inactive"]) -> tuple[bool, str]:
        """
        Changes status of the user
        :param user_id: user id (set by the database) to update
        :param status: new status of the user
        :return: a tuple with a bool: True if the user's status was updated or False otherwise and a string
        with an error or a result message
        """
        if not user_id or not isinstance(user_id, int):
            cls.__logger.info(f"No valid value was passed to update a User {user_id} must be an integer")
            return False, "[Error] No user was passed"

        session = get_session()

        with session as sm:
            try:
                cls.__logger.info(f"Querying the Database")
                cls.__logger.debug(f"Trying to find the user with the {user_id=}")

                user = sm.query(User).get(user_id)
            except sqlalchemy.exc.OperationalError:
                cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                       f"the User", exc_info=True)
                return False, "[Error] There was a problem with the Database and couldn't update the user"
            except sqlalchemy.exc.NoSuchTableError:
                cls.__logger.exception(f"There was a problem with the Database, couldn't find the "
                                       f"table {User.__tablename__}", exc_info=True)
                return False, f"[Error] Couldn't find the table {User.__tablename__}"
            else:
                user.status = status
                try:
                    cls.__logger.debug(f"Trying to update the User status: {user.name}")
                    sm.commit()
                except sqlalchemy.exc.OperationalError:
                    cls.__logger.exception(f"There was a problem with the Database and couldn't update "
                                           f"the User", exc_info=True)
                    return False, "[Error] Couldn't update the user"
        cls.__logger.info(f"[Success] Status changed to: {status}")
        return True, f"User's status changed to: {status}"
