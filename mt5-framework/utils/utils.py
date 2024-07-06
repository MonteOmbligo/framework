import MetaTrader5 as mt5

# Crear un metodo estatico para poder convertir una divisa a otra
class Utils():
    
    def __init__(self):
        pass

    @staticmethod
    def convert_currency_amount_to_another_currency(amount: float, from_ccy: str, to_ccy: str):
        
        all_fx_symbol = ("AUDCAD", "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD", "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD",
                        "EURCHF", "EURGBP", "EURJPY", "EURNZD", "EURUSD", "GBPAUD", "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD",
                        "GBPUSD", "NZDCAD", "NZDCHF", "NZDJPY", "NZDUSD", "USDCAD", "USDCHF", "USDJPY", "USDSEK", "USDNOK")
        
        # Convertir las divisas a mayusculas
        from_ccy = from_ccy.upper()
        to_ccy = to_ccy.upper()

        # Buscamos el simbolo que relaciona nuestra divisa origen con su divisa destino (list comprehension)
        fx_symbol = [symbol for symbol in all_fx_symbol if from_ccy in symbol and to_ccy in symbol][0]                                 # for symbol in all_fx_symbol:
        fx_symbol_base = fx_symbol[:3]
        # Recuperamos los ultimos datos disponibles del fx_symbol
        try:
            tick = mt5.symbol_info_tick(fx_symbol)
            if tick is None:
                raise Exception(f"El simbolo {fx_symbol} no está disponible en la plataforma MT5. Por favor revisa los simbolos disponibles de tu broker")

        except Exception as e:
            print(f"ERROR: No se pudo recuperar el ultimo tick del simbolo {fx_symbol}. MT5 Error: {mt5.last_error()}, Exception: {e}")
            return 0.0
        
        else:
            # Recuperamos el ultimo precio disponible del simbolo
            last_price = tick.bid

            # Convertimos la cantidad de la divisa origen a la de destino
            converted_amount = amount / last_price if fx_symbol_base == to_ccy else amount * last_price
            return converted_amount

        
