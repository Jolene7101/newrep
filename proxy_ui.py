import requests
import streamlit as st
import time

PROXY_API_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"

TEST_URL = "http://httpbin.org/ip"
TEST_TIMEOUT = 5

def fetch_proxies():
    try:
        resp = requests.get(PROXY_API_URL, timeout=10)
        if resp.status_code == 200:
            proxies = [line.strip() for line in resp.text.splitlines() if line.strip()]
            return proxies
        else:
            st.error(f"Failed to fetch proxies: HTTP {resp.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching proxies: {e}")
        return []

def test_proxy(proxy):
    proxies = {"http": proxy, "https": proxy}
    try:
        start = time.time()
        resp = requests.get(TEST_URL, proxies=proxies, timeout=TEST_TIMEOUT)
        latency = time.time() - start
        if resp.status_code == 200:
            return True, f"OK ({latency:.2f}s)"
        else:
            return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)

def proxy_selector_ui():
    st.subheader("Proxy Settings")
    if st.button("Load Free Proxies"):
        st.session_state['proxies'] = fetch_proxies()
        st.session_state['proxy_health'] = {}
    proxies = st.session_state.get('proxies', [])
    proxy_health = st.session_state.get('proxy_health', {})
    if proxies:
        if st.button("Test All Proxies"):
            health = {}
            with st.spinner("Testing proxies..."):
                for p in proxies[:20]:  # Limit to first 20 for speed
                    ok, msg = test_proxy(p)
                    health[p] = (ok, msg)
            st.session_state['proxy_health'] = health
            proxy_health = health
        display = []
        for p in proxies:
            status = proxy_health.get(p)
            if status is None:
                display.append(f"{p} (untested)")
            else:
                emoji = "🟢" if status[0] else "🔴"
                display.append(f"{emoji} {p} [{status[1]}]")
        selected = st.selectbox("Select a proxy for scraping:", proxies, format_func=lambda x: next((d for d in display if x in d), x), key="proxy_select")
        st.session_state['selected_proxy'] = selected
        st.success(f"Proxy selected: {selected}")
    else:
        st.info("No proxies loaded. Click 'Load Free Proxies' to fetch.")

def get_selected_proxy():
    return st.session_state.get('selected_proxy', None)
