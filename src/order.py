import logging
import yaml
import sys, getopt

from binance.client import Client
from binance.enums import *


logging.basicConfig(format='%(asctime)s - (%(threadName)-10s) - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
LOG = logging.getLogger(__name__)


api = None
with open("src/key.yaml", 'r') as stream:
    try:
        api = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        raise Exception("Can not load key/secret")


client = Client(api['k'], api['s'])

LOG.info("Account info...")
status = client.get_account_status()
LOG.info(status)


def get_qty(opts):
    for opt, arg in opts:
        if opt in ('-q', '--qty'):
            return float(arg)
    return None


def get_price(opts):
    for opt, arg in opts:
        if opt in ('-p', '--price'):
            return float(arg)
    return None


def get_order_id(opts):
    for opt, arg in opts:
        if opt in ('-i', '--orderid'):
            return arg
    return None


def check_orders(symbol=None):
    LOG.info(f"Check orders of symbol {symbol}...")
    balances = { b['asset']: b for b in client.get_account()["balances"] if (float(b["free"]) > .5 or float(b["locked"]) > .5) }
    order_info = "\n"
    for b in sorted(balances.keys()):
        if symbol and not symbol.upper().startswith(b):
            continue
        for o in client.get_open_orders():
            if not o['symbol'].startswith(b) or (symbol and symbol.upper() != o['symbol']):
                continue
            unit = o['symbol'].replace(b, '')
            qty = float(o['origQty'])
            price = float(o['price'])
            value = qty * price
            order_info = order_info + f"Order {o['symbol']} ({o['status']}): ID: {o['orderId']} - {o['type']} - {value:9.2f} {unit} Qty. {qty:9.2f} Price {price:9.2f} {unit}\n"
    LOG.info(f"{order_info}")


def cancel_order(symbol=None, order_id=None):
    if not symbol:
        LOG.error(f"Can not cancel order of a UNDEFINED symbol!")
        pass
    if not order_id:
        LOG.error(f"Can not cancel order of a UNDEFINED order-id!")
        pass
    r = client.cancel_order(
        symbol=symbol.upper(),
        orderId=order_id
    )
    LOG.info(f"{r['status']}::{r['side']} order of {r['symbol']} - Price {r['price']} Qty. {r['origQty']}")


def place_order(symbol=None, qty=0.0, price=0.0, type=None):
    if not symbol:
        LOG.error(f"Can not place order of a UNDEFINED symbol!")
        pass
    if not type or not type in ('sell', 'buy'):
        LOG.error(f"Can not place order of a UNDEFINED type!")
        pass
    if qty <= 0.0:
        LOG.error(f"Can not place order of a INVALID quantity!")
        pass
    if qty <= 0.0:
        LOG.error(f"Can not place order of a INVALID price!")
        pass
    r = client.create_order(
        symbol=symbol.upper(),
        side=SIDE_BUY if type == 'buy' else SIDE_SELL,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=qty,
        price=str(price)
    )
    LOG.info(f"{r['status']}::{r['side']} order of {r['symbol']} - Price {r['price']} Qty. {r['origQty']}")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hs:b:c:q:p:i:v", ["sell=", "buy=", "cancel=", "qty=", "price=", "orderid=", "view="])
    except getopt.GetoptError as e:
        LOG.error(e, exc_info=True)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(
                """
    Place a sell order            
    python|python3.8 ./order.py -s <symbol> -q <qty> -p <price> 

    Place a buy order            
    python|python3.8 ./order.py -b <symbol> -q <qty> -p <price> 
        
    Cancel a order
    python|python3.8 ./order.py -c <symbol> -i <order_id>
    
    View open orders of a symbol. If symbol not defined, all open orders will be shown
    python|python3.8 ./order.py -s <symbol> -v 

        -s/--sell: e.g. -s ETHBTC
        -b/--buy: e.g. -b ETHBTC
        -c/--cancel: e.g. -c ETHBTC     
        -i/--orderid: which order_id should be canceled
        -q/--qty
        -p/--price
        -v/--view: list all current open orders
                """
            )
            sys.exit()
        elif opt in ("-c", "--cancel"):
            cancel_order(symbol=arg, order_id=get_order_id(opts))
            sys.exit()
        elif opt in ("-s", "--sell"):
            place_order(symbol=arg, qty=get_qty(opts), price=get_price(opts), type='sell')
            sys.exit()
        elif opt in ("-b", "--buy"):
            place_order(symbol=arg, qty=get_qty(opts), price=get_price(opts), type='buy')
            sys.exit()
        elif opt in ("-v", "--view"):
            check_orders(arg if opt == "--view" else args[0] if len(args) > 0 else None)


if __name__ == "__main__":
    main(sys.argv[1:])
