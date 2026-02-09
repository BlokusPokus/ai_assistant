"""
Prometheus /metrics HTTP server for the Celery worker (Option A).

Runs in a daemon thread so the worker can expose its metrics to Prometheus
without blocking the main Celery process. Serves the same registry updated
by record_task_execution() and update_task_metrics().
"""

import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)

_server: HTTPServer | None = None
_server_thread: threading.Thread | None = None


def _metrics_handler_factory():
    """Build a handler that serves get_metrics_service().generate_metrics() for GET /metrics."""

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/metrics":
                self.send_error(404)
                return
            try:
                from personal_assistant.monitoring import get_metrics_service

                metrics_service = get_metrics_service()
                body = metrics_service.generate_metrics()
                content_type = metrics_service.get_metrics_content_type()
            except Exception as e:
                logger.exception("Failed to generate metrics: %s", e)
                self.send_error(500)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, format, *args):
            logger.debug("metrics_server %s", args[0] if args else format)

    return _Handler


def start_metrics_server(host: str = "0.0.0.0", port: int = 9091) -> int:
    """
    Start the /metrics HTTP server in a daemon thread.
    Use port=0 to bind to an ephemeral port.
    Returns the port the server is listening on.
    """
    global _server, _server_thread
    if _server is not None:
        return _server.socket.getsockname()[1]

    server = HTTPServer((host, port), _metrics_handler_factory())
    actual_port = server.socket.getsockname()[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    _server = server
    _server_thread = thread
    logger.info("Worker metrics server listening on %s:%s", host, actual_port)
    return actual_port


def stop_metrics_server() -> None:
    """Stop the metrics server (for tests)."""
    global _server, _server_thread
    if _server is None:
        return
    _server.shutdown()
    _server = None
    _server_thread = None
    logger.debug("Worker metrics server stopped")
