import requests
import pandas as pd
import json
from collections import defaultdict
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

API_BASE_URL = "https://svm.cert.siemens.com/portal/api/v1/"
CLIENT_CERT = "C:/Users/z0051rra/OneDrive - Innomotics/OpenSSL-Win64/bin/certificate.pem"
CLIENT_KEY = "C:/Users/z0051rra/OneDrive - Innomotics/OpenSSL-Win64/bin/pri-key.pem"
CLIENT_KEY_PASSPHRASE = "arbazkhan123456789$@"
CA_BUNDLE = "C:/Users/z0051rra/OneDrive - Innomotics/OpenSSL-Win64/bin/ca-bundle.pem"

# === SSL Adapter with passphrase ===
class SSLAdapterWithPassphrase(HTTPAdapter):
    def __init__(self, certfile, keyfile, password, ca_bundle, **kwargs):
        self.certfile = certfile
        self.keyfile = keyfile
        self.password = password
        self.ca_bundle = ca_bundle
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile, password=self.password)
        context.load_verify_locations(self.ca_bundle)
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# === Create session ===
session = requests.Session()
adapter = SSLAdapterWithPassphrase(
    certfile=CLIENT_CERT,
    keyfile=CLIENT_KEY,
    password=CLIENT_KEY_PASSPHRASE,
    ca_bundle=CA_BUNDLE
)
session.mount('https://', adapter)

# === Functions ===
def get_monitoring_list_ids():
    url = urljoin(API_BASE_URL, "common/monitoring_lists")
    response = session.get(url)
    response.raise_for_status()
    return response.json()

def get_monitoring_list_details(list_id):
    url = urljoin(API_BASE_URL, f"common/monitoring_lists/{list_id}")
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "name": data.get("name"),
            "creation_date": data.get("creation_date")
        }
    else:
        print(f"Warning: Could not fetch details for ID {list_id}")
        return None

def get_monitoring_list_components(list_id):
    url = urljoin(API_BASE_URL, f"common/monitoring_lists/{list_id}/components")
    response = session.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Warning: Could not fetch details for ID {list_id}")
        return None


def get_component_details(comp_id):
    url = urljoin(API_BASE_URL, f"public/components/{comp_id}")
    response = session.get(url)
    if response.status_code == 200:
        comp = response.json()
        return {
            "component_id ": comp.get("component_id"),
            "component_name": comp.get("component_name"),
            "version": comp.get("version"),
            "monitored_since": comp.get("monitored_since"),
            "eol_date": comp.get("eol_date"),
            "eol_reached": comp.get("eol_reached"),
        }
    else:
        print(f"Warning: Could not fetch component details for ID {comp_id}")
        return None
    
# def get_monitoring_list_subscribers(list_id):
#     url = urljoin(API_BASE_URL, f"common/monitoring_lists/{list_id}/subscribers")
#     response = session.get(url)
#     if response.status_code == 200:
#         subs = response.json()
#         return [
#             {
#                 "gid": sub.get("gid"),
#                 "email": sub.get("email"),
#                 "first_name": sub.get("first_name"),
#                 "last_name": sub.get("last_name"),
#                 "role": sub.get("role")
#             } for sub in subs
#         ]
#     else:
#         print(f"Warning: Could not fetch subscribers for list ID {list_id}")
#         return []


# def unique_component_usages_with_details():
#     component_usage = defaultdict(int)
#     details_dict = {}
#     comp_id_to_list_ids = defaultdict(set)
#     for list_id in get_monitoring_list_ids():
#         component_ids = get_monitoring_list_components(list_id)
#         unique_components_in_list = set(component_ids)
#         for comp_id in unique_components_in_list:
#             comp_id_to_list_ids[comp_id].add(list_id)
#             component_usage[comp_id] += 1
#             if comp_id not in details_dict:
#                 details = get_component_details(comp_id)
#                 if details:
#                     details_dict[comp_id] = details

#             list_name = get_monitoring_list_names(list_id)
#             list_subscribers = get_monitoring_list_subscribers(list_id)
#             if list_name is not None:
#                 sub_details = "\n".join(
#                     [f" {sub['gid']} | {sub['email']} | {sub['first_name']} | {sub['last_name']} | {sub['role']}" for sub in list_subscribers]) or " No subscribers"
#                 monitoring_info = f"{list_name}: \n{sub_details}"
#                 if "monitoring_lists" in details_dict[comp_id]:
#                     details_dict[comp_id]["monitoring_lists"] += f"\n\n{monitoring_info}"
#                 else:
#                     details_dict[comp_id]["monitoring_lists"] = monitoring_info
        

#     details_with_usage = []
#     for comp_id, usage_count in component_usage.items():
#         details = details_dict.get(comp_id, {})
#         details["usage"] = usage_count
#         monitoring_info = details.get("monitoring_lists", "No monitoring lists")
#         details["monitoring_lists"] = monitoring_info
#         details_with_usage.append(details)

#     return details_with_usage

def unique_component_usages_with_details():
    component_usage = defaultdict(int)
    details_dict = {}
    comp_id_to_list_ids = defaultdict(list)
    for list_id in get_monitoring_list_ids():

        list_data = get_monitoring_list_details(list_id)
        name = list_data.get("name", "Unknown List")
        creation_date = list_data.get("creation_date", "Unknown Date")

        component_ids = get_monitoring_list_components(list_id)
        unique_components_in_list = set(component_ids)
        for comp_id in unique_components_in_list:

            monitoring_list_entry = f"{name}\n{creation_date}"
            # comp_id_to_list_ids[comp_id].add(list_id)
            if monitoring_list_entry not in comp_id_to_list_ids[comp_id]:
                comp_id_to_list_ids[comp_id].append(monitoring_list_entry)

            component_usage[comp_id] += 1
            if comp_id not in details_dict:
                details = get_component_details(comp_id)
                if details:
                    details_dict[comp_id] = details

    details_with_usage = []
    for comp_id, usage_count in component_usage.items():
        details = details_dict.get(comp_id, {})
        details["usage"] = usage_count

        monitoring_list_info = comp_id_to_list_ids.get(comp_id, [])
        for i, monitoring_list_entry in enumerate(monitoring_list_info):
            details[f"monitoring_list_{i+1}"] = monitoring_list_entry

        details_with_usage.append(details)

    return details_with_usage


def export_to_excel(component_usage, filename="monitoring_lists.xlsx"):
    # df = pd.DataFrame(list(component_usage.items()), cSolumns=['Component', 'Usage Count'])
    df = pd.DataFrame(component_usage)
    df.to_excel(filename, index=False)
    print(f"Exported {len(component_usage)} records to {filename}")

def export_to_json(data, filename="monitoring_lists.json"):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Exported {len(data)} records to {filename}")

def main():
    unique_usage_dict = unique_component_usages_with_details()
    if unique_usage_dict:
        export_to_excel(unique_usage_dict)
        export_to_json(unique_usage_dict)
    else:
        print("No data to export.")

if __name__ == "__main__":
    main()