{
    "name": "FTP Save",
    "version": "15.0.0.1.0",
    "author": "Humanytek",
    "license": "LGPL-3",
    "depends": [],
    "data": [
        # security
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        # data
        # reports
        # views
        "views/ftp_server.xml",
    ],
    "external_dependencies": {
        "python": ["pysftp"],
    },
}
