-- Update old onboarding requests to completed status
UPDATE hr_onboarding_requests SET status = 'completed', step_results = '{"db_record": "success", "ad_user_created": "skipped"}' WHERE status = 'pending';

-- Update old offboarding requests to completed status
UPDATE hr_offboarding_requests SET status = 'completed', step_results = '{"db_record": "success", "ad_account_disabled": "skipped"}' WHERE status = 'pending';

-- Verify
SELECT sam_account_name, status, step_results FROM hr_onboarding_requests;