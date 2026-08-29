import asyncio
from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any, Dict, Optional

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

from app.config import settings

logger = logging.getLogger("mt5_manager")


class ConnectionState(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"
    INITIALIZING = "INITIALIZING"


class MT5Manager:
    """Manages the full lifecycle, monitoring, and auto-reconnection loop for MT5."""

    def __init__(self):
        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.last_error: Optional[str] = None
        self.last_error_code: int = 0
        self.connected_at: Optional[datetime] = None
        self.reconnect_attempts: int = 0
        self.total_reconnections: int = 0
        self._running: bool = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._trade_lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        return self.state == ConnectionState.CONNECTED

    async def initialize(self) -> bool:
        """Initializes the MT5 connection at application startup."""
        logger.info("Initializing MetaTrader 5 connection...")
        self.state = ConnectionState.INITIALIZING
        connected = await self._connect()
        return connected

    async def _connect(self) -> bool:
        """Synchronously attempts initialization and login in a background thread."""
        if mt5 is None:
            self.state = ConnectionState.DISCONNECTED
            self.last_error = "MetaTrader5 Python package is not installed or not supported on this OS."
            self.last_error_code = -1
            logger.error(self.last_error)
            return False

        def _sync_init_and_login() -> tuple[bool, int, Optional[str]]:
            init_kwargs: Dict[str, Any] = {
                "timeout": settings.MT5_TIMEOUT,
                "portable": settings.MT5_PORTABLE,
            }
            if settings.MT5_PATH:
                init_kwargs["path"] = settings.MT5_PATH
            if settings.MT5_LOGIN:
                init_kwargs["login"] = settings.MT5_LOGIN
            if settings.MT5_PASSWORD:
                init_kwargs["password"] = settings.MT5_PASSWORD
            if settings.MT5_SERVER:
                init_kwargs["server"] = settings.MT5_SERVER

            # Step 1: Initialize terminal
            initialized = mt5.initialize(**init_kwargs)
            if not initialized:
                err = mt5.last_error()
                return False, err[0], f"mt5.initialize() failed: code={err[0]}, desc={err[1]}"

            # Step 2: Login if explicit credentials provided
            if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
                logged_in = mt5.login(
                    login=settings.MT5_LOGIN,
                    password=settings.MT5_PASSWORD,
                    server=settings.MT5_SERVER,
                    timeout=settings.MT5_TIMEOUT,
                )
                if not logged_in:
                    err = mt5.last_error()
                    return False, err[0], f"mt5.login() failed: code={err[0]}, desc={err[1]}"

            return True, 0, None

        success, code, error_msg = await asyncio.to_thread(_sync_init_and_login)

        if success:
            self.state = ConnectionState.CONNECTED
            self.last_error = None
            self.last_error_code = 0
            self.connected_at = datetime.now(timezone.utc)
            self.reconnect_attempts = 0
            logger.info("Successfully established and authenticated MetaTrader 5 connection.")
            return True
        else:
            self.state = ConnectionState.DISCONNECTED
            self.last_error = error_msg
            self.last_error_code = code
            logger.error(f"Failed to connect to MetaTrader 5: {error_msg}")
            return False

    async def start_monitoring(self):
        """Launches the continuous background health monitor and reconnection loop."""
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(), name="mt5_monitor_task")
        logger.info("Started MT5 connection health check and auto-reconnection monitor.")

    async def _monitor_loop(self):
        """Continuously checks terminal health and retries when disconnected."""
        delay = settings.MT5_RETRY_BASE_DELAY

        while self._running:
            try:
                if self.state == ConnectionState.CONNECTED:
                    # Check if terminal connection is alive
                    terminal_alive = await asyncio.to_thread(lambda: mt5.terminal_info() is not None if mt5 else False)
                    if not terminal_alive:
                        logger.warning("MT5 heartbeat lost: terminal_info() returned None. Initiating reconnection...")
                        self.state = ConnectionState.RECONNECTING

                if self.state in (ConnectionState.DISCONNECTED, ConnectionState.RECONNECTING):
                    self.state = ConnectionState.RECONNECTING
                    self.reconnect_attempts += 1
                    logger.info(
                        f"Attempting MT5 reconnection #{self.reconnect_attempts} in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)

                    success = await self._connect()
                    if success:
                        self.total_reconnections += 1
                        delay = settings.MT5_RETRY_BASE_DELAY  # Reset backoff
                    else:
                        delay = min(delay * settings.MT5_RETRY_BACKOFF_FACTOR, settings.MT5_RETRY_MAX_DELAY)
                else:
                    await asyncio.sleep(settings.MT5_HEARTBEAT_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as ex:
                logger.error(f"Unexpected error in MT5 monitor loop: {ex}", exc_info=True)
                await asyncio.sleep(settings.MT5_RETRY_BASE_DELAY)

    async def shutdown(self):
        """Cleanly shuts down MT5 connection during application termination."""
        logger.info("Shutting down MT5 Manager...")
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        if mt5 is not None:
            await asyncio.to_thread(mt5.shutdown)

        self.state = ConnectionState.DISCONNECTED
        self.connected_at = None
        logger.info("MetaTrader 5 connection shutdown completed.")

    def get_status_summary(self) -> Dict[str, Any]:
        """Returns connection diagnostics for health check endpoint."""
        uptime_seconds = None
        if self.connected_at and self.state == ConnectionState.CONNECTED:
            uptime_seconds = (datetime.now(timezone.utc) - self.connected_at).total_seconds()

        return {
            "state": self.state.value,
            "is_connected": self.is_connected,
            "connected_at": self.connected_at.isoformat() if self.connected_at else None,
            "uptime_seconds": uptime_seconds,
            "reconnect_attempts": self.reconnect_attempts,
            "total_reconnections": self.total_reconnections,
            "last_error": self.last_error,
            "last_error_code": self.last_error_code,
        }


# Singleton instance shared across the entire application
mt5_manager = MT5Manager()
