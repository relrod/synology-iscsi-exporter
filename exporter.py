#!/usr/bin/env python3
import os
import time

from prometheus_client import start_http_server, Gauge
from synology_api import core_sys_info

class CoreSysInfo(core_sys_info.SysInfo):
    def iscsi_lun_info(self) -> dict[str, object] | str:
        api_name = 'SYNO.Core.ISCSI.LUN'
        info = self.gen_list[api_name]
        api_path = info['path']
        req_param = {'version': info['maxVersion'], 'method': 'list', 'additional': '["allocated_size"]'}
        return self.request_data(api_name, api_path, req_param)

class LUNExporter:
    def __init__(self, dsm_host, dsm_port, dsm_user, dsm_pass, dsm_secure, dsm_cert_verify, dsm_version):
        self.client = CoreSysInfo(
            dsm_host,
            dsm_port,
            dsm_user,
            dsm_pass,
            secure=dsm_secure,
            cert_verify=dsm_cert_verify,
            dsm_version=7,
            debug=True,
            otp_code=None
        )
        self.lun_allocated_size = Gauge('lun_allocated_size', 'Allocated size of LUN', labelnames=['name', 'lun_id'], unit='bytes')
        self.lun_size = Gauge('lun_size', 'Used size of LUN in bytes', labelnames=['name', 'lun_id'], unit='bytes')

    def get_lun_sizes(self):
        luns = self.client.iscsi_lun_info()['data']['luns']
        for lun in luns:
            self.lun_allocated_size.labels(lun['name'], lun['lun_id']).set(lun['allocated_size'])
            self.lun_size.labels(lun['name'], lun['lun_id']).set(lun['size'])

def main():
    start_http_server(19001)
    dsm_host = os.environ.get('DSM_HOST')
    dsm_port = os.environ.get('DSM_PORT')
    dsm_user = os.environ.get('DSM_USERNAME')
    dsm_pass = os.environ.get('DSM_PASSWORD')
    dsm_secure = os.environ.get('DSM_SECURE') in ['True', 'true', '1']
    dsm_cert_verify = os.environ.get('DSM_CERT_VERIFY') in ['True', 'true', '1']
    dsm_version = os.environ.get('DSM_VERSION', '7')
    exporter = LUNExporter(dsm_host, dsm_port, dsm_user, dsm_pass, dsm_secure, dsm_cert_verify, dsm_version)

    while True:
        exporter.get_lun_sizes()
        time.sleep(60)

if __name__ == '__main__':
    main()
