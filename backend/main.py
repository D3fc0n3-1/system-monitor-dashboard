from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import requests
import config  # Import the config module
from urllib.parse import urljoin

app = FastAPI()

SERVER_CONFIGS = []  # Global variable to store server configurations


@app.on_event("startup")
async def startup_event():
    """Loads server configurations on startup."""
    global SERVER_CONFIGS
    try:
        SERVER_CONFIGS = config.load_config()
    except Exception as e:
        print(f"Error loading configuration during startup: {e}")
        # In a real application, you might want to handle this more gracefully,
        # e.g., stop the app or use default configurations.


def fetch_glances_data(glances_api_url: str) -> Dict[str, Any]:
    """Fetches data from a Glances API endpoint."""
    try:
        # Determine the correct API endpoint suffix ('all' or maybe something else?)
        # For now, we assume 'all' works based on previous tests, but keep API version in mind
        api_suffix = "all"
        full_url = urljoin(glances_api_url, api_suffix)
        # print(f"DEBUG: Fetching data from URL: {full_url}") # Debug URL
        response = requests.get(full_url, timeout=5) # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.Timeout:
         # print(f"ERROR: Timeout fetching data from {glances_api_url}")
         raise HTTPException(status_code=504, detail=f"Timeout fetching data from Glances API: {glances_api_url}")
    except requests.exceptions.RequestException as e:
        # print(f"ERROR: RequestException fetching data from {glances_api_url}: {e}") # Debug error
        raise HTTPException(status_code=500, detail=f"Error fetching data from Glances API: {e}")


@app.get("/servers")
async def get_servers_overview() -> List[Dict[str, Any]]:
    """Returns an overview of all configured servers."""
    servers_overview = []
    for server_config in SERVER_CONFIGS:
        server_name = server_config.get('name', 'Unknown') # Use .get() for safety
        server_id = server_name # Use name as ID for now
        try:
            # print(f"\n--- Processing Server: {server_name} ---")
            glances_data = fetch_glances_data(server_config['glances_api_url'])

            # --- Disk I/O Calculation ---
            # print(f"DEBUG: {server_name} - Starting Disk I/O calculation...") # Keep this one temporarily if you like
            disk_io_rate_mbps = 0 # Initialize rate
            diskio_list = glances_data.get('diskio', [])
            if isinstance(diskio_list, list): # <<< Start of IF block
                disk_io_bytes_sec_list = []
                for i, disk_stats in enumerate(diskio_list):
                    if isinstance(disk_stats, dict):
                        # Use '_ps' keys for rate (Bytes/sec)
                        read_ps = disk_stats.get('read_bytes_ps', 0) or 0
                        write_ps = disk_stats.get('write_bytes_ps', 0) or 0
                        disk_io_bytes_sec_list.append(read_ps + write_ps)
                    # else: # Optional inner else (can be removed if empty)
                        # pass # Or keep the commented-out print if you prefer
                disk_io_bytes_sec_total = sum(disk_io_bytes_sec_list)
                # Convert Bytes/sec to Megabytes/sec (MB/s)
                disk_io_rate_mbps = disk_io_bytes_sec_total / (1024 * 1024)
                # Line 71 might have been here
            # <<< End of IF block. NO 'else' here.
            # --- Network I/O Calculation ---
            #  print(f"DEBUG: {server_name} - Starting Network I/O calculation...")
            net_io_rate_mbps = 0
            network_data = glances_data.get('network', []) # Default to empty list now
            # print(f"DEBUG: {server_name} - Type of network_data: {type(network_data)}")

            if isinstance(network_data, list): # <--- Check if it's a LIST
                # print(f"DEBUG: {server_name} - network_data IS a list (Length: {len(network_data)}). Iterating...")
                net_io_bytes_sec_list = []
                for i, interface in enumerate(network_data): # <--- Iterate through the list
                    # print(f"DEBUG: {server_name} - Processing interface {i}. Type: {type(interface)}")
                    if isinstance(interface, dict): # Each item in the list should be a dict
                        # Use 'bytes_sent_rate_per_sec' and 'bytes_recv_rate_per_sec' if available (Glances v4?)
                        # Fallback to 'tx_bytes_ps' and 'rx_bytes_ps' (Glances v3?)
                        tx = interface.get('bytes_sent_rate_per_sec', interface.get('tx_bytes_ps', 0)) or 0
                        rx = interface.get('bytes_recv_rate_per_sec', interface.get('rx_bytes_ps', 0)) or 0
                        # print(f"DEBUG: {server_name} - Interface {i} IS dict. tx_ps={tx}, rx_ps={rx}")
                        net_io_bytes_sec_list.append(tx + rx)
                    else:
                        # print(f"WARN: {server_name} - Interface {i} in list IS NOT dict. Skipping.")
                # print(f"DEBUG: {server_name} - net_io_bytes_sec_list: {net_io_bytes_sec_list}")
                net_io_bytes_sec_total = sum(net_io_bytes_sec_list)
                # Convert Bytes/sec to Megabits/sec (Mbps) which is more common for network speed
                net_io_rate_mbps = (net_io_bytes_sec_total * 8) / (1024 * 1024)
                # print(f"DEBUG: {server_name} - Calculated net_io_rate_mbps: {net_io_rate_mbps}")
            else:
                 # print(f"WARN: {server_name} - network_data IS NOT a list ({type(network_data)}). Skipping network calculation.")

            # --- Assemble Overview Data ---
            # print(f"DEBUG: {server_name} - Assembling overview data...")
            cpu_data = glances_data.get('cpu', {})
            mem_data = glances_data.get('mem', {})
            overview_data = {
                "id": server_id,
                "name": server_name,
                "cpu_usage_percent": cpu_data.get('total', 0) if isinstance(cpu_data, dict) else 0,
                "mem_usage_percent": mem_data.get('percent', 0) if isinstance(mem_data, dict) else 0,
                "disk_io_rate": disk_io_rate_mbps, # Still needs proper rate calculation
                "net_io_rate": net_io_rate_mbps,
                "status": "online"
            }
            servers_overview.append(overview_data)
            # print(f"--- Finished Processing Server: {server_name} (Status: online) ---")

        except HTTPException as e:
             # print(f"ERROR: {server_name} - HTTPException caught: {e.status_code} - {e.detail}")
             servers_overview.append({
                 "id": server_id,
                 "name": server_name,
                 "status": "offline", # Or maybe "unreachable"?
                 "error": str(e.detail)
             })
             # print(f"--- Finished Processing Server: {server_name} (Status: offline/error) ---")
        except Exception as e:
             # Catching the specific AttributeError here if it propagates
             # print(f"ERROR: {server_name} - Outer Exception caught: {type(e).__name__}: {e}")
             import traceback
             # traceback.print_exc() # Print full traceback for unexpected errors
             servers_overview.append({
                 "id": server_id,
                 "name": server_name,
                 "status": "error",
                 "error": f"Unexpected error: {e}"
             })
             # print(f"--- Finished Processing Server: {server_name} (Status: error) ---")

    return servers_overview


@app.get("/servers/{server_id}")
async def get_server_details(server_id: str) -> Dict[str, Any]:
    """Returns detailed information for a specific server."""
    server_config = next((server for server in SERVER_CONFIGS if server.get('name') == server_id), None)
    if not server_config:
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        glances_data = fetch_glances_data(server_config['glances_api_url'])
        return glances_data
    except HTTPException as e:
        raise e # Re-raise the HTTPException from fetch_glances_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving server details: {e}")
