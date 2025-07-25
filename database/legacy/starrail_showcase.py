import zlib

import aiosqlite
from mihomo import StarrailInfoParsedV1


class StarrailShowcaseTable:
    """Table for Starrail Showcase data."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        self.db = db

    async def create(self) -> None:
        """Create the table in the database."""
        await self.db.execute(
            """CREATE TABLE IF NOT EXISTS starrail_showcase (
                uid int NOT NULL PRIMARY KEY,
                data blob
            )"""
        )
        await self.db.commit()

    async def add(self, uid: int, data: StarrailInfoParsedV1) -> None:
        """Add user data to the table."""
        json_data = data.json(by_alias=True, ensure_ascii=False)
        compressed_data = zlib.compress(json_data.encode(encoding="utf8"), level=5)
        await self.db.execute(
            "INSERT OR REPLACE INTO starrail_showcase VALUES(?, ?)", [uid, compressed_data]
        )
        await self.db.commit()

    async def remove(self, uid: int) -> None:
        """Remove user data from the table."""
        await self.db.execute("DELETE FROM starrail_showcase WHERE uid=?", [uid])
        await self.db.commit()

    async def get(self, uid: int) -> StarrailInfoParsedV1 | None:
        """Get user data from the table."""
        async with self.db.execute("SELECT * FROM starrail_showcase WHERE uid=?", [uid]) as cursor:
            row = await cursor.fetchone()
            if row is not None:
                json_data = zlib.decompress(row["data"]).decode(encoding="utf8")
                return StarrailInfoParsedV1.parse_raw(json_data)
            return None
