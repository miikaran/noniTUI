from dataclasses import dataclass, field
import aiohttp

@dataclass
class HTTPSessionManager:
    """Client side session manager."""
    session: aiohttp.ClientSession = field(default=None, init=False)

    async def init(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            await self.init()
        return self.session

    async def close(self):
        if self.session is not None:
            await self.session.close()
            self.session = None

session_manager =  HTTPSessionManager()