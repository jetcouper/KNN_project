from abc import ABC, abstractmethod
from typing import override

class DBCredential(ABC):

    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        self.host: str = host
        self.port: int = port
        self.database: str = database
        self.user: str = user
        self.password: str = password

    @property
    @abstractmethod
    def connection_string(self) -> str:
        raise NotImplementedError


class PostgreSQLCredential(DBCredential):

    def __init__(self, 
                 password: str = '', 
                 host: str = 'localhost', 
                 port: int = 5432, 
                 database: str = 'postgres', 
                 user: str = 'postgres') -> None:
        super().__init__(host, port, database, user, password)

    @override
    @property
    def connection_string(self) -> str:
        return f"host='{self.host}' port={self.port} dbname='{self.database}' user='{self.user}' password='{self.password}'"