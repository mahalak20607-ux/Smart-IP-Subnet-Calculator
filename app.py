
import ipaddress
from io import StringIO

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Smart IP Subnet Calculator",
    page_icon="🌐",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 750;
        margin-bottom: 0;
    }
    .subtitle {
        color: #94a3b8;
        margin-top: 5px;
        margin-bottom: 22px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def calculate_subnet(ip_text, prefix):
    """Validate IPv4 input and calculate subnet information."""
    try:
        interface = ipaddress.IPv4Interface(f"{ip_text}/{prefix}")
        network = interface.network
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError,
            ValueError) as exc:
        raise ValueError("Enter a valid IPv4 address and prefix.") from exc

    if network.prefixlen == 32:
        first_host = str(network.network_address)
        last_host = str(network.network_address)
        usable_hosts = 1
    elif network.prefixlen == 31:
        first_host = str(network.network_address)
        last_host = str(network.broadcast_address)
        usable_hosts = 2
    else:
        first_host = str(network.network_address + 1)
        last_host = str(network.broadcast_address - 1)
        usable_hosts = network.num_addresses - 2

    mask_bits = f"{int(network.netmask):032b}"
    binary_mask = ".".join(
        mask_bits[i:i + 8] for i in range(0, 32, 8)
    )

    return {
        "input_ip": str(interface.ip),
        "cidr": network.prefixlen,
        "network": str(network.network_address),
        "netmask": str(network.netmask),
        "wildcard": str(network.hostmask),
        "broadcast": str(network.broadcast_address),
        "first_host": first_host,
        "last_host": last_host,
        "total_addresses": network.num_addresses,
        "usable_hosts": usable_hosts,
        "binary_mask": binary_mask,
        "network_object": network,
    }


def split_subnets(network, new_prefix):
    """Split a network into smaller subnets."""
    if new_prefix < network.prefixlen:
        raise ValueError(
            "New prefix must be greater than or equal to the current prefix."
        )

    if new_prefix > 32:
        raise ValueError("Prefix cannot exceed 32.")

    return list(network.subnets(new_prefix=new_prefix))


# Sidebar
st.sidebar.title("🌐 Smart IP Calculator")
st.sidebar.caption("IPv4 addressing and subnetting tool")
st.sidebar.divider()
st.sidebar.markdown("### Quick Guide")
st.sidebar.write("1. Enter an IPv4 address.")
st.sidebar.write("2. Select a CIDR prefix.")
st.sidebar.write("3. View subnet details.")
st.sidebar.write("4. Generate a subnet report.")
st.sidebar.divider()
st.sidebar.caption("Built for Computer Networks learning.")

# Header
st.markdown(
    '<div class="main-title">🌐 Smart IP Address & Subnet Calculator</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Calculate IPv4 network details, host ranges, and smaller subnets.'
    '</div>',
    unsafe_allow_html=True,
)

# Inputs
st.subheader("IP Address Configuration")

col_ip, col_prefix = st.columns([2, 1])

with col_ip:
    ip_text = st.text_input(
        "IPv4 Address",
        value="192.168.1.10",
        placeholder="Example: 192.168.1.10",
    ).strip()

with col_prefix:
    prefix = st.selectbox(
        "CIDR Prefix",
        options=list(range(8, 33)),
        index=16,  # /24
        format_func=lambda value: f"/{value}",
    )

try:
    result = calculate_subnet(ip_text, prefix)
except ValueError:
    st.error("Invalid input. Example: 192.168.1.10 with prefix /24.")
    st.stop()

network = result["network_object"]

st.success(
    f"Valid IPv4 address: {result['input_ip']}/{result['cidr']}"
)

# Main metrics
st.subheader("Network Summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total IP Addresses", f"{result['total_addresses']:,}")
m2.metric("Usable Host Addresses", f"{result['usable_hosts']:,}")
m3.metric("CIDR Prefix", f"/{result['cidr']}")
m4.metric("Subnet Mask", result["netmask"])

st.divider()

# Detailed information
st.subheader("Subnet Details")

detail_col1, detail_col2 = st.columns(2)

with detail_col1:
    st.markdown("#### Network Information")
    st.text_input(
        "Network Address",
        value=result["network"],
        disabled=True,
    )
    st.text_input(
        "Broadcast Address",
        value=result["broadcast"],
        disabled=True,
    )
    st.text_input(
        "Wildcard Mask",
        value=result["wildcard"],
        disabled=True,
    )

with detail_col2:
    st.markdown("#### Host Information")
    st.text_input(
        "First Usable Host",
        value=result["first_host"],
        disabled=True,
    )
    st.text_input(
        "Last Usable Host",
        value=result["last_host"],
        disabled=True,
    )
    st.text_input(
        "Binary Subnet Mask",
        value=result["binary_mask"],
        disabled=True,
    )

# Address-space visualization
st.divider()
st.subheader("Address Space Visualization")

if result["total_addresses"] <= 256:
    st.caption(
        f"This subnet contains {result['total_addresses']} IPv4 addresses."
    )
    st.progress(
        min(result["usable_hosts"] / result["total_addresses"], 1.0),
        text="Usable host address proportion",
    )
else:
    st.info(
        f"This subnet contains {result['total_addresses']:,} addresses. "
        "A full address-by-address view is omitted for large subnets."
    )

# Subnet splitting
st.divider()
st.subheader("Subnet Division")

st.write(
    "Current network-ai smaller subnets-ah split pannalaam. "
    "New prefix current prefix-ai vida smaller subnet size create pannum."
)

default_new_prefix = min(network.prefixlen + 2, 32)

split_prefix = st.selectbox(
    "New subnet prefix",
    options=list(range(network.prefixlen, 33)),
    index=default_new_prefix - network.prefixlen,
    format_func=lambda value: f"/{value}",
)

subnet_count = 2 ** (split_prefix - network.prefixlen)

st.caption(f"Generated subnets: {subnet_count:,}")

if subnet_count > 512:
    st.warning(
        "This setting creates more than 512 subnets. "
        "Choose a larger prefix to generate a smaller list."
    )
else:
    subnets = split_subnets(network, split_prefix)

    subnet_rows = []
    for index, subnet in enumerate(subnets, start=1):
        if subnet.prefixlen == 32:
            usable = 1
        elif subnet.prefixlen == 31:
            usable = 2
        else:
            usable = subnet.num_addresses - 2

        subnet_rows.append({
            "Subnet #": index,
            "Network Address": str(subnet.network_address),
            "CIDR": f"/{subnet.prefixlen}",
            "Broadcast Address": str(subnet.broadcast_address),
            "Total Addresses": subnet.num_addresses,
            "Usable Hosts": usable,
        })

    subnet_df = pd.DataFrame(subnet_rows)
    st.dataframe(subnet_df, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download Subnet Report (CSV)",
        data=subnet_df.to_csv(index=False).encode("utf-8"),
        file_name="subnet_report.csv",
        mime="text/csv",
    )

# Full calculation report
st.divider()
st.subheader("Export Calculation")

report_df = pd.DataFrame([{
    "Input IP": result["input_ip"],
    "CIDR": f"/{result['cidr']}",
    "Network Address": result["network"],
    "Subnet Mask": result["netmask"],
    "Wildcard Mask": result["wildcard"],
    "Broadcast Address": result["broadcast"],
    "First Usable Host": result["first_host"],
    "Last Usable Host": result["last_host"],
    "Total Addresses": result["total_addresses"],
    "Usable Hosts": result["usable_hosts"],
}])

st.download_button(
    "⬇️ Download IP Calculation (CSV)",
    data=report_df.to_csv(index=False).encode("utf-8"),
    file_name="ip_calculation_report.csv",
    mime="text/csv",
)

st.caption(
    "Note: /31 is treated as a point-to-point subnet and /32 as a "
    "single-address route. This tool calculates IPv4 subnet information; "
    "it does not configure your computer or router."
)
