import pytest
import httpx
import os

TOKEN = os.getenv('INTELAI_INTERNAL_TOKEN', '')
HEADERS = {'X-IntelAI-Internal-Token': TOKEN}
BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:8000')
job_id = "test"
file_id = "test"
session_id = "test"
user_id = "test"
log_id = "test"


@pytest.mark.asyncio
async def test_e2e_api_get__health_0():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/health', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_status_1():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/status', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_auth_login_2():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/auth/login', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_auth_demo_login_3():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/auth/demo-login', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_auth_register_4():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/auth/register', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_auth_me_5():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/auth/me', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_chat_6():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/chat', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_personas_7():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/personas', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_glossary_8():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/glossary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_files_9():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/files', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_files_file_id_preview_10():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/files/{file_id}/preview', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_delete__api_v1_files_file_id_11():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.delete(f'{BASE_URL}/api/v1/files/{file_id}', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_files_file_id_download_12():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/files/{file_id}/download', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_ingest_metrics_13():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/ingest/metrics', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_ingest_csv_14():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/ingest/csv', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_ingest_document_15():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/ingest/document', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_kpis_16():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/kpis', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_kpis_periods_17():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/kpis/periods', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_kpis_metrics_18():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/kpis/metrics', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_kpis_categories_19():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/kpis/categories', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_financial_statement_20():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/financial/statement', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_forecast_21():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/forecast', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_insights_health_22():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/insights/health', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_insights_risk_23():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/insights/risk', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_insights_summary_24():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/insights/summary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_insights_anomalies_25():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/insights/anomalies', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_hr_summary_26():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/hr/summary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_hr_departments_27():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/hr/departments', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_hr_recruitment_28():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/hr/recruitment', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_hr_training_29():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/hr/training', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_hr_health_30():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/hr/health', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_logistics_summary_31():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/logistics/summary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_logistics_inventory_32():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/logistics/inventory', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_logistics_shipping_33():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/logistics/shipping', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_logistics_suppliers_34():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/logistics/suppliers', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_logistics_health_35():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/logistics/health', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_it_overview_36():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/it/overview', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_it_tickets_37():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/it/tickets', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_it_security_38():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/it/security', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_it_infrastructure_39():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/it/infrastructure', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_it_devops_40():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/it/devops', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_it_health_41():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/it/health', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_operations_summary_42():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/operations/summary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_operations_quality_43():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/operations/quality', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_operations_production_44():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/operations/production', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_operations_safety_45():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/operations/safety', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_operations_health_46():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/operations/health', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_growth_summary_47():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/growth/summary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_esg_summary_48():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/esg/summary', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_agent_tools_49():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/agent/tools', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_agent_run_50():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/agent/run', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_admin_users_51():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/admin/users', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_put__api_v1_admin_users_user_id_52():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.put(f'{BASE_URL}/api/v1/admin/users/{user_id}', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_admin_roles_53():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/admin/roles', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_admin_audit_54():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/admin/audit', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_admin_seed_55():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/admin/seed', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_admin_scenario_56():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/admin/scenario', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_admin_scenario_57():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/admin/scenario', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_admin_cleanup_58():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/admin/cleanup', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_admin_vsdebug_59():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/admin/vsdebug', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_admin_reindex_60():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/admin/reindex', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_chat_sessions_61():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/chat/sessions', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_chat_sessions_session_id_messages_62():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/chat/sessions/{session_id}/messages', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_chat_sessions_63():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/chat/sessions', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_put__api_v1_chat_sessions_session_id_title_64():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.put(f'{BASE_URL}/api/v1/chat/sessions/{session_id}/title', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_delete__api_v1_chat_sessions_session_id_65():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.delete(f'{BASE_URL}/api/v1/chat/sessions/{session_id}', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_knowledge_search_66():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/knowledge/search', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_knowledge_stats_67():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/knowledge/stats', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_chatbot_domain_68():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/chatbot/domain', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_get__api_v1_chatbot_domain_69():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.get(f'{BASE_URL}/api/v1/chatbot/domain', headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

@pytest.mark.asyncio
async def test_e2e_api_post__api_v1_data_export_70():
    # Extracted from server.py
    async with httpx.AsyncClient() as ac:
        response = await ac.post(f'{BASE_URL}/api/v1/data/export', json={}, headers=HEADERS)
        assert response.status_code in (200, 400, 401, 403, 404, 405, 422)

