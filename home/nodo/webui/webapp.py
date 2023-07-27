#!/usr/bin/env python

import sys
import json
import dash
import dash_bootstrap_components as dbc
from dash_breakpoints import WindowBreakpoints
from dash import Input, Output, State, dcc, html
from dash_bootstrap_components._components.Container import Container
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import datetime
from typing import Tuple
import re
from dash import html
from dash.dependencies import ALL, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_daq as daq
import dash_table
import pandas as pd
from pandas import json_normalize
from furl import furl

## parameters
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

# Page 5.1 ( BLOCK EXPLORER -> TRANSACTION POOL )
# transaction_pool_infomation={}


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
    ## Page 0

    # Sync Status
    page0_sync_status["sync_status"] = "Synchronized"
    page0_sync_status["timestamp"] = "1685381909"
    page0_sync_status["current_sync_height"] = 0
    page0_sync_status["monero_version"] = "0.18.0.0"
    page0_sync_status["outgoing_connections"] = 0
    page0_sync_status["incoming_connections"] = 0
    page0_sync_status["white_peerlist_size"] = 0
    page0_sync_status["grey_peerlist_size"] = 0
    page0_sync_status["update_available"] = "false"

    # System Status
    page0_system_status["mainnet_node"] = "Running"
    page0_system_status["private_node"] = "Running"
    page0_system_status["tor_node"] = "Running"
    page0_system_status["i2p_node"] = "Running"
    page0_system_status["monero_lws_admin"] = "Scanning"
    page0_system_status["block_explorer"] = "Running"

    # Hardware Status
    page0_hardware_status["cpu_percentage"] = 30
    page0_hardware_status["cpu_temp"] = 40.4
    page0_hardware_status["primary_storage"] = 50.5
    page0_hardware_status["backup_storage"] = 60.6
    page0_hardware_status["ram_percentage"] = 70.7

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================


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

    # Networks -> Clearnet
    page1_networks_clearnet["address"] = "address.test.com"
    page1_networks_clearnet["port"] = 1024
    page1_networks_clearnet["peer"] = "clearnet.peer.com"

    # Networks -> Tor
    page1_networks_tor["tor_switch"] = 1  # 1: true, 0: false
    page1_networks_tor[
        "route_all_connections_through_tor_switch"
    ] = 1  # 1: true, 0: false
    page1_networks_tor["onion_addr"] = 1024
    page1_networks_tor["port"] = 1024
    page1_networks_tor["peer"] = "tor.peer.com"

    # Networks -> I2P
    page1_networks_i2p["i2p_switch"] = 1  # 1: true, 0: false
    page1_networks_i2p["i2p_b32_addr"] = 1234
    page1_networks_i2p["port"] = 1234
    page1_networks_i2p["peer"] = "i2p.peer.com"

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================


# ====================================================================
# Description: load values for page2 web ui (Node)
# page2_node_rpc            : datatype python dictionary
# page2_node_bandwidth      : datatype python dictionary
# ====================================================================
def load_page2_values():
    global page2_node_rpc
    global page2_node_bandwidth
    ## Page 2

    # Node -> RPC
    page2_node_rpc["rpc_switch"] = 1  # 1: true, 0: false
    page2_node_rpc["port"] = 1024
    page2_node_rpc["username"] = "username"
    page2_node_rpc["password"] = "password"

    # Node -> Bandwidth
    page2_node_bandwidth["incoming_peers_limit"] = 20
    page2_node_bandwidth["outgoing_peers_limit"] = 20
    page2_node_bandwidth["rate_limit_up"] = -1
    page2_node_bandwidth["rate_limit_down"] = -1

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================


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

    # Device -> Wi-Fi
    page3_device_wifi["wifi_switch"] = 1  # 1: true, 0: false
    page3_device_wifi["ssid"] = "Nodo"
    page3_device_wifi["ssids"] = ["Nodo", "Nodo01", "Nodo02"]
    page3_device_wifi["passphrase"] = "password"
    page3_device_wifi["status"] = "connected"
    page3_device_wifi["automatic_switch"] = 1  # 1: true, 0: false
    page3_device_wifi["ip_address"] = "192.168.0.10"
    page3_device_wifi["subnet_mask"] = "255.255.255.0"
    page3_device_wifi["router"] = "192.168.0.1"
    page3_device_wifi["dhcp"] = "192.168.0.1"

    # Device -> Bandwidth
    page3_device_ethernet["automatic_switch"] = 1  # 1: true, 0: false
    page3_device_ethernet["ip_address"] = "192.168.0.10"
    page3_device_ethernet["subnet_mask"] = "255.255.255.0"
    page3_device_ethernet["router"] = "192.168.0.1"
    page3_device_ethernet["dhcp"] = "192.168.0.1"

    # Device -> System
    page3_device_system = {}

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary type
    # ...
    # ================================================================


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
                dbc.NavLink(("Clearnet").upper(), href="/page-1.1", active="partial"),
                dbc.NavLink(("Tor").upper(), href="/page-1.2", active="partial"),
                dbc.NavLink(("I2P").upper(), href="/page-1.3", active="partial"),
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
                    ("Private Node").upper(), href="/page-2.1", active="partial"
                ),
                dbc.NavLink(("Bandwidth").upper(), href="/page-2.2", active="partial"),
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
                dbc.NavLink(("Wi-Fi").upper(), href="/page-3.1", active="partial"),
                dbc.NavLink(("Ethernet").upper(), href="/page-3.2", active="partial"),
                dbc.NavLink(("System").upper(), href="/page-3.3", active="partial"),
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
                dbc.NavLink(("Active").upper(), href="/page-4.1", active="partial"),
                dbc.NavLink(("Inactive").upper(), href="/page-4.2", active="partial"),
                dbc.NavLink(
                    ("Add Account").upper(), href="/page-4.3", active="partial"
                ),
                dbc.NavLink(
                    ("Account Creation Requests").upper(),
                    href="/page-4.4",
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
                    ("Transaction Pool").upper(), href="/page-5.1", active="partial"
                ),
                dbc.NavLink(
                    ("Transaction Pusher").upper(), href="/page-5.2", active="partial"
                ),
                dbc.NavLink(
                    ("Key Images Checker").upper(), href="/page-5.3", active="partial"
                ),
                dbc.NavLink(
                    ("Output Keys Checker").upper(), href="/page-5.4", active="partial"
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
        dbc.DropdownMenuItem(("Clearnet").upper(), href="/page-1.1"),
        dbc.DropdownMenuItem(("Tor").upper(), href="/page-1.2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem(("I2P").upper(), href="/page-1.3"),
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
        dbc.DropdownMenuItem("RPC", href="/page-2.1"),
        dbc.DropdownMenuItem("Bandwidth", href="/page-2.2"),
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
        dbc.DropdownMenuItem("Wi-Fi", href="/page-3.1"),
        dbc.DropdownMenuItem("Ethernet", href="/page-3.2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("System", href="/page-3.3"),
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
        dbc.DropdownMenuItem("Active", href="/page-4.1"),
        dbc.DropdownMenuItem("Inactive", href="/page-4.2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Add Account", href="/page-4.3"),
        dbc.DropdownMenuItem("Account Creation Requests", href="/page-4.4"),
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
        dbc.DropdownMenuItem("Transaction Pool", href="/page-5.1"),
        dbc.DropdownMenuItem("Transaction Pusher", href="/page-5.2"),
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Key Images Checker", href="/page-5.3"),
        dbc.DropdownMenuItem("Output keys Checker", href="/page-5.4"),
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
NODO_LOGO = "assets/colors-and-nodo-150px.png"
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
                href="/page-0",
                style={"padding-left": "15px", "padding-right": "30px"},
            ),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink(
                            ("Networks").upper(),
                            href="/page-1",
                            class_name="",
                            id="navbar-collapse-navlink-networks",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Node").upper(),
                            href="/page-2",
                            class_name="",
                            id="navbar-collapse-navlink-node",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Device").upper(),
                            href="/page-3",
                            class_name="",
                            id="navbar-collapse-navlink-device",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Monero-LWS").upper(),
                            href="/page-4",
                            class_name="",
                            id="navbar-collapse-navlink-lws-admin",
                            active="partial",
                        ),
                        dbc.NavLink(
                            ("Block Explorer").upper(),
                            href="/page-5",
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


# Sync Status
# Sync Status: Synchronized/Synchronizing
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
    monero_version = page0_sync_status["monero_version"]
    timestamp = page0_sync_status["timestamp"]
    current_sync_height = page0_sync_status["current_sync_height"]
    outgoing_connections = page0_sync_status["outgoing_connections"]
    incoming_connections = page0_sync_status["incoming_connections"]
    white_peerlist_size = page0_sync_status["white_peerlist_size"]
    grey_peerlist_size = page0_sync_status["grey_peerlist_size"]
    update_available = page0_sync_status["update_available"]
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.Label("Sync Status:", className="me-1 mt-1"),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Sync Status:", className="homeBoxNodo"),
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
                            dbc.InputGroupText("Timestamp:", className="homeBoxNodo"),
                            dbc.Input(
                                type="text",
                                id="page0_sync_status_timestamp",
                                className="homeBoxNodoInput",
                                value=timestamp,
                                disabled=True,
                            ),
                        ],
                        className="me-1 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Current Sync Height:", className="homeBoxNodo"
                            ),
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
                                "Monero Version:", className="homeBoxNodo"
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
                                "Outgoing Connections:", className="homeBoxNodo"
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
                                "Incoming Connections:", className="homeBoxNodo"
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
                                "White Peerlist Size:", className="homeBoxNodo"
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
                                "Grey Peerlist Size:", className="homeBoxNodo"
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
                                "Update Available:", className="homeBoxNodo"
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


# System Status
# Mainnet Node: Running/Inactive
# Private Node: Running/Inactive
# Tor Node: Running/Inactive
# I2P Node: Running/Inactive
# Monero-LWS-Admin: Scanning/Inactive
# Block Explorer: Running
def make_page0_system_status():
    mainnet_node = page0_system_status["mainnet_node"]
    private_node = page0_system_status["private_node"]
    tor_node = page0_system_status["tor_node"]
    i2p_node = page0_system_status["i2p_node"]
    monero_lws_admin = page0_system_status["monero_lws_admin"]
    block_explorer = page0_system_status["block_explorer"]
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.Label("System Status:", className="me-0 mt-1"),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                "Mainnet Node:", className="homeBoxNodo"
                            ),
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
                            dbc.InputGroupText(
                                "Private Node:", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="text",
                                id="page0_system_status_private_node",
                                className="homeBoxNodoInput",
                                value=private_node,
                                disabled=True,
                            ),
                        ],
                        className="me-0 mt-1",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("Tor Node:", className="homeBoxNodo"),
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
                            dbc.InputGroupText("I2P Node:", className="homeBoxNodo"),
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
                            dbc.InputGroupText(
                                "Monero-LWS-Admin:", className="homeBoxNodo"
                            ),
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
                                "Block Explorer:", className="homeBoxNodo"
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


# Hardware Status
# CPU("%"): int
# CPU temp("°C"): float
# Primary Storage: Used SSD/Total SSD ("GB")
# Backup Storage: Used EMMC/Total EMMC ("GB")
# RAM: x ("%") Used RAM/ Total RAM ("GB")
def make_page0_hardware_status():
    global page0_sync_status
    global page0_system_status
    global page0_hardware_status
    cpu_percentage = str(page0_hardware_status["cpu_percentage"]) + " (%)"
    cpu_temp = str(page0_hardware_status["cpu_temp"]) + " (°C)"
    primary_storage = page0_hardware_status["primary_storage"]
    backup_storage = page0_hardware_status["backup_storage"]
    ram_percentage = page0_hardware_status["ram_percentage"]

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    "",
                    dbc.Label("Hardware Status:", className="me-0 mt-1"),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText("CPU:", className="homeBoxNodo"),
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
                            dbc.InputGroupText("CPU temp:", className="homeBoxNodo"),
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
                                "Primary Storage:", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="number",
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
                                "Backup Storage:", className="homeBoxNodo"
                            ),
                            dbc.Input(
                                type="number",
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
                            dbc.InputGroupText("RAM:", className="homeBoxNodo"),
                            dbc.Input(
                                type="number",
                                id="page0_system_status_monero_lws_admin",
                                className="homeBoxNodoInput",
                                value=ram_percentage,
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
                                            href="page-1.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Tor").upper(),
                                            href="page-1.2",
                                            class_name="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("I2P").upper(),
                                            href="page-1.3",
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
                        id="input-networks-clearnet-address", type="text", value=address
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
                style={"max-width": "150px"},
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
            dbc.Col(
                dbc.Button(
                    "Add Peer",
                    className="buttonNodo ms-auto fa fa-send ",
                    id="button-networks-clearnet-add-peer",
                    n_clicks=0,
                ),
                width="auto",
                className="me-1 mt-1 pt-2",
            ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="networks-clearnet-hidden-div", style={"display": "none"}),
            html.Div(id="networks-clearnet-port-hidden-div", style={"display": "none"}),
            html.Div(id="networks-clearnet-peer-hidden-div", style={"display": "none"}),
            html.Div(
                id="networks-clearnet-add-peer-hidden-div", style={"display": "none"}
            ),
            html.Br(),
            html.Br(),
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
                                            href="page-1.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Tor").upper(),
                                            href="page-1.2",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("I2P").upper(),
                                            href="page-1.3",
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
                    dbc.Label("Tor", className="me-1 mt-1"),
                    daq.BooleanSwitch(
                        on=tor_switch,
                        label="",
                        color="#0d6efd",
                        id="switch-networks-tor",
                    ),
                ],
                style={"min-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.Label(
                        "Route all connections through Tor", className="me-1 mt-1"
                    ),
                    daq.BooleanSwitch(
                        on=route_all_connections_through_tor_switch,
                        label="",
                        color="#0d6efd",
                        id="switch-networks-tor-route-all-connections-through-tor-switch",
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
                className="me-1 mt-1",
            ),
            dbc.Col(
                dbc.Button(
                    "Change",
                    className="buttonNodo ms-auto fa fa-send",
                    id="button-networks-tor-change",
                    n_clicks=0,
                ),
                width="auto",
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Port"),
                    dbc.Input(
                        id="input-networks-tor-port",
                        type="number",
                        min=1024,
                        max=65535,
                        step=1,
                        value=port,
                    ),
                ],
                className="me-1 mt-1 pt-2 pb-2",
                style={"max-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Peer"),
                    dbc.Input(id="input-networks-tor-peer", type="text", value=peer),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.Col(
                dbc.Button(
                    "Add Peer",
                    className="buttonNodo ms-auto fa fa-send ",
                    id="button-networks-tor-add-peer",
                    n_clicks=0,
                ),
                width="auto",
                className="me-1 mt-1 pt-2",
            ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="networks-tor-hidden-div", style={"display": "none"}),
            html.Div(
                id="networks-tor--route-all-connections-through-tor-hidden-div",
                style={"display": "none"},
            ),
            html.Div(id="networks-tor-port-hidden-div", style={"display": "none"}),
            html.Div(id="networks-tor-peer-hidden-div", style={"display": "none"}),
            html.Div(id="networks-tor-add-peer-hidden-div", style={"display": "none"}),
            html.Br(),
            html.Br(),
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
                                            href="page-1.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Tor").upper(),
                                            href="page-1.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("I2P").upper(),
                                            href="page-1.3",
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
                    dbc.Label("I2P", className="me-1 mt-1"),
                    daq.BooleanSwitch(
                        on=i2p_switch,
                        label="",
                        color="#0d6efd",
                        id="switch-networks-i2p",
                    ),
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
                className="me-1 mt-1",
            ),
            dbc.Col(
                dbc.Button(
                    "Change",
                    className="buttonNodo ms-auto fa fa-send",
                    id="button-networks-i2p-change",
                    n_clicks=0,
                ),
                width="auto",
                className="me-1 mt-1 pt-2",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Port"),
                    dbc.Input(
                        type="number",
                        min=1024,
                        max=65535,
                        step=1,
                        id="input-networks-i2p-port",
                        value=port,
                    ),
                ],
                className="me-1 mt-1 pt-2 pb-2",
                style={"max-width": "150px"},
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupText("Peer"),
                    dbc.Input(id="input-networks-i2p-peer", type="text", value=peer),
                ],
                className="me-1 mt-1 pt-2",
            ),
            dbc.Col(
                dbc.Button(
                    "Add Peer",
                    className="buttonNodo ms-auto fa fa-send ",
                    id="button-networks-i2p-add-peer",
                    n_clicks=0,
                ),
                width="auto",
                className="me-1 mt-1 pt-2",
            ),
            html.Div(html.P("", className="text-center"), style={"width": "95vw"}),
            html.Div(id="networks-i2p-hidden-div", style={"display": "none"}),
            html.Div(id="networks-i2p-port-hidden-div", style={"display": "none"}),
            html.Div(id="networks-i2p-peer-hidden-div", style={"display": "none"}),
            html.Div(id="networks-i2p-add-peer-hidden-div", style={"display": "none"}),
            html.Br(),
            html.Br(),
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
                                            href="page-2.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Bandwidth").upper(),
                                            href="page-2.2",
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
                        color="#0d6efd",
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
                style={"max-width": "150px"},
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
            dbc.Col(
                dbc.Button(
                    "Apply",
                    className="buttonNodo ms-auto fa fa-send ",
                    id="button-node-rpc-apply",
                    n_clicks=0,
                ),
                width="auto",
                className="me-1 mt-1 pt-2",
            ),
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
                                            href="page-2.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Bandwidth").upper(),
                                            href="page-2.2",
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
                    dbc.InputGroupText("Rate-limit up"),
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
                    dbc.InputGroupText("Rate-limit down"),
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
                                            href="page-3.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="page-3.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="page-3.3",
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
                        color="#0d6efd",
                        id="switch-device-wifi",
                    ),
                ],
                style={"min-width": "150px"},
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
                        color="#0d6efd",
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
        ]
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
                                            href="page-3.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="page-3.2",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="page-3.3",
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
                        color="#0d6efd",
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
                                            href="page-3.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Ethernet").upper(),
                                            href="page-3.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("System").upper(),
                                            href="page-3.3",
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
            dbc.Label(""),
            dbc.Col(
                dbc.Button(
                    "Reset",
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
                    href="/page-3.3.2",
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
            dbc.RadioItems(
                options=[
                    {"label": "  Attempt to repair filesystem", "value": "REPAIR"},
                    {"label": "  Wipe and reformat file system", "value": "WIPE"},
                ],
                value="REPAIR",
                id="radioitems-inline-input",
            ),
            dbc.Checklist(
                options=[
                    {"label": "  Purge blockchain", "value": 1},
                ],
                value=[],
                id="checklist-inline-input",
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
                href="/page-3.3",
                className="ml-8 me-1 mt-1 node-system-recovery-cancel-button",
                id="submit-val-node-system-recovery-cancel",
                n_clicks=0,
            ),
        ]
    )


def make_inactive_card(n_add, address, height, rescan_height):
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
                                                    address,
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
                                                    },
                                                ),
                                                style={
                                                    "min-width": "100px",
                                                    "max-width": "850px",
                                                },
                                            ),
                                        ],
                                        className="flex-grow-1 g-0 w-100 LWSCardBG",
                                    ),
                                ],
                                className=" me-1 mt-1 g-0 account_card",  # style={"min-width":"300px","max-width": "65%"}
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "Height",
                                        className="LWSBoxNodo text-left",
                                        style={"max-width": "110px", "height": "100%"},
                                    ),
                                    dbc.Input(
                                        type="text",
                                        value=height,
                                        className="NodoLWSInput",
                                        disabled=True,
                                        style={"height": "100%"},
                                    ),
                                ],
                                className="d-flex align-content-start  me-1 mt-1 LWSCardBG",
                                style={"max-width": "200px"},
                            ),
                        ],
                        className="d-flex align-content-start LWSCardBG",
                    ),
                    dbc.Label("Rescan Height", className="me-1 mt-3 mb-0"),
                    dbc.InputGroup(
                        [
                            dbc.Input(type="text", value=rescan_height, disabled=True),
                        ],
                        className="me-1 mt-0 mb-2",
                        style={"width": "150px"},
                    ),
                    dbc.Label(""),
                    dbc.Button(
                        "Reactivate",
                        className="buttonNodo me-1 mt-1 ms-auto fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1",
                        id={"type": "inactive-reactivate-button", "index": n_add},
                    ),
                    dbc.Button(
                        "Delete",
                        className="buttonNodo me-1 mt-1 ms-auto fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1 ",
                        id={"type": "inactive-delete-button", "index": n_add},
                    ),
                ]
            ),
        ],
        id={"type": "inactive-card", "index": n_add},
        # style={"max-width": "1150px"},
        className="mt-1 LWSCardBG",
    )


def make_inactive_cards():
    global inactive_address_height
    address = "4567"
    height = ""
    rescan_height = ""
    index = 0
    print("----")
    print("The inactive_address_height pair list is :", inactive_address_height)

    account_create_request_lists = []
    for item in inactive_address_height:
        print(item)
        print(item[0])
        print(item[1])
        print(item[2])
        address = str(item[0])
        height = str(item[1])
        rescan_height = str(item[2])
        account_create_request_lists.append(
            make_inactive_card(index, address, height, rescan_height)
        )
        index = index + 1

    return account_create_request_lists


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
                                                    address,
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
                                                    },
                                                ),
                                                style={
                                                    "min-width": "100px",
                                                    "max-width": "850px",
                                                },
                                            ),
                                        ],
                                        className="flex-grow-1 g-0 w-100 LWSCardBG",
                                    ),
                                ],
                                className=" me-1 mt-1 g-0 account_card",  # style={"min-width":"300px","max-width": "65%"}
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "Height",
                                        className="LWSBoxNodo text-left",
                                        style={"max-width": "110px", "height": "100%"},
                                    ),
                                    dbc.Input(
                                        type="text",
                                        value=height,
                                        className="NodoLWSInput",
                                        disabled=True,
                                        style={"height": "100%"},
                                    ),
                                ],
                                className="d-flex align-content-start  me-1 mt-1 LWSCardBG",
                                style={"max-width": "200px"},
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
                    dbc.Label(""),
                    dbc.Button(
                        "Rescan",
                        className="buttonNodo me-1 mt-1 ms-auto fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1",
                        id={"type": "active-rescan-button", "index": n_add},
                        disabled=rescan_button_disable,
                    ),
                    dbc.Button(
                        "Deactivate",
                        className="buttonNodo me-1 mt-1 ms-auto fa fa-send mt-1 ml-1 mr-1 pt-1 pl-1 pr-1 ",
                        id={"type": "active-deactivate-button", "index": n_add},
                    ),
                ]
            ),
        ],
        id={"type": "active-card", "index": n_add},
        # style={"max-width": "1150px"},
        className="mt-1 LWSCardBG",
    )


def make_active_cards():
    global active_address_height
    address = "4567"
    height = ""
    rescan_height = ""
    index = 0
    print("----")
    print("The active_address_height pair list is :", active_address_height)

    account_create_request_lists = []
    for item in active_address_height:
        print(item)
        print(item[0])
        print(item[1])
        print(item[2])
        address = str(item[0])
        height = str(item[1])
        rescan_height = str(item[2])
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
                                                    address,
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
                                                    },
                                                ),
                                                style={
                                                    "min-width": "100px",
                                                    "max-width": "850px",
                                                },
                                            ),
                                        ],
                                        className="flex-grow-1 g-0 w-100 LWSCardBG",
                                    ),
                                ],
                                className=" me-1 mt-1 g-0 account_card",  # style={"min-width":"300px","max-width": "65%"}
                            ),
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        "Start Height",
                                        className="LWSBoxNodo text-left",
                                        style={"max-width": "110px", "height": "100%"},
                                    ),
                                    dbc.Input(
                                        type="text",
                                        value=height,
                                        className="NodoLWSInput",
                                        disabled=True,
                                        style={"height": "100%"},
                                    ),
                                ],
                                className="d-flex align-content-start  me-1 mt-1 LWSCardBG",
                                style={"max-width": "200px"},
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
    address = "4567"
    viewkey = "1234"
    height = "100"
    index = 0
    print("----")
    print("The pair list is :", account_address_viewkey_height)

    account_create_request_lists = []
    for item in account_address_viewkey_height:
        print(item)
        print(item[0])
        print(item[1])
        print(item[2])
        address = str(item[0])
        viewkey = str(item[1])
        height = str(item[2])
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
                                        href="page-4.1",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="page-4.2",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="page-4.3",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="page-4.4",
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
                                        href="page-4.1",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="page-4.2",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="page-4.3",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="page-4.4",
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
                                        href="page-4.1",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="page-4.2",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="page-4.3",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="page-4.4",
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
                                        href="page-4.1",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Inactive").upper(),
                                        href="page-4.2",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Add Account").upper(),
                                        href="page-4.3",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Account Creation Requests").upper(),
                                        href="page-4.4",
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
    # transaction_pool_infomation;
    transaction_pool_infomation = {}
    transaction_pool_infomation["server_time"] = "2023-4-27 20:36:27"
    transaction_pool_infomation["network_difficulty"] = "327906897405"
    transaction_pool_infomation["hard_fork"] = "v16"
    transaction_pool_infomation["hash_rate"] = "2.732 GH/s"
    transaction_pool_infomation["fee_per_byte"] = "0.000000020000"
    transaction_pool_infomation["median_block_size_limit"] = "292.97 kB"
    transaction_pool_infomation["monero_emission"] = "18271422.065"
    transaction_pool_infomation["monero_emission_fees"] = "99595.517"
    transaction_pool_infomation["monero_emission_fees_as_of_block"] = "2873707"

    transaction_pool_infomation["no_of_txs"] = "17"
    transaction_pool_infomation["size_of_txs"] = "29.46kB"
    transaction_pool_infomation["transactions_in_the_last_blocks"] = "11"
    transaction_pool_infomation["median_size_of_100_blocks"] = "292.97 kB"
    ## parameters for transaction pool ( Page 5.1 Transaction Pool)
    transactionPoolDF = pd.DataFrame(
        {
            "age [h:m:s]": ["00:00:22", "00:00:37", "00:00:44"],
            "transaction hash": [
                "[e7cbf1e76041d93ef0b672955ebecfc52b4d24e5402168548855cc0f6049e67e](/txe7cbf1e76041d93ef0b672955ebecfc52b4d24e5402168548855cc0f6049e67e)",
                "[153bada79026d209316145984b8aa98141fe34f62f05a300f85ab74f1f728284](/tx153bada79026d209316145984b8aa98141fe34f62f05a300f85ab74f1f728284)",
                "[2eed4ea669d552215ec2be3e9c6686da2e488391d79b56f3b8fae73500578a5d](/tx2eed4ea669d552215ec2be3e9c6686da2e488391d79b56f3b8fae73500578a5d)",
            ],
            "fee/per_kB [µɱ]": ["0031/0020", "0160/0107", "0044/0020"],
            "in/out": ["1/2", "1/2", "2/2"],
            "tx size [kB]": ["1.50", "1.50", "2.17"],
        }
    )

    transactionInTheLastBlock = pd.DataFrame(
        {
            "height": [
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
                "[2902010](block2902010)",
            ],
            "age [h:m:s]": [
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
                "00:05:13",
            ],
            "size [kB]": [
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
                "34.45",
            ],
            "transaction hash": [
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
                "[8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667](/tx8ecec2abff451e7ff0eff2e8e2278d080d9808f17182fbded0da81fc9bdd6667)",
                "[f2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb](/txf2d5fd936429b2c54ad47cf5ac508580767e92fac210861295cd8139c41c5ccb)",
                "[709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691](/tx709817acf581b6feae569a5239a80093e6547d339c261ecab406a63a2ee2e691)",
            ],
            "fee [µɱ]": [
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
                "N/A",
                "0044",
                "0122",
            ],
            "outputs": [
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
                "0.602",
                "?",
                "?",
            ],
            "in/out": [
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
                "0/36",
                "2/2",
                "1/2",
            ],
            "tx size [kB]": [
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
                "1.46",
                "2.16",
                "1.50",
            ],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # transaction_pool_infomation:  dictionary
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
    f = open("./json/demo/transactions.json")

    # returns JSON object as
    # a dictionary
    transactionInTheLastBlock = transactionInTheLastBlock.iloc[0:0]
    data = json.load(f)
    print(data)
    outputs_DataFrame = json_normalize(data["data"]["blocks"])
    print(outputs_DataFrame)
    for ind in outputs_DataFrame.index:
        outputs_txs_DataFrame = json_normalize(outputs_DataFrame["txs"][ind])
        height = (
            "["
            + str(outputs_DataFrame["height"][ind])
            + "](block"
            + str(outputs_DataFrame["height"][ind])
            + ")"
        )
        age = outputs_DataFrame["age"][ind]
        size = str(round((outputs_DataFrame["size"][ind] / 1024), 2))
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
            tx_fee = str(round(outputs_txs_DataFrame["tx_fee"][indexTXS] / 1000000, 0))
            tx_size = str(round(outputs_txs_DataFrame["tx_size"][indexTXS] / 1024, 0))
            xmr_outputs = str(
                round(outputs_txs_DataFrame["xmr_outputs"][indexTXS] / 1000000000000, 3)
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
                                            href="page-5.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                        id="transcation-pool-hash-search",
                        n_clicks=0,
                        color="black",
                        className="d-flex align-content-start  border border-whilte",
                    ),
                ],
                className="mt-1 mb-1",
            ),
            html.P(
                "Server time: "
                + transaction_pool_infomation["server_time"]
                + " | Network difficulty: "
                + transaction_pool_infomation["network_difficulty"]
                + " | Hard fork: "
                + transaction_pool_infomation["hard_fork"]
                + " | Hash rate: "
                + transaction_pool_infomation["hash_rate"]
                + " | Fee per byte: "
                + transaction_pool_infomation["fee_per_byte"]
                + " | Median block size limit: "
                + transaction_pool_infomation["median_block_size_limit"]
                + " ",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Monero emission (fees) is "
                + transaction_pool_infomation["monero_emission"]
                + "("
                + transaction_pool_infomation["monero_emission_fees"]
                + ") as of "
                + transaction_pool_infomation["monero_emission_fees_as_of_block"]
                + " block",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "Transaction Pool",
                className="text-center",
                style={"overflow-wrap": "break-word"},
            ),
            html.P(
                "(no of txs: "
                + transaction_pool_infomation["no_of_txs"]
                + ", size: "
                + transaction_pool_infomation["size_of_txs"]
                + ", updated every 5 seconds)",
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
                        {
                            "if": {"column_id": "age [h:m:s]"},
                            "width": "21%",
                            "min-width": "225px",
                        },
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
                    html.P(
                        "(Median size of 100 blocks: 292.97 kB)",
                        className="text-center",
                    ),
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
                                href="/page-5.1-tx-decode-outputs",
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
# key image 00: 3f6e7190d088c0f61554d554c6318ee99518c30a1e81082f570ff086d0ae9167	amount: ?
# ring members	blk	ring size	in/out	timestamp	age [y:d:h:m:s]
# - 00: 52c013c1e6cf535a06b3763a07651211239d225db73b5e731bba71b0733bdd87	02306487	11	1/2	2021-02-28 04:21:18	02:103:22:58:49
# - 01: d6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1	02435894	11	2/2	2021-08-26 23:19:37	01:289:04:00:30
# - 02: f7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa	02442403	11	2/5	2021-09-04 23:42:21	01:280:03:37:46
# - 03: 4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8	02445287	11	1/2	2021-09-08 23:57:27	01:276:03:22:40
# - 04: 82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387	02446488	11	2/2	2021-09-10 17:34:37	01:274:09:45:30
# - 05: 8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab	02447662	11	1/2	2021-09-12 08:46:30	01:272:18:33:37
# - 06: 879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353	02447969	11	2/2	2021-09-12 18:20:54	01:272:08:59:13
# - 07: 0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972	02447992	11	1/2	2021-09-12 19:18:47	01:272:08:01:20
# - 08: ab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd	02448050	11	2/2	2021-09-12 21:31:16	01:272:05:48:51
# - 09: ee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881	02448269	0	0/1	2021-09-13 05:07:24	01:271:22:12:43
# - 10: f938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac	02448306	11	1/2	2021-09-13 06:47:28	01:271:20:32:39
# ring members	blk	ring size	in/out	timestamp	age [y:d:h:m:s]
def make_page_5_1_and_5_2_tx_inputs_of_total_xmrs(tx):
    transaction_pool_tx_inputs_of_total_xmrs = {}
    transaction_pool_tx_inputs_of_total_xmrs["num_of_xmrs"] = "31"
    key_image_DataFrame = pd.DataFrame(
        {
            "col0": [
                "key image 00: 3f6e7190d088c0f61554d554c6318ee99518c30a1e81082f570ff086d0ae9167"
            ],
            #        'col1': ["amount: ?"],
        }
    )
    key_image_ring_members_DataFrame = pd.DataFrame(
        {
            "ring members": [
                "[- 00: 52c013c1e6cf535a06b3763a07651211239d225db73b5e731bba71b0733bdd87](tx52c013c1e6cf535a06b3763a07651211239d225db73b5e731bba71b0733bdd87)",
                "[- 01: d6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1](txd6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1)",
                "[- 02: f7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa](txf7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa)",
                "[- 03: 4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8](tx4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8)",
                "[- 04: 82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387](tx82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387)",
                "[- 05: 8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab](tx8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab)",
                "[- 06: 879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353](tx879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353)",
                "[- 07: 0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972](tx0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972)",
                "[- 08: ab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd](txab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd)",
                "[- 09: ee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881](txee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881)",
                "[- 10: f938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac](txf938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac)",
                "[- 11: d6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1](txd6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1)",
                "[- 12: f7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa](txf7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa)",
                "[- 13: 4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8](tx4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8)",
                "[- 14: 82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387](tx82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387)",
                "[- 15: 8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab](tx8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab)",
                "[- 16: 879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353](tx879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353)",
                "[- 17: 0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972](tx0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972)",
                "[- 18: ab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd](txab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd)",
                "[- 19: ee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881](txee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881)",
                "[- 20: f938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac](txf938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac)",
                "[- 21: d6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1](txd6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1)",
                "[- 22: f7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa](txf7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa)",
                "[- 23: 4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8](tx4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8)",
                "[- 24: 82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387](tx82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387)",
                "[- 25: 8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab](tx8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab)",
                "[- 26: 879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353](tx879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353)",
                "[- 27: 0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972](tx0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972)",
                "[- 28: ab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd](txab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd)",
                "[- 29: ee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881](txee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881)",
                "[- 30: f938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac](txf938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac)",
            ],
            "blk": [
                "02306487",
                "02435894",
                "02442403",
                "02445287",
                "02446488",
                "02447662",
                "02447969",
                "02447992",
                "02448269",
                "02448306",
                "02448306",
                "02306487",
                "02435894",
                "02442403",
                "02445287",
                "02446488",
                "02447662",
                "02447969",
                "02447992",
                "02448269",
                "02448306",
                "02448306",
                "02306487",
                "02435894",
                "02442403",
                "02445287",
                "02446488",
                "02447662",
                "02447969",
                "02447992",
                "02448269",
            ],
            "ring size": [
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "0",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "0",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "0",
            ],
            "in/out": [
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
                "1/2",
                "1/2",
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
                "1/2",
                "1/2",
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
            ],
            "timestamp": [
                "2021-02-28 04:21:18",
                "2021-08-26 23:19:37",
                "2021-09-04 23:42:21",
                "2021-09-08 23:57:27",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-08-26 23:19:37",
                "2021-09-04 23:42:21",
                "2021-09-08 23:57:27",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-08-26 23:19:37",
                "2021-09-04 23:42:21",
                "2021-09-08 23:57:27",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
            ],
            "age [y:d:h:m:s]": [
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
            ],
        }
    )

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
    if prove == 0:
        f = open("./json/demo/decode_outputs.json")
    else:
        f = open("./json/demo/sending_prove.json")

    # returns JSON object as
    # a dictionary
    data = json.load(f)
    print(data)
    outputs_DataFrame = json_normalize(data["data"]["outputs"])
    outputs_DataFrame = outputs_DataFrame.reindex(
        columns=["output_pubkey", "amount", "match"]
    )
    outputs_DataFrame.rename(
        columns={"output_pubkey": "output public key", "match": "output match?"},
        inplace=True,
    )

    print(outputs_DataFrame)

    tx_decode_or_prove_outputs_output["address"] = data["data"]["address"]
    tx_decode_or_prove_outputs_output["tx_hash"] = data["data"]["tx_hash"]
    tx_decode_or_prove_outputs_output["viewkey"] = data["data"]["viewkey"]
    tx_decode_or_prove_outputs_output[
        "tx_public_key"
    ] = "4463830f3d76317d8e3ef6a922c8ff9c480520b49b60144d6f88f2440c978ace"
    tx_decode_or_prove_outputs_output["paymentid"] = "1c4d48af4a071950"

    tx_decode_or_prove_outputs_output["block"] = "2738885"
    tx_decode_or_prove_outputs_output["timestamp_utc"] = "2022-10-22 07:52:33"
    tx_decode_or_prove_outputs_output["age"] = "00:228:02:08:24"
    tx_decode_or_prove_outputs_output["fee"] = "99595.517"
    tx_decode_or_prove_outputs_output["tx_size"] = "1.50 kB"

    # ================================================================

    description = ""
    if prove == 0:
        description = "Checking which outputs belong to the given address and viewkey"
    else:
        description = "prove that you send this tx to the given address"
    print("address ", tx_decode_or_prove_outputs_output["address"])

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
    key_image_ring_members_DataFrame = pd.DataFrame(
        {
            "ring members": [
                "[- 00: 52c013c1e6cf535a06b3763a07651211239d225db73b5e731bba71b0733bdd87](tx52c013c1e6cf535a06b3763a07651211239d225db73b5e731bba71b0733bdd87)",
                "[- 01: d6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1](txd6cdf4e3daa6304a5b75ac9e7c3c1f3e92bd6918715002c660565e408e75a3c1)",
                "[- 02: f7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa](txf7646b9c37d2138197b137baf5d0cf65e2c7205779b86bbc412e5369b81531fa)",
                "[- 03: 4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8](tx4b19284488fb9140d89c1c6e3bfe72cb55ec21a2fcbd5f0081162a7a4894a7e8)",
                "[- 04: 82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387](tx82ee6551022def3521efe2ba86ed307f8c6327fde90c88811b15b62b24ccb387)",
                "[- 05: 8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab](tx8c217e2dfa0115215f6b510216e737499d5175b86503a3f2f5c982885db809ab)",
                "[- 06: 879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353](tx879cdada6c53ec4655168afee5d8ad6cee38cef9ec06a2ec104587627eed3353)",
                "[- 07: 0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972](tx0b1d030a5adced75f75f28cf8c35ca7daeda8961074118f7cddba637d12d7972)",
                "[- 08: ab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd](txab35133310dd16941f75746706da4909957b98be3f11c370fcff139f548517dd)",
                "[- 09: ee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881](txee8cd35e9de1cdcad1a5c250e8ad4454c0eb56771e207d8483a8b45a34845881)",
                "[- 10: f938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac](txf938a09cbf70d8b476b9515c06f741aa6e29a13b3eb29803e99f167b53f2f2ac)",
            ],
            "blk": [
                "02306487",
                "02435894",
                "02442403",
                "02445287",
                "02446488",
                "02447662",
                "02447969",
                "02447992",
                "02448269",
                "02448306",
                "02448306",
            ],
            "ring size": [
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "11",
                "0",
                "11",
                "11",
            ],
            "in/out": [
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
                "1/2",
                "1/2",
            ],
            "timestamp": [
                "2021-02-28 04:21:18",
                "2021-08-26 23:19:37",
                "2021-09-04 23:42:21",
                "2021-09-08 23:57:27",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
                "2021-02-28 04:21:18",
            ],
            "age [y:d:h:m:s]": [
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
                "02:103:22:58:49",
            ],
        }
    )
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
                                            href="page-5.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            "Transaction Pusher",
                                            href="page-5.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            "Key Images Checker",
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            "Output Keys Checker",
                                            href="page-5.4",
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
# Timestamp: 1666425153	Timestamp [UTC]: 2022-10-22 07:52:33	Age [y:d:h:m:s]: 00:228:02:08:24
# Block: 2738885	Fee (per_kB): 0.000137980000 (0.000040965938)	Tx size: 3.3682 kB
# Tx version: 2	No of confirmations: 163951	RingCT/type: yes/6
# Extra: 01d1041b3ab9294e944c1c1b1a5d3424e2af8810fae0a1160bd51aa597203f60ae0209018ecf9de6d87a19f9


# 2 output(s) for total of ? xmr
# stealth address	amount	amount idx	tag
# 00: 21e4b7d27dcdf46c7bfec7219ac8c6e82eaa8e586cf63d9f07467fec0be7d7e7	?	N/A of 74900354	<ba>
# 01: 21d470eaec5c8deb6e11a73c1525883828217d62ae35993330bcf379eea25c80	?	N/A of 74900354	<2b>
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
                                            href="page-5.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                        className="d-flex align-content-start  border border-whilte",
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
    block_transaction_infomation = {}
    block_transaction_infomation[
        "hash"
    ] = "c7e17c513d8f8fe7e271ce5343a903fd531e7214c1d706f8543a2851e1744320"
    block_transaction_infomation["outputs"] = "0.867455"
    block_transaction_infomation["size"] = "0.1025"
    block_transaction_infomation["version"] = "2"
    miner_reward_transaction_DataFrame = pd.DataFrame(
        {
            "hash": [
                "["
                + block_transaction_infomation["hash"]
                + "](tx"
                + block_transaction_infomation["hash"]
                + ")"
            ],
            "outputs": [block_transaction_infomation["outputs"]],
            "size [kB]": [block_transaction_infomation["size"]],
            "version": [block_transaction_infomation["version"]],
        }
    )

    block_transaction_infomation["num_of_transactions"] = "33"

    block_transaction_numbers_DataFrame = pd.DataFrame(
        {
            "hash": [
                "[7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53](tx7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53)",
                "[6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a](tx6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a)",
                "[2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd](tx2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd)",
                "[2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd](tx2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd)",
                "[5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0](tx5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0)",
                "[97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37](tx97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37)",
                "[f2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213](txf2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213)",
                "[c80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744](txc80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744)",
                "[65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59](tx65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59)",
                "[e2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d](txe2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d)",
                "[db96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228](txdb96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228)",
                "[7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53](tx7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53)",
                "[6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a](tx6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a)",
                "[2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd](tx2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd)",
                "[2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd](tx2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd)",
                "[5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0](tx5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0)",
                "[97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37](tx97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37)",
                "[f2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213](txf2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213)",
                "[c80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744](txc80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744)",
                "[65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59](tx65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59)",
                "[e2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d](txe2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d)",
                "[db96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228](txdb96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228)",
                "[7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53](tx7944a59efda1c2cb54dc97668566972ba8d7f73abaa8b918184329af28cd7e53)",
                "[6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a](tx6f579b10a789c8cae399e422fae8a03780a218952ed7ec83921d1fcbd696251a)",
                "[2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd](tx2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd)",
                "[2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd](tx2fba95397e861d51fd5d8677e2c0cd78d434c0213b1471bd3d7a68e52ffd35fd)",
                "[5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0](tx5b04593ea16e548a1ff111cf3e8db5d3d224791379f9e08e3e3fd5bad10350f0)",
                "[97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37](tx97df3f8dcad258b12a852c5d28c9152a553c33971b837975e24175c12aae2e37)",
                "[f2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213](txf2fba93c5ca8e95641a36b4ac19e23d85ac34f93ab7f37d4fd2ae872b532c213)",
                "[c80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744](txc80e4eb074eb40b4519028809a4377c8f3d9cbefab03fe3147a2914fb9444744)",
                "[65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59](tx65dbe3de7326b7869404a82e6ccdf771f6ac3713f46c5cefc72c6b2449a64f59)",
                "[e2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d](txe2ba7203615cf28bd147ba1600f88fabf32b55a7d605edba7ae2e101645cd54d)",
                "[db96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228](txdb96848d6da225271b6010377145ca3a4af7eefdf2522ff2a475e40a5d36a228)",
            ],
            "outputs": [
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
                "?",
            ],
            "fee [µɱ]": [
                "0210",
                "0044",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0210",
                "0044",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0210",
                "0044",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
                "0011",
            ],
            "in/out": [
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
                "1/2",
                "1/2",
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
                "1/2",
                "1/2",
                "1/2",
                "2/2",
                "2/5",
                "1/2",
                "2/2",
                "2/2",
                "1/2",
                "2/2",
                "0/1",
                "1/2",
                "1/2",
            ],
            "size [kB]": [
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
                "1.4209",
            ],
            "version": [
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
                "2",
            ],
        }
    )

    # ================================================================
    # Add query function here to load data from backend
    # And convert datatype just like above python dictionary and dataframe type
    #
    # block_transaction_infomation:                  dictionary
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
                + str(block_transaction_infomation["num_of_transactions"])
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
                                            href="page-5.1",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                        className="d-flex align-content-start  border border-whilte",
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
                                            href="page-5.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                        className="d-flex align-content-start  border border-whilte",
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
                                            href="page-5.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                                        href="page-5.1",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Transaction Pusher").upper(),
                                        href="page-5.2",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Key Images Checker").upper(),
                                        href="page-5.3",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Output Keys Checker").upper(),
                                        href="page-5.4",
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
                    className="d-flex align-content-start  border border-whilte",
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
            '(In Windows, can get the raw tx data: certuntil.exe -encode -f raw_monero_tx_encoded.ext & type "encoded.txt" | clip)',
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
                                href="/page-5.2-tx-check",
                                className="d-flex justify-content-end text-center buttonNodo me-1 mt-1 ",
                                id="submit-val_explorer_transaction_pusher_check",
                                n_clicks=0,
                                style={"textAlign": "center"},
                            ),
                            dbc.Button(
                                "Push",
                                href="/page-5.2-tx-push",
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
                                            href="page-5.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlinkActive",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                        className="d-flex align-content-start  border border-whilte",
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
                                        href="page-5.1",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Transaction Pusher").upper(),
                                        href="page-5.2",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Key Images Checker").upper(),
                                        href="page-5.3",
                                        className="sencondLevelNavlinkActive",
                                    ),
                                    dbc.NavLink(
                                        ("Output Keys Checker").upper(),
                                        href="page-5.4",
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
                    className="d-flex align-content-start  border border-whilte",
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
            "(In Linux, can get base64 signed raw tx data: based64 your_key_images_file | xclip -selection clipboard)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            '(In Windows, can get base64 signed raw tx data: certuntil.exe -encode -f your_key_images_file_encoded.txt & type "encoded.txt" | clip)',
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
            "Viewkey (key image file is encoded using your viewkey. This is needed for descryption)",
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
                                href="/page-5-3-key-images-checker-check",
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
                                            href="page-5.1",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Transaction Pusher").upper(),
                                            href="page-5.2",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Key Images Checker").upper(),
                                            href="page-5.3",
                                            className="sencondLevelNavlink",
                                        ),
                                        dbc.NavLink(
                                            ("Output Keys Checker").upper(),
                                            href="page-5.4",
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
                        className="d-flex align-content-start  border border-whilte",
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
                                        href="page-5.1",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Transaction Pusher").upper(),
                                        href="page-5.2",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Key Images Checker").upper(),
                                        href="page-5.3",
                                        className="sencondLevelNavlink",
                                    ),
                                    dbc.NavLink(
                                        ("Output Keys Checker").upper(),
                                        href="page-5.4",
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
                    className="d-flex align-content-start  border border-whilte",
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
            "(In Linux, can get base64 signed raw tx data: based64 your_key_images_file | xclip -selection clipboard)",
            className="text-center",
            style={"overflow-wrap": "break-word"},
        ),
        html.P(
            '(In Windows, can get base64 signed raw tx data: certuntil.exe -encode -f your_key_images_file_encoded.txt & type "encoded.txt" | clip)',
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
            "Viewkey (key image file is encoded using your viewkey. This is needed for descryption)",
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
                                href="/page-5-4-signed-output-public-keys-checker-check",
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
    print(pathname)
    print(str(value))
    pattTx = re.compile(".*\/tx(.*)$")
    pattBlock = re.compile(".*\/block(.*)$")
    matchPattTx = pattTx.match(pathname)
    matchPattBlock = pattBlock.match(pathname)
    if pathname == "/":
        return make_page0()
    elif pathname == "/page-0":
        return make_page0()
    elif pathname == "/page-1":
        return make_page1_1()
    elif pathname == "/page-1.1":
        return make_page1_1()
    elif pathname == "/page-1.2":
        return make_page1_2()
    elif pathname == "/page-1.3":
        return make_page1_3()
    elif pathname == "/page-2":
        return make_page2_1()
    elif pathname == "/page-2.1":
        return make_page2_1()
    elif pathname == "/page-2.2":
        return make_page2_2()
    elif pathname == "/page-3":
        return make_page3_1()
    elif pathname == "/page-3.1":
        return make_page3_1()
    elif pathname == "/page-3.2":
        return make_page3_2()
    elif pathname == "/page-3.3":
        return make_page3_3()
    elif pathname == "/page-3.3.2":
        return make_page3_3_2()
    elif pathname == "/page-4.1":
        return page4_1
    elif pathname == "/page-4.2":
        return page4_2
    elif pathname == "/page-4":
        return page4_3
    elif pathname == "/page-4.3":
        return page4_3
    elif pathname == "/page-4.4":
        return page4_4
    elif pathname == "/page-5":
        return make_page5_1()
    elif pathname == "/page-5.1":
        return make_page5_1()
    elif pathname == "/page-5.2":
        return page5_2
    elif pathname == "/page-5.2-tx-check":
        f = furl(value)
        param1 = f.args["param1"]
        print(f.args["param1"])
        return make_page_5_2_tx_check(param1)
    elif pathname == "/page-5.2-tx-push":
        f = furl(value)
        param1 = f.args["param1"]
        print(f.args["param1"])
        return make_page_5_2_tx_push(param1)
    elif pathname == "/page-5.3":
        return page5_3
    elif pathname == "/page-5-3-key-images-checker-check":
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return page5_3_key_images_checker_check(param1, param2)
    elif pathname == "/page-5.4":
        return page5_4
    elif pathname == "/page-5-4-signed-output-public-keys-checker-check":
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return page5_4_signed_output_public_keys_checker_check(param1, param2)
    elif pathname == "/page-5.1-tx-decode-outputs":
        prove = 0
        f = furl(value)
        param1 = f.args["param1"]
        param2 = f.args["param2"]
        print(f.args["param1"])
        print(f.args["param2"])
        return make_page_5_1_tx_decode_or_prove_outputs(param1, param2, prove)
    elif pathname == "/page-5.1-tx-prove-sending":
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

    return ""


# ====================================================================
# Page 1_1 Networks -> Clearnet -> Add Peer (Button)
# Trigger by clicking the clearnet -> Add Peer (Button)
# ====================================================================
@app.callback(
    Output("networks-clearnet-add-peer-hidden-div", "children"),
    Input("button-networks-clearnet-add-peer", "n_clicks"),
    [
        State("input-networks-clearnet-port", "value"),
        State("input-networks-clearnet-peer", "value"),
    ],
    prevent_initial_call=True,
)
def update_switch_networks_clearnet_add_peer(n_clicks, port, peer):
    global page1_networks_clearnet
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Button) callback by button-networks-clearnet-add-peer Port : "
        + str(port)
        + ", Peer "
        + str(peer)
    )
    page1_networks_clearnet["port"] = port
    page1_networks_clearnet["peer"] = peer

    # ================================================================
    # Add save function to write back
    # page1_networks_clearnet["port"] into backend.
    # page1_networks_clearnet["peer"] into backend.
    # ...
    # ================================================================

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
def update_switch_networks_clearnet(value):
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
    output_value = page1_networks_tor["onion_addr"]
    # ================================================================

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

    return ""


# ====================================================================
# Page 1_2 Networks -> Tor -> Add Peer (Button)
# Trigger by clicking the Tor -> Add Peer (Button)
# ====================================================================
@app.callback(
    Output("networks-tor-add-peer-hidden-div", "children"),
    Input("button-networks-tor-add-peer", "n_clicks"),
    [
        State("input-networks-tor-port", "value"),
        State("input-networks-tor-peer", "value"),
    ],
    prevent_initial_call=True,
)
def update_switch_networks_tor_add_peer(n_clicks, port, peer):
    global page1_networks_tor
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Button) callback by button-networks-tor-add-peer Port : "
        + str(port)
        + ", Peer "
        + str(peer)
    )
    page1_networks_tor["port"] = port
    page1_networks_tor["peer"] = peer

    # ================================================================
    # Add save function to write back
    # page1_networks_tor["port"] into backend.
    # page1_networks_tor["peer"] into backend.
    # ...
    # ================================================================

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

    return output_value


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

    return ""


# ====================================================================
# Page 1_3 Networks -> I2P -> Add Peer (Button)
# Trigger by clicking the I2P -> Add Peer (Button)
# ====================================================================
@app.callback(
    Output("networks-i2p-add-peer-hidden-div", "children"),
    Input("button-networks-i2p-add-peer", "n_clicks"),
    [
        State("input-networks-i2p-port", "value"),
        State("input-networks-i2p-peer", "value"),
    ],
    prevent_initial_call=True,
)
def update_switch_networks_i2p_add_peer(n_clicks, port, peer):
    global page1_networks_i2p
    ctx = dash.callback_context

    if not ctx.triggered:
        raise PreventUpdate
    print(
        "(Button) callback by button-networks-i2p-add-peer Port : "
        + str(port)
        + ", Peer "
        + str(peer)
    )
    page1_networks_i2p["port"] = port
    page1_networks_i2p["peer"] = peer

    # ================================================================
    # Add save function to write back
    # page1_networks_i2p["port"] into backend.
    # page1_networks_i2p["peer"] into backend.
    # ...
    # ================================================================

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
def update_input_node_rpc_port(value):
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
def update_input_node_rpc_port(value):
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
        return True, False
    else:
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
        return True, False
    else:
        return False, True


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
@app.callback(
    Output("active-card-input-rescan-height-hidden-div", "children"),
    Input({"type": "active-rescan-input", "index": ALL}, "value"),
)
def account_input_rescan_height(value):
    global active_address_height
    global account_address_viewkey_height
    ctx = dash.callback_context

    if value != None:
        button_id, _ = ctx.triggered[0]["prop_id"].split(".")

        print(button_id)
        button_id = json.loads(button_id)
        index_clicked = button_id["index"]
        print(
            "index clicked",
            index_clicked,
        )
        print("active-rescan-input ", value)
        (active_address_height[index_clicked])[2] = value[index_clicked]
        return ""
    else:
        return ""
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
# Page 4_3 LWS Admin -> Add Account -> Address (Input)
# ====================================================================
@app.callback(
    Output("button-lwsadmin-add-account", "disabled"),
    Input("input-lwsadmin-add-account-address", "value"),
    Input("input-lwsadmin-add-account-private-viewkey", "value"),
)
def update_add_account(addressValue, privateViewkeyValue):
    global account_address_viewkey_height
    print(addressValue)
    print(privateViewkeyValue)
    if addressValue != None and privateViewkeyValue != None:
        matchObj = re.match(r"^4", addressValue, re.M | re.I)
        if matchObj:
            return False
        else:
            print("Address must be started with 4.")
            return True

    print("Address must be started with 4.")
    return True


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
    print("==== ==== press_request_accept_button")
    print(n)
    print("++++")
    print("The pair list is :", account_address_viewkey_height)
    print("-----")
    for index in account_address_viewkey_height:
        address = index[0]
        height = index[2]
        rescan_height = ""
        active_address_height.append([address, height, rescan_height])
    print("The active_address_height pair list is :", active_address_height)
    account_address_viewkey_height.clear()
    print("++++")
    print("The pair list is :", account_address_viewkey_height)
    print("-----")
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
        address = index[0]
        height = index[2]
        rescan_height = ""
        active_address_height.append([address, height, rescan_height])
        account_address_viewkey_height.pop(index_to_remove)
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
        # active_address_height.append([address,height,rescan_height]);
        account_address_viewkey_height.pop(index_to_remove)
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
            f = furl("/page-5.1-tx-decode-outputs")
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
            f = furl("/page-5.1-tx-prove-sending")
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
            f = furl("/page-5.2-tx-check")
            f.add({"param1": textarea_explorer_transaction_pusher})
            f2 = furl("/page-5.2-tx-push")
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
            f = furl("/page-5-3-key-images-checker-check")
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
            f = furl("/page-5-4-signed-output-public-keys-checker-check")
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

    load_page0_values()
    load_page1_values()
    load_page2_values()
    load_page3_values()
    load_page4_values()
    app.run_server(host=host, port=port, debug=False)
