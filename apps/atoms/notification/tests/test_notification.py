from unittest.mock import patch, MagicMock
from apps.atoms.notification import service

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_notification_log(client):
    service.notification_log.clear()
    service.notification_log.append({"to": "123", "body": "test", "status": "MOCK_SENT"})
    
    response = client.get("/notifications/log")
    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 1

def test_send_sms_no_creds():
    with patch("apps.atoms.notification.service.TWILIO_SID", ""):
        service.notification_log.clear()
        res = service.send_sms("123", "hello")
        assert res["status"] == "MOCK_SENT"
        assert len(service.notification_log) == 1

def test_on_notification_confirmed():
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.routing_key = "order.confirmed"
    mock_method.delivery_tag = 1
    
    body = '{"phone_number": "123", "order_id": "O1"}'
    
    service.notification_log.clear()
    service.on_notification(mock_channel, mock_method, None, body)
    
    assert len(service.notification_log) == 1
    assert "ORDER_CONFIRMED" in service.notification_log[0]["body"]
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

def test_on_notification_failed():
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.routing_key = "order.failed"
    mock_method.delivery_tag = 2
    
    body = '{"phone_number": "123", "order_id": "O1"}'
    
    service.notification_log.clear()
    service.on_notification(mock_channel, mock_method, None, body)
    
    assert "ORDER_CANCELLED" in service.notification_log[0]["body"]
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=2)

def test_on_notification_general():
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.routing_key = "notify.sms"
    mock_method.delivery_tag = 3
    
    body = '{"phone_number": "123", "message": "Manual alert"}'
    
    service.notification_log.clear()
    service.on_notification(mock_channel, mock_method, None, body)
    
    assert "GENERAL" in service.notification_log[0]["body"]
    assert "Manual alert" in service.notification_log[0]["body"]
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=3)

def test_on_notification_error():
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 4
    
    body = 'invalid json'
    
    service.on_notification(mock_channel, mock_method, None, body)
    mock_channel.basic_nack.assert_called_once_with(delivery_tag=4, requeue=True)
