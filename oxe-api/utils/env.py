from config.config import ENVIRONMENT, BASE_DOMAIN


def get_admin_portal_url():
    if ENVIRONMENT == "dev":
        return "http://localhost:3000"
    return "".join(["https://openxecoadmin.jenusplanet.com"])


def get_community_portal_url():
    if ENVIRONMENT == "dev":
        return "http://localhost:3000"
    return "".join(["https://openxecocommunity.jenusplanet.com"])
