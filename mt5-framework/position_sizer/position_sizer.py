from data_provider.data_provider import DataProvider
from events.events import SignalEvent,SizingEvent
from .interfaces.position_sizer_interface import IPositionSizer
from .properties.position_sizer_properties import BaseSizerProps,MinSizingProps,FixedSizingProps,RiskPctSizingProps
from .position_sizers.min_size_position_sizer import MinSizePositionSizer
from .position_sizers.fixed_size_position_sizer import FixedSizePositionSizer
from .position_sizers.risk_pct_position_sizer import RiskPctPositionSizer

import MetaTrader5 as mt5

from queue import Queue

class PositionSizer(IPositionSizer):

    def __init__ (self, events_queue: Queue, data_provider: DataProvider, sizing_properties: BaseSizerProps):
        self.events_queue = events_queue
        self.DATA_PROVIDER = data_provider
        self.position_sizing_method = self._get_position_sizing_method(sizing_properties)


    def _get_position_sizing_method(self, sizing_props: BaseSizerProps) -> IPositionSizer:
        """
        Devuelve una instancia del PositionSizer apropiado en funcion del objeto de propiedades recibido
        """
        if isinstance(sizing_props, MinSizingProps):
            return  MinSizePositionSizer()
        elif isinstance(sizing_props, FixedSizingProps):
            return FixedSizePositionSizer(properties=sizing_props)
        elif isinstance(sizing_props, RiskPctSizingProps):
            return RiskPctPositionSizer(properties=sizing_props)
        
        else:
            raise Exception(f"ERROR: Metodo de sizing desconocido: {sizing_props}")

    
    def _create_and_put_sizing_event(self, signal_event: SignalEvent, volume: float) -> None:
        
        # Creamos el SizingEvent a partir del SignalEvent y el volume
        sizing_event = SizingEvent(symbol=signal_event.symbol,
                                    signal=signal_event.signal,
                                    target_order=signal_event.target_order,
                                    target_price=signal_event.target_price,
                                    magic_number=signal_event.magic_number,
                                    sl=signal_event.sl,
                                    tp=signal_event.tp,
                                    volume=volume)

        # Colocamos el SizingEvent a la cola de eventos
        self.events_queue.put(sizing_event)


    def size_signal(self, signal_event: SignalEvent) -> None:
        
        # Obtener el volumen adecuado segun el metodo de sizing
        volume = self.position_sizing_method.size_signal(signal_event, self.DATA_PROVIDER)

        if volume < mt5.symbol_info(signal_event.symbol).volume_min:
            print(f"ERROR: El volumen {volume} es menmor al volumen minimo admitido por el simbolo {signal_event.symbol}")
            return

        # Colocar este volumen dentro de un sizing_event
        # Colocar el sizing event a la events_queue
        self._create_and_put_sizing_event(signal_event, volume)