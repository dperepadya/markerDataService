from abc import abstractmethod, ABC
class ExchangeClient(ABC):
    def __init__(self, login: str, password: str, host: str):
        # {name, ...}
        self.symbols = []

    @abstractmethod
    async def init_client(self):
        pass

    @abstractmethod
    async def subscribe(self, symbol: str, channel: str):
        pass

    @abstractmethod
    async def unsubscribe(self, symbol: str, channel: str):
        pass

    @abstractmethod
    async def get_symbols(self):
        pass
