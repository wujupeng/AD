SELECT 'ad_users' AS tbl, COUNT(*) AS cnt FROM ad_users
UNION ALL SELECT 'ad_groups', COUNT(*) FROM ad_groups
UNION ALL SELECT 'ad_ous', COUNT(*) FROM ad_ous
UNION ALL SELECT 'ad_group_members', COUNT(*) FROM ad_group_members
UNION ALL SELECT 'dc_registries', COUNT(*) FROM dc_registries;
