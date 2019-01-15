import logging
# You shouldn't be here, but as you already are, maybe you want faster loading times? Check the DEV constant.

# If you want faster loading, but with some visual glitches at the startup (words rapidly changing) while it loads,
# change this to "True" (no quotes, capitalized), else, leave it as "False"
DEV = True

# Do not change BASE_URL under no circumstances.
BASE_URL = 'http://dedeco.me'
BASE_URL = 'http://127.0.0.1'

if not 'https://' in BASE_URL or DEV:
    from warnings import warn

    if not 'https://' in BASE_URL:
        warn("Not using HTTPS for communications, this is insecure! Please change BASE_URL for production.", Warning)

    if DEV:
        warn("Using DEV mode. Please change DEV to False for production.", Warning)

# URLS:
BUG_REPORT_URL = BASE_URL + "/api/bug-report"
VERSION_CONTROL_URL = BASE_URL + "/api/version-control"
CREATE_ACCOUNT_URL = BASE_URL + "/api/create-account"
VALIDATE_TOKEN_URL = BASE_URL + "/api/validate-token"
SCORE_URL = BASE_URL + '/api/check-score'
UPLOAD_DATA_URL = BASE_URL + "/api/data-upload"
RANKING_URL = BASE_URL + "/ranking"
HOME_PAGE_URL = BASE_URL + "/home"
LOGIN_URL = BASE_URL + "/accounts/reddit/login/"
GET_TOKEN_URL = BASE_URL + "/ranking/?token=show"

# Version info
VERSION = 1.1
RELEASE_DATE = "2018-06-23"
