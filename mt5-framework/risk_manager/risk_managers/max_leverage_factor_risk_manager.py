from events.events import SizingEvent
from ..interfaces.risk_manager_interface import IRiskManager
from ..properties.risk_manager_properties import MaxLeverageFactorRiskProps

import MetaTrader5 as mt5
import sys

class MaxLeverageFactorRiskManager(IRiskManager):

    def __init__(self, properties: MaxLeverageFactorRiskProps):
        self.max_leverage_factor = properties.max_leverage_factor

    def _compute_leverage_factor(self, account_value_acc_ccy: float) -> float:

        account_equity = mt5.account_info().equity

        if account_equity <= 0:
            return sys.float_info.max
        else:
            return account_value_acc_ccy / account_equity                                   # Factor de apalancamiento
    
    def _check_expected_new_position_is_compliant_with_max_leverage_factor(self, sizing_event: SizingEvent, current_positions_value_acc_ccy:  float, new_position_value_acc_ccy: float) -> bool:

        
        #Calculamos el nuevo expected account value que tendria la cuenta si ejecutaramos la nueva posicion
        new_account_value = current_positions_value_acc_ccy + new_position_value_acc_ccy

        #Calculamos el nuevo factor de apalancamiento si ejecutaramos esa posicion
        new_leverage_factor = self._compute_leverage_factor(new_account_value)

        #Comprobamos si el nuevo leverage factor seria mayor a nuestro maximo leverage factor
        if abs(new_leverage_factor) <= self.max_leverage_factor:
            return True
        else:
            print(f"RISK MGMT: La posicion objetivo {sizing_event.signal} {sizing_event.volume} implica un Leverage Factor de {abs(new_leverage_factor)} supera el maximo de {self.max_leverage_factor}")
            return False

    def assess_order(self, sizing_event: SizingEvent, current_positions_value_acc_ccy: float, new_position_value_acc_ccy: float) -> float:

        # Este metodo va a "dejar pasar" la operacion o no en funcion del maximo factor de apalancamiento

        if self._check_expected_new_position_is_compliant_with_max_leverage_factor(sizing_event, current_positions_value_acc_ccy, new_position_value_acc_ccy):
            return sizing_event.volume
        else:
            return 0.0