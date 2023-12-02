import logging
from ftplib import FTP
from io import BytesIO
from typing import Union

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:
    _logger.error("pysftp not installed, sftp will not be available")


class FTPServer(models.Model):
    _name = "ftp_server"
    _description = "FTP Server"
    _rec_name = "host"

    host = fields.Char(
        index=True,
        required=True,
    )
    port = fields.Integer(
        default=21,
        required=True,
    )
    user = fields.Char()
    password = fields.Char(
        groups="ftp_save.group_ftp_server_admin",
    )
    tls = fields.Boolean(
        default=True,
    )
    home_path = fields.Char()

    def _full_path(self, file_path: str) -> str:
        return f"{self.home_path}/{file_path}" if self.home_path else file_path

    def upload(self, file_path: str, file_content: bytes) -> None:
        ftp_connector = self.get_ftp_connector()
        self._upload(ftp_connector, file_path, file_content)

    def _upload_ftp(self, connector: FTP, file_path: str, file_content: bytes) -> None:
        connector.storbinary(
            f"STOR {self._full_path(file_path)}", BytesIO(file_content)
        )

    def _upload_sftp(
        self, connector: pysftp.Connection, file_path: str, file_content: bytes
    ) -> None:
        connector.putfo(BytesIO(file_content), self._full_path(file_path))

    def _upload(
        self,
        connector: Union[FTP, pysftp.Connection],
        file_path: str,
        file_content: bytes,
    ) -> None:
        if isinstance(connector, FTP):
            self._upload_ftp(connector, file_path, file_content)
        elif isinstance(connector, pysftp.Connection):
            self._upload_sftp(connector, file_path, file_content)
        else:
            raise TypeError(f"Unknown connector type: {type(connector)}")

    def get_ftp_connector(self) -> Union[FTP, pysftp.Connection]:
        host = self.host
        port = self.port
        username = self.user
        password = self.password
        ftp_tls = self.tls
        if ftp_tls:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            return pysftp.Connection(
                host=host,
                username=username,
                password=password,
                cnopts=cnopts,
                port=port,
            )
        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        return ftp

    def test_connection(self) -> bool:
        try:
            self.get_ftp_connector()
            return True
        except Exception as e:
            raise e
