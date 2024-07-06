import MetaTrader5 as mt5
import os
from dotenv import load_dotenv, find_dotenv

class PlatformConnector():

    def __init__(self, symbol_list: list):
        # Buscamos el archivo y cargamos sus valores
        load_dotenv(find_dotenv())

        #Inicializacion de la plataforma
        self._initialize_platform()

        #Comprobacion del tipo de cuenta
        self._live_account_warning()

        #Imprimimos informacion de la cuenta
        self._print_account_info()

        #Comprobacion de la opcion de trading algoritmico
        self._check_algo_trading_enabled()

        #Añadimos los simbolos al Marketwatch
        self._add_symbols_to_marketwatch(symbol_list)


    def _initialize_platform(self) -> None:
        """
        Initializes the MT5 platform.
        Raises:
            Exception: If there is any error while initializing the Platform

        Returns:
            None
        """
        if mt5.initialize(
            path=os.getenv("MT5_PATH"),
            login=int(os.getenv("MT5_LOGIN")),
            password=os.getenv("MT5_PASSWORD"),
            server=os.getenv("MT5_SERVER"),
            timeout=int(os.getenv("MT5_TIMEOUT")),
            portable=eval(os.getenv("MT5_PORTABLE"))):
            print("La plataforma de MT5 se ha lanzado con exito")
        else:
            raise Exception(f"Ha ocurrido un error al inicializar la plataforma MT5: {mt5.last_error()}")


    def _live_account_warning(self):
        #Recuperamos el objeto de tipo AccountInfo
        account_info = mt5.account_info()

        #Comprobar el tipo de cuenta que se ha lanzado
        if mt5.account_info().trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
            print("Cuenta demo")
        elif account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_REAL:
            if not input("Cuenta real, capital EN RIESGO ¿Desea continuar? (y/n) : ").lower() == "y":
                mt5.shutdown()
                raise Exception("El usuario ha decidido detener el programa")
        else:
            print("Cuenta concurso")

    def _check_algo_trading_enabled(self) -> None:

        #Vamos a comprobar que el trading algoritmico esta activado en MT5
        if not mt5.terminal_info().trade_allowed:
            raise Exception("El trading algoritmico esta deshabilitado. Actívalo manualmente en MT5 Herramientas/Opciones/Asesores Expertos")

    def _add_symbols_to_marketwatch(self, symbols: list) -> None:

        #1)Comprobamos si el simbolo ya es visible en el Marketwatch
        #2)Si no lo esta, lo añadiremos

        for symbol in symbols:
            if mt5.symbol_info(symbol) is None:
                print(f"No se ha podido añadir el simbolo {symbol} al Marketwatch: {mt5.last_error()}")
                continue

            if not mt5.symbol_info(symbol).visible:
                if not mt5.symbol_select(symbol, True):
                    print(f"No se ha podido añadir el simbolo {symbol} al Marketwatch: {mt5.last_error()}")
                else:
                    print(f"Simbolo {symbol} añadido con exito al Marketwatch")
            else:
                print(f"El simbolo {symbol} ya estaba en el Marketwatch")

    def _print_account_info(self) -> None:

        #Recuperar un objeto de tipo AccountInfo
        account_info = mt5.account_info()._asdict()

        print("+-------------- Informacion de la cuenta -------------- ")
        print(f"|- ID de la cuenta: {account_info['login']}")
        print(f"|- Nombre del trader: {account_info['name']}")
        print(f"|- Broker: {account_info['company']}")
        print(f"|- Servidor: {account_info['server']}")
        print(f"|- Apalancamiento: {account_info['leverage']}")
        print(f"|- Divisa de la cuenta: {account_info['currency']}")
        print(f"|- Balance de la cuenta: {account_info['balance']}")
        print("+-------------------------------------------------------")