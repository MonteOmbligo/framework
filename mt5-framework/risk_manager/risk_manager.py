from .interfaces.risk_manager_interface import IRiskManager
from .properties.risk_manager_properties import BaseRiskProps, MaxLeverageFactorRiskProps
from .risk_managers.max_leverage_factor_risk_manager import MaxLeverageFactorRiskManager
from data_provider.data_provider import DataProvider
from portfolio.portfolio import Portfolio
from events.events import SizingEvent, OrderEvent
from utils.utils import Utils
from queue import Queue
import MetaTrader5 as mt5

class RiskManager(IRiskManager):

    def __init__(self, events_queue: Queue, data_provider: DataProvider, portfolio: Portfolio, risk_properties: BaseRiskProps):
        self.events_queue = events_queue
        self.DATA_PROVIDER = data_provider
        self.PORTFOLIO = portfolio

        self.risk_management_method = self._get_risk_management_method(risk_properties)


    def _get_risk_management_method(self, risk_props: BaseRiskProps) -> IRiskManager:

        if isinstance(risk_props, MaxLeverageFactorRiskProps):
            return MaxLeverageFactorRiskManager(risk_props)
        else:
            raise Exception(f"ERROR: Metodo de Risk Management desconocido: {risk_props}")
        
    def _compute_current_value_of_positions_in_account_currency(self) -> float:
        #Recopilamos las posiciones abiertas por nuestra estrategia
        current_positions = self.PORTFOLIO.get_strategy_open_positions()

        #Vamos a calcular el valor de las posiciones abiertas
        total_value = 0.0
        for position in current_positions:
            total_value += self._compute_value_of_position_in_account_currency(position.symbol, position.volume, position.type)
        
        return total_value
    
    def _compute_value_of_position_in_account_currency(self, symbol: str, volume: float, position_type: int) -> float:

        symbol_info = mt5.symbol_info(symbol)

        #Unidades operadas en las unidades del symbol: (Cantidad de moneda base, barriles de petroleo, onzas de oro...)
        traded_units = volume * symbol_info.trade_contract_size

        #Valor de las unidades operadas en la divisa cotizada del simbolo (USD para el Oro, petroleo... EUR para el DAX...)
        value_traded_in_profit_ccy = traded_units * self.DATA_PROVIDER.get_latest_tick(symbol)['bid']

        #Valor de las unidades operadas en la divisa de nuestra cuenta (la cuenta en el broker, cuenta de MT5)
        value_traded_in_account_ccy = Utils.convert_currency_amount_to_another_currency(value_traded_in_profit_ccy, symbol_info.currency_profit, mt5.account_info().currency)

        if position_type == mt5.ORDER_TYPE_SELL:
            return -value_traded_in_account_ccy
        else:
            return value_traded_in_account_ccy
        
    def _create_and_put_order_event(self, sizing_event: SizingEvent, volume: float) -> None:

        # Creamos el OrderEvent a partir del SizingEvent y el volume
        order_event = OrderEvent(symbol=sizing_event.symbol,
                                signal=sizing_event.signal,
                                target_order=sizing_event.target_order,
                                target_price=sizing_event.target_price,
                                magic_number=sizing_event.magic_number,
                                sl=sizing_event.sl,
                                tp=sizing_event.tp,
                                volume=volume)

        # Colocamos el OrderEvent a la cola de eventos
        self.events_queue.put(order_event)
        
    def assess_order(self, sizing_event: SizingEvent) -> None:
        
        #Obtenemos el valor de todas las posiciones abiertas por la estrategia
        current_position_value = self._compute_current_value_of_positions_in_account_currency()
        
        #Obtenemos el valor que tendria la nueva posicion tambien en la divisa de la cuenta
        position_type = mt5.ORDER_TYPE_BUY if sizing_event.signal == "BUY" else mt5.ORDER_TYPE_SELL
        new_position_value = self._compute_value_of_position_in_account_currency(sizing_event.symbol, sizing_event.volume, position_type)

        #Obtenemos el nuevo volumen de la operacion que queremos ejecutar despues de pasar por el risk manager
        new_volume = self.risk_management_method.assess_order(sizing_event, current_position_value, new_position_value)

        #Evaluamos el nuevo volumen
        if new_volume > 0.0:
            #Colocar el OrderEvent en la cola de eventos
            self._create_and_put_order_event(sizing_event, new_volume)