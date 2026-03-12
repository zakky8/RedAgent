from .api_key_bruteforce import APIKeyBruteforce
from .jwt_manipulation import JWTManipulation
from .mfa_bypass import MFABypass
from .oauth_hijack import OAuthHijack
from .privesc_via_prompt import PrivEscViaPrompt
from .rbac_bypass import RBACBypassViaPrompt
from .service_account_takeover import ServiceAccountTakeover
from .session_fixation import SessionFixation
from .sso_abuse import SSOAbuse
from .token_replay import TokenReplay

__all__ = [
    "APIKeyBruteforce",
    "JWTManipulation",
    "MFABypass",
    "OAuthHijack",
    "PrivEscViaPrompt",
    "RBACBypassViaPrompt",
    "ServiceAccountTakeover",
    "SessionFixation",
    "SSOAbuse",
    "TokenReplay",
]
