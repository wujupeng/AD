-- Update dc4 record: now a domain controller for cii.sh.cn
UPDATE dc_registries 
SET dc_hostname = 'dc4',
    dc_site = 'cii_factory',
    is_gc = true,
    is_dns_integrated = true,
    os_version = 'Windows Server 2022 (DC)',
    health_status = 'healthy'
WHERE dc_ip_address = '192.168.1.11';

-- Also update site_configs to reflect dc4 as part of cii_factory
SELECT dc_hostname, dc_site, dc_ip_address, is_gc, is_dns_integrated, health_status, os_version FROM dc_registries ORDER BY dc_ip_address;
