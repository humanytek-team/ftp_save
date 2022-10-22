{
    "name": "FTP Save",
    "version": "15.0.0.1.0",
    "author": "HomebrewSoft",
    "website": "https://homebrewsoft.dev",
    "license": "LGPL-3",
    "depends": [],
    "data": [
        # security
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
