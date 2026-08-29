import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, List, Optional

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.core.constants import MT5CopyTicks, MT5Timeframe
from app.core.exceptions import MT5ServiceException
from app.schemas.orders import TradeRequest

logger = logging.getLogger("mt5_service")

# Map timeframe enum strings to MetaTrader5 integer constants
TIMEFRAME_MAP = {
    MT5Timeframe.TIMEFRAME_M1: getattr(mt5, "TIMEFRAME_M1", 1) if mt5 else 1,
    MT5Timeframe.TIMEFRAME_M2: getattr(mt5, "TIMEFRAME_M2", 2) if mt5 else 2,
    MT5Timeframe.TIMEFRAME_M3: getattr(mt5, "TIMEFRAME_M3", 3) if mt5 else 3,
    MT5Timeframe.TIMEFRAME_M4: getattr(mt5, "TIMEFRAME_M4", 4) if mt5 else 4,
    MT5Timeframe.TIMEFRAME_M5: getattr(mt5, "TIMEFRAME_M5", 5) if mt5 else 5,
    MT5Timeframe.TIMEFRAME_M6: getattr(mt5, "TIMEFRAME_M6", 6) if mt5 else 6,
    MT5Timeframe.TIMEFRAME_M10: getattr(mt5, "TIMEFRAME_M10", 10) if mt5 else 10,
    MT5Timeframe.TIMEFRAME_M12: getattr(mt5, "TIMEFRAME_M12", 12) if mt5 else 12,
    MT5Timeframe.TIMEFRAME_M15: getattr(mt5, "TIMEFRAME_M15", 15) if mt5 else 15,
    MT5Timeframe.TIMEFRAME_M20: getattr(mt5, "TIMEFRAME_M20", 20) if mt5 else 20,
    MT5Timeframe.TIMEFRAME_M30: getattr(mt5, "TIMEFRAME_M30", 30) if mt5 else 30,
    MT5Timeframe.TIMEFRAME_H1: getattr(mt5, "TIMEFRAME_H1", 16385) if mt5 else 16385,
    MT5Timeframe.TIMEFRAME_H2: getattr(mt5, "TIMEFRAME_H2", 16386) if mt5 else 16386,
    MT5Timeframe.TIMEFRAME_H3: getattr(mt5, "TIMEFRAME_H3", 16387) if mt5 else 16387,
    MT5Timeframe.TIMEFRAME_H4: getattr(mt5, "TIMEFRAME_H4", 16388) if mt5 else 16388,
    MT5Timeframe.TIMEFRAME_H6: getattr(mt5, "TIMEFRAME_H6", 16390) if mt5 else 16390,
    MT5Timeframe.TIMEFRAME_H8: getattr(mt5, "TIMEFRAME_H8", 16392) if mt5 else 16392,
    MT5Timeframe.TIMEFRAME_H12: getattr(mt5, "TIMEFRAME_H12", 16396) if mt5 else 16396,
    MT5Timeframe.TIMEFRAME_D1: getattr(mt5, "TIMEFRAME_D1", 16408) if mt5 else 16408,
    MT5Timeframe.TIMEFRAME_W1: getattr(mt5, "TIMEFRAME_W1", 32769) if mt5 else 32769,
    MT5Timeframe.TIMEFRAME_MN1: getattr(mt5, "TIMEFRAME_MN1", 49153) if mt5 else 49153,
}


class MT5Service:
    """Thread-safe service wrapping all MetaTrader 5 C-extension API calls."""

    # -------------------------------------------------------------
    # Terminal & Version
    # -------------------------------------------------------------
    async def get_version(self) -> dict:
        def _get():
            res = mt5.version()
            if res is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.version() failed: {err[1]}", error_code=err[0])
            return {"version": str(res[0]), "build": res[1], "release_date": res[2]}

        return await asyncio.to_thread(_get)

    async def get_terminal_info(self) -> dict:
        def _get():
            info = mt5.terminal_info()
            if info is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.terminal_info() failed: {err[1]}", error_code=err[0])
            return info._asdict()

        return await asyncio.to_thread(_get)

    async def get_last_error(self) -> dict:
        def _get():
            err = mt5.last_error()
            return {"code": err[0], "description": err[1]}

        return await asyncio.to_thread(_get)

    # -------------------------------------------------------------
    # Account
    # -------------------------------------------------------------
    async def get_account_info(self) -> dict:
        def _get():
            acc = mt5.account_info()
            if acc is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.account_info() failed: {err[1]}", error_code=err[0])
            return acc._asdict()

        return await asyncio.to_thread(_get)

    # -------------------------------------------------------------
    # Symbols & Market Data
    # -------------------------------------------------------------
    async def get_symbols_total(self) -> int:
        return await asyncio.to_thread(mt5.symbols_total)

    async def get_symbols(self, group: Optional[str] = None) -> List[dict]:
        def _get():
            symbols = mt5.symbols_get(group) if group else mt5.symbols_get()
            if symbols is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.symbols_get() failed: {err[1]}", error_code=err[0])
            return [s._asdict() for s in symbols]

        return await asyncio.to_thread(_get)

    async def get_symbol_info(self, symbol: str) -> dict:
        def _get():
            info = mt5.symbol_info(symbol)
            if info is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"Symbol '{symbol}' not found: {err[1]}", error_code=err[0])
            return info._asdict()

        return await asyncio.to_thread(_get)

    async def get_symbol_tick(self, symbol: str) -> dict:
        def _get():
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"Tick for '{symbol}' not available: {err[1]}", error_code=err[0])
            return tick._asdict()

        return await asyncio.to_thread(_get)

    async def select_symbol(self, symbol: str, enable: bool = True) -> bool:
        def _select():
            res = mt5.symbol_select(symbol, enable)
            if not res:
                err = mt5.last_error()
                raise MT5ServiceException(f"Failed to select symbol '{symbol}': {err[1]}", error_code=err[0])
            return res

        return await asyncio.to_thread(_select)

    # -------------------------------------------------------------
    # Market Depth (DOM)
    # -------------------------------------------------------------
    async def market_book_add(self, symbol: str) -> bool:
        def _add():
            res = mt5.market_book_add(symbol)
            if not res:
                err = mt5.last_error()
                raise MT5ServiceException(f"Failed to subscribe to DOM for '{symbol}': {err[1]}", error_code=err[0])
            return res

        return await asyncio.to_thread(_add)

    async def market_book_get(self, symbol: str) -> List[dict]:
        def _get():
            book = mt5.market_book_get(symbol)
            if book is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"Failed to get DOM for '{symbol}': {err[1]}", error_code=err[0])
            return [b._asdict() for b in book]

        return await asyncio.to_thread(_get)

    async def market_book_release(self, symbol: str) -> bool:
        def _release():
            res = mt5.market_book_release(symbol)
            if not res:
                err = mt5.last_error()
                raise MT5ServiceException(f"Failed to release DOM for '{symbol}': {err[1]}", error_code=err[0])
            return res

        return await asyncio.to_thread(_release)

    # -------------------------------------------------------------
    # Rates (OHLCV)
    # -------------------------------------------------------------
    async def copy_rates_from(self, symbol: str, timeframe: MT5Timeframe, date_from: datetime, count: int) -> List[dict]:
        tf = TIMEFRAME_MAP.get(timeframe, 1)

        def _copy():
            rates = mt5.copy_rates_from(symbol, tf, date_from, count)
            if rates is None or len(rates) == 0:
                err = mt5.last_error()
                raise MT5ServiceException(f"No rates returned for '{symbol}': {err[1]}", error_code=err[0])
            return [
                {
                    "time": int(r["time"]),
                    "time_iso": datetime.fromtimestamp(r["time"], timezone.utc).isoformat(),
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "tick_volume": int(r["tick_volume"]),
                    "spread": int(r["spread"]),
                    "real_volume": int(r["real_volume"]),
                }
                for r in rates
            ]

        return await asyncio.to_thread(_copy)

    async def copy_rates_from_pos(self, symbol: str, timeframe: MT5Timeframe, start_pos: int, count: int) -> List[dict]:
        tf = TIMEFRAME_MAP.get(timeframe, 1)

        def _copy():
            rates = mt5.copy_rates_from_pos(symbol, tf, start_pos, count)
            if rates is None or len(rates) == 0:
                err = mt5.last_error()
                raise MT5ServiceException(f"No rates returned for '{symbol}': {err[1]}", error_code=err[0])
            return [
                {
                    "time": int(r["time"]),
                    "time_iso": datetime.fromtimestamp(r["time"], timezone.utc).isoformat(),
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "tick_volume": int(r["tick_volume"]),
                    "spread": int(r["spread"]),
                    "real_volume": int(r["real_volume"]),
                }
                for r in rates
            ]

        return await asyncio.to_thread(_copy)

    async def copy_rates_range(self, symbol: str, timeframe: MT5Timeframe, date_from: datetime, date_to: datetime) -> List[dict]:
        tf = TIMEFRAME_MAP.get(timeframe, 1)

        def _copy():
            rates = mt5.copy_rates_range(symbol, tf, date_from, date_to)
            if rates is None or len(rates) == 0:
                err = mt5.last_error()
                raise MT5ServiceException(f"No rates returned for '{symbol}': {err[1]}", error_code=err[0])
            return [
                {
                    "time": int(r["time"]),
                    "time_iso": datetime.fromtimestamp(r["time"], timezone.utc).isoformat(),
                    "open": float(r["open"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                    "close": float(r["close"]),
                    "tick_volume": int(r["tick_volume"]),
                    "spread": int(r["spread"]),
                    "real_volume": int(r["real_volume"]),
                }
                for r in rates
            ]

        return await asyncio.to_thread(_copy)

    # -------------------------------------------------------------
    # Ticks Data
    # -------------------------------------------------------------
    async def copy_ticks_from(self, symbol: str, date_from: datetime, count: int, flags: MT5CopyTicks) -> List[dict]:
        def _copy():
            ticks = mt5.copy_ticks_from(symbol, date_from, count, flags.value)
            if ticks is None or len(ticks) == 0:
                err = mt5.last_error()
                raise MT5ServiceException(f"No ticks returned for '{symbol}': {err[1]}", error_code=err[0])
            return [
                {
                    "time": int(t["time"]),
                    "bid": float(t["bid"]),
                    "ask": float(t["ask"]),
                    "last": float(t["last"]),
                    "volume": int(t["volume"]),
                    "time_msc": int(t["time_msc"]),
                    "flags": int(t["flags"]),
                    "volume_real": float(t["volume_real"]),
                }
                for t in ticks
            ]

        return await asyncio.to_thread(_copy)

    async def copy_ticks_range(self, symbol: str, date_from: datetime, date_to: datetime, flags: MT5CopyTicks) -> List[dict]:
        def _copy():
            ticks = mt5.copy_ticks_range(symbol, date_from, date_to, flags.value)
            if ticks is None or len(ticks) == 0:
                err = mt5.last_error()
                raise MT5ServiceException(f"No ticks returned for '{symbol}': {err[1]}", error_code=err[0])
            return [
                {
                    "time": int(t["time"]),
                    "bid": float(t["bid"]),
                    "ask": float(t["ask"]),
                    "last": float(t["last"]),
                    "volume": int(t["volume"]),
                    "time_msc": int(t["time_msc"]),
                    "flags": int(t["flags"]),
                    "volume_real": float(t["volume_real"]),
                }
                for t in ticks
            ]

        return await asyncio.to_thread(_copy)

    # -------------------------------------------------------------
    # Orders & Trading
    # -------------------------------------------------------------
    async def get_orders_total(self) -> int:
        return await asyncio.to_thread(mt5.orders_total)

    async def get_orders(self, symbol: Optional[str] = None, group: Optional[str] = None, ticket: Optional[int] = None) -> List[dict]:
        def _get():
            if ticket is not None:
                orders = mt5.orders_get(ticket=ticket)
            elif symbol is not None:
                orders = mt5.orders_get(symbol=symbol)
            elif group is not None:
                orders = mt5.orders_get(group=group)
            else:
                orders = mt5.orders_get()

            if orders is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.orders_get() failed: {err[1]}", error_code=err[0])
            return [o._asdict() for o in orders]

        return await asyncio.to_thread(_get)

    async def order_check(self, req: TradeRequest) -> dict:
        def _check():
            payload = {k: v for k, v in req.model_dump().items() if v is not None}
            res = mt5.order_check(payload)
            if res is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.order_check() failed: {err[1]}", error_code=err[0])
            return res._asdict()

        return await asyncio.to_thread(_check)

    async def order_send(self, req: TradeRequest) -> dict:
        def _send():
            payload = {k: v for k, v in req.model_dump().items() if v is not None}
            # Auto-populate price if DEAL market order and price is omitted
            if payload.get("price") is None:
                tick = mt5.symbol_info_tick(payload["symbol"])
                if tick:
                    payload["price"] = tick.ask if payload["type"] == 0 else tick.bid

            res = mt5.order_send(payload)
            if res is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.order_send() failed: {err[1]}", error_code=err[0])
            return res._asdict()

        return await asyncio.to_thread(_send)

    async def order_calc_margin(self, action: int, symbol: str, volume: float, price: float) -> Optional[float]:
        def _calc():
            margin = mt5.order_calc_margin(action, symbol, volume, price)
            if margin is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.order_calc_margin() failed: {err[1]}", error_code=err[0])
            return margin

        return await asyncio.to_thread(_calc)

    async def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> Optional[float]:
        def _calc():
            profit = mt5.order_calc_profit(action, symbol, volume, price_open, price_close)
            if profit is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.order_calc_profit() failed: {err[1]}", error_code=err[0])
            return profit

        return await asyncio.to_thread(_calc)

    # -------------------------------------------------------------
    # Positions
    # -------------------------------------------------------------
    async def get_positions_total(self) -> int:
        return await asyncio.to_thread(mt5.positions_total)

    async def get_positions(self, symbol: Optional[str] = None, group: Optional[str] = None, ticket: Optional[int] = None) -> List[dict]:
        def _get():
            if ticket is not None:
                positions = mt5.positions_get(ticket=ticket)
            elif symbol is not None:
                positions = mt5.positions_get(symbol=symbol)
            elif group is not None:
                positions = mt5.positions_get(group=group)
            else:
                positions = mt5.positions_get()

            if positions is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.positions_get() failed: {err[1]}", error_code=err[0])
            return [p._asdict() for p in positions]

        return await asyncio.to_thread(_get)

    async def close_position(self, ticket: int, deviation: int = 10, comment: str = "Close via API") -> dict:
        """Closes an open position by ticket with opposite market order."""
        def _close():
            positions = mt5.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                raise MT5ServiceException(f"Position ticket #{ticket} not found.")

            pos = positions[0]
            symbol = pos.symbol
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                raise MT5ServiceException(f"Could not fetch tick to close position #{ticket}")

            # Opposite order type and price
            close_type = 1 if pos.type == 0 else 0  # 1=SELL to close BUY, 0=BUY to close SELL
            close_price = tick.bid if pos.type == 0 else tick.ask

            request = {
                "action": 1,  # TRADE_ACTION_DEAL
                "symbol": symbol,
                "volume": pos.volume,
                "type": close_type,
                "position": ticket,
                "price": close_price,
                "deviation": deviation,
                "magic": pos.magic,
                "comment": comment,
                "type_time": 0,  # ORDER_TIME_GTC
                "type_filling": 1,  # ORDER_FILLING_IOC
            }

            result = mt5.order_send(request)
            if result is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"Failed to close position #{ticket}: {err[1]}", error_code=err[0])
            return result._asdict()

        return await asyncio.to_thread(_close)

    # -------------------------------------------------------------
    # History (Deals & Orders)
    # -------------------------------------------------------------
    async def get_history_orders_total(self, date_from: datetime, date_to: datetime) -> int:
        def _get():
            return mt5.history_orders_total(date_from, date_to)

        return await asyncio.to_thread(_get)

    async def get_history_orders(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        group: Optional[str] = None,
        ticket: Optional[int] = None,
        position: Optional[int] = None,
    ) -> List[dict]:
        def _get():
            if ticket is not None:
                orders = mt5.history_orders_get(ticket=ticket)
            elif position is not None:
                orders = mt5.history_orders_get(position=position)
            elif date_from is not None and date_to is not None:
                orders = mt5.history_orders_get(date_from, date_to, group=group) if group else mt5.history_orders_get(date_from, date_to)
            else:
                orders = mt5.history_orders_get()

            if orders is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.history_orders_get() failed: {err[1]}", error_code=err[0])
            return [o._asdict() for o in orders]

        return await asyncio.to_thread(_get)

    async def get_history_deals_total(self, date_from: datetime, date_to: datetime) -> int:
        def _get():
            return mt5.history_deals_total(date_from, date_to)

        return await asyncio.to_thread(_get)

    async def get_history_deals(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        group: Optional[str] = None,
        ticket: Optional[int] = None,
        position: Optional[int] = None,
    ) -> List[dict]:
        def _get():
            if ticket is not None:
                deals = mt5.history_deals_get(ticket=ticket)
            elif position is not None:
                deals = mt5.history_deals_get(position=position)
            elif date_from is not None and date_to is not None:
                deals = mt5.history_deals_get(date_from, date_to, group=group) if group else mt5.history_deals_get(date_from, date_to)
            else:
                deals = mt5.history_deals_get()

            if deals is None:
                err = mt5.last_error()
                raise MT5ServiceException(f"mt5.history_deals_get() failed: {err[1]}", error_code=err[0])
            return [d._asdict() for d in deals]

        return await asyncio.to_thread(_get)


mt5_service = MT5Service()
