-- Update dc4/dcser1 OS versions
UPDATE dc_registries SET os_version = 'Windows Server 2022 Standard' WHERE dc_hostname = 'dc4';
UPDATE dc_registries SET os_version = 'Windows Server 2022 Standard' WHERE dc_hostname = 'dcser1';

-- Seed LDAP directory configs
INSERT INTO ldap_directory_configs (config_id, config_name, server_url, base_dn, bind_dn, bind_password_encrypted, search_filter, connection_test_status, is_enabled, created_at, updated_at)
VALUES
('ldap-hq-001', 'HQ-AD-LDAP', 'ldap://192.168.2.110', 'DC=company,DC=local', 'CN=svc_adbiz,OU=ServiceAccounts,OU=Company,DC=company,DC=local', 'SvcP@ss2026!', '(objectClass=user)', 'success', true, NOW(), NOW()),
('ldap-cii-001', 'CII-AD-LDAP', 'ldap://192.168.2.88', 'DC=cii,DC=sh,DC=cn', 'CN=Administrator,CN=Users,DC=cii,DC=sh,DC=cn', 'Htkiss@01', '(objectClass=user)', 'success', true, NOW(), NOW())
ON CONFLICT (config_name) DO NOTHING;

-- Seed DFS replication links
INSERT INTO dfs_replication_links (link_id, source_site, target_site, replicated_folders, backlog_count, last_sync_time, sync_latency_seconds, bandwidth_usage_mbps, link_status)
VALUES
('dfsr-hq-cii-001', 'hq', 'cii_factory', ARRAY['share','SYSVOL'], 0, NOW(), 5, 12.5, 'healthy'),
('dfsr-cii-hq-001', 'cii_factory', 'hq', ARRAY['share','SYSVOL'], 0, NOW(), 5, 12.5, 'healthy')
ON CONFLICT (source_site, target_site) DO NOTHING;

-- Seed PKI certificate templates
INSERT INTO pki_certificate_templates (template_name, usage_scenario, template_oid, key_length, validity_period_days, auto_enrollment, is_enabled, description)
VALUES
('WebServer', 'server_authentication', '1.3.6.1.5.5.7.3.1', 2048, 365, false, true, 'Web服务器SSL证书'),
('UserAuthentication', 'client_authentication', '1.3.6.1.5.5.7.3.2', 2048, 365, true, true, '用户身份验证证书'),
('CodeSigning', 'code_signing', '1.3.6.1.5.5.7.3.3', 4096, 730, false, true, '代码签名证书'),
('DocumentEncryption', 'email_protection', '1.3.6.1.5.5.7.3.4', 2048, 365, true, true, '文档加密/邮件保护证书'),
('MachineAuthentication', 'client_authentication', '1.3.6.1.5.5.7.3.2', 2048, 365, true, true, '计算机身份验证证书')
ON CONFLICT (template_name) DO NOTHING;

-- Seed external integration configs
INSERT INTO external_integration_configs (integration_id, integration_type, integration_name, server_url, api_key_encrypted, connection_status, extra_config, is_enabled, created_at, updated_at)
VALUES
('ext-zabbix-001', 'zabbix', 'Zabbix监控', 'http://192.168.2.110:8080', NULL, 'connected', '{"host": "192.168.2.110", "port": 8080}', true, NOW(), NOW()),
('ext-veeam-001', 'veeam', 'Veeam备份', 'http://192.168.2.110:9398', NULL, 'not_tested', '{"repo": "DefaultBackupRepo"}', true, NOW(), NOW()),
('ext-entra-001', 'entra_id', 'Entra ID同步', 'https://graph.microsoft.com', NULL, 'not_tested', '{"tenant_id": "contoso.onmicrosoft.com"}', false, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Verify counts
SELECT 'ldap_directory_configs' AS tbl, COUNT(*) AS cnt FROM ldap_directory_configs
UNION ALL SELECT 'dfs_replication_links', COUNT(*) FROM dfs_replication_links
UNION ALL SELECT 'pki_certificate_templates', COUNT(*) FROM pki_certificate_templates
UNION ALL SELECT 'external_integration_configs', COUNT(*) FROM external_integration_configs
UNION ALL SELECT 'dc_registries (192.168)', COUNT(*) FROM dc_registries WHERE dc_ip_address LIKE '192.168%';
