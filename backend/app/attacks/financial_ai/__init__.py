"""Financial AI security attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []

try:
    from .market_manipulation import MarketManipulationAttack
    attack_classes.append(MarketManipulationAttack)
except Exception:
    pass

try:
    from .fraud_enablement import FraudEnablement
    attack_classes.append(FraudEnablement)
except Exception:
    pass

try:
    from .insider_trading_assist import InsiderTradingAssist
    attack_classes.append(InsiderTradingAssist)
except Exception:
    pass

try:
    from .tax_evasion_advice import TaxEvasionAdvice
    attack_classes.append(TaxEvasionAdvice)
except Exception:
    pass

try:
    from .loan_fraud_assist import LoanFraudAssist
    attack_classes.append(LoanFraudAssist)
except Exception:
    pass

try:
    from .financial_model_poisoning import FinancialModelPoisoning
    attack_classes.append(FinancialModelPoisoning)
except Exception:
    pass

try:
    from .algo_trading_exploit import AlgoTradingExploit
    attack_classes.append(AlgoTradingExploit)
except Exception:
    pass

try:
    from .aml_bypass import AMLBypass
    attack_classes.append(AMLBypass)
except Exception:
    pass

__all__ = ["attack_classes"]
