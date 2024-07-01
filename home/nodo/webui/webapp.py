#!/usr/bin/env python

from io import TextIOWrapper
from dasbus.connection import SystemMessageBus
import socket
import psutil
import threading
import subprocess as proc
import sys
import json
import requests
import os
from requests.auth import HTTPDigestAuth
from requests import JSONDecodeError
import dash
import dash_bootstrap_components as dbc
import dash_qr_manager as dqm
from dash_breakpoints import WindowBreakpoints
from dash import Input, Output, State, dcc, html
from dash_iconify import DashIconify
import datetime
import re
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
import dash_daq as daq
from dash import dash_table
import pandas as pd
from pandas import json_normalize
from furl import furl
from dataclasses import dataclass

api: str = "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies={0}&precision=2"


def get_rate(cur="usd") -> str:
    r = requests.get(api.format(cur))
    resp = r.json()
    if "error_code" in resp["status"]:
        print(resp["status"]["error_code"])
        return "???.??"

    return resp["monero"][cur] or "???.??"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


class TimerThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(2):
            update_config()
            # call a function


# parameters
# Page 0 : Python dictionary variables for ui status
page0_sync_status = {}
page0_system_status = {}
page0_hardware_status = {}

# Page 1 : Python dictionary variables for ui status
page1_networks_clearnet = {}
page1_networks_tor = {}
page1_networks_i2p = {}

# Page 2 : Python dictionary variables for ui status
page2_node_rpc = {}
page2_node_bandwidth = {}

# Page 3 : Python dictionary variables for ui status
page3_device_wifi = {}
page3_device_ethernet = {}
page3_device_system = {}

# Page 4.1 ( AWS Admin -> Active )
active_address_height = []

# Page 4.1 ( AWS Admin -> Active -> Deactivate )
# Page 4.2 ( AWS Admin -> InActive )
inactive_address_height = []

# Page 4.3 ( AWS Admin -> Add Account )
# Page 4.4 ( AWS Admin -> Account Creation Requests )
account_address_viewkey_height = []

switch_col: str = "#ff5100"

# Page 5.1 ( BLOCK EXPLORER -> TRANSACTION POOL )
# transaction_pool_information={}

conf_dict: dict = dict()
conf_file: str = "/home/nodo/variables/config.json"

node_dict: dict = dict()

statustable: dict = {
    "dead\n": "Inactive",
    "failed\n": "Inactive (failed)",
    "exited\n": "Stopped",
    "auto-restart\n": "Stopped",
    "running\n": "Running",
    "active\n": "Active",
    "activating\n": "Starting",
    "deactivating\n": "Stopping",
}


def node_info():
    global node_dict
    p = conf_dict["config"]["monero_public_port"]
    try:
        auth = None
        if conf_dict["config"]["rpc_enabled"] == "TRUE":
            auth = HTTPDigestAuth(
                conf_dict["config"]["rpcu"], conf_dict["config"]["rpcp"]
            )
        r = requests.get("http://127.0.0.1:" + str(p) + "/get_info", auth=auth)
        node_dict = r.json()
    except (IOError, JSONDecodeError) as e:
        print("connection to monerod failed")
        print(e)
    return node_dict


def load_config():
    with open(conf_file, "r") as json_file:
        global conf_dict
        conf_dict = json.load(json_file)


lws_command = "/home/nodo/monero-lws/build/src/monero-lws-admin"
update_time: datetime.datetime = datetime.datetime.now()
written: bool = True
applied: bool = True
timedelta_config: datetime.timedelta = datetime.timedelta(seconds=10)
timedelta_restart: datetime.timedelta = datetime.timedelta(seconds=30)

timedelta_ticker: datetime.timedelta = datetime.timedelta(hours=6)
time_ticker: datetime.datetime = datetime.datetime.now()
price: str = "$" + str(get_rate())
lockfile: str = "/home/nodo/variables/config.json.lock"

bus = SystemMessageBus()

backend_obj = bus.get_proxy(
    "com.monero.nodo",
    "/com/monero/nodo"
)

def update_price():
    global price
    global timedelta_ticker
    global time_ticker
    if time_ticker < datetime.datetime.now() - timedelta_ticker:
        time_ticker = datetime.datetime.now()
        price = "$" + str(get_rate())


def write_config():
    global written
    if conf_dict == None:
        return

    if os.path.isfile(lockfile):
        print("Config.json locked...")
    else:
        open(lockfile, 'a').close()
        with open(conf_file, "w") as outfile:
            outfile.write(json.dumps(conf_dict, indent=2))
        os.remove(lockfile)
        written = True


def update_config():
    global written, applied
    if not written and update_time < datetime.datetime.now():
        write_config()
    if not applied and update_time < datetime.datetime.now() - timedelta_restart:
        backend_obj.serviceManager("restart", "monero-lws block-explorer monerod")
        miner: bool = conf_dict["config"]["mining"]["enabled"] == "TRUE"
        backend_obj.serviceManager("enable" if miner else "disable", "xmrig")
        backend_obj.serviceManager("start" if miner else "stop", "xmrig")
        applied = True


def save_config():
    global update_time
    global written, applied
    update_time = datetime.datetime.now() + timedelta_config
    written = applied = False


# ====================================================================
# Description: load values for page0 web ui
# page0_sync_status     : datatype python dictionary
# page0_system_status   : datatype python dictionary
# page0_hardware_status : datatype python dictionary
# ====================================================================
def load_page0_values():
    global page0_sync_status
    global page0_system_status
    global page0_hardware_status
    global page2_node_rpc
    ## Page 0

    # Monero
    page0_sync_status["sync_status"] = "Loading data"

    # rpc_switch = (conf_dict["config"]["rpc_enabled"] == "TRUE")
    # mode = {1: "Private", 2: "Public"}[rpc_switch]

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================
    load_config()
    page0_sync_status = node_info().copy()

    if page0_sync_status["synchronized"]:
        page0_sync_status["sync_status"] = "Synchronized"
    else:
        if page0_sync_status["busy_syncing"]:
            page0_sync_status["sync_status"] = "Syncing..."
        else:
            page0_sync_status["sync_status"] = "Not syncing..."

    s: list[str] = ["systemctl", "show", "--no-pager", "--property=SubState", ""]
    s[4] = "monerod"
    page0_system_status["mainnet_node"] = statustable[
        proc.run(s, stdout=proc.PIPE).stdout.decode().split("=")[1]
    ]  # + " ({0})".format(mode)

    s[4] = "tor"
    page0_system_status["tor_node"] = statustable[
        proc.run(s, stdout=proc.PIPE).stdout.decode().split("=")[1]
    ]

    s[4] = "i2pd"
    page0_system_status["i2p_node"] = statustable[
        proc.run(s, stdout=proc.PIPE).stdout.decode().split("=")[1]
    ]

    s[4] = "monero-lws"
    page0_system_status["monero_lws_admin"] = statustable[
        proc.run(s, stdout=proc.PIPE).stdout.decode().split("=")[1]
    ]

    s[4] = "block-explorer"
    page0_system_status["block_explorer"] = statustable[
        proc.run(s, stdout=proc.PIPE).stdout.decode().split("=")[1]
    ]

    page0_hardware_status["cpu_percentage"] = backend_obj.getAverageCPUFreq
    page0_hardware_status["primary_storage"] = backend_obj.getSystemStorageUsage
    page0_hardware_status["backup_storage"] = backend_obj.getBlockchainStorageUsage
    page0_hardware_status["ram_percentage"] = backend_obj.getRamUsage


# ====================================================================
# Description: load values for page1 web ui (Networks)
# page1_networks_clearnet : datatype python dictionary
# page1_networks_tor      : datatype python dictionary
# page1_networks_i2p      : datatype python dictionary
# ====================================================================
def load_page1_values():
    global page1_networks_clearnet
    global page1_networks_tor
    global page1_networks_i2p
    ## Page 1

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================
    load_config()
    c: dict = conf_dict["config"]
    page1_networks_clearnet["address"] = get_ip()
    page1_networks_clearnet["port"] = c["monero_public_port"]
    page1_networks_clearnet["peer"] = c["add_clearnet_peer"]

    page1_networks_tor["tor_switch"] = 1 if c["tor_enabled"] == "TRUE" else 0
    page1_networks_tor["port"] = c["tor_port"]
    page1_networks_tor["onion_addr"] = c["onion_addr"]
    page1_networks_tor["peer"] = c["add_tor_peer"]
    page1_networks_tor["route_all_connections_through_tor_switch"] = (
        1 if c["torproxy_enabled"] == "TRUE" else 0
    )

    page1_networks_i2p["i2p_switch"] = 1 if c["i2p_enabled"] == "TRUE" else 0
    page1_networks_i2p["port"] = c["i2p_port"]
    page1_networks_i2p["i2p_b32_addr"] = c["i2p_b32_addr_rpc"]
    page1_networks_i2p["peer"] = c["add_i2p_peer"]


# ====================================================================
# Description: load values for page2 web ui (Node)
# page2_node_rpc            : datatype python dictionary
# page2_node_bandwidth      : datatype python dictionary
# ====================================================================
def load_page2_values():
    global page2_node_rpc
    global page2_node_bandwidth
    ## Page 2

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================
    load_config()
    c: dict = conf_dict["config"]

    page2_node_rpc["rpc_switch"] = 1 if c["rpc_enabled"] == "TRUE" else 0
    page2_node_rpc["port"] = c["monero_port"]
    page2_node_rpc["username"] = c["rpcu"]
    page2_node_rpc["password"] = c["rpcu"]

    page2_node_bandwidth["incoming_peers_limit"] = c["in_peers"]
    page2_node_bandwidth["outgoing_peers_limit"] = c["out_peers"]
    page2_node_bandwidth["rate_limit_up"] = c["limit_rate_up"]
    page2_node_bandwidth["rate_limit_down"] = c["limit_rate_down"]


# ====================================================================
# Description: load values for page3 web ui (Device)
# page3_device_wifi         : datatype python dictionary
# page3_device_ethernet     : datatype python dictionary
# page3_device_system       : datatype python dictionary
# ====================================================================
def load_page3_values():
    global page3_device_wifi
    global page3_device_ethernet
    global page3_device_system
    ## Page 3

    # Device -> System
    page3_device_system = {}

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================
    load_config()
    w: dict = conf_dict["config"]["wifi"]
    page3_device_wifi["wifi_switch"] = 1 if w["enabled"] == "TRUE" else 0
    page3_device_wifi["automatic_switch"] = 1 if w["auto"] == "TRUE" else 0
    page3_device_wifi["status"] = proc.run(
        ["nmcli", "-c", "no", "-t", "-f", "WIFI", "general"], stdout=proc.PIPE
    ).stdout.decode()
    page3_device_wifi["ssid"] = w["ssid"]
    page3_device_wifi["ssids"] = w["ssids"]
    page3_device_wifi["passphrase"] = w["pw"]
    page3_device_wifi["ip_address"] = w["ip"]
    page3_device_wifi["subnet_mask"] = w["subnet"]
    page3_device_wifi["router"] = w["router"]
    page3_device_wifi["dhcp"] = w["dhcp"]

    w: dict = conf_dict["config"]["ethernet"]
    f: TextIOWrapper = open("/sys/class/net/eth0/operstate", "r")
    page3_device_ethernet["status"] = f.read()
    page3_device_ethernet["automatic_switch"] = 1 if w["auto"] == "TRUE" else 0
    page3_device_ethernet["ip_address"] = w["ip"]
    page3_device_ethernet["subnet_mask"] = w["subnet"]
    page3_device_ethernet["router"] = w["router"]
    page3_device_ethernet["dhcp"] = w["dhcp"]
    f.close()


# ====================================================================
# Description: load values for page4 web ui (LWS Admin)
# active_address_height          : datatype python list
# inactive_address_height        : datatype python list
# account_address_viewkey_height : datatype python list
# ====================================================================
def load_page4_values():
    # Page 4.1 ( AWS Admin -> Active )
    # [ [adress,height,rescan_height], [adress,height,rescan_height], ... ]
    # Example:
    # [ ['4567', '100', ''], ['45678', '100', ''] ... ]
    global active_address_height

    # Page 4.1 ( AWS Admin -> Active -> Deactivate )
    # Page 4.2 ( AWS Admin -> InActive )
    # [ [adress,height,rescan_height], [adress,height,rescan_height], ... ]
    # Example:
    # [ ['4567', '100', ''], ['45678', '100', ''] ... ]
    global inactive_address_height

    # Page 4.3 ( AWS Admin -> Add Account )
    # Page 4.4 ( AWS Admin -> Account Creation Requests )
    # [ [adress,private_viewkey,height], [adress,private_viewkey,height], ... ]
    # Example:
    # [ ['4567', '1111', '100'], '45678', '11111', '100'] ... ]
    global account_address_viewkey_height

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python list type
    # ...
    # ================================================================


FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

# Meta tags for viewport responsiveness
meta_viewport = {
    "name": "viewport",
    "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
}

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
)

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "display": "block",
    "position": "float",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "10rem",
    # "padding": "1rem 1rem",
    "background-color": "#000000",
    "border-color": "#000000",
}
submenu_1 = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col(("Networks").upper()),
                dbc.Col(html.I(className="fas fa-chevron-right mr-3"), width="auto"),
            ],
            className="my-2",
        ),
        id="submenu-1",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        dbc.Nav(
            [
                dbc.NavLink(
                    ("Clearnet").upper(), href="/networks/clearnet", active="partial"
                ),
                dbc.NavLink(("Tor").upper(), href="/networks/tor", active="partial"),
                dbc.NavLink(("I2P").upper(), href="/networks/i2p", active="partial"),
            ],
            pills=True,
            className="d-flex flex-column",
        ),
        id="submenu-1-collapse",
    ),
]

submenu_2 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col(("Node").upper()),
                dbc.Col(html.I(className="fas fa-chevron-right mr-3"), width="auto"),
            ],
            className="my-2",
        ),
        id="submenu-2",
    ),
    dbc.Collapse(
        dbc.Nav(
            [
                dbc.NavLink(
                    ("Private Node").upper(),
                    href="/node/private-node",
                    active="partial",
                ),
                dbc.NavLink(
                    ("Bandwidth").upper(), href="/node/bandwidth", active="partial"
                ),
            ],
            pills=True,
            className="d-flex flex-column",
        ),
        id="submenu-2-collapse",
    ),
]

submenu_3 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col(("Device").upper()),
                dbc.Col(html.I(className="fas fa-chevron-right mr-3"), width="auto"),
            ],
            className="my-2",
        ),
        id="submenu-3",
    ),
    dbc.Collapse(
        dbc.Nav(
            [
                dbc.NavLink(("Wi-Fi").upper(), href="/device/wifi", active="partial"),
                dbc.NavLink(
                    ("Ethernet").upper(), href="/device/ethernet", active="partial"
                ),
                dbc.NavLink(
                    ("System").upper(), href="/device/system", active="partial"
                ),
            ],
            pills=True,
            className="d-flex flex-column",
        ),
        id="submenu-3-collapse",
    ),
]

submenu_4 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col(("Monero-LWS").upper()),
                dbc.Col(html.I(className="fas fa-chevron-right mr-3"), width="auto"),
            ],
            className="my-2",
        ),
        id="submenu-4",
    ),
    dbc.Collapse(
        dbc.Nav(
            [
                dbc.NavLink(("Active").upper(), href="/lws/active", active="partial"),
                dbc.NavLink(
                    ("Inactive").upper(), href="/lws/inactive", active="partial"
                ),
                dbc.NavLink(
                    ("Add Account").upper(), href="/lws/add-account", active="partial"
                ),
                dbc.NavLink(
                    ("Account Creation Requests").upper(),
                    href="/lws/requests",
                    active="partial",
                ),
            ],
            pills=True,
            className="d-flex flex-column",
        ),
        id="submenu-4-collapse",
    ),
]


submenu_5 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col(("Block Explorer").upper()),
                dbc.Col(html.I(className="fas fa-chevron-right mr-3"), width="auto"),
            ],
            className="my-2",
        ),
        id="submenu-5",
    ),
    dbc.Collapse(
        dbc.Nav(
            [
                dbc.NavLink(
                    ("Transaction Pool").upper(),
                    href="/block-explorer/tx-pool",
                    active="partial",
                ),
                dbc.NavLink(
                    ("Transaction Pusher").upper(),
                    href="/block-explorer/tx-pusher",
                    active="partial",
                ),
                dbc.NavLink(
                    ("Key Images Checker").upper(),
                    href="/block-explorer/key-images-checker",
                    active="partial",
                ),
                dbc.NavLink(
                    ("Output Keys Checker").upper(),
                    href="/block-explorer/output-keys-checker",
                    active="partial",
                ),
            ],
            pills=True,
            className="d-flex flex-column",
        ),
        id="submenu-5-collapse",
    ),
]
# make a reuseable navitem for the different examples
nav_item = dbc.NavItem(dbc.NavLink("Link", href="#"))

# make a reuseable dropdown for the different examples
NetworkDropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem(("Clearnet").upper(), href="/networks/clearnet"),
        dbc.DropdownMenuItem(("Tor").upper(), href="/networks/tor"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem(("I2P").upper(), href="/networks/i2p"),
    ],
    nav=True,
    in_navbar=True,
    label="Networks",
    # toggle_style={
    #    "color": "white",
    #    "background": "#000000",
    #    "border-color": "#000000",
    # },
    # className="dropdownNodo",
    # toggleClassName="fst-italic border border-dark",
)
NodeDropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("RPC", href="/node/private-node"),
        dbc.DropdownMenuItem("Bandwidth", href="/node/bandwidth"),
    ],
    nav=True,
    in_navbar=True,
    label="Node",
    # toggle_style={
    #    "color": "white",
    #    "background": "#000000",
    # },
    # toggleClassName="fst-italic border border-dark",
)
DeviceDropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Wi-Fi", href="/device/wifi"),
        dbc.DropdownMenuItem("Ethernet", href="/device/ethernet"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("System", href="/device/system"),
    ],
    nav=True,
    in_navbar=True,
    label="Device",
    # toggle_style={
    #    "color": "white",
    #    "background": "#000000",
    # },
    # toggleClassName="fst-italic border border-dark",
)
LWSAdminDropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Active", href="/lws/active"),
        dbc.DropdownMenuItem("Inactive", href="/lws/inactive"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Add Account", href="/lws/add-account"),
        dbc.DropdownMenuItem("Account Creation Requests", href="/lws/requests"),
    ],
    nav=True,
    in_navbar=True,
    label="Monero-LWS",
    # toggle_style={
    #    "color": "white",
    #    "background": "#000000",
    # },
    # toggleClassName="fst-italic border border-dark",
)
BlockExplorerDropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Transaction Pool", href="/block-explorer/tx-pool"),
        dbc.DropdownMenuItem("Transaction Pusher", href="/block-explorer/tx-pusher"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem(
            "Key Images Checker", href="/block-explorer/key-images-checker"
        ),
        dbc.DropdownMenuItem(
            "Output keys Checker", href="/block-explorer/output-keys-checker"
        ),
    ],
    nav=True,
    in_navbar=True,
    label="Block Explorer",
    # toggle_style={
    #    "color": "white",
    #    "background": "#000000",
    # },
    # toggleClassName="fst-italic border border-dark",
)

FA_icon = html.I(className="fa-solid fa-cloud-arrow-down me-2")
# settings_icon = DashIconify(icon="fluent:settings-64-regular", style={"marginRight": 5})
settings_icon = DashIconify(icon="fluent:settings-32-regular", color="white", width=30)
search_icon = DashIconify(icon="fluent-mdl2:search", color="white", width=30)


search_bar = dbc.Row(
    [
        dbc.Col(
            # dbc.Button(
            #    "Search", color="primary", className="ms-auto fa fa-send",id="submit-val", n_clicks=0
            # ),
            dbc.Button([settings_icon, ""], id="submit-val", n_clicks=0, color="black"),
            # width="auto",
        ),
    ],
    # className="d-md-none d-lg-none g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    className="d-flex align-content-end d-md-none d-lg-none",
    align="center",
)
# here's how you can recreate the same thing using Navbar
# (see also required callback at the end of the file)
NODO_LOGO = "/assets/nodologo_original150.png"
nav = dbc.Container(
    [
        dbc.NavLink("Internal link", href="/l/components/nav"),
        dbc.NavLink("External link", href="https://github.com"),
        dbc.NavLink(
            "External relative",
            href="/l/components/nav",
            external_link=True,
        ),
        dbc.NavLink("Button", id="button-link", n_clicks=0),
    ],
    class_name="text-white pt-0 pl-0 pr-0 pb-0",
)

custom_default = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=NODO_LOGO, width="150px", height="50px")),
                    ],
                    className="flex-grow-1 g-0 w-100",
                ),
                href="/status",
                style={"padding-left": "15px", "padding-right": "30px"},
            ),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink(
                            ("Networks").upper(),
                            href="/networks",
                            class_name="",
                            id="navbar-collapse-navlink-networks",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Device").upper(),
                            href="/device",
                            class_name="",
                            id="navbar-collapse-navlink-device",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Node").upper(),
                            href="/node",
                            class_name="",
                            id="navbar-collapse-navlink-node",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Miner").upper(),
                            href="/miner",
                            class_name="",
                            id="navbar-collapse-navlink-miner",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("LWS").upper(),
                            href="/lws/add-account",
                            class_name="",
                            id="navbar-collapse-navlink-lws-admin",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Block Explorer").upper(),
                            href="/block-explorer",
                            class_name="",
                            id="navbar-collapse-navlink-block-explorer",
                            active="partial",
                        ),
                    ],
                    className="d-flex align-content-start",
                    navbar=True,
                    pills=True,
                ),
                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                id="navbar-collapse1",
                navbar=True,
            ),
            search_bar,
            html.Div([], id="label-time", style={"padding-right": "20px"}),
        ],
        fluid=True,
    ),
    className="pt-0 pl-0 pr-0 pb-0 ",
    color="black",
)

sidebar = html.Div(
    [
        dbc.Nav(
            submenu_1 + submenu_2 + submenu_3 + submenu_4 + submenu_5, vertical=True
        ),
    ],
    className="mt-0 pt-0 d-md-none d-lg-none",
    style=SIDEBAR_STYLE,
    id="sidebar",
)

sidebar1 = html.Div(
    [
        # sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        html.Div(
            [
                html.Hr(),
                html.P(
                    "A responsive sidebar layout with collapsible navigation " "links.",
                    className="lead",
                ),
                dbc.Nav(submenu_1, horizontal=True, pills=True),
            ],
            id="blurb",
        ),
    ],
    id="sidebar",
)

offcanvas = dbc.Row(
    [
        dbc.Offcanvas(
            dbc.Col([sidebar], width=199),
            id="offcanvas-placement",
            title="Settings",
            close_button=False,
            is_open=False,
            placement="end",
            style={"horizontal-width": 10},
            className="d-md-none d-lg-none sidebar",
        ),
    ]
)


# Monero
# Monero: Synchronized/Synchronizing
# Timestamp:
# Current Sync Height: int
# Monero Version: string
# Outgoing Connections: int
# Incoming Connections: int
# While Peerlist Size: int
# Grey Peerlist Size: int
# Update Available: false
def make_page0_sync_status():
    sync_status = page0_sync_status["sync_status"]
    monero_version = page0_sync_status["version"]
    timestamp = page0_sync_status["start_time"]
    date = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y, %H:%M:%S")
    current_sync_height = page0_sync_status["height"]
    outgoing_connections = page0_sync_status["outgoing_connections_count"]
    incoming_connections = page0_sync_status["incoming_connections_count"]
    white_peerlist_size = page0_sync_status["white_peerlist_size"]
    grey_peerlist_size = page0_sync_status["grey_peerlist_size"]
    update_available = page0_sync_status["update_available"]
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.Label("Monero", className="me-1 mt-1"),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Monero", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_sync_status_sync_status",
                                className="homeBoxNodoInput",
                                value=sync_status,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Timestamp", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_sync_status_timestamp",
                                className="homeBoxNodoInput",
                                value=date,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Sync Height", className="homeBoxNodo"),
                            dbc.Input(
                                type="number",
                                id="page0_sync_status_current_sync_height",
                                className="homeBoxNodoInput",
                                value=current_sync_height,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Monero Version", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="text",
                                id="page0_sync_status_monero_version",
                                className="homeBoxNodoInput",
                                value=monero_version,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Outgoing Peers", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="number",
                                id="page0_sync_status_current_outgoing_connections",
                                className="homeBoxNodoInput",
                                value=outgoing_connections,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Incoming Peers", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="number",
                                id="page0_sync_status_current_incoming_connections",
                                className="homeBoxNodoInput",
                                value=incoming_connections,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "White Peerlist", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="number",
                                id="page0_sync_status_white_peerlist_size",
                                className="homeBoxNodoInput",
                                value=white_peerlist_size,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Grey Peerlist", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="number",
                                id="page0_sync_status_grey_peerlist_size",
                                className="homeBoxNodoInput",
                                value=grey_peerlist_size,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Update Available", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="text",
                                id="page0_sync_status_update_available",
                                className="homeBoxNodoInput",
                                value=update_available,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                ]
            ),
        ],
        className="d-flex align-content-start homeCardNodo0",
        color="black",
        # id={"type": "card", "index": n_add},
        # style={"min-width": "32vw","max-width": "95vw"},
    )


# Services
# Mainnet Node: Running/Inactive
# Private Node: Running/Inactive
# Tor Node: Running/Inactive
# I2P Node: Running/Inactive
# Monero-LWS-Admin: Scanning/Inactive
# Block Explorer: Running
def make_page0_system_status():
    mainnet_node = page0_system_status["mainnet_node"]
    tor_node = page0_system_status["tor_node"]
    i2p_node = page0_system_status["i2p_node"]
    monero_lws_admin = page0_system_status["monero_lws_admin"]
    block_explorer = page0_system_status["block_explorer"]
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.Label("Services", className="me-0 mt-1"),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Monero Node", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_mainnet_node",
                                className="homeBoxNodoInput",
                                value=mainnet_node,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Tor Service", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_tor_node",
                                className="homeBoxNodoInput",
                                value=tor_node,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("I2P Service", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_i2p_node",
                                className="homeBoxNodoInput",
                                value=i2p_node,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Monero LWS", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_monero_lws_admin",
                                className="homeBoxNodoInput",
                                value=monero_lws_admin,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Block Explorer", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_block_explorer",
                                className="homeBoxNodoInput",
                                value=block_explorer,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                ],
            ),
        ],
        className="d-flex align-content-start homeCardNodo1",
        color="black",
        # id={"type": "card", "index": n_add},
        # style={"min-width": "32vw","max-width": "95vw"},
    )


# System
# CPU("%"): int
# CPU temp("°C"): float
# Primary Storage: Used SSD/Total SSD ("GB")
# Backup Storage: Used EMMC/Total EMMC ("GB")
# RAM: x ("%") Used RAM/ Total RAM ("GB")
def make_page0_hardware_status():
    global page0_sync_status
    global page0_system_status
    global page0_hardware_status
    cpu_percentage = str(page0_hardware_status["cpu_percentage"]) + " %"
    cpu_temp = str(page0_hardware_status["cpu_temp"]) + " °C"
    primary_storage = str(page0_hardware_status["primary_storage"]) + " % in use"
    backup_storage = str(page0_hardware_status["backup_storage"]) + " % in use"
    ram_percentage = str(page0_hardware_status["ram_percentage"]) + " % in use"
    uptime = proc.run(["uptime", "-p"], stdout=proc.PIPE).stdout.decode()[3:]

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.Label("System", className="me-0 mt-1"),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("CPU", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_hardware_status_cpu_percentage",
                                className="homeBoxNodoInput",
                                value=cpu_percentage,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("CPU Temp", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_hardware_status_cpu_temp",
                                className="homeBoxNodoInput",
                                value=cpu_temp,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Primary Storage", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="text",
                                id="page0_hardware_status_primary_storage",
                                className="homeBoxNodoInput",
                                value=primary_storage,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Backup Storage", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_i2p_node",
                                className="homeBoxNodoInput",
                                value=backup_storage,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("RAM", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_hardware_status_memory",
                                className="homeBoxNodoInput",
                                value=ram_percentage,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Uptime", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_hardware_status_uptime",
                                className="homeBoxNodoInput",
                                value=uptime,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                ],
            ),
        ],
        className="d-flex align-content-start homeCardNodo2",
        color="black",
        # id={"type": "card", "index": n_add},
        # style={"min-width": "31vw","max-width": "95vw"},
    )


def make_page0():
    return html.Div(
        [
            make_page0_sync_status(),
            make_page0_system_status(),
            make_page0_hardware_status(),
        ],
        className="d-flex align-content-start homeCardNodo",
        # style={"flex-wrap": "nowrap","max-width": "100vw"}
    )


def make_page1_1():
    global page1_networks_clearnet
    address = page1_networks_clearnet["address"]
    port = page1_networks_clearnet["port"]
    peer = page1_networks_clearnet["peer"]

    return html.Div(
        [
            html.P("Networks -> Clearnet", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Clearnet").upper(),
                                            href="/networks/clearnet",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Tor").upper(),
                                            href="/networks/tor",
                                            class_name="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("I2P").upper(),
                                            href="/networks/i2p",
                                            class_name="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse-page1_1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Address"),
                    dbc.Input(
                        id="input-networks-clearnet-address",
                        type="text",
                        value=address,
                        disabled=True,
                    ),
                ],
                className="me-1 mt-1",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Port"),
                    dbc.Input(
                        id="input-networks-clearnet-port",
                        type="number",
                        min=1024,
                        max=65535,
                        step=1,
                        value=port,
                    ),
                ],
                className="me-1 mt-1 pt-2 pb-2",
                style={"max-width": "350px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Peer"),
                    dbc.Input(
                        id="input-networks-clearnet-peer", type="text", value=peer
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="networks-clearnet-hidden-div", style={"display": "none"}),
            html.Div(id="networks-clearnet-port-hidden-div", style={"display": "none"}),
            html.Br(),
            html.Br(),
            html.Div(
                id="qr-code-clearnet",
                children=[
                    dqm.DashQrGenerator(
                        data=address + ":" + str(port),
                        framed=True,
                    )
                ],
            ),
        ]
    )


def make_page1_2():
    global page1_networks_tor
    tor_switch = bool(page1_networks_tor["tor_switch"] == 1)
    route_all_connections_through_tor_switch = bool(
        page1_networks_tor["route_all_connections_through_tor_switch"] == 1
    )
    onion_addr = page1_networks_tor["onion_addr"]
    port = page1_networks_tor["port"]
    peer = page1_networks_tor["peer"]

    return html.Div(
        [
            html.P("Networks -> Tor", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Clearnet").upper(),
                                            href="/networks/clearnet",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Tor").upper(),
                                            href="/networks/tor",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("I2P").upper(),
                                            href="/networks/i2p",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse-page1_2",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    daq.BooleanSwitch(
                        on=tor_switch,
                        label="",
                        color=switch_col,
                        id="switch-networks-tor",
                        style={"min-width": "80px"},
                    ),
                    dbc.Label("Tor", className="me-1 mt-1"),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    daq.BooleanSwitch(
                        on=route_all_connections_through_tor_switch,
                        label="",
                        color=switch_col,
                        id="switch-networks-tor-route-all-connections-through-tor-switch",
                        style={"min-width": "80px"},
                    ),
                    dbc.Label(
                        "Route all connections through Tor", className="me-1 mt-1"
                    ),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Onion Addr"),
                    dbc.Input(
                        id="input-networks-tor-onion-addr",
                        type="text",
                        disabled=True,
                        value=onion_addr,
                    ),
                ],
                className="me-1 mt-1 pb-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Port"),
                    dbc.Input(
                        id="input-networks-tor-port",
                        disabled=True,
                        type="number",
                        min=1024,
                        max=65535,
                        step=1,
                        value=port,
                    ),
                ],
                className="me-1 mt-1 pt-2 pb-2",
                style={"max-width": "350px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Peer"),
                    dbc.Input(id="input-networks-tor-peer", type="text", value=peer),
                ],
                className="me-1 mt-1 pt-2",
            ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="networks-tor-hidden-div", style={"display": "none"}),
            html.Div(
                id="networks-tor--route-all-connections-through-tor-hidden-div",
                style={"display": "none"},
            ),
            html.Div(id="networks-tor-port-hidden-div", style={"display": "none"}),
            html.Br(),
            html.Br(),
            html.Div(
                id="qr-code-tor",
                children=[
                    dqm.DashQrGenerator(
                        data=onion_addr + ":" + str(port),
                        framed=True,
                    )
                ],
            ),
        ]
    )


def make_page1_3():
    global page1_networks_i2p
    i2p_switch = bool(page1_networks_i2p["i2p_switch"] == 1)
    i2p_b32_addr = page1_networks_i2p["i2p_b32_addr"]
    port = page1_networks_i2p["port"]
    peer = page1_networks_i2p["peer"]

    return html.Div(
        [
            html.P("Networks -> I2P", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Clearnet").upper(),
                                            href="/networks/clearnet",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Tor").upper(),
                                            href="/networks/tor",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("I2P").upper(),
                                            href="/networks/i2p",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse-page1_3",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    daq.BooleanSwitch(
                        on=i2p_switch,
                        label="",
                        color=switch_col,
                        id="switch-networks-i2p",
                        style={"min-width": "80px"},
                    ),
                    dbc.Label("I2P", className="me-1 mt-1"),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("I2P b32 Addr"),
                    dbc.Input(
                        type="text",
                        disabled=True,
                        id="input-networks-i2p-i2p-b32-addr",
                        value=i2p_b32_addr,
                    ),
                ],
                className="me-1 mt-1 pb-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Port"),
                    dbc.Input(
                        type="number",
                        disabled=True,
                        min=1024,
                        max=65535,
                        step=1,
                        id="input-networks-i2p-port",
                        value=port,
                    ),
                ],
                className="me-1 mt-1 pt-2 pb-2",
                style={"max-width": "350px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Peer"),
                    dbc.Input(id="input-networks-i2p-peer", type="text", value=peer),
                ],
                className="me-1 mt-1 pt-2",
            ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="networks-i2p-hidden-div", style={"display": "none"}),
            html.Div(id="networks-i2p-port-hidden-div", style={"display": "none"}),
            html.Br(),
            html.Br(),
            html.Div(
                id="qr-code-i2p",
                children=[
                    dqm.DashQrGenerator(
                        data=i2p_b32_addr + ":" + str(port),
                        framed=True,
                    )
                ],
            ),
        ]
    )


def make_page2_1():
    global page2_node_rpc
    rpc_switch = bool(page2_node_rpc["rpc_switch"] == 1)
    port = page2_node_rpc["port"]
    username = page2_node_rpc["username"]
    password = page2_node_rpc["password"]

    return html.Div(
        [
            html.P("Node -> RPC", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Private Node").upper(),
                                            href="/node/private-node",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Bandwidth").upper(),
                                            href="/node/bandwidth",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Label("Private Node", className="me-1 mt-1"),
                    daq.BooleanSwitch(
                        on=rpc_switch,
                        label="",
                        color=switch_col,
                        id="switch-node-rpc",
                    ),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Port"),
                    dbc.Input(
                        type="number",
                        min=1024,
                        max=65535,
                        step=1,
                        id="input-node-rpc-port",
                        value=port,
                    ),
                ],
                className="me-1 mt-1",
                style={"max-width": "350px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Username"),
                    dbc.Input(
                        type="text", id="input-node-rpc-username", value=username
                    ),
                ],
                className="me-1 mt-1 pt-2",
                style={"max-width": "300px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Password"),
                    dbc.Input(
                        type="password", id="input-node-rpc-password", value=password
                    ),
                ],
                className="me-1 mt-1 pt-2",
                style={"max-width": "300px"},
            ),
            # dbc.Col(
            #     dbc.Button(
            #         "Apply",
            #         className="buttonNodo ms-auto fa fa-send ",
            #         id="button-node-rpc-apply",
            #         n_clicks=0,
            #     ),
            #     width="auto",
            #     className="me-1 mt-1 pt-2",
            # ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="node-rpc-hidden-div", style={"display": "none"}),
            html.Div(id="node-rpc-port-hidden-div", style={"display": "none"}),
            html.Div(id="node-rpc-username-hidden-div", style={"display": "none"}),
            html.Div(id="node-rpc-password-hidden-div", style={"display": "none"}),
            html.Div(id="node-rpc-apply-hidden-div", style={"display": "none"}),
            html.Br(),
            html.Br(),
        ]
    )


def make_page2_2():
    global page2_node_bandwidth
    incoming_peers_limit = page2_node_bandwidth["incoming_peers_limit"]
    outgoing_peers_limit = page2_node_bandwidth["outgoing_peers_limit"]
    rate_limit_up = page2_node_bandwidth["rate_limit_up"]
    rate_limit_down = page2_node_bandwidth["rate_limit_down"]

    return html.Div(
        [
            html.P("Node -> Bandwidth", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Private Node").upper(),
                                            href="/node/private-node",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Bandwidth").upper(),
                                            href="/node/bandwidth",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Incoming peers limit"),
                    dbc.Input(
                        type="number",
                        min=-1,
                        max=65535,
                        step=1,
                        id="input-node-bandwidth-incoming-peers-limit",
                        value=incoming_peers_limit,
                    ),
                ],
                className="me-1 mt-1",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Outgoing peers limit"),
                    dbc.Input(
                        type="number",
                        min=-1,
                        max=65535,
                        step=1,
                        id="input-node-bandwidth-outgoing-peers-limit",
                        value=outgoing_peers_limit,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Bandwidth Up"),
                    dbc.Input(
                        type="number",
                        min=-1,
                        max=65535,
                        step=1,
                        id="input-node-bandwidth-rate-limit-up",
                        value=rate_limit_up,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Bandwidth down"),
                    dbc.Input(
                        type="number",
                        min=-1,
                        max=65535,
                        step=1,
                        id="input-node-bandwidth-rate-limit-down",
                        value=rate_limit_down,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            html.Div(id="node-bandwidth-hidden-div", style={"display": "none"}),
            html.Div(
                id="node-bandwidth-incoming-peers-limit-hidden-div",
                style={"display": "none"},
            ),
            html.Div(
                id="node-bandwidth-outgoing-peers-limit-hidden-div",
                style={"display": "none"},
            ),
            html.Div(
                id="node-bandwidth-rate-limit-up-hidden-div", style={"display": "none"}
            ),
            html.Div(
                id="node-bandwidth-rate-limit-down-hidden-div",
                style={"display": "none"},
            ),
            html.Br(),
            html.Br(),
        ]
    )


def make_page3_1():
    global page3_device_wifi
    global page3_device_ethernet
    global page3_device_system
    wifi_switch = bool(page3_device_wifi["wifi_switch"] == 1)
    ssid = page3_device_wifi["ssid"]
    ssids = page3_device_wifi["ssids"]
    passphrase = page3_device_wifi["passphrase"]
    status = page3_device_wifi["status"]
    automatic_switch = bool(page3_device_wifi["automatic_switch"] == 1)
    ip_address = page3_device_wifi["ip_address"]
    subnet_mask = page3_device_wifi["subnet_mask"]
    router = page3_device_wifi["router"]
    dhcp = page3_device_wifi["dhcp"]

    return html.Div(
        [
            html.P("Device -> Wi-Fi", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Wi-Fi").upper(),
                                            href="/device/wifi",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="/device/ethernet",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="/device/system",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Label("Wi-Fi", className="me-1 mt-1"),
                    daq.BooleanSwitch(
                        on=wifi_switch,
                        label="",
                        color=switch_col,
                        id="switch-device-wifi",
                    ),
                ],
                style={"min-width": "350px"},
            ),
            dcc.Dropdown(
                ssids,
                id="device_wifi_ssid_dropdown",
                className="networkDropdown me-1 mt-1",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("SSID"),
                    dbc.Input(type="text", id="input-device-wifi-ssid", value=ssid),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Passphrase"),
                    dbc.Input(
                        type="password",
                        id="input-device-wifi-passphrase",
                        value=passphrase,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Status"),
                    dbc.Input(
                        type="text",
                        disabled=True,
                        id="input-device-wifi-status",
                        value=status,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            html.Br(),
            dbc.InputGroup(
                [
                    dbc.Label("Automatic", className="me-1 mt-1"),
                    daq.BooleanSwitch(
                        on=automatic_switch,
                        label="",
                        color=switch_col,
                        id="switch-device-wifi-automatic",
                    ),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText(
                        "IP Address",
                    ),
                    dbc.Input(
                        type="text",
                        id="input-device-wifi-ip-address",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=ip_address,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Subnet Mask"),
                    dbc.Input(
                        type="text",
                        id="input-device-wifi-subnet-mask",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=subnet_mask,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Router"),
                    dbc.Input(
                        type="text",
                        id="input-device-wifi-router",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=router,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("DHCP"),
                    dbc.Input(
                        type="text",
                        id="input-device-wifi-dhcp",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=dhcp,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            html.Div(id="device-wifi-hidden-div", style={"display": "none"}),
            html.Div(id="device-wifi-ssid-hidden-div", style={"display": "none"}),
            html.Div(id="device-wifi-passphrase-hidden-div", style={"display": "none"}),
            html.Div(id="device-wifi-ip-address-hidden-div", style={"display": "none"}),
            html.Div(
                id="device-wifi-subnet-mask-hidden-div", style={"display": "none"}
            ),
            html.Div(id="device-wifi-router-hidden-div", style={"display": "none"}),
            html.Div(id="device-wifi-dhcp-hidden-div", style={"display": "none"}),
        ],
    )


def make_page3_2():
    global page3_device_wifi
    global page3_device_ethernet
    global page3_device_system
    automatic_switch = bool(page3_device_ethernet["automatic_switch"] == 1)
    ip_address = page3_device_ethernet["ip_address"]
    subnet_mask = page3_device_ethernet["subnet_mask"]
    router = page3_device_ethernet["router"]
    dhcp = page3_device_ethernet["dhcp"]

    return html.Div(
        [
            html.P("Device -> Ethernet", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Wi-Fi").upper(),
                                            href="/device/wifi",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="/device/ethernet",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="/device/system",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Label("Automatic", className="me-1 mt-1"),
                    daq.BooleanSwitch(
                        on=automatic_switch,
                        label="",
                        color=switch_col,
                        id="switch-device-ethernet-automatic",
                    ),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("IP Address"),
                    dbc.Input(
                        type="text",
                        id="input-device-ethernet-ip-address",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=ip_address,
                    ),
                ],
                className="me-1 mt-1",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Subnet Mask"),
                    dbc.Input(
                        type="text",
                        id="input-device-ethernet-subnet-mask",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=subnet_mask,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Router"),
                    dbc.Input(
                        type="text",
                        id="input-device-ethernet-router",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=router,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("DHCP"),
                    dbc.Input(
                        type="text",
                        id="input-device-ethernet-dhcp",
                        className="input-device-wifi-eth",
                        pattern="^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                        value=dhcp,
                    ),
                ],
                className="me-1 mt-1 pt-2",
            ),
        ]
    )


def make_page3_3():
    global page3_device_wifi
    global page3_device_ethernet
    global page3_device_system

    return html.Div(
        [
            html.P("Device -> System", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Wi-Fi").upper(),
                                            href="/device/wifi",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="/device/ethernet",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="/device/system",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        # dbc.NavLink(
                                        #     ("News feeds").upper(),
                                        #     href="/device/newsfeeds",
                                        #     className="sencondLevelNavlink",
                                        # ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            html.Div(id="inactive_dummy_components3_1a", children=""),
            html.Div(id="inactive_dummy_components3_1b", children=""),
            html.Div(id="inactive_dummy_components3_1c", children=""),
            dbc.Label(""),
            dbc.Col(
                dbc.Button(
                    "Restart",
                    className="me-1 mt-1 ms-auto fa fa-send buttonNodo",
                    id="submit-val-node-system-reset",
                    n_clicks=0,
                ),
                width="auto",
            ),
            dbc.Label(""),
            dbc.Col(
                dbc.Button(
                    "Shutdown",
                    className="me-1 mt-1 ms-auto fa fa-send buttonNodo",
                    id="submit-val-node-system-shutdown",
                    n_clicks=0,
                ),
                width="auto",
            ),
            dbc.Label(""),
            dbc.Col(
                dbc.Button(
                    "Recovery",
                    href="/device/system/recovery",
                    className="me-1 mt-1 ms-auto fa fa-send node-system-recovery-button",
                    id="submit-val-node-system-recovery",
                    n_clicks=0,
                ),
                width="auto",
            ),
        ]
    )


def make_page3_3_2():
    global page3_device_wifi
    global page3_device_ethernet
    global page3_device_system

    return html.Div(
        [
            html.P("Device -> System -> Recovery", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Wi-Fi").upper(),
                                            href="/device/wifi",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="/device/ethernet",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="/device/system",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        # dbc.NavLink(
                                        #     ("News feeds").upper(),
                                        #     href="/device/newsfeeds",
                                        #     className="sencondLevelNavlink",
                                        # ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.Checklist(
                options=[
                    {"label": "  Attempt to repair the filesystem", "value": 1},
                ],
                value=[],
                id="checklist-inline-input-repair",
            ),
            dbc.Label("In case this fails, it will reformat the drive entirely. This means the blockchain will be re-synced, and LWS data will be reset."),
            dbc.Checklist(
                options=[
                    {"label": "  Purge and resync blockchain", "value": 1},
                ],
                value=[],
                id="checklist-inline-input-purge",
            ),
            dbc.Label(""),
            dbc.Button(
                "Start",
                className="me-1 mt-1 node-system-recovery-start-button",
                id="submit-val-node-system-recovery-start",
                n_clicks=0,
            ),
            dbc.Button(
                "Cancel",
                href="/device/system",
                className="ml-8 me-1 mt-1 node-system-recovery-cancel-button",
                id="submit-val-node-system-recovery-cancel",
                n_clicks=0,
            ),
        ]
    )


def make_page3_4():
    global page3_device_wifi
    global page3_device_ethernet
    global page3_device_system

    return html.Div(
        [
            html.P("Device -> System", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Wi-Fi").upper(),
                                            href="/device/wifi",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="/device/ethernet",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="/device/system",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            html.Div(id="inactive_dummy_components3_4a", children=""),
        ]
    )


def make_inactive_card(n_add, address, height):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.InputGroup(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.InputGroupText(
                                                    "Address",
                                                    className="LWSBoxNodo text-left",
                                                    style={
                                                        "min-width": "100px",
                                                        "height": "100%",
                                                        "border-radius": "5px 0 0 5px",
                                                    },
                                                ),
                                                style={"min-width": "100px"},
                                                width=1,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    truncate_address(address),
                                                    className="NodoLWSInput",
                                                    style={
                                                        "padding-left": "12px",
                                                        "padding-top": "6px",
                                                        "justify-content": "center",
                                                        "height": "100%",
                                                        "max-width": "650px",
                                                        "border-radius": "0 5px 5px 0",
                                                        "font-family": "monospace",
                                                    },
                                                ),
                                                style={
                                                    "min-width": "50px",
                                                    "max-width": "650px",
                                                },
                                            ),
                                        ],
                                        className="flex-grow-1 g-0 w-100 LWSCardBG",
                                    ),
                                ],
                                className=" me-1 mt-1 g-0 account_card",  # style={"min-width":"300px","max-width": "65%"}
                                style={"max-width": "28.75em"},
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "Height",
                                        className="LWSBoxNodo text-left",
                                        style={
                                            "max-width": "70px",
                                            "min-width": "90px",
                                            "height": "100%",
                                        },
                                    ),
                                    dbc.Input(
                                        type="text",
                                        value=height,
                                        className="NodoLWSInput",
                                        disabled=True,
                                        style={
                                            "height": "100%",
                                            "font-family": "monospace",
                                        },
                                    ),
                                ],
                                className="d-flex align-content-start  me-1 mt-1 LWSCardBG",
                                style={"max-width": "260px"},
                            ),
                            dbc.Label(""),
                            dbc.Button(
                                "Reactivate",
                                className="buttonNodo me-1 mt-1 fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1",
                                id={
                                    "type": "inactive-reactivate-button",
                                    "index": n_add,
                                },
                                style={"margin-left": "4px"},
                            ),
                            dbc.Button(
                                "Delete",
                                className="buttonNodo me-1 mt-1 fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1 ",
                                id={"type": "inactive-delete-button", "index": n_add},
                            ),
                        ],
                        className="d-flex align-content-start LWSCardBG",
                    ),
                    dbc.Label(""),
                ]
            ),
        ],
        id={"type": "inactive-card", "index": n_add},
        # style={"max-width": "1150px"},
        className="mt-1 LWSCardBG",
    )


def make_inactive_cards():
    global inactive_address_height
    accounts = lws_admin_cmd("list_accounts")
    if "inactive" in accounts:
        inactive_address_height = accounts["inactive"]
    address = "4567"
    height = ""
    rescan_height = ""
    index = 0
    print("----")
    print("The inactive_address_height pair list is :", inactive_address_height)

    account_create_request_lists = []
    for item in inactive_address_height:
        address = str(item["address"])
        height = str(item["scan_height"])
        account_create_request_lists.append(make_inactive_card(index, address, height))
        index = index + 1

    return account_create_request_lists


def truncate_address(address):
    return "{0} {1} {2} .. {3} {4} {5}".format(
        address[:4],
        address[4:8],
        address[8:12],
        address[-12:-8],
        address[-8:-4],
        address[-4:],
    )


def make_active_card(n_add, address, height, rescan_height):
    if rescan_height != None:
        if len(rescan_height) > 0:
            rescan_button_disable = False
        else:
            rescan_button_disable = True

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.InputGroup(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.InputGroupText(
                                                    "Address",
                                                    className="LWSBoxNodo text-left",
                                                    style={
                                                        "min-width": "100px",
                                                        "height": "100%",
                                                        "border-radius": "5px 0 0 5px",
                                                    },
                                                ),
                                                style={"min-width": "100px"},
                                                width=1,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    truncate_address(address),
                                                    className="NodoLWSInput",
                                                    style={
                                                        "padding-left": "12px",
                                                        "padding-top": "6px",
                                                        "justify-content": "center",
                                                        "height": "100%",
                                                        "max-width": "650px",
                                                        "border-radius": "0 5px 5px 0",
                                                        "font-family": "monospace",
                                                    },
                                                ),
                                                style={
                                                    "min-width": "50px",
                                                    "max-width": "650px",
                                                },
                                            ),
                                        ],
                                        className="flex-grow-1 g-0 w-100 LWSCardBG",
                                    ),
                                ],
                                className=" me-1 mt-1 g-0 account_card",
                                style={"max-width": "28.75em"},
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "Height",
                                        className="LWSBoxNodo text-left",
                                        style={
                                            "max-width": "70px",
                                            "min-width": "90px",
                                            "height": "100%",
                                        },
                                    ),
                                    dbc.Input(
                                        type="text",
                                        value=height,
                                        className="NodoLWSInput",
                                        disabled=True,
                                        style={
                                            "height": "100%",
                                            "font-family": "monospace",
                                        },
                                    ),
                                ],
                                className="d-flex align-content-start  me-1 mt-1 LWSCardBG",
                                style={"max-width": "260px"},
                            ),
                            dbc.Label(""),
                            dbc.Button(
                                "Deactivate",
                                className="buttonNodo me-1 mt-1 fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1 ",
                                id={"type": "active-deactivate-button", "index": n_add},
                                style={"margin-left": "4px"},
                            ),
                        ],
                        className="d-flex align-content-start LWSCardBG",
                    ),
                    dbc.Label("Rescan Height", className="me-1 mt-3 mb-0"),
                    dbc.InputGroup(
                        [
                            dbc.Input(
                                type="text",
                                value=rescan_height,
                                id={"type": "active-rescan-input", "index": n_add},
                            ),
                        ],
                        className="me-1 mt-0 mb-2 LWSCardBG",
                        style={"width": "150px"},
                    ),
                    dbc.Button(
                        "Rescan",
                        className="buttonNodo me-1 mt-1 ms-auto fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1",
                        id={"type": "active-rescan-button", "index": n_add},
                        disabled=rescan_button_disable,
                    ),
                ]
            ),
        ],
        id={"type": "active-card", "index": n_add},
        # style={"max-width": "1150px"},
        className="mt-1 LWSCardBG",
    )


lws_cache: str = None
lws_reparse: bool = True


def lws_admin_cmd(*command) -> dict:
    global lws_cache
    global lws_reparse
    if not lws_reparse and lws_cache != None and len(command) > 0:
        if command[0] == "list_accounts":
            return lws_cache
        else:
            lws_reparse = True
    cmd = [
        "/home/nodo/monero-lws/build/src/monero-lws-admin",
        "--db-path={0}/light_wallet_server",
    ]
    cmd[1] = cmd[1].format(conf_dict["config"]["data_dir"])
    cmd += command
    print(cmd)
    resp = proc.run(cmd, stdout=proc.PIPE).stdout.decode()

    print(resp)
    lws_cache = json.loads(resp)
    lws_reparse = False
    return lws_cache


def make_active_cards():
    global active_address_height
    # print(lws_admin_cmd("list_requests"))
    accounts = lws_admin_cmd("list_accounts")
    if "active" in accounts:
        active_address_height = accounts["active"]
    address = "4567"
    height = ""
    rescan_height = ""
    index = 0
    print("----")
    print("The active_address_height pair list is :", active_address_height)

    account_create_request_lists = []
    for item in active_address_height:
        print(item)
        address = str(item["address"])
        height = str(item["scan_height"])
        # rescan_height = str(item[2])
        account_create_request_lists.append(
            make_active_card(index, address, height, rescan_height)
        )
        index = index + 1

    return account_create_request_lists


def make_account_create_request_card(n_add, address, height):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.InputGroup(
                        [
                            dbc.InputGroup(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.InputGroupText(
                                                    "Address",
                                                    className="LWSBoxNodo text-left",
                                                    style={
                                                        "min-width": "100px",
                                                        "height": "100%",
                                                        "border-radius": "5px 0 0 5px",
                                                    },
                                                ),
                                                style={"min-width": "100px"},
                                                width=1,
                                            ),
                                            dbc.Col(
                                                html.Div(
                                                    truncate_address(address),
                                                    className="NodoLWSInput",
                                                    style={
                                                        "padding-left": "12px",
                                                        "padding-top": "6px",
                                                        "justify-content": "center",
                                                        "height": "100%",
                                                        "min-width": "20%",
                                                        "max-width": "850px",
                                                        "word-break": "break-all",
                                                        "overflow-wrap": "break-word",
                                                        "border-radius": "0 5px 5px 0",
                                                        "font-family": "monospace",
                                                    },
                                                ),
                                                style={
                                                    "min-width": "50px",
                                                    "max-width": "650px",
                                                },
                                            ),
                                        ],
                                        className="flex-grow-1 g-0 w-100 LWSCardBG",
                                    ),
                                ],
                                className=" me-1 mt-1 g-0 account_card",  # style={"min-width":"300px","max-width": "65%"}
                                style={"max-width": "28.75em"},
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "Start Height",
                                        className="LWSBoxNodo text-left",
                                        style={
                                            "max-width": "70px",
                                            "min-width": "110px",
                                            "height": "100%",
                                        },
                                    ),
                                    dbc.Input(
                                        type="text",
                                        value=height,
                                        className="NodoLWSInput",
                                        disabled=True,
                                        style={
                                            "height": "100%",
                                            "font-family": "monospace",
                                        },
                                    ),
                                ],
                                className="d-flex align-content-start  me-1 mt-1 LWSCardBG",
                                style={"max-width": "260px"},
                            ),
                        ],
                        className="d-flex align-content-start LWSCardBG",
                    ),
                    dbc.Button(
                        "Accept",
                        className="buttonNodo me-1 ms-auto fa fa-send mt-2 ml-1 mr-1 pt-1 pl-1 pr-1",
                        id={"type": "request-accept-button", "index": n_add},
                    ),
                    dbc.Button(
                        "Reject",
                        className="buttonNodo me-1 ms-auto fa fa-send mt-2 ml-1 mr-1 pt-1 pl-1 pr-1 ",
                        id={"type": "request-reject-button", "index": n_add},
                    ),
                ]
            ),
        ],
        id={"type": "card", "index": n_add},
        # style={"max-width": "1150px"},
        className="mt-1 LWSCardBG",
    )


def make_account_create_request_cards():
    global account_address_viewkey_height
    requests: dict = lws_admin_cmd("list_requests")
    if "create" in requests:
        account_address_viewkey_height = lws_admin_cmd("list_requests")["create"]

    address = "4567"
    viewkey = "1234"
    height = "100"
    index = 0

    account_create_request_lists = []
    for item in account_address_viewkey_height:
        address = str(item["address"])
        viewkey = str(item["view_key"] if "view_key" in item else "hidden")
        height = str(item["start_height"])
        account_create_request_lists.append(
            make_account_create_request_card(index, address, height)
        )
        index = index + 1

    return account_create_request_lists


page4_1 = html.Div(
    [
        html.P("LWS Admin -> Active", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Active").upper(),
                                        href="/lws/active",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="/lws/inactive",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="/lws/add-account",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="/lws/requests",
                                        className="sencondLevelNavlink",
                                    ),
                                ],
                                className="d-flex align-content-start bg-black",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
        html.Div(
            id="active_card_components",
        ),
        html.Div(id="container-button-basic4_1a", children=""),
        html.Div(id="container-button-basic4_1b", children=""),
        html.Div(
            id="active-card-input-rescan-height-hidden-div", style={"display": "none"}
        ),
    ]
)

page4_2 = html.Div(
    [
        html.P("LWS Admin -> Inactive", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Active").upper(),
                                        href="/lws/active",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="/lws/inactive",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="/lws/add-account",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="/lws/requests",
                                        className="sencondLevelNavlink",
                                    ),
                                ],
                                className="d-flex align-content-start bg-black",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
        html.Div(
            id="inactive_card_components",
        ),
        html.Div(id="inactive_dummy_components4_2a", children=""),
        html.Div(id="inactive_dummy_components4_2b", children=""),
    ]
)

page4_3 = html.Div(
    [
        html.P("LWS Admin -> Add Account", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Active").upper(),
                                        href="/lws/active",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="/lws/inactive",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="/lws/add-account",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="/lws/requests",
                                        className="sencondLevelNavlink",
                                    ),
                                ],
                                className="d-flex align-content-start bg-black",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        dbc.Label("Main Address", className="me-1 mt-1"),
        dbc.Label("(Starts with 4)", className="me-1 mt-1"),
        dbc.InputGroup(
            [
                # dbc.InputGroupText(""),
                # dbc.Input(placeholder="Amount", type="number", min=1, max=65535, step=1),
                dbc.Input(type="text", id="input-lwsadmin-add-account-address"),
            ],
            className="me-1 mt-1",
        ),
        dbc.Label("Private Viewkey", className="me-1 mt-1"),
        dbc.InputGroup(
            [
                # dbc.InputGroupText(""),
                # dbc.Input(placeholder="Amount", type="number", min=1, max=65535, step=1),
                dbc.Input(type="text", id="input-lwsadmin-add-account-private-viewkey"),
            ],
            className="me-1 mt-1",
        ),
        dbc.Label(""),
        dbc.Col(
            dbc.Button(
                "Add Account",
                className="buttonNodo ms-auto fa fa-send ",
                id="button-lwsadmin-add-account",
                n_clicks=0,
            ),
            width="auto",
            className="me-1 mt-1",
        ),
        html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
        html.Div(id="lwsadmin-add-account-hidden-div", style={"display": "none"}),
        html.Div(
            id="lwsadmin-add-account-address-hidden-div", style={"display": "none"}
        ),
    ]
)

page4_4 = html.Div(
    [
        html.P("LWS Admin -> Account Creation Requests", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Active").upper(),
                                        href="/lws/active",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="/lws/inactive",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="/lws/add-account",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="/lws/requests",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                ],
                                className="d-flex align-content-start bg-black",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        dbc.Col(
            dbc.Button(
                "Accept All Requests",
                className="buttonNodo ms-auto fa fa-send ",
                id="button-lwsadmin-account-creation-requests",
                n_clicks=0,
            ),
            width="auto",
            className="me-1 mt-1 mb-1",
        ),
        html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
        html.Div(
            id="lwsadmin-account-creation-requests-hidden-div",
            style={"display": "none"},
        ),
        html.Div(
            id="lwsadmin-account-creation-requests-request-accept-button-hidden-div",
            style={"display": "none"},
        ),
        html.Div(
            id="lwsadmin-account-creation-requests-request-reject-button-hidden-div",
            style={"display": "none"},
        ),
        html.Div(
            id="request_card_components",
        )
        # dbc.Row([], style={"width":"850px"},id="output_all_request_cards"),
    ]
)


def make_page5_1():
    # transaction_pool_information;
    transaction_pool_information = {}
    ## parameters for transaction pool ( Page 5.1 Transaction Pool)
    transactionPoolDF = pd.DataFrame(
        {
            "age [h:m:s]": [],
            "transaction hash": [],
            "fee/per_kB [µɱ]": [],
            "in/out": [],
            "tx size [kB]": [],
        }
    )

    transactionInTheLastBlock = pd.DataFrame(
        {
            "height": [],
            "age [h:m:s]": [],
            "size [kB]": [],
            "transaction hash": [],
            "fee [µɱ]": [],
            "outputs": [],
            "in/out": [],
            "tx size [kB]": [],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # transaction_pool_information:  dictionary
    # transactionPoolDF:            DataFrame
    # transactionInTheLastBlock:    DataFrame
    # ...
    #
    # +++ transactionInTheLastBlock
    # Following is an example to load data to transactionInTheLastBlock
    # Example: get data for transactionInTheLastBlock 11
    #   curl  -w "\n" -X GET "https://xmrchain.net/" > transactions.html
    #   curl  -w "\n" -X GET "https://xmrchain.net/api/transactions?limit=11" > "json/transactions.json"
    # Opening JSON file
    r = requests.get("http://127.0.0.1:8081/api/networkinfo")
    if r.json()["status"] == "success":
        transaction_pool_information = r.json()["data"].copy()
        transaction_pool_information["server_time"] = datetime.datetime.now().strftime(
            "%d/%m/%Y, %H:%M:%S"
        )

        r = requests.get("http://127.0.0.1:8081/api/transactions?limit=3")

        # returns JSON object as
        # a dictionary
        transactionInTheLastBlock = transactionInTheLastBlock.iloc[0:0]
        data = r.json()
        outputs_DataFrame = json_normalize(data["data"]["blocks"])

        for ind in outputs_DataFrame.index:
            outputs_txs_DataFrame = json_normalize(outputs_DataFrame["txs"][ind])
            height = (
                "["
                + str(outputs_DataFrame["height"][ind])
                + "](block"
                + str(outputs_DataFrame["height"][ind])
                + ")"
            )
            size = str(round((outputs_DataFrame["size"][ind] / 1024), 2))
            age = outputs_DataFrame["age"][ind]
            tx_hash = ""
            tx_fee = ""
            in_out = "?/?"
            tx_size = "0"

            for indexTXS in outputs_txs_DataFrame.index:
                tx_hash = (
                    "["
                    + str(outputs_txs_DataFrame["tx_hash"][indexTXS])
                    + "](tx"
                    + str(outputs_txs_DataFrame["tx_hash"][indexTXS])
                    + ")"
                )
                tx_fee = str(
                    round(outputs_txs_DataFrame["tx_fee"][indexTXS] / 1000000, 0)
                )
                tx_size = str(round(outputs_txs_DataFrame["tx_size"][indexTXS], 0))
                xmr_outputs = str(
                    round(
                        outputs_txs_DataFrame["xmr_outputs"][indexTXS] / 1000000000000,
                        3,
                    )
                )
                transactionInTheLastBlock.loc[-1] = [
                    height,
                    age,
                    size,
                    tx_hash,
                    tx_fee,
                    xmr_outputs,
                    in_out,
                    tx_size,
                ]  # adding a row
                transactionInTheLastBlock.index = (
                    transactionInTheLastBlock.index + 1
                )  # shifting index

    r = requests.get("http://127.0.0.1:8081/api/mempool?limit=40")
    transactionPoolDF = transactionPoolDF.iloc[0:0]
    data = r.json()
    outputs_DataFrame = json_normalize(data["data"])
    outputs_txs_DataFrame = json_normalize(data["data"]["txs"])
    tx_hash = ""
    tx_fee = ""
    in_out = "?/?"
    tx_size = "0"

    for indexTXS in outputs_txs_DataFrame.index:
        tx_hash = (
            "["
            + str(outputs_txs_DataFrame["tx_hash"][indexTXS])
            + "](/tx"
            + str(outputs_txs_DataFrame["tx_hash"][indexTXS])
            + ")"
        )
        age = (
            datetime.datetime.now().timestamp()
            - outputs_txs_DataFrame["timestamp"][indexTXS]
        )
        age = datetime.datetime.fromtimestamp(age).strftime("%H:%M:%S")
        tx_fee = str(round(outputs_txs_DataFrame["tx_fee"][indexTXS] / 1000000, 0))
        tx_size = str(round(outputs_txs_DataFrame["tx_size"][indexTXS], 0))
        xmr_outputs = str(
            round(outputs_txs_DataFrame["xmr_outputs"][indexTXS] / 1000000000000, 3)
        )
        transactionPoolDF.loc[-1] = [
            age,
            tx_hash,
            tx_fee,
            in_out,
            tx_size,
        ]  # adding a row
        transactionPoolDF.index = transactionPoolDF.index + 1  # shifting index

    # r= requests.get(
    #         "http://127.0.0.1:8081/api/emission"
    # )
    # transaction_pool_information.update(r.json()['data'])
    # print(transactionInTheLastBlock)
    # --- transactionInTheLastBlock
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Transaction Pool", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        type="text",
                        placeholder="block height, block hash, transaction hash",
                        className="d-flex align-content-start boxNodo",
                    ),
                    dbc.Button(
                        [search_icon, ""],
                        id="transcation-pool-hash-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-white",
                    ),
                ],
                className="mt-1 mb-1",
            ),
            html.P(
                "Server time: "
                + str(transaction_pool_information["server_time"])
                + " | Network difficulty: "
                + str(transaction_pool_information["difficulty"])  # TODO randomly null?
                + " | Hard fork: v"
                + str(transaction_pool_information["current_hf_version"])
                + " | Hash rate: "
                + str(transaction_pool_information["hash_rate"])
                + " | Fee per byte: "
                + "{:.12f}".format(
                    float(
                        str(int(transaction_pool_information["fee_per_kb"]) * 10**-15)
                    )
                )
                + " | Median block size limit: "
                + str(transaction_pool_information["block_size_limit"])
                + " ",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            # html.P(
            #     "Monero emission (fees) is "
            #     + str(int(transaction_pool_information["coinbase"]) * 10**-12)
            #     + "("
            #     + str(int(transaction_pool_information["fee"]) * 10**-12)
            #     + ") as of "
            #     + transaction_pool_information["blk_no"]
            #     + " block",
            #     className="text-center",
            #     style={"overflow-wrap": "break-word"},
            # ),
            html.P(
                "Transaction Pool",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "(no of txs: "
                + str(transaction_pool_information["tx_pool_size"])
                + ", size: "
                + str(transaction_pool_information["tx_pool_size_kbytes"])
                + "kB, updated every 5 seconds)",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                dash_table.DataTable(
                    data=transactionPoolDF.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "transaction hash"
                        else {"id": x, "name": x}
                        for x in transactionPoolDF.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-top": "0",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "age [h:m:s]"}, "width": "12%"},
                        {"if": {"column_id": "transaction hash"}, "width": "63%"},
                        {"if": {"column_id": "fee/per_kB [µɱ]"}, "width": "8%"},
                        {"if": {"column_id": "in/out"}, "width": "4%"},
                        {"if": {"column_id": "tx size [kB]"}, "width": "4%"},
                    ],
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Div(
                [
                    html.P(
                        "Transactions in the last 11 blocks", className="text-center"
                    ),
                    # html.P(
                    #     "(Median size of 100 blocks: 292.97 kB)",
                    #     className="text-center",
                    # ),
                ]
            ),
            html.P(
                dash_table.DataTable(
                    data=transactionInTheLastBlock.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "transaction hash" or x == "height"
                        else {"id": x, "name": x}
                        for x in transactionInTheLastBlock.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflow": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "max-height": "30vh",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
        ]
    )


tab_page5_1_tx_decode_outputs = html.Div(
    [
        html.P(
            "Check which outputs belong to given Monero address/subaddress and viewkey",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "For RingCT transactions, outputs' amounts are also decoded",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "Note: address/subaddress and viewkey are sent to the server, as the calculations are done on the server side",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="Monero address/subaddress",
                    id="input-page5_1_tx_monero_address_subaddress",
                ),
            ],
            className="me-1 mt-1",
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="Private viewkey",
                    id="input-page5_1_tx_viewkey",
                ),
            ],
            className="me-1 mt-1",
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Decode outputs",
                                href="/block-explorer/tx-pool/decode-outputs",
                                className="d-flex justify-content-end text-center buttonNodo ml-8 me-1 mt-1 ",
                                id="submit-val-page5_1_decode_outputs",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                        ],
                        className="d-flex justify-content-center ",
                        width=2,
                    )
                ],
                className="w-100",
                align="center",
                justify="center",
            ),
        ),
    ]
)

tab_page5_1_tx_prove_sending = html.Div(
    [
        html.P(
            "Prove to someone that you have sent them Monero in this transaction",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "Tx private key can be obtained using get_tx_key command in monero-wallet-cli command line tool",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "Note: address/subaddress and tx private key are sent to the server, as the calculations are done on the server side",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="Tx private key",
                    id="input-page5_1_tx_tx_private_key",
                ),
            ],
            className="me-1 mt-1",
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="Recipient's monero address/subaddress",
                    id="input-page5_1_tx_recipients_monero_address_subaddress",
                ),
            ],
            className="me-1 mt-1",
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Prove sending",
                                className="d-flex justify-content-end text-center buttonNodo ml-8 me-1 mt-1 ",
                                id="submit-val-page5_1_prove_sending",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                        ],
                        className="d-flex justify-content-center ",
                        width=2,
                    )
                ],
                className="w-100",
                align="center",
                justify="center",
            ),
        ),
    ]
)


# 1 input(s) for total of ? xmr
def make_page_5_1_and_5_2_tx_inputs_of_total_xmrs(tx):
    transaction_pool_tx_inputs_of_total_xmrs = {}
    transaction_pool_tx_inputs_of_total_xmrs["num_of_xmrs"] = "31"
    key_image_DataFrame = pd.DataFrame()
    key_image_ring_members_DataFrame = pd.DataFrame()

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # transaction_pool_tx_inputs_of_total_xmrs:     dictionary
    # key_image_DataFrame:                          DataFrame
    # key_image_ring_members_DataFrame:             DataFrame
    # ...
    # ================================================================

    return html.Div(
        [
            html.P(
                str(transaction_pool_tx_inputs_of_total_xmrs["num_of_xmrs"])
                + " input(s) for total of ? xmr",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=key_image_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in key_image_DataFrame.columns
                    ],
                    style_header={"display": "none"},
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "left",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "0vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: left")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-0",
            ),
            # html.Br(),
            # html.Br(),
            html.P(
                dash_table.DataTable(
                    data=key_image_ring_members_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "ring members" or x == "height"
                        else {"id": x, "name": x}
                        for x in key_image_ring_members_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "ring size"}, "min-width": "40px"},
                    ],
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflow": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "max-height": "30vh",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: left")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start",
            ),
            html.Br(),
            html.Br(),
        ]
    )


def make_page_5_1_tx_decode_or_prove_outputs_output(param1, param2, prove):
    tx_decode_or_prove_outputs_output = {}

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # tx_decode_or_prove_outputs_output:           dictionary
    # outputs_DataFrame:                           DataFrame
    # ...
    # Opening JSON file

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    outputs_DataFrame = json_normalize(data["data"]["outputs"])
    outputs_DataFrame = outputs_DataFrame.reindex(
        columns=["output_pubkey", "amount", "match"]
    )
    outputs_DataFrame.rename(
        columns={"output_pubkey": "output public key", "match": "output match?"},
        inplace=True,
    )

    # TODO check if these are still needed
    # tx_decode_or_prove_outputs_output["address"] = data["data"]["address"]
    # tx_decode_or_prove_outputs_output["tx_hash"] = data["data"]["tx_hash"]
    # tx_decode_or_prove_outputs_output["viewkey"] = data["data"]["viewkey"]
    # tx_decode_or_prove_outputs_output[
    #     "tx_public_key"
    # ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    # tx_decode_or_prove_outputs_output["paymentid"] = "1c4d48af4a071950"

    # tx_decode_or_prove_outputs_output["block"] = "2738885"
    # tx_decode_or_prove_outputs_output["timestamp_utc"] = "2022-10-22 07:52:33"
    # tx_decode_or_prove_outputs_output["age"] = "00:228:02:08:24"
    # tx_decode_or_prove_outputs_output["fee"] = "99595.517"
    # tx_decode_or_prove_outputs_output["tx_size"] = "1.50 kB"

    # ================================================================

    description = ""
    if prove == 0:
        description = "Checking which outputs belong to the given address and viewkey"
    else:
        description = "prove that you send this tx to the given address"

    num_of_xmrs = len(data["data"]["outputs"])

    key_image_DataFrame = pd.DataFrame(
        {
            "col0": ["Block: " + tx_decode_or_prove_outputs_output["block"]],
            "col1": [
                "Timestamp [UTC]: " + tx_decode_or_prove_outputs_output["timestamp_utc"]
            ],
            "col2": ["Age[y:d:h:m:s]: " + tx_decode_or_prove_outputs_output["age"]],
            "col3": ["Fee: " + tx_decode_or_prove_outputs_output["fee"]],
            "col4": ["Tx size: " + tx_decode_or_prove_outputs_output["tx_size"]],
        }
    )
    key_image_ring_members_DataFrame = pd.DataFrame()
    return html.Div(
        [
            html.P(
                "Tx hash: " + tx_decode_or_prove_outputs_output["tx_hash"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Tx public key: " + tx_decode_or_prove_outputs_output["tx_public_key"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Paymentid (decrypted): "
                + tx_decode_or_prove_outputs_output["paymentid"]
                + "(value incorrect if you are not the recipient of the tx)",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=key_image_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in key_image_DataFrame.columns
                    ],
                    style_header={"display": "none"},
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "left",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "0vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: left")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-0",
            ),
            html.Br(),
            html.Br(),
            html.P(
                description,
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.Br(),
            html.P(
                "address: " + tx_decode_or_prove_outputs_output["address"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "private key: " + tx_decode_or_prove_outputs_output["viewkey"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Outputs(" + str(num_of_xmrs) + ")",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.Br(),
            html.Br(),
            html.P(
                dash_table.DataTable(
                    data=outputs_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "ring members" or x == "height"
                        else {"id": x, "name": x}
                        for x in outputs_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "left",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: left")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start",
            ),
            html.Br(),
            html.Br(),
        ]
    )


def make_page_5_1_tx_decode_or_prove_outputs(param1, param2, prove):
    return html.Div(
        [
            html.P("Block Explorer -> Transaction Pool", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            "Transaction Pool",
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            "Transaction Pusher",
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            "Key Images Checker",
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            "Output Keys Checker",
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            html.Br(),
            html.Br(),
            make_page_5_1_tx_decode_or_prove_outputs_output(param1, param2, prove),
        ]
    )


tabs_styles = {"text-decoration": "none", "color": "white"}
tab_style = {
    "text-decoration": "none",
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "borderLeft": "1px solid #d6d6d6",
    "borderRight": "1px solid #d6d6d6",
    "backgroundColor": "black",
    "color": "#CFCFCF",
    "padding": "6px",
}

tab_selected_style = {
    "text-decoration": "none",
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "borderLeft": "1px solid #d6d6d6",
    "borderRight": "1px solid #d6d6d6",
    "backgroundColor": "white",
    "color": "black",
    "padding": "6px",
}


# 2 output(s) for total of ? xmr
# stealth address	amount	amount idx	tag
def make_page_5_1_tx(tx):
    transaction_pool_tx = {}
    transaction_pool_tx[
        "txPrefixHash"
    ] = "f16f681796ef2aa4cae46acf502d03f52d6843de00a4b0d8b2144c26e09ce2e6"
    transaction_pool_tx[
        "txPublicKey"
    ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    transaction_pool_tx["txPaymentId"] = "1c4d48af4a071950"

    transaction_pool_tx["txTable1_timestamp"] = "Timestamp: 1666425153"
    transaction_pool_tx[
        "txTable1_timestamp_utc"
    ] = "Timestamp [UTC]: 2022-10-22 07:52:33"
    transaction_pool_tx["txTable1_age"] = "Age [y:d:h:m:s]: 00:228:02:08:24"

    transaction_pool_tx["txTable1_block"] = "[Block: 2738885](block2738885)"
    transaction_pool_tx["txTable1_fee_per_kB"] = "0.000137980000 (0.000040965938)"
    transaction_pool_tx["txTable1_tx_size"] = "Tx size: 3.3682 kB"

    transaction_pool_tx["txTable1_tx_version"] = "Tx version: 2"
    transaction_pool_tx["txTable1_no_of_confirmations"] = "No of confirmations: 163951"
    transaction_pool_tx["txTable1_ringct_type"] = "RingCT/type: yes/6"
    transaction_pool_tx["outputs_of_total_xmr"] = "2"

    txTable1_DataFrame = pd.DataFrame(
        {
            "col0": [
                transaction_pool_tx["txTable1_timestamp"],
                transaction_pool_tx["txTable1_block"],
                transaction_pool_tx["txTable1_tx_version"],
            ],
            "col1": [
                transaction_pool_tx["txTable1_timestamp_utc"],
                transaction_pool_tx["txTable1_fee_per_kB"],
                transaction_pool_tx["txTable1_no_of_confirmations"],
            ],
            "col2": [
                transaction_pool_tx["txTable1_age"],
                transaction_pool_tx["txTable1_tx_size"],
                transaction_pool_tx["txTable1_ringct_type"],
            ],
        }
    )
    transaction_pool_tx[
        "txExtra"
    ] = "01d1041b3ab9294e944c1c1b1a5d3424e2af8810fae0a1160bd51aa597203f60ae0209018ecf9de6d87a19f9"

    txTable2_DataFrame = pd.DataFrame(
        {
            "stealth": ["00:", "01:"],
            "address": [
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
            ],
            "amount": ["?", "?"],
            "amount idx": ["N/A of 74900354", "N/A of 74900354"],
            "tag": ["<ba>", "<2b>"],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # transaction_pool_tx:              dictionary
    # txTable1_DataFrame:               DataFrame
    # txTable2_DataFrame:               DataFrame
    # ...
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Transaction Pool", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        type="text",
                        placeholder="block height,block hash, transaction hash",
                        className="d-flex align-content-start",
                    ),
                    dbc.Button(
                        [search_icon, ""],
                        id="transcation-publisher-hash-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-white",
                    ),
                ],
                className="mt-1 mb-1 mr-10",
            ),
            html.P(""),
            html.P(
                "Tx Hash: " + tx,
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Tx prefix Hash: " + transaction_pool_tx["txPrefixHash"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Tx public Key: " + transaction_pool_tx["txPublicKey"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Payment id (encrypted): " + transaction_pool_tx["txPaymentId"],
                className="text-center mb-0 pb-0",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=txTable1_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in txTable1_DataFrame.columns
                    ],
                    style_header={"display": "none"},
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10 mt-0 pt-0",
            ),
            # html.Br(),
            # html.Br(),
            html.P(
                "Extra: " + transaction_pool_tx["txExtra"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                transaction_pool_tx["outputs_of_total_xmr"]
                + " Output(s) of total ? xmr",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=txTable2_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in txTable2_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "amount"}, "min-width": "40px"},
                    ],
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "5vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            dbc.Tabs(
                [
                    dbc.Tab(
                        tab_page5_1_tx_decode_outputs,
                        label="Decode outputs",
                        label_style=tab_style,
                        active_label_style=tab_selected_style,
                    ),
                    dbc.Tab(
                        tab_page5_1_tx_prove_sending,
                        label="Prove Sending",
                        label_style=tab_style,
                        active_label_style=tab_selected_style,
                    ),
                ],
                style=tabs_styles,
            ),
            html.Br(),
            html.Br(),
            make_page_5_1_and_5_2_tx_inputs_of_total_xmrs(tx),
        ]
    )


# Timestamp [UTC] (epoch):	2021-09-13 16:38:19 (1631551099)
# Major.minor version:	14.14
# nonce:	16470
# PoW hash:	0fd78b42f6a98cb932a76ade002489709f24f99aa2e795e9e9fd730200000000


def make_page5_block_status(block):
    block_status = {}
    block_status["timestampUTC"] = "2021-12-05 06:03:06 (1638684186)"
    block_status["age"] = "01:214:03:45:56"
    block_status["delta"] = "00:01:46"
    block_status["major_minor_version"] = "14.4"
    block_status["block_reward"] = "0.774172"
    block_status["block_size"] = "21.6582"
    block_status["nonce"] = "2667915013"
    block_status["total_fees"] = "0.000504"
    block_status["no_of_txs"] = "12"
    block_status[
        "pow_hash"
    ] = "cfae919165dd44891954037d3927a118e3efce72f1c8d17b44d35a0100000000"
    block_status["difficulty"] = "346501777606"
    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    #
    # block_status:              dictionary
    # ...
    # ================================================================

    return html.Div(
        html.P(
            dbc.Container(
                dbc.Table(
                    [
                        html.Tbody(
                            [
                                html.Tr(
                                    [
                                        html.Td(
                                            "Timestamp [UTC] (epoch): "
                                            + block_status["timestampUTC"],
                                            style={
                                                "color": "white",
                                                "border-left": "1px solid #202020",
                                                "border-right": "1px solid #000000",
                                                "border-top": "1px solid #202020",
                                            },
                                        ),
                                        html.Td(
                                            "Age [y:d:h:m:s]: " + block_status["age"],
                                            style={
                                                "color": "white",
                                                "text-align": "left",
                                                "border-right": "1px solid #000000",
                                                "border-top": "1px solid #202020",
                                            },
                                        ),
                                        html.Td(
                                            "Δ [h:m:s]: " + block_status["delta"],
                                            style={
                                                "color": "white",
                                                "border-right": "1px solid #202020",
                                                "border-top": "1px solid #202020",
                                            },
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td(
                                            "Major.minor version: "
                                            + block_status["major_minor_version"],
                                            style={
                                                "color": "white",
                                                "border-left": "1px solid #202020",
                                                "border-right": "1px solid #000000",
                                            },
                                        ),
                                        html.Td(
                                            "Block reward: "
                                            + block_status["block_reward"],
                                            style={
                                                "color": "white",
                                                "text-align": "left",
                                                "border-right": "1px solid #000000",
                                            },
                                        ),
                                        html.Td(
                                            "Block size [kB]: "
                                            + block_status["block_size"],
                                            style={
                                                "color": "white",
                                                "border-right": "1px solid #202020",
                                            },
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td(
                                            "nonce: " + block_status["nonce"],
                                            style={
                                                "color": "white",
                                                "border-left": "1px solid #202020",
                                                "border-right": "1px solid #000000",
                                            },
                                        ),
                                        html.Td(
                                            "Total fees: " + block_status["total_fees"],
                                            style={
                                                "color": "white",
                                                "text-align": "left",
                                                "border-right": "1px solid #000000",
                                            },
                                        ),
                                        html.Td(
                                            "No of txs: " + block_status["no_of_txs"],
                                            style={
                                                "color": "white",
                                                "border-right": "1px solid #202020",
                                            },
                                        ),
                                    ]
                                ),
                                html.Tr(
                                    [
                                        html.Td(
                                            "PoW hash: " + block_status["pow_hash"],
                                            colSpan=2,
                                            style={
                                                "color": "white",
                                                "border-left": "1px solid #202020",
                                                "border-right": "1px solid #000000",
                                            },
                                        ),
                                        html.Td(
                                            "Difficulty: " + block_status["difficulty"],
                                            style={
                                                "color": "white",
                                                "border-right": "1px solid #202020",
                                            },
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ],
                    className="TB_COLLAPSE",
                    striped=True,
                    bordered=True,
                )
            )
        ),
        style={
            "overflow-x": "auto",
            "margin-right": "auto",
            "margin-left": "auto",
            "width": "95vw",
        },
    )


# Miner reward transaction
# hash	outputs	size [kB]	version
# c7e17c513d8f8fe7e271ce5343a903fd531e7214c1d706f8543a2851e1744320	0.867455	0.1025	2

# Transactions (15)
# hash	outputs	fee [µɱ]	in/out	size [kB]	version
# 7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53	?	0210	1/2	1.4209	2
# 6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a	?	0044	1/2	1.4150	2
# 2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd	?	0011	2/2	1.9229	2
# bdf6c961840ba69ce14858ae8c2672d2b0011852d352eddb3cbee465973d0f69	?	0011	2/2	1.9180	2
# 5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0	?	0011	2/2	1.9248	2
# 97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37	?	0011	2/2	1.9199	2
# f2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213	?	0008	1/2	1.4219	2
# c80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744	?	0013	1/3	1.6406	2
# 65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59	?	0011	2/2	1.9219	2
# e2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d	?	0011	2/2	1.9219	2
# db96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228	?	0011	2/2	1.9238	2
# d8a9120b61b7b982765ae20dfe2b217d46b3b35ed1cdb0b2178c2f4fff5168a8	?	0011	2/2	1.9238	2
# ff3b91d3bc1fce464cd31935e7663eef28e168b1fa676795f8797c694bb90611	?	0011	2/2	1.9258	2
# 9af7e021acddc0eb766ba185fc6f79eebb9e1bdcb688b4f8cfc37728e1aaca79	?	0011	2/2	1.9209	2
# a3bfe489bb4ea021a7d45d40b803770b8892a09025170b290f74beb08e84659e	?	0008	1/2	1.4209	2


def make_page_5_1_block_transaction_numbers(block):
    block_transaction_information = {}
    block_transaction_information[
        "hash"
    ] = "c7e17c513d8f8fe7e271ce5343a903fd531e7214c1d706f8543a2851e1744320"
    block_transaction_information["outputs"] = "0.867455"
    block_transaction_information["size"] = "0.1025"
    block_transaction_information["version"] = "2"
    miner_reward_transaction_DataFrame = pd.DataFrame(
        {
            "hash": [
                "["
                + block_transaction_information["hash"]
                + "](tx"
                + block_transaction_information["hash"]
                + ")"
            ],
            "outputs": [block_transaction_information["outputs"]],
            "size [kB]": [block_transaction_information["size"]],
            "version": [block_transaction_information["version"]],
        }
    )

    block_transaction_information["num_of_transactions"] = "33"

    block_transaction_numbers_DataFrame = []

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # block_transaction_information:                  dictionary
    # miner_reward_transaction_DataFrame:            DataFrame
    # block_transaction_numbers_DataFrame:           DataFrame
    # ...
    # ================================================================

    return html.Div(
        [
            html.P(
                "Miner reward transaction",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=miner_reward_transaction_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "hash" or x == "height"
                        else {"id": x, "name": x}
                        for x in miner_reward_transaction_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "left",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: left")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start",
            ),
            html.P(
                "Transactions"
                + "("
                + str(block_transaction_information["num_of_transactions"])
                + ")",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=block_transaction_numbers_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "hash" or x == "height"
                        else {"id": x, "name": x}
                        for x in block_transaction_numbers_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell_conditional=[
                        {"if": {"column_id": "outputs"}, "min-width": "40px"},
                        {"if": {"column_id": "version"}, "min-width": "40px"},
                    ],
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "left",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflow": "auto",
                        "top": "0vh",
                        "left": "0vw",
                        "width": "95vw",
                        "max-height": "30vh",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: left")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start",
            ),
            html.Br(),
            html.Br(),
        ]
    )


# Block hash (height): 8831d7896711fe0b6bf85d40858cfd4c090e9b837cd522458954bae0d84e6f60 (2448593)
# Previous block: a12aab4f0b7ec8d75d8d0e8c350862a3f3411e24c8ccb5a91e44ecbacae366ae
# Next block: 0e19d20bfe45f4a9317e7665e2be4149ffe9bc49796342ebeae0527c388fc444
# BlockHeight: 2448590


# Timestamp [UTC] (epoch):	2021-09-13 16:38:19 (1631551099)	Age [y:d:h:m:s]:	01:271:13:59:26	Δ [h:m:s]:	00:01:04
# Major.minor version:	14.14	Block reward:	0.867058	Block size [kB]:	27.1699
# nonce:	16470	Total fees:	0.000398	No of txs:	15
# PoW hash:	0fd78b42f6a98cb932a76ade002489709f24f99aa2e795e9e9fd730200000000	Difficulty:	316629479126
def make_page_5_1_block(block):
    block_dictionary = {}
    block_dictionary[
        "blockHash"
    ] = "945d8cbf3db17b01633f99490886befc8d09d8e4f508545d7bf889f51aa8e7c7"
    block_dictionary[
        "previous_block"
    ] = "a12aab4f0b7ec8d75d8d0e8c350862a3f3411e24c8ccb5a91e44ecbacae366ae"
    block_dictionary[
        "next_block"
    ] = "0e19d20bfe45f4a9317e7665e2be4149ffe9bc49796342ebeae0527c388fc444"
    block_dictionary["blockHeight"] = "2448590"
    if len(block) > 7:
        block_dictionary["blockHash"] = block
    else:
        block_dictionary["blockHeight"] = block

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    #
    # block_dictionary:                     dictionary
    # ...
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Transaction Pool", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        type="text",
                        placeholder="block height,block hash, transaction hash",
                        className="d-flex align-content-start",
                    ),
                    dbc.Button(
                        [search_icon, ""],
                        id="transcation-publisher-hash-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-white",
                    ),
                ],
                className="mt-1 mb-1 mr-10",
            ),
            html.P(
                "Block hash (height): "
                + block_dictionary["blockHash"]
                + "("
                + block_dictionary["blockHeight"]
                + ")",
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                [
                    "Previous block: ",
                    html.A(
                        "" + block_dictionary["previous_block"],
                        href="block" + block_dictionary["previous_block"],
                    ),
                    "",
                ],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                [
                    "Next block: ",
                    html.A(
                        "" + block_dictionary["next_block"],
                        href="block" + block_dictionary["next_block"],
                    ),
                    "",
                ],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            make_page5_block_status(block),
            make_page_5_1_block_transaction_numbers(block),
        ],
        style={},
    )


def make_page_5_2_tx_check(param1):
    tx_check = {}
    tx_check[
        "txHash"
    ] = "f16f681796ef2aa4cae46acf502d03f52d6843de00a4b0d8b2144c26e09ce2e6"
    tx_check[
        "txPrefixHash"
    ] = "f16f681796ef2aa4cae46acf502d03f52d6843de00a4b0d8b2144c26e09ce2e6"
    tx_check[
        "txPublicKey"
    ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    tx_check["txPaymentId"] = "1c4d48af4a071950"

    tx_check["txTable1_timestamp"] = "Timestamp: 1666425153"
    tx_check["txTable1_timestamp_utc"] = "Timestamp [UTC]: 2022-10-22 07:52:33"
    tx_check["txTable1_age"] = "Age [y:d:h:m:s]: 00:228:02:08:24"

    tx_check["txTable1_block"] = "[Block: 2738885](block2738885)"
    tx_check["txTable1_fee_per_kB"] = "0.000137980000 (0.000040965938)"
    tx_check["txTable1_tx_size"] = "Tx size: 3.3682 kB"

    tx_check["txTable1_tx_version"] = "Tx version: 2"
    tx_check["txTable1_no_of_confirmations"] = "No of confirmations: 163951"
    tx_check["txTable1_ringct_type"] = "RingCT/type: yes/6"

    txTable1_DataFrame = pd.DataFrame(
        {
            "col0": [
                tx_check["txTable1_timestamp"],
                tx_check["txTable1_block"],
                tx_check["txTable1_tx_version"],
            ],
            "col1": [
                tx_check["txTable1_timestamp_utc"],
                tx_check["txTable1_fee_per_kB"],
                tx_check["txTable1_no_of_confirmations"],
            ],
            "col2": [
                tx_check["txTable1_age"],
                tx_check["txTable1_tx_size"],
                tx_check["txTable1_ringct_type"],
            ],
        }
    )
    tx_check[
        "txExtra"
    ] = "01d1041b3ab9294e944c1c1b1a5d3424e2af8810fae0a1160bd51aa597203f60ae0209018ecf9de6d87a19f9"

    tx_check["txNumOutputs"] = "2"
    txTable2_DataFrame = pd.DataFrame(
        {
            "stealth": ["00:", "01:"],
            "address": [
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
            ],
            "amount": ["?", "?"],
            "amount idx": ["N/A of 74900354", "N/A of 74900354"],
            "tag": ["<ba>", "<2b>"],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # param1 is the data sent from the textarea input
    #
    # tx_check:                        dictionary
    # txTable1_DataFrame:              DataFrame
    # txTable2_DataFrame:              DataFrame
    # ...
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Transaction Pool", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        type="text",
                        placeholder="block height,block hash, transaction hash",
                        className="d-flex align-content-start",
                    ),
                    dbc.Button(
                        [search_icon, ""],
                        id="transcation-publisher-hash-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-white",
                    ),
                ],
                className="mt-1 mb-1 mr-10",
            ),
            html.P(
                "Tx Hash: " + tx_check["txHash"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Tx prefix Hash: " + tx_check["txPrefixHash"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Tx public Key: " + tx_check["txPublicKey"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                "Payment id (encrypted): " + tx_check["txPaymentId"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=txTable1_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in txTable1_DataFrame.columns
                    ],
                    style_header={"display": "none"},
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "5vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
            html.P(
                "Extra: " + tx_check["txExtra"],
                className="text-center",
                style={"width": "95vw", "line-break": "anywhere"},
            ),
            html.P(
                dash_table.DataTable(
                    data=txTable2_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in txTable2_DataFrame.columns
                    ],
                    # style_header = {'display': 'none'},
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    fixed_rows={"headers": True},
                    page_size=1000,
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "5vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
            make_page_5_1_and_5_2_tx_inputs_of_total_xmrs(tx_check["txHash"]),
        ]
    )


def make_page_5_2_tx_push(param1):
    tx_push = {}
    tx_push[
        "txHash"
    ] = "f16f681796ef2aa4cae46acf502d03f52d6843de00a4b0d8b2144c26e09ce2e6"
    tx_push[
        "txPublicKey"
    ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    tx_push["txPaymentId"] = "1c4d48af4a071950"

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    #
    # param1 is the data sent from the textarea input
    #
    # tx_push:                        dictionary
    # ...
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Transaction Pool", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            html.Div(
                html.P("Transaction Pusher", className="text-center"),
                style={"width": "95vw"},
            ),
            html.P(
                "Attempting to push tx:" + tx_push["txHash"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Success",
                className="text-center",
                style={"overflow-wrap": "break-word", "color": "green"},
            ),
            html.P(
                "Your tx should aready in the txpool waiting to be included in an upcoming block.",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Go to tx: " + tx_push["txHash"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "source code | explorer version (api): master-2023-03-28-d669720(1.2)",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
        ]
    )


def make_page6():
    global conf_dict
    m = conf_dict["config"]["mining"]
    miner_enabled = True if m["enabled"] == "TRUE" else False
    miner_address = m["address"]
    miner_difficulty = m["difficulty"]

    return html.Div(
        [
            html.Br(),
            html.P("Miner", className="d-none"),
            dbc.InputGroup(
                [
                    daq.BooleanSwitch(
                        on=miner_enabled,
                        label="",
                        color=switch_col,
                        id="switch-miner-enabled",
                        style={"min-width": "80px"},
                    ),
                    dbc.Label("Miner", className="me-1 mt-1"),
                ],
                style={"min-width": "350px"},
            ),
            html.Div(
                [
                    "Mining is done with ",
                    html.A("P2Pool", href="https://github.com/SChernykh/p2pool"),
                    " and ",
                    html.A("XMRig", href="https://github.com/xmrig/xmrig"),
                    ".",
                ]
            ),
            html.Br(),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Mining Difficulty"),
                    dbc.Input(
                        type="number",
                        min=1024,
                        max=65535,
                        step=1,
                        id="input-miner-difficulty",
                        value=miner_difficulty,
                    ),
                ],
                className="me-1 mt-1",
                style={"max-width": "350px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Deposit Address"),
                    dbc.Input(
                        type="text",
                        value=miner_address,
                        style={"font-family": "monospace"},
                        id="input-miner-address",
                        pattern="^[4][1-9A-HJ-NP-Za-km-z]{94}$",
                    ),
                ],
                className="me-1 mt-1 pt-2",
                # style={"max-width": "800px"},
            ),
            html.Br(),
            dbc.Label("Warning: Your deposit address must start with a 4!"),
            dbc.Label(
                "Warning: The deposit address will be publicly viewable. For privacy, use a different wallet!"
            ),
        ]
    )


page5_2 = html.Div(
    [
        html.P("Block Explorer -> Transaction Pusher", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Transaction Pool").upper(),
                                        href="/block-explorer/tx-pool",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Transaction Pusher").upper(),
                                        href="/block-explorer/tx-pusher",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Key Images Checker").upper(),
                                        href="/block-explorer/key-images-checker",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Output Keys Checker").upper(),
                                        href="/block-explorer/output-keys-checker",
                                        className="sencondLevelNavlink",
                                    ),
                                ],
                                className="d-flex align-content-start bg-black",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="block height,block hash, transaction hash",
                    className="d-flex align-content-start boxNodo",
                ),
                dbc.Button(
                    [search_icon, ""],
                    id="transcation-publisher-hash-search",
                    n_clicks=0,
                    color="black",
                    className="d-flex align-content-start  border border-white",
                ),
            ],
            className="mt-1 mb-1 mr-10",
        ),
        html.Div(
            html.P("Transaction Pusher", className="text-center"),
            style={"width": "95vw"},
        ),
        html.P(
            "Paste here either a hex string or raw transaction",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "(the tx_blob response in the wallet RPC, or the raw_monero_tx file saved by the wallet CLI with --do-not-relay option specified), or base64 encoded, unsigned or signed transaction data.",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "(In Linux, can get the raw tx data: cat raw_monero_tx | xclip -selection clipboard)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            '(In Windows, can get the raw tx data: certutil.exe -encode -f raw_monero_tx_encoded.ext & type "encoded.txt" | clip)',
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dcc.Textarea(
            id="textarea_explorer_transaction_pusher",
            value="",
            className="boxNodo",
            style={"width": "100%", "height": 300},
        ),
        html.P(
            "Note: data is sent to the server, as the calculations are done on the server side",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            'Note: "check" does not work for the hex string of raw transaction',
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Check",
                                href="/block-explorer/tx-pusher/check",
                                className="d-flex justify-content-end text-center buttonNodo me-1 mt-1 ",
                                id="submit-val_explorer_transaction_pusher_check",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                            dbc.Button(
                                "Push",
                                href="/block-explorer/tx-pusher/push",
                                className="d-flex justify-content-end text-center buttonNodo ml-8 me-1 mt-1 ",
                                id="submit-val_explorer_transaction_pusher_push",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                        ],
                        className="d-flex justify-content-center ",
                        width=2,
                    )
                ],
                className="w-100",
                align="center",
                justify="center",
            ),
        ),
    ]
)


def page5_3_key_images_checker_check(param1, param2):
    key_images_checker_check = {}
    key_images_checker_check[
        "data_prefix"
    ] = "d8a53d51a8fc167fac8268214ef50165214dcf3abd30dbb2340f3f990398c42a"
    key_images_checker_check[
        "address"
    ] = "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7"
    key_images_checker_check[
        "viewkey"
    ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    key_images_DataFrame = pd.DataFrame(
        {
            "Key no.": ["00:", "01:"],
            "Key image": [
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
            ],
            "Is spent?": [True, False],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # param1 is the data sent from textarea input
    # param2 is the viewkey sent from text input
    #
    # key_images_checker_check:          dictionary
    # key_images_DataFrame:              DataFrame
    # ...
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Key Images Checker", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        type="text",
                        placeholder="block height,block hash, transaction hash",
                        className="d-flex align-content-start boxNodo",
                    ),
                    dbc.Button(
                        [search_icon, ""],
                        id="key-images-checker-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-white",
                    ),
                ],
                className="mt-1 mb-1",
            ),
            html.Div(
                html.P("Signed Key Images Checker", className="text-center"),
                style={"width": "95vw"},
            ),
            html.P(
                "Data file prefix: " + key_images_checker_check["data_prefix"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Key images for address: " + key_images_checker_check["address"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Viewkey: " + key_images_checker_check["viewkey"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                dash_table.DataTable(
                    data=key_images_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in key_images_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "5vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
        ]
    )


page5_3 = html.Div(
    [
        html.P("Block Explorer -> Key Images Checker", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Transaction Pool").upper(),
                                        href="/block-explorer/tx-pool",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Transaction Pusher").upper(),
                                        href="/block-explorer/tx-pusher",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Key Images Checker").upper(),
                                        href="/block-explorer/key-images-checker",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Output Keys Checker").upper(),
                                        href="/block-explorer/output-keys-checker",
                                        className="sencondLevelNavlink",
                                    ),
                                ],
                                className="d-flex align-content-start bg-black",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="block height,block hash, transaction hash",
                    className="d-flex align-content-start boxNodo",
                ),
                dbc.Button(
                    [search_icon, ""],
                    id="key-images-checker-search",
                    n_clicks=0,
                    color="black",
                    className="d-flex align-content-start  border border-white",
                ),
            ],
            className="mt-1 mb-1",
        ),
        html.Div(
            html.P("Signed Key Images Checker", className="text-center"),
            style={"width": "95vw"},
        ),
        html.P(
            "Paste base64 encoded, signed key images data here",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "(In Linux, can get base64 signed raw tx data: base64 your_key_images_file | xclip -selection clipboard)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            '(In Windows, can get base64 signed raw tx data: certutil.exe -encode -f your_key_images_file_encoded.txt & type "encoded.txt" | clip)',
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dcc.Textarea(
            id="textarea_explorer_transaction_key_images_checker",
            value="",
            className="boxNodo",
            style={"width": "100%", "height": 300},
        ),
        html.P(
            "Viewkey (key image file is encoded using your viewkey. This is needed for description)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "Note: data and viewkey are sent to the server, as the calculations are done on the server side.",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    id="input_explorer_transaction_key_images_checker",
                    className="boxNodo",
                ),
            ],
            className="me-1 mt-1",
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Check",
                                href="/block-explorer/key-images-checker/check",
                                className="d-flex justify-content-end text-center buttonNodo me-1 mt-1 ",
                                id="submit-val_explorer_transaction_key_images_checker_check",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                        ],
                        className="d-flex justify-content-center ",
                        width=2,
                    )
                ],
                className="w-100",
                align="center",
                justify="center",
            ),
        ),
    ]
)


def page5_4_signed_output_public_keys_checker_check(param1, param2):
    signed_output_public_keys_checker_check = {}
    signed_output_public_keys_checker_check[
        "data_prefix"
    ] = "d8a53d51a8fc167fac8268214ef50165214dcf3abd30dbb2340f3f990398c42a"
    signed_output_public_keys_checker_check[
        "address"
    ] = "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7"
    signed_output_public_keys_checker_check[
        "viewkey"
    ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    signed_output_public_keys_checker_check["total_xmr"] = 2
    output_public_key_DataFrame = pd.DataFrame(
        {
            "Output no.": ["00:", "01:"],
            "Public key": [
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
                "21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7",
            ],
            "Timestamp": [1666425153, 1666425150],
            "RingCT": ["yes/6", "yes/6"],
            "Is spent?": [True, False],
            "Amount": ["1", "2"],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # param1 is the data sent from textarea input
    # param2 is the viewkey sent from text input
    #
    # signed_output_public_keys_checker_check:    dictionary
    # output_public_key_DataFrame:                DataFrame
    # ...
    # ================================================================

    return html.Div(
        [
            html.P("Block Explorer -> Output Keys Checker", className="d-none"),
            html.Div(
                dbc.Navbar(
                    dbc.Container(
                        [
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavLink(
                                            ("Transaction Pool").upper(),
                                            href="/block-explorer/tx-pool",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="/block-explorer/tx-pusher",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="/block-explorer/key-images-checker",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="/block-explorer/output-keys-checker",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                    ],
                                    className="d-flex align-content-start bg-black",
                                    navbar=True,
                                ),
                                className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                                id="navbar-collapse1",
                                navbar=True,
                            ),
                        ]
                    ),
                    color="black",
                ),
                className="d-flex align-content-start",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        type="text",
                        placeholder="block height,block hash, transaction hash",
                        className="d-flex align-content-start boxNodo",
                    ),
                    dbc.Button(
                        [search_icon, ""],
                        id="key-images-checker-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-white",
                    ),
                ],
                className="mt-1 mb-1",
            ),
            html.Div(
                html.P("Signed Outputs Public Keys Checker", className="text-center"),
                style={"width": "95vw"},
            ),
            html.P(
                "Data file prefix: "
                + signed_output_public_keys_checker_check["data_prefix"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Key images for address: "
                + signed_output_public_keys_checker_check["address"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Viewkey: " + signed_output_public_keys_checker_check["viewkey"],
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Total xmr: "
                + str(signed_output_public_keys_checker_check["total_xmr"]),
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                dash_table.DataTable(
                    data=output_public_key_DataFrame.to_dict(orient="records"),
                    columns=[
                        {"id": x, "name": x, "presentation": "markdown"}
                        if x == "col0" or x == "height"
                        else {"id": x, "name": x}
                        for x in output_public_key_DataFrame.columns
                    ],
                    style_header={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_data={
                        "backgroundColor": "black",
                        "color": "white",
                        "border": "1px solid #202020",
                    },
                    style_cell={
                        "textAlign": "center",
                        "backgroundColor": "black",
                        "margin-bottom": "0",
                    },
                    style_table={
                        "overflowX": "auto",
                        "top": "5vh",
                        "left": "0vw",
                        "width": "95vw",
                        "bottom": "5vh",
                        "background-color": "black",
                        "marginLeft": "auto",
                        "marginRight": "auto",
                    },
                    css=[dict(selector="p", rule="margin: 0; text-align: center")],
                    markdown_options={"link_target": "_self"},
                    cell_selectable=False,
                ),
                className="d-flex align-content-start mb-10",
            ),
            html.Br(),
            html.Br(),
        ]
    )


page5_4 = html.Div(
    [
        html.P("Block Explorer -> Output Keys Checker", className="d-none"),
        html.Div(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        ("Transaction Pool").upper(),
                                        href="/block-explorer/tx-pool",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Transaction Pusher").upper(),
                                        href="/block-explorer/tx-pusher",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Key Images Checker").upper(),
                                        href="/block-explorer/key-images-checker",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Output Keys Checker").upper(),
                                        href="/block-explorer/output-keys-checker",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                ],
                                className="d-flex align-content-start",
                                navbar=True,
                            ),
                            className="d-sm-none d-md-none pt-0 pl-0 pr-0 pb-0",
                            id="navbar-collapse1",
                            navbar=True,
                        ),
                    ]
                ),
                color="black",
            ),
            className="d-flex align-content-start",
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    placeholder="block height,block hash, transaction hash",
                    className="d-flex align-content-start boxNodo",
                ),
                dbc.Button(
                    [search_icon, ""],
                    id="output-keys-checker-search",
                    n_clicks=0,
                    color="black",
                    className="d-flex align-content-start  border border-white",
                ),
            ],
            className="mt-1 mb-1",
        ),
        html.Div(
            html.P("Signed Output Public Keys Checker", className="text-center"),
            style={"width": "95vw"},
        ),
        html.P(
            "Paste base64 encoded, signed key images data here",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "(In Linux, can get base64 signed raw tx data: base64 your_key_images_file | xclip -selection clipboard)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            '(In Windows, can get base64 signed raw tx data: certutil.exe -encode -f your_key_images_file_encoded.txt & type "encoded.txt" | clip)',
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dcc.Textarea(
            id="textarea_explorer_transaction_output_keys_checker",
            value="",
            className="boxNodo",
            style={"width": "100%", "height": 300},
        ),
        html.P(
            "Viewkey (key image file is encoded using your viewkey. This is needed for description)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            "Note: data and viewkey are sent to the server, as the calculations are done on the server side.",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        dbc.InputGroup(
            [
                dbc.Input(
                    type="text",
                    id="input_explorer_transaction_output_keys_checker",
                    className="boxNodo",
                ),
            ],
            className="me-1 mt-1",
        ),
        dbc.Container(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Check",
                                href="/block-explorer/output-keys-checker/check",
                                className="d-flex justify-content-end text-center buttonNodo me-1 mt-1 ",
                                id="submit-val_explorer_transaction_output_keys_checker_check",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                        ],
                        className="d-flex justify-content-center ",
                        width=2,
                    )
                ],
                className="w-100",
                align="center",
                justify="center",
            ),
        ),
    ]
)


content = html.Div(id="page-content", className="d-flex justify-content-start")

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        custom_default,
        content,
        offcanvas,
        dcc.Interval(
            id="interval-component", interval=1000, n_intervals=0  # in milliseconds
        ),
        WindowBreakpoints(
            id="breakpoints",
            # Define the breakpoint thresholds
            widthBreakpointThresholdsPx=[650, 1000],
            # And their name, note that there is one more name than breakpoint thresholds
            widthBreakpointNames=["sm", "md", "lg"],
        ),
    ]
)


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname"), Input("url", "href")],
)
def render_page_content(pathname, value):
    # f=furl(pathname)
    # pathname = furl(pathname).netloc
    pattTx = re.compile(".*\/tx(.*)$")
    pattBlock = re.compile(".*\/block(.*)$")
    matchPattTx = pattTx.match(pathname)
    matchPattBlock = pattBlock.match(pathname)
    if pathname == "/":
        return make_page0()  # status
    elif pathname == "/status":  # /page-0
        return make_page0()
    elif pathname == "/networks":  # /page-1
        return make_page1_1()
    elif pathname == "/networks/clearnet":  # /page-1.1
        return make_page1_1()
    elif pathname == "/networks/tor":  # /page-1.2
        return make_page1_2()
    elif pathname == "/networks/i2p":  # /page-1.3
        return make_page1_3()
    elif pathname == "/node":  # /page-2
        return make_page2_1()
    elif pathname == "/node/private-node":  # /page-2.1
        return make_page2_1()
    elif pathname == "/node/bandwidth":  # /page-2.2
        return make_page2_2()
    elif pathname == "/device":  # /page-3
        return make_page3_1()
    elif pathname == "/device/wifi":  # /page-3.1
        return make_page3_1()
    elif pathname == "/device/ethernet":  # /page-3.2
        return make_page3_2()
    elif pathname == "/device/system":  # /page-3.3
        return make_page3_3()
    elif pathname == "/device/system/recovery":  # /page-3.3.2
        return make_page3_3_2()
    elif pathname == "/lws/active":  # /page-4.1
        return page4_1
    elif pathname == "/lws/inactive":  # /page-4.2
        return page4_2
    elif pathname == "/lws/add-account":  # /page-4
        return page4_3
    elif pathname == "/lws/add-account":  # /page-4.3
        return page4_3
    elif pathname == "/lws/requests":  # /page-4.4
        return page4_4
    elif pathname == "/block-explorer":  # /page-5
        return make_page5_1()
    elif pathname == "/block-explorer/tx-pool":  # /page-5.1
        return make_page5_1()
    elif pathname == "/block-explorer/tx-pusher":  # /page-5.2
        return page5_2
    elif pathname == "/block-explorer/tx-pusher/check":  # /page-5.2-tx-check
        f = furl(value)
        param1 = f.args["param1"]
        print(f.args["param1"])
        return make_page_5_2_tx_check(param1)
    elif pathname == "/block-explorer/tx-pusher/push":  # /page-5.2-tx-push
        f = furl(value)
        param1 = f.args["param1"]
        print(f.args["param1"])
        return make_page_5_2_tx_push(param1)
    elif pathname == "/block-explorer/key-images-checker":  # /page-5.3
        return page5_3
    elif (
        pathname == "/block-explorer/key-images-checker/check"
    ):  # /page-5-3-key-images-checker-check
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return page5_3_key_images_checker_check(param1, param2)
    elif pathname == "/block-explorer/output-keys-checker":  # /page-5.4
        return page5_4
    elif (
        pathname == "/block-explorer/output-keys-checker/check"
    ):  # /page-5-4-signed-output-public-keys-checker-check
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return page5_4_signed_output_public_keys_checker_check(param1, param2)
    elif (
        pathname == "/block-explorer/tx-pool/decode-outputs"
    ):  # /page-5.1-tx-decode-outputs
        prove = 0
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return make_page_5_1_tx_decode_or_prove_outputs(param1, param2, prove)
    elif (
        pathname == "/block-explorer/tx-pool/prove-spend"
    ):  # /page-5.1-tx-prove-sending
        prove = 1
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return make_page_5_1_tx_decode_or_prove_outputs(param1, param2, prove)
    elif matchPattTx:
        return make_page_5_1_tx(matchPattTx.group(1))
    elif matchPattBlock:
        return make_page_5_1_block(matchPattBlock.group(1))
    elif pathname == "/miner":  # /page-6
        return make_page6()
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 rounded-3",
    )


# ====================================================================
# ====================================================================
# Page 1 Callback Functions
# ====================================================================


# ====================================================================
# Page 1_1 Networks -> Clearnet -> Port (Input)
# Trigger by clicking the clearnet port (Input)
# ====================================================================
@app.callback(
    Output("networks-clearnet-port-hidden-div", "children"),
    Input("input-networks-clearnet-port", "value"),
    prevent_initial_call=True,
)
def update_switch_networks_clearnet_port(value):
    global page1_networks_clearnet
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by switch-networks-clearnet-port : " + str(value))
    page1_networks_clearnet["port"] = value

    # ================================================================
    # Add save function to write back
    # page1_networks_clearnet["port"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["monero_public_port"] = value

    return ""


# ====================================================================
# Page 1_1 Networks -> Clearnet -> Peer (Input)
# Trigger by clicking the clearnet peer (Input)
# ====================================================================
@app.callback(
    Output("networks-clearnet-peer-hidden-div", "children"),
    Input("input-networks-clearnet-peer", "value"),
    prevent_initial_call=True,
)
def update_switch_networks_clearnet_peer(value):
    global page1_networks_clearnet
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by switch-networks-clearnet-peer : " + str(value))
    page1_networks_clearnet["peer"] = value

    # ================================================================
    # Add save function to write back
    # page1_networks_clearnet["peer"] into backend.
    # ...
    # ================================================================
    # <++>

    return ""


# ====================================================================
# Page 1_2 Networks -> Tor -> Tor (Switch)
# Trigger by clicking the Tor (switch)
# ====================================================================
@app.callback(
    Output("networks-tor-hidden-div", "children"),
    Input("switch-networks-tor", "on"),
    prevent_initial_call=True,
)
def update_switch_networks_tor(value):
    global page1_networks_tor
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Switch) callback by switch-networks-tor : " + str(value))
    if value == True:
        page1_networks_tor["tor_switch"] = 1
    else:
        page1_networks_tor["tor_switch"] = 0
    # ================================================================
    # Add save function to write back
    # page1_networks_tor["tor_switch"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["tor_enabled"] = "TRUE" if value else "FALSE"
    save_config()

    return ""


# ====================================================================
# Page 1_2 Networks -> Tor -> Tor (Switch)
# Trigger by clicking the Tor (switch)
# ====================================================================
@app.callback(
    Output("networks-tor--route-all-connections-through-tor-hidden-div", "children"),
    Input("switch-networks-tor-route-all-connections-through-tor-switch", "on"),
    prevent_initial_call=True,
)
def update_switch_networks_clearnet(value):
    global page1_networks_tor
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Switch) callback by switch-networks-tor-route-all-connections-through-tor-switch : "
        + str(value)
    )
    if value == True:
        page1_networks_tor["route_all_connections_through_tor_switch"] = 1
    else:
        page1_networks_tor["route_all_connections_through_tor_switch"] = 0
    # ================================================================
    # Add save function to write back
    # page1_networks_tor["route_all_connections_through_tor_switch"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["torproxy_enabled"] = "TRUE" if value else "FALSE"
    save_config()

    return ""


# ====================================================================
# Page 1_2 Networks -> Tor -> Change (Button)
# Trigger by clicking the Tor -> Change (Button)
# ====================================================================
@app.callback(
    Output("input-networks-tor-onion-addr", "value"),
    Input("button-networks-tor-change", "n_clicks"),
    prevent_initial_call=True,
)
def update_switch_networks_tor_add_peer(n_clicks):
    global page1_networks_tor
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Button) callback by button-networks-tor-change")

    # ================================================================
    # Add update function here
    # Add load function here
    # Add Save function here
    # ...
    # ================================================================
    output_value = page1_networks_tor["onion_addr"]
    conf_dict["config"]["tor_address"] = output_value
    save_config()

    return output_value


# ====================================================================
# Page 1_2 Networks -> Tor -> Port (Input)
# Trigger by clicking the Tor port (Input)
# ====================================================================
@app.callback(
    Output("networks-tor-port-hidden-div", "children"),
    Input("input-networks-tor-port", "value"),
    prevent_initial_call=True,
)
def update_switch_networks_tor_port(value):
    global page1_networks_tor
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by switch-networks-tor-port : " + str(value))
    page1_networks_tor["port"] = value

    # ================================================================
    # Add save function to write back
    # page1_networks_tor["port"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["tor_port"] = value
    save_config()

    return ""


# ====================================================================
# Page 1_2 Networks -> Tor -> Peer (Input)
# Trigger by clicking the Tor peer (Input)
# ====================================================================
@app.callback(
    Output("networks-tor-peer-hidden-div", "children"),
    Input("input-networks-tor-peer", "value"),
    prevent_initial_call=True,
)
def update_switch_networks_tor_peer(value):
    global page1_networks_tor
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by switch-networks-tor-peer : " + str(value))
    page1_networks_tor["peer"] = value

    # ================================================================
    # Add save function to write back
    # page1_networks_tor["peer"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["add_tor_peer"] = value
    save_config()

    return ""

# ====================================================================
# Page 1_3 Networks -> I2P -> I2P Switch
# Trigger by clicking the Tor switch
# ====================================================================
@app.callback(
    Output("networks-i2p-hidden-div", "children"),
    Input("switch-networks-i2p", "on"),
    prevent_initial_call=True,
)
def update_switch_networks_i2p(value):
    global page1_networks_i2p
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Switch) callback by switch-networks-i2p : " + str(value))
    if value == True:
        page1_networks_i2p["i2p_switch"] = 1
    else:
        page1_networks_i2p["i2p_switch"] = 0
    # ================================================================
    # Add save function to write back
    # page1_networks_i2p["i2p_switch"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["i2p_enabled"] = "TRUE" if value else "FALSE"
    save_config()

    return ""


# ====================================================================
# Page 1_3 Networks -> I2P -> Change (Button)
# Trigger by clicking the I2P -> Change (Button)
# ====================================================================
@app.callback(
    Output("input-networks-i2p-i2p-b32-addr", "value"),
    Input("button-networks-i2p-change", "n_clicks"),
    prevent_initial_call=True,
)
def update_switch_networks_i2p_change(n_clicks):
    global page1_networks_i2p
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Button) callback by button-networks-i2p-change")

    # ================================================================
    # Add update function here
    # Add load function here
    # Add Save function here
    # ...
    output_value = page1_networks_i2p["i2p_b32_addr"]
    # ================================================================
    conf_dict["config"]["i2p_address"] = output_value
    save_config()

    return output_value


@app.callback(
    Output("qr-code-clearnet", "children"),
    Input("input-networks-clearnet-port", "value"),
    prevent_initial_call=True,
)
def update_qr_code_i2p(value):
    return dqm.DashQrGenerator(data=get_ip() + ":" + str(value), framed=True)


@app.callback(
    Output("qr-code-tor", "children"),
    Input("input-networks-tor-port", "value"),
    prevent_initial_call=True,
)
def update_qr_code_i2p(value):
    global page1_networks_i2p

    return dqm.DashQrGenerator(
        data=page1_networks_tor["onion_addr"] + ":" + str(value), framed=True
    )


@app.callback(
    Output("qr-code-i2p", "children"),
    Input("input-networks-i2p-port", "value"),
    prevent_initial_call=True,
)
def update_qr_code_i2p(value):
    global page1_networks_i2p

    return dqm.DashQrGenerator(
        data=page1_networks_i2p["i2p_b32_addr"] + ":" + str(value), framed=True
    )


# ====================================================================
# Page 1_3 Networks -> I2P -> Port (Input)
# Trigger by clicking the I2P port (Input)
# ====================================================================
@app.callback(
    Output("networks-i2p-port-hidden-div", "children"),
    Input("input-networks-i2p-port", "value"),
    prevent_initial_call=True,
)
def update_switch_networks_i2p_port(value):
    global page1_networks_i2p
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by switch-networks-i2p-port : " + str(value))
    page1_networks_i2p["port"] = value

    # ================================================================
    # Add save function to write back
    # page1_networks_i2p["port"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["i2p_port"] = value
    save_config()

    return ""


# ====================================================================
# Page 1_3 Networks -> I2P -> Peer (Input)
# Trigger by clicking the I2P Peer (Input)
# ====================================================================
@app.callback(
    Output("networks-i2p-peer-hidden-div", "children"),
    Input("input-networks-i2p-peer", "value"),
    prevent_initial_call=True,
)
def update_switch_networks_i2p_peer(value):
    global page1_networks_i2p
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by switch-networks-i2p-peer : " + str(value))
    page1_networks_i2p["peer"] = value

    # ================================================================
    # Add save function to write back
    # page1_networks_i2p["peer"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["add_i2p_peer"] = value
    save_config()

    return ""

# ====================================================================
# ====================================================================
# Page 2 Callback Functions
# ====================================================================
# Page 2_1 Node -> RPC -> RPC (Switch)
# Trigger by clicking the RPC (switch)
# ====================================================================
@app.callback(
    Output("node-rpc-hidden-div", "children"),
    Input("switch-node-rpc", "on"),
    prevent_initial_call=True,
)
def update_switch_node_rpc(value):
    global page2_node_rpc
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Switch) callback by switch-node-rpc : " + str(value))
    if value == True:
        page2_node_rpc["rpc_switch"] = 1
    else:
        page2_node_rpc["rpc_switch"] = 0

    # ================================================================
    # Add save function to write back
    # page2_node_rpc["rpc_switch"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["rpc_enabled"] = "TRUE" if value else "FALSE"
    save_config()

    return ""


# ====================================================================
# Page 2_1 Node -> RPC -> Apply (Button)
# Trigger by clicking the RPC -> Apply (Button)
# ====================================================================
@app.callback(
    Output("node-rpc-apply-hidden-div", "children"),
    Input("button-node-rpc-apply", "n_clicks"),
    [
        State("input-node-rpc-port", "value"),
        State("input-node-rpc-username", "value"),
        State("input-node-rpc-password", "value"),
    ],
    prevent_initial_call=True,
)
def update_node_rpc_apply(n_clicks, port, username, password):
    global page2_node_rpc
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Button) callback by button-node-rpc-apply Port: "
        + str(port)
        + ", Username "
        + str(username)
        + ", Password "
        + str(password)
    )
    page2_node_rpc["port"] = port
    page2_node_rpc["username"] = username
    page2_node_rpc["password"] = password

    # ================================================================
    # Add save function to write back
    # page2_node_rpc["port"] into backend.
    # page2_node_rpc["username"] into backend.
    # page2_node_rpc["password"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["monero_port"] = port
    conf_dict["config"]["rpcu"] = username
    conf_dict["config"]["rpcp"] = password
    save_config()

    return ""


# ====================================================================
# Page 2_2 Node -> Bandwidth -> Incoming peers limit (Input)
# Trigger by clicking the bandwidth -> Incoming peers limit (Input)
# ====================================================================
@app.callback(
    Output("node-bandwidth-incoming-peers-limit-hidden-div", "children"),
    Input("input-node-bandwidth-incoming-peers-limit", "value"),
    prevent_initial_call=True,
)
def update_input_node_bandwidth_incoming_peers_limit(value):
    global conf_dict
    global page2_node_bandwidth
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Input) callback by input-node-bandwidth-incoming-peers-limit : " + str(value)
    )
    page2_node_bandwidth["incoming_peers_limit"] = value

    # ================================================================
    # Add save function to write back
    # page2_node_bandwidth["incoming-peers-limit"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["in_peers"] = value
    save_config()

    return ""


# ====================================================================
# Page 2_2 Node -> Bandwidth -> Outgoing peers limit (Input)
# Trigger by clicking the bandwidth -> Outgoing peers limit (Input)
# ====================================================================
@app.callback(
    Output("node-bandwidth-outgoing-peers-limit-hidden-div", "children"),
    Input("input-node-bandwidth-outgoing-peers-limit", "value"),
    prevent_initial_call=True,
)
def update_input_node_bandwidth_outgoing_peers_limit(value):
    global conf_dict
    global page2_node_bandwidth
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Input) callback by input-node-bandwidth-outgoing-peers-limit : " + str(value)
    )
    page2_node_bandwidth["outgoing_peers_limit"] = value

    # ================================================================
    # Add save function to write back
    # page2_node_bandwidth["outgoing_peers_limit"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["out_peers"] = value
    save_config()

    return ""


# ====================================================================
# Page 2_2 Node -> Bandwidth -> Rate Limit Up (Input)
# Trigger by clicking the bandwidth -> Rate Limit Up (Input)
# ====================================================================
@app.callback(
    Output("node-bandwidth-rate-limit-up-hidden-div", "children"),
    Input("input-node-bandwidth-rate-limit-up", "value"),
    prevent_initial_call=True,
)
def update_input_node_bandwidth_rate_limit_up(value):
    global conf_dict
    global page2_node_bandwidth
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by input-node-bandwidth--rate-limit-up: " + str(value))
    page2_node_bandwidth["rate_limit_up"] = value

    # ================================================================
    # Add save function to write back
    # page2_node_bandwidth["rate_limit_up"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["limit_rate_up"] = value
    save_config()

    return ""


# ====================================================================
# Page 2_2 Node -> Bandwidth -> Rate Limit Down (Input)
# Trigger by clicking the bandwidth -> Rate Limit Down (Input)
# ====================================================================
@app.callback(
    Output("node-bandwidth-rate-limit-down-hidden-div", "children"),
    Input("input-node-bandwidth-rate-limit-down", "value"),
    prevent_initial_call=True,
)
def update_input_node_bandwidth_rate_limit_down(value):
    global conf_dict
    global page2_node_bandwidth
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by input-node-bandwidth--rate-limit-down: " + str(value))
    page2_node_bandwidth["rate_limit_down"] = value

    # ================================================================
    # Add save function to write back
    # page2_node_bandwidth["rate_limit_up"] into backend.
    # ...
    # ================================================================
    conf_dict["config"]["limit_rate_down"] = value
    save_config()

    return ""


# ====================================================================
# ====================================================================
# Page 3 Callback Functions
# ====================================================================
# Page 3_1 Device -> Wi-Fi -> Wi-Fi (Switch)
# Trigger by clicking the Wi-Fi (switch)
# ====================================================================
@app.callback(
    Output("device-wifi-hidden-div", "children"),
    Input("switch-device-wifi", "on"),
    prevent_initial_call=True,
)
def update_switch_device_wifi(value):
    global page3_device_wifi
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Switch) callback by switch-device-wifi : " + str(value))

    if value == True:
        page3_device_wifi["wifi_switch"] = 1
    else:
        page3_device_wifi["wifi_switch"] = 0

    # ================================================================
    # Add save function to write back
    # page3_device_wifi["wifi_switch"] into backend.
    # ...
    # ================================================================
    w: dict = conf_dict["config"]["wifi"]
    w["enabled"] = "TRUE" if value else "FALSE"
    proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
    save_config()

    return ""


# ====================================================================
# Page 3_1 Device -> Wi-Fi -> SSID (Input)
# Trigger by clicking the Wi-Fi -> SSID (Input)
# ====================================================================
@app.callback(
    Output("device-wifi-ssid-hidden-div", "children"),
    Input("input-device-wifi-ssid", "value"),
    prevent_initial_call=True,
)
def update_input_node_wifi_ssid(value):
    global conf_dict
    global page3_device_wifi
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by input-device-wifi-ssid : " + str(value))
    page3_device_wifi["ssid"] = value

    # ================================================================
    # Add save function to write back
    # page3_device_wifi["ssid"] into backend.
    # ...
    # ================================================================
    w: dict = conf_dict["config"]["wifi"]
    w["ssid"] = value
    proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
    save_config()

    return ""


# ====================================================================
# Page 3_1 Device -> Wi-Fi -> Passphrase (Input)
# Trigger by clicking the Wi-Fi -> Passphrase (Input)
# ====================================================================
@app.callback(
    Output("device-wifi-passphrase-hidden-div", "children"),
    Input("input-device-wifi-passphrase", "value"),
    prevent_initial_call=True,
)
def update_input_node_wifi_password(value):
    global conf_dict
    global page3_device_wifi
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print("(Input) callback by input-device-wifi-passphrase : " + str(value))
    page3_device_wifi["passphrase"] = value

    # ================================================================
    # Add save function to write back
    # page3_device_wifi["passphrase"] into backend.
    # ...
    # ================================================================
    w: dict = conf_dict["config"]["wifi"]
    w["pw"] = value
    proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
    save_config()

    return ""


# ====================================================================
# Page 3_1 Device -> Wi-Fi-> Automatic (Switch)
# Trigger by clicking the Wi-Fi -> Automatic (Switch)
# ====================================================================
@app.callback(
    [
        Output("input-device-wifi-ip-address", "disabled"),
        Output("input-device-wifi-subnet-mask", "disabled"),
        Output("input-device-wifi-router", "disabled"),
        Output("input-device-wifi-dhcp", "disabled"),
    ],
    Input("switch-device-wifi-automatic", "on"),
)
def update_input_device_wifi_ip_address_by_switches_input_device_wifi_automatic(value):
    global page3_device_wifi

    print("(Switch) callback by switch-device-wifi-automatic : " + str(value))
    if value == True:
        page3_device_wifi["automatic_switch"] = 1
    else:
        page3_device_wifi["automatic_switch"] = 0

    # ================================================================
    # Add save function to write back
    # page3_device_wifi["automatic_switch"] into backend.
    # ...
    # ================================================================
    w: dict = conf_dict["config"]["wifi"]
    w["auto"] = "TRUE" if value else "FALSE"
    proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
    save_config()

    if page3_device_wifi["automatic_switch"] == 1:
        return [True, True, True, True]
    else:
        return [False, False, False, False]
    return [False, False, False, False]


# ====================================================================
# Page 3_1 Device -> Wi-Fi-> IP Address text validation (Input)
# Trigger by clicking the Wi-Fi -> IP Address text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-wifi-ip-address", "valid"),
        Output("input-device-wifi-ip-address", "invalid"),
    ],
    [Input("input-device-wifi-ip-address", "value")],
    [State("input-device-wifi-ip-address", "pattern")],
)
def validate_input_device_wifi_ip_address_by_regex(value, pattern):
    global page3_device_wifi
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        page3_device_wifi["ip_address"] = value
        # ============================================================
        # Add save function to write back
        # page3_device_wifi["ip_address"] into backend.
        # ...
        # ============================================================
        w: dict = conf_dict["config"]["wifi"]
        w["ip"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# Page 3_1 Device -> Wi-Fi-> Subnet Mask text validation (Input)
# Trigger by clicking the Wi-Fi -> Subnet Mask text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-wifi-subnet-mask", "valid"),
        Output("input-device-wifi-subnet-mask", "invalid"),
    ],
    [Input("input-device-wifi-subnet-mask", "value")],
    [State("input-device-wifi-subnet-mask", "pattern")],
)
def validate_input_device_wifi_subnet_mask_by_regex(value, pattern):
    global page3_device_wifi
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        page3_device_wifi["subnet_mask"] = value
        # ============================================================
        # Add save function to write back
        # page3_device_wifi["subnet_mask"] into backend.
        # ...
        # ============================================================
        w: dict = conf_dict["config"]["wifi"]
        w["subnet"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# Page 3_1 Device -> Wi-Fi-> Router text validation (Input)
# Trigger by clicking the Wi-Fi -> Router text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-wifi-router", "valid"),
        Output("input-device-wifi-router", "invalid"),
    ],
    [Input("input-device-wifi-router", "value")],
    [State("input-device-wifi-router", "pattern")],
)
def validate_input_device_wifi_router_by_regex(value, pattern):
    global page3_device_wifi
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        page3_device_wifi["router"] = value
        # ============================================================
        # Add save function to write back
        # page3_device_wifi["router"] into backend.
        # ...
        # ============================================================
        w: dict = conf_dict["config"]["wifi"]
        w["router"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# Page 3_1 Device -> Wi-Fi-> dhcp text validation (Input)
# Trigger by clicking the Wi-Fi -> dhcp text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-wifi-dhcp", "valid"),
        Output("input-device-wifi-dhcp", "invalid"),
    ],
    [Input("input-device-wifi-dhcp", "value")],
    [State("input-device-wifi-dhcp", "pattern")],
)
def validate_input_device_wifi_dhcp_by_regex(value, pattern):
    global page3_device_wifi
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        page3_device_wifi["dhcp"] = value
        # ============================================================
        # Add save function to write back
        # page3_device_wifi["dhcp"] into backend.
        # ...
        # ============================================================
        w: dict = conf_dict["config"]["wifi"]
        w["dhcp"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# Page 3_2 Device -> Ethernet -> Automatic (Switch)
# Trigger by clicking the Ethernet -> Automatic (Switch)
# ====================================================================
@app.callback(
    [
        Output("input-device-ethernet-ip-address", "disabled"),
        Output("input-device-ethernet-subnet-mask", "disabled"),
        Output("input-device-ethernet-router", "disabled"),
        Output("input-device-ethernet-dhcp", "disabled"),
    ],
    # Input("switch-device-ethernet-automatic", "value")
    Input("switch-device-ethernet-automatic", "on"),
)
def update_input_device_ethernet_ip_address_by_switches_input_device_ethernet_automatic(
    value,
):
    global page3_device_ethernet

    print("(Switch) callback by switch-device-ethernet-automatic : " + str(value))
    if value == True:
        page3_device_ethernet["automatic_switch"] = 1
    else:
        page3_device_ethernet["automatic_switch"] = 0

    # ================================================================
    # Add save function to write back
    # page3_device_ethernet["automatic_switch"] into backend.
    # ...
    w: dict = conf_dict["config"]["ethernet"]
    w["auto"] = value
    proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
    save_config()

    if page3_device_ethernet["automatic_switch"] == 1:
        return [True, True, True, True]
    else:
        return [False, False, False, False]
    return [False, False, False, False]


# ====================================================================
# Page 3_2 Device -> Ethernet -> IP Address text validation (Input)
# Trigger by clicking the Ethernet -> IP Address text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-ethernet-ip-address", "valid"),
        Output("input-device-ethernet-ip-address", "invalid"),
    ],
    [Input("input-device-ethernet-ip-address", "value")],
    [State("input-device-ethernet-ip-address", "pattern")],
)
def validate_input_device_ethernet_ip_address_by_regex(value, pattern):
    global page3_device_ethernet
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        # ================================================================
        # Add save function to write back
        # page3_device_ethernet["ip_address"] into backend.
        # ...
        page3_device_ethernet["ip_address"] = value
        w: dict = conf_dict["config"]["ethernet"]
        w["ip"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# Page 3_2 Device -> Ethernet -> Subnet Mask text validation (Input)
# Trigger by clicking the Ethernet -> Subnet Mask text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-ethernet-subnet-mask", "valid"),
        Output("input-device-ethernet-subnet-mask", "invalid"),
    ],
    [Input("input-device-ethernet-subnet-mask", "value")],
    [State("input-device-ethernet-subnet-mask", "pattern")],
)
def validate_input_device_ethernet_subnet_mask_by_regex(value, pattern):
    global page3_device_ethernet
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        # ================================================================
        # Add save function to write back
        # page3_device_ethernet["subnet_mask"] into backend.
        # ...
        page3_device_ethernet["subnet_mask"] = value
        w: dict = conf_dict["config"]["ethernet"]
        w["subnet"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# Page 3_2 Device -> Ethernet -> Router text validation (Input)
# Trigger by clicking the Ethernet -> Router text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-ethernet-router", "valid"),
        Output("input-device-ethernet-router", "invalid"),
    ],
    [Input("input-device-ethernet-router", "value")],
    [State("input-device-ethernet-router", "pattern")],
)
def validate_input_device_ethernet_router_by_regex(value, pattern):
    global page3_device_ethernet
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        # ================================================================
        # Add save function to write back
        # page3_device_ethernet["router"] into backend.
        # ...
        page3_device_ethernet["router"] = value
        w: dict = conf_dict["config"]["ethernet"]
        w["router"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


# ====================================================================
# miner
# ====================================================================
@app.callback(
    [
        Output("input-miner-address", "valid"),
        Output("input-miner-address", "invalid"),
    ],
    [
        Input("switch-miner-enabled", "on"),
        Input("input-miner-difficulty", "value"),
        Input("input-miner-address", "value"),
    ],
    [State("input-miner-address", "pattern")],
)
def callback_miner(enabled, difficulty, address, pattern):
    global page3_device_ethernet
    patt = re.compile(pattern)

    if patt.match(address):
        # ================================================================
        # Add save function to write back
        # page3_device_ethernet["dhcp"] into backend.
        # ...
        w: dict = conf_dict["config"]["mining"]
        w["address"] = address
        w["enabled"] = "TRUE" if enabled else "FALSE"
        w["difficulty"] = difficulty
        save_config()
        return True, False
    return False, True


# ====================================================================
# Page 3_2 Device -> Ethernet -> dhcp text validation (Input)
# Trigger by clicking the Ethernet -> dhcp text validation (Input)
# ====================================================================
@app.callback(
    [
        Output("input-device-ethernet-dhcp", "valid"),
        Output("input-device-ethernet-dhcp", "invalid"),
    ],
    [Input("input-device-ethernet-dhcp", "value")],
    [State("input-device-ethernet-dhcp", "pattern")],
)
def validate_input_device_ethernet_dhcp_by_regex(value, pattern):
    global page3_device_ethernet
    patt = re.compile(pattern)

    if not value:
        return dash.no_update, dash.no_update

    if patt.match(value):
        # ================================================================
        # Add save function to write back
        # page3_device_ethernet["dhcp"] into backend.
        # ...
        page3_device_ethernet["dhcp"] = value
        w: dict = conf_dict["config"]["ethernet"]
        w["dhcp"] = value
        proc.run(["/usr/bin/bash", "/home/nodo/execScripts/update-net.sh"])
        save_config()
        return True, False
    else:
        return False, True


@app.callback(
    Output("label-time", "children"),
    [Input("interval-component", "n_intervals")],
)
def callback_time(n):
    time = datetime.datetime.now().strftime("%a %b %d, %I:%M %p")
    return [
        dbc.Label("XMR/USD: " + price, style={"padding-right": "20px"}),
        dbc.Label(time),
    ]


# ====================================================================
# ====================================================================
# Page 4 Callback Functions
# ====================================================================
# Page 4_1 Time interval callback for active_card_components
# ====================================================================
@app.callback(
    Output("active_card_components", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_active_card_components(n):
    global active_address_height
    global account_address_viewkey_height
    print("timer active_card_components")
    print("The active_address_height pair list is :", active_address_height)
    print(
        "The account_address_viewkey_height pair list is :",
        account_address_viewkey_height,
    )
    some_stuff = make_active_cards()  # your custom function
    component = html.Div(some_stuff)  # create new children for some-output-component
    return component


# ====================================================================
# Page 4_1 LWS -> Active -> Rescan Height (Input)
# ====================================================================
# TODO
@app.callback(
    Output("active-card-input-rescan-height-hidden-div", "children"),
    Input({"type": "active-rescan-input", "index": ALL}, "value"),
)
def account_input_rescan_height(value):
    global active_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if value != None and len(value) > 0:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

        if len(button_id) > 1:
            button_id = json.loads(button_id)
            index_clicked = button_id["index"]
            print(
                "index clicked",
                index_clicked,
            )
            print("active-rescan-input ", value)
            # (active_address_height[index_clicked])["scan_height"] = value[index_clicked]
            # lws_admin_cmd("rescan", "--arguments", str(value[index_clicked]),
            #             "--arguments", active_address_height[index_clicked]["address"])
        return ""
    else:
        return ""


# ====================================================================
# Page 4_1 LWS -> Active -> Rescan (Button)
# ====================================================================
@app.callback(
    Output("container-button-basic4_1a", "children"),
    [Input({"type": "active-rescan-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "active-rescan-button", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def account_creation_request_rescan_button(n_clicks, close_id):
    global active_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

    print(button_id)
    button_id = json.loads(button_id)
    index_clicked = button_id["index"]
    print(
        "index clicked",
        index_clicked,
    )
    print("n_clicks ", n_clicks[0])
    if n_clicks[0] != None or index_clicked > 0:
        print("do active-rescan action!!")
    return ""


# ====================================================================
# Page 4_1 LWS -> Active -> Deactive (button)
# ====================================================================
@app.callback(
    Output("container-button-basic4_1b", "children"),
    [Input({"type": "active-deactivate-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "active-deactivate-button", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def account_creation_request_deactivate_button(n_clicks, close_id):
    global active_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

    print(button_id)
    button_id = json.loads(button_id)
    index_clicked = button_id["index"]
    print(
        "index clicked",
        index_clicked,
    )
    print("n_clicks ", n_clicks[0])
    if n_clicks[0] != None or index_clicked > 0:
        print("do active-deactivate action!!")
        addr = active_address_height[index_clicked]["address"]
        lws_admin_cmd(
            "modify_account_status", "--arguments", "inactive", "--arguments", addr
        )
        inactive_address_height.append(active_address_height[index_clicked])
        active_address_height.pop(index_clicked)
        # ============================================================
        # Add save function to write back
        # inactive_address_height / active_address_height into backend.
        # ...
        # ============================================================
    return ""


# ====================================================================
# Page 4_2 Time interval callback for active_card_components
# ====================================================================
@app.callback(
    Output("inactive_card_components", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_active_card_components(n):
    global inactive_address_height
    global account_address_viewkey_height
    print("timer inactive_card_components")
    print("The inactive_address_height pair list is :", inactive_address_height)
    print(
        "The account_address_viewkey_height pair list is :",
        account_address_viewkey_height,
    )
    some_stuff = make_inactive_cards()  # your custom function
    component = html.Div(some_stuff)  # create new children for some-output-component
    return component


@app.callback(
    Output("submit-val-node-system-shutdown", "children"),
    [Input("submit-val-node-system-shutdown", "n_clicks")],
    prevent_initial_call=True,
)
def poweroff_button(n_clicks):
    print("callback triggered for shutdown")
    if n_clicks == 1:
        return "Click to Confirm"
    if n_clicks == 2:
        print("shutting down")
        backend_obj.shutdown();
        return "Shutting down!"

    return ""


# submit-val-node-system-recovery-start
@app.callback(
    [
        Output("submit-val-node-system-recovery-start", "children"),
        Output("submit-val-node-system-recovery-start", "disabled"),
    ],
    Input("checklist-inline-input-purge", "value"),
    [
        Input("checklist-inline-input-repair", "value"),
        Input("submit-val-node-system-recovery-start", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def restart_button(purge_value, repair_value, n_clicks):
    if n_clicks == 1:
        return "Click to Confirm", False
    if n_clicks == 2:
        repair = True if len(repair_value) > 0 and repair_value[0] == 1 else False
        purge = True if len(purge_value) > 0 and purge_value[0] == 1 else False
        e = os.environ.copy()
        if repair:
            e["REPAIR_FILESYSTEM"] = "1"
        if purge:
            e["PURGE_BLOCKCHAIN"] = "1"

        proc.Popen(["/usr/bin/bash", "/home/nodo/recovery.sh"], env=e)
        return "Running!", True

    return "Start", False


@app.callback(
    Output("submit-val-node-system-reset", "children"),
    [Input("submit-val-node-system-reset", "n_clicks")],
    prevent_initial_call=True,
)
def restart_button(n_clicks):
    if n_clicks == 1:
        return "Click to Confirm"
    if n_clicks == 2:
        print("shutting down")
        backend_obj.reboot()
        return "Restarting!"

    return ""


# ====================================================================
# Page 4_2 LWS Admin -> InActive -> Reactive
# ====================================================================
@app.callback(
    Output("inactive_dummy_components4_2a", "children"),
    [Input({"type": "inactive-reactivate-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "inactive-reactivate-button", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def inactive_reactivate_button(n_clicks, close_id):
    global inactive_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

    print(button_id)
    button_id = json.loads(button_id)
    index_clicked = button_id["index"]
    print(
        "index clicked",
        index_clicked,
    )
    print("n_clicks ", n_clicks[0])
    if n_clicks[0] != None or index_clicked > 0:
        print("do active-reactivate action!!")
        addr = inactive_address_height[index_clicked]["address"]
        lws_admin_cmd(
            "modify_account_status", "--arguments", "active", "--arguments", addr
        )
        active_address_height.append(inactive_address_height[index_clicked])
        inactive_address_height.pop(index_clicked)
        # ============================================================
        # Add save function to write back
        # inactive_address_height / active_address_height into backend.
        # ...
        # ============================================================
    return ""


# ====================================================================
# Page 4_2 LWS Admin -> InActive -> Delete
# ====================================================================
@app.callback(
    Output("inactive_dummy_components4_2b", "children"),
    [Input({"type": "inactive-delete-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "inactive-delete-button", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def inactive_delete_button(n_clicks, close_id):
    global inactive_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

    print(button_id)
    button_id = json.loads(button_id)
    index_clicked = button_id["index"]
    print(
        "index clicked",
        index_clicked,
    )
    print("n_clicks ", n_clicks[0])
    if n_clicks[0] != None or index_clicked > 0:
        print("do active-delete action!!")
        inactive_address_height.pop(index_clicked)

        # ============================================================
        # Add save function to write back
        # inactive_address_height into backend.
        # ...
        # ============================================================
    return ""


# ====================================================================
# Page 4_3 LWS Admin -> Add Account (Button)
# ====================================================================
@app.callback(
    Output("lwsadmin-add-account-address-hidden-div", "children"),
    Input("button-lwsadmin-add-account", "n_clicks"),
    State("input-lwsadmin-add-account-address", "value"),
    State("input-lwsadmin-add-account-private-viewkey", "value"),
)
def update_add_account(n_clicks, addressValue, privateViewkeyValue):
    global account_address_viewkey_height
    print(n_clicks)
    print(addressValue)
    print(privateViewkeyValue)
    start_height = "100"
    if addressValue != None and privateViewkeyValue != None:
        matchObj = re.match(r"^4", addressValue, re.M | re.I)
        if matchObj:
            # ========================================================
            # Add query function here to get "start_height" from backend
            # Add save function to save account_address_viewkey_height

            # ...
            # ========================================================
            lws_admin_cmd("add_account", addressValue, privateViewkeyValue)
            account_address_viewkey_height.append(
                (addressValue, privateViewkeyValue, start_height)
            )
        else:
            print("Address must be started with 4.")
    print("++++")
    print("The pair list is :", account_address_viewkey_height)
    print("-----")
    return ""


# ====================================================================
# Page 4_4 Time interval callback for request_card_components
# ====================================================================
@app.callback(
    Output("request_card_components", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_request_card_components(n):
    global active_address_height
    global account_address_viewkey_height
    print("timer request_card_components")
    print("The active_address_height pair list is :", active_address_height)
    print(
        "The account_address_viewkey_height pair list is :",
        account_address_viewkey_height,
    )
    some_stuff = make_account_create_request_cards()  # your custom function
    component = html.Div(some_stuff)  # create new children for some-output-component
    return component


# ====================================================================
# Page 4_4 Accept Creation Requests
# ====================================================================
@app.callback(
    Output("lwsadmin-account-creation-requests-hidden-div", "children"),
    [Input("button-lwsadmin-account-creation-requests", "n_clicks")],
)
def account_creation_request_accept_all_button(n):
    global active_address_height
    global account_address_viewkey_height
    if n == 0:
        return ""
    requests: dict = lws_admin_cmd("list_requests")
    if "create" in requests:
        requests = lws_admin_cmd("list_requests")["create"]
    for item in requests:
        address = str(item["address"])
        lws_admin_cmd("accept_requests", "create", "--arguments", address)
    # ============================================================
    # Add save function to write back
    # account_address_viewkey_height / account_address_viewkey_height  into backend.
    # ...
    # ============================================================
    return ""


# ====================================================================
# Page 4_4 Accept Creation Requests -> Accept Card
# ====================================================================
@app.callback(
    Output(
        "lwsadmin-account-creation-requests-request-accept-button-hidden-div",
        "children",
    ),
    [Input({"type": "request-accept-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "request-accept-button", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def account_creation_request_close_button(n_clicks, close_id):
    global active_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

    print(button_id)
    button_id = json.loads(button_id)
    index_to_remove = button_id["index"]
    print(
        "index_to_remove ",
        index_to_remove,
    )
    print("n_clicks ", n_clicks[0])
    if n_clicks[0] != None or index_to_remove > 0:
        print("do remove item action!!")
        index = account_address_viewkey_height[index_to_remove]
        print(index)
        address = index["address"]
        height = index["start_height"]
        rescan_height = ""
        # active_address_height.append([address, height, rescan_height])
        # account_create_request_lists.pop(index_to_remove)

        lws_admin_cmd("accept_requests", "create", "--arguments", address)
        # ============================================================
        # Add save function to write back
        # account_address_viewkey_height / account_address_viewkey_height  into backend.
        # ...
        # ============================================================
    return ""


# ====================================================================
# Page 4_4 Accept Creation Requests -> Reject Card
# ====================================================================
@app.callback(
    Output(
        "lwsadmin-account-creation-requests-request-reject-button-hidden-div",
        "children",
    ),
    [Input({"type": "request-reject-button", "index": ALL}, "n_clicks")],
    [
        State({"type": "request-reject-button", "index": ALL}, "id"),
    ],
    prevent_initial_call=True,
)
def account_creation_request_reject_button(n_clicks, reject_id):
    global active_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

    print(button_id)
    button_id = json.loads(button_id)
    index_to_remove = button_id["index"]
    print(
        "index_to_remove ",
        index_to_remove,
    )
    print("n_clicks ", n_clicks[0])
    if n_clicks[0] != None or index_to_remove > 0:
        print("do remove item action!!")
        index = account_address_viewkey_height[index_to_remove]
        address = index[0]
        height = index[2]
        rescan_height = ""

        lws_admin_cmd("reject_requests", "create", "--arguments", address)
        # ============================================================
        # Add save function to write back
        # account_address_viewkey_height / account_address_viewkey_height  into backend.
        # ...
        # ============================================================
    return ""


# ====================================================================
# Page 5_1 Decode Outputs (Input)
# ====================================================================
@app.callback(
    Output("submit-val-page5_1_decode_outputs", "href"),
    Input("input-page5_1_tx_monero_address_subaddress", "value"),
    Input("input-page5_1_tx_viewkey", "value"),
)
def update_button_decode_outputs_href(tx_monero_address_subaddress, tx_viewkey):
    global account_address_viewkey_height
    print("update_button_decode_outputs_href")
    print("tx_monero_address_subaddress", tx_monero_address_subaddress)
    print("tx_viewkey", tx_viewkey)
    print("tx_monero_address_subaddress", tx_monero_address_subaddress != None)
    print("tx_viewkey", tx_viewkey != None)
    if tx_monero_address_subaddress != None and tx_viewkey != None:
        if len(tx_monero_address_subaddress) > 0 and len(tx_viewkey) > 0:
            f = furl("/block-explorer/tx-pool/decode-outputs")
            f.add({"param1": tx_monero_address_subaddress})
            f.add({"param2": tx_viewkey})
            print(f.url)
            return f.url
    else:
        return ""

    return ""


# ====================================================================
# Page 5_1 Prove Sending (Input)
# ====================================================================
@app.callback(
    Output("submit-val-page5_1_prove_sending", "href"),
    Input("input-page5_1_tx_tx_private_key", "value"),
    Input("input-page5_1_tx_recipients_monero_address_subaddress", "value"),
)
def update_button_decode_outputs_href(
    tx_tx_private_key, tx_recipients_monero_address_subaddress
):
    print("update_button_decode_outputs_href")
    print("tx_tx_private_key", tx_tx_private_key)
    print(
        "tx_recipients_monero_address_subaddress",
        tx_recipients_monero_address_subaddress,
    )
    print("tx_tx_private_key", tx_tx_private_key != None)
    print(
        "tx_recipients_monero_address_subaddress",
        tx_recipients_monero_address_subaddress != None,
    )
    if tx_tx_private_key != None and tx_recipients_monero_address_subaddress != None:
        if (
            len(tx_tx_private_key) > 0
            and len(tx_recipients_monero_address_subaddress) > 0
        ):
            f = furl("/block-explorer/tx-pool/prove-spend")
            f.add({"param1": tx_tx_private_key})
            f.add({"param2": tx_recipients_monero_address_subaddress})
            print(f.url)
            return f.url
    else:
        return ""

    return ""


# ====================================================================
# Page 5_2 Transaction Pusher -> textarea (Input)
# ====================================================================
@app.callback(
    [
        Output("submit-val_explorer_transaction_pusher_check", "href"),
        Output("submit-val_explorer_transaction_pusher_push", "href"),
    ],
    Input("textarea_explorer_transaction_pusher", "value"),
)
def update_button_explorer_transaction_pusher_check_href(
    textarea_explorer_transaction_pusher,
):
    print("update href of submit-val_explorer_transaction_pusher_check")
    print("textarea_explorer_transaction_pusher", textarea_explorer_transaction_pusher)
    print(
        "textarea_explorer_transaction_pusher",
        textarea_explorer_transaction_pusher != None,
    )
    if textarea_explorer_transaction_pusher != None:
        if len(textarea_explorer_transaction_pusher) > 0:
            f = furl("/block-explorer/tx-pusher/check")
            f.add({"param1": textarea_explorer_transaction_pusher})
            f2 = furl("/block-explorer/tx-pusher/push")
            f2.add({"param1": textarea_explorer_transaction_pusher})
            print(f.url)
            print(f2.url)
            return [f.url, f2.url]
    else:
        return "", ""

    return "", ""


# ====================================================================
# Page 5_3 Key Images Checker -> textarea (Input)
# ====================================================================
@app.callback(
    Output("submit-val_explorer_transaction_key_images_checker_check", "href"),
    [
        Input("textarea_explorer_transaction_key_images_checker", "value"),
        Input("input_explorer_transaction_key_images_checker", "value"),
    ],
)
def update_button_explorer_transaction_key_images_checker_check_href(
    textarea_explorer_transaction_key_images_checker,
    input_explorer_transaction_key_images_checker,
):
    print("update href of submit-val_explorer_transaction_pusher_check")
    print(
        "textarea_explorer_transaction_key_images_checker",
        textarea_explorer_transaction_key_images_checker,
    )
    print(
        "textarea_explorer_transaction_key_images_checker",
        textarea_explorer_transaction_key_images_checker != None,
    )
    print(
        "input_explorer_transaction_key_images_checker",
        input_explorer_transaction_key_images_checker,
    )
    print(
        "input_explorer_transaction_key_images_checker",
        input_explorer_transaction_key_images_checker != None,
    )
    if (
        textarea_explorer_transaction_key_images_checker != None
        and input_explorer_transaction_key_images_checker != None
    ):
        if (
            len(textarea_explorer_transaction_key_images_checker) > 0
            and len(input_explorer_transaction_key_images_checker) > 0
        ):
            f = furl("/block-explorer/key-images-checker/check")
            f.add({"param1": textarea_explorer_transaction_key_images_checker})
            f.add({"param2": input_explorer_transaction_key_images_checker})
            print(f.url)
            return f.url
    else:
        return ""

    return ""


# ====================================================================
# Page 5_4 Output keys Checker -> textarea (Input)
# ====================================================================
@app.callback(
    Output("submit-val_explorer_transaction_output_keys_checker_check", "href"),
    [
        Input("textarea_explorer_transaction_output_keys_checker", "value"),
        Input("input_explorer_transaction_output_keys_checker", "value"),
    ],
)
def update_button_explorer_transaction_output_keys_checker_href(
    textarea_explorer_transaction_output_keys_checker,
    input_explorer_transaction_output_keys_checker,
):
    print("update href of submit-val_explorer_transaction_output_keys_checker_check")
    print(
        "textarea_explorer_transaction_output_keys_checker",
        textarea_explorer_transaction_output_keys_checker,
    )
    print(
        "textarea_explorer_transaction_output_keys_checker",
        textarea_explorer_transaction_output_keys_checker != None,
    )
    print(
        "input_explorer_transaction_output_keys_checker",
        input_explorer_transaction_output_keys_checker,
    )
    print(
        "input_explorer_transaction_output_keys_checker",
        input_explorer_transaction_output_keys_checker != None,
    )
    if (
        textarea_explorer_transaction_output_keys_checker != None
        and input_explorer_transaction_output_keys_checker != None
    ):
        if (
            len(textarea_explorer_transaction_output_keys_checker) > 0
            and len(input_explorer_transaction_output_keys_checker) > 0
        ):
            f = furl("/block-explorer/output-keys-checker/check")
            f.add({"param1": textarea_explorer_transaction_output_keys_checker})
            f.add({"param2": input_explorer_transaction_output_keys_checker})
            print(f.url)
            return f.url
    else:
        return ""

    return ""


## offcanvas floats on the top of website when it's opened
@app.callback(
    Output("offcanvas-placement", "is_open"),
    Input("submit-val", "n_clicks"),
    [State("offcanvas-placement", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


## submenu inside the offcanvas
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


def set_navitem_class(is_open):
    if is_open:
        return "open"
    return ""


for i in [1, 2, 3, 4, 5]:
    app.callback(
        Output(f"submenu-{i}-collapse", "is_open"),
        [Input(f"submenu-{i}", "n_clicks")],
        [State(f"submenu-{i}-collapse", "is_open")],
    )(toggle_collapse)

    app.callback(
        Output(f"submenu-{i}", "className"),
        [Input(f"submenu-{i}-collapse", "is_open")],
    )(set_navitem_class)


@app.callback(
    Output(f"sidebar", "style"),
    [Input(f"submit-val", "n_clicks")],
)
def update_style(click):
    if click == None:
        return SIDEBAR_STYLE
    if click % 2 == 0:
        return SIDEBAR_STYLE
    else:
        return SIDEBAR_STYLE


if __name__ == "__main__":
    if len(sys.argv) != 3:
        host = "127.0.0.1"
        port = 8888
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    stopFlag = threading.Event()
    thread = TimerThread(stopFlag)
    thread.start()
    load_config()
    load_page0_values()
    load_page1_values()
    load_page2_values()
    load_page3_values()
    load_page4_values()
    app.run_server(host=host, port=str(port), debug=False)
    stopFlag.set()
