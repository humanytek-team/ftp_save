from ftplib import FTP
from io import BytesIO
from typing import Any, Dict, Iterable, Union

import pysftp
from odoo import _, api, fields, models
from odoo.exceptions import UserError

OdooAction = Dict[str, Any]


class FTPServer(models.Model):
    _name = "ftp_server"
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
        string="TLS",
        default=True,
    )
    home_path = fields.Char()

    def _full_path(self, file_path: str) -> str:
        return f"{self.home_path}/{file_path}" if self.home_path else file_path

    def upload(self, file_path: str, file_content: bytes) -> None:
        ftp_connector = self.get_ftp_connector()
        self._upload(ftp_connector, file_path, file_content)

    def _upload_ftp(self, connector: FTP, file_path: str, file_content: bytes) -> None:
        connector.storbinary(f"STOR {self._full_path(file_path)}", BytesIO(file_content))

    def _upload_sftp(
        self, connector: pysftp.Connection, file_path: str, file_content: bytes
    ) -> None:
        connector.putfo(BytesIO(file_content), self._full_path(file_path))

    def delete(self, file_path: str) -> None:
        ftp_connector = self.get_ftp_connector()
        self._delete(ftp_connector, file_path)

    def _delete(self, connector: Union[FTP, pysftp.Connection], file_path: str) -> None:
        if isinstance(connector, FTP):
            self._delete_ftp(connector, file_path)
        elif isinstance(connector, pysftp.Connection):
            self._delete_sftp(connector, file_path)
        else:
            raise TypeError(f"Unknown connector type: {type(connector)}")

    def _delete_ftp(self, connector: FTP, file_path: str) -> None:
        connector.delete(self._full_path(file_path))

    def _delete_sftp(self, connector: pysftp.Connection, file_path: str) -> None:
        connector.remove(self._full_path(file_path))

    def _upload(
        self, connector: Union[FTP, pysftp.Connection], file_path: str, file_content: bytes
    ) -> None:
        if isinstance(connector, FTP):
            self._upload_ftp(connector, file_path, file_content)
        elif isinstance(connector, pysftp.Connection):
            self._upload_sftp(connector, file_path, file_content)
        else:
            raise TypeError(f"Unknown connector type: {type(connector)}")

    def list(self, dir_path: str) -> Iterable[str]:
        ftp_connector = self.get_ftp_connector()
        return self._list(ftp_connector, dir_path)

    def _list(self, connector: Union[FTP, pysftp.Connection], dir_path: str) -> Iterable[str]:
        if isinstance(connector, FTP):
            return self._list_ftp(connector, dir_path)
        elif isinstance(connector, pysftp.Connection):
            return self._list_sftp(connector, dir_path)
        else:
            raise TypeError(f"Unknown connector type: {type(connector)}")

    def _list_ftp(self, connector: FTP, dir_path: str) -> Iterable[str]:
        dir_path = self._full_path(dir_path)
        return connector.nlst(dir_path)

    def _list_sftp(self, connector: pysftp.Connection, dir_path: str) -> Iterable[str]:
        dir_path = self._full_path(dir_path)
        return connector.listdir(dir_path)

    def download(self, file_path: str) -> bytes:
        ftp_connector = self.get_ftp_connector()
        return self._download(ftp_connector, file_path)

    def _download(self, connector: Union[FTP, pysftp.Connection], file_path: str) -> bytes:
        if isinstance(connector, FTP):
            return self._download_ftp(connector, file_path)
        elif isinstance(connector, pysftp.Connection):
            return self._download_sftp(connector, file_path)
        else:
            raise TypeError(f"Unknown connector type: {type(connector)}")

    def _download_ftp(self, connector: FTP, file_path: str) -> bytes:
        file_path = self._full_path(file_path)
        file_content = BytesIO()
        connector.retrbinary(f"RETR {file_path}", file_content.write)
        return file_content.getvalue()

    def _download_sftp(self, connector: pysftp.Connection, file_path: str) -> bytes:
        file_path = self._full_path(file_path)
        file_content = BytesIO()
        connector.getfo(file_path, file_content)
        return file_content.getvalue()

    def get_ftp_connector(self) -> Union[FTP, pysftp.Connection]:
        try:
            return self.sudo()._get_ftp_connector()
        except Exception as e:
            raise UserError(_("Connection failed: %s") % e)

    def _get_ftp_connector(self) -> Union[FTP, pysftp.Connection]:
        host = self.host
        port = self.port
        username = self.user
        password = self.password
        ftp_tls = self.tls
        if ftp_tls:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            return pysftp.Connection(
                host=host, username=username, password=password, cnopts=cnopts, port=port
            )
        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(username, password)
        return ftp

    def test_connection(self) -> OdooAction:
        self.get_ftp_connector()
        title = _("FTP Connection Test Succeeded!")
        message = _("Everything seems properly set up!")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "sticky": False,
            },
        }
